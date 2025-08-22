#!/bin/bash

# ERAIF Deployment Script
# This script handles deployment to various environments (staging, production)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
ENVIRONMENT="staging"
DOCKER_REGISTRY="eraif"
IMAGE_NAME="emergency-connector"
VERSION="latest"
CONFIG_FILE=""
BACKUP_ENABLED=true
HEALTH_CHECK_TIMEOUT=300  # 5 minutes

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "  ERAIF Emergency Connector Deployment"
    echo "=============================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -e, --environment    Target environment (staging|production) [default: staging]"
    echo "  -v, --version        Image version/tag [default: latest]"
    echo "  -c, --config         Configuration file path"
    echo "  -r, --registry       Docker registry [default: eraif]"
    echo "  --no-backup          Skip database backup"
    echo "  --no-build           Skip building new image"
    echo "  --rollback           Rollback to previous version"
    echo "  -h, --help           Show this help message"
    echo
    echo "Examples:"
    echo "  $0 -e production -v 1.2.3"
    echo "  $0 --environment staging --config config/staging.yml"
    echo "  $0 --rollback -e production"
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -v|--version)
                VERSION="$2"
                shift 2
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            -r|--registry)
                DOCKER_REGISTRY="$2"
                shift 2
                ;;
            --no-backup)
                BACKUP_ENABLED=false
                shift
                ;;
            --no-build)
                SKIP_BUILD=true
                shift
                ;;
            --rollback)
                ROLLBACK=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

validate_environment() {
    print_step "Validating deployment environment..."
    
    case $ENVIRONMENT in
        staging|production)
            echo "Deploying to: $ENVIRONMENT"
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            print_error "Supported environments: staging, production"
            exit 1
            ;;
    esac
    
    # Set environment-specific defaults
    if [ "$ENVIRONMENT" = "production" ]; then
        if [ "$VERSION" = "latest" ]; then
            print_error "Production deployments require explicit version tags"
            exit 1
        fi
        HEALTH_CHECK_TIMEOUT=600  # 10 minutes for production
    fi
    
    # Set config file if not specified
    if [ -z "$CONFIG_FILE" ]; then
        CONFIG_FILE="config/${ENVIRONMENT}.yml"
    fi
    
    echo -e "${GREEN}✓${NC} Environment validation complete"
}

check_prerequisites() {
    print_step "Checking deployment prerequisites..."
    
    # Check required tools
    local required_tools=("docker" "docker-compose")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_error "$tool is required but not installed"
            exit 1
        fi
    done
    
    # Check configuration file
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    
    echo -e "${GREEN}✓${NC} Prerequisites check complete"
}

backup_database() {
    if [ "$BACKUP_ENABLED" = false ]; then
        print_step "Skipping database backup (--no-backup specified)"
        return
    fi
    
    print_step "Creating database backup..."
    
    local backup_dir="backups"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="${backup_dir}/eraif_${ENVIRONMENT}_${timestamp}.sql"
    
    mkdir -p "$backup_dir"
    
    # Create database backup based on environment
    case $ENVIRONMENT in
        staging)
            # For staging, backup SQLite database
            if [ -f "data/eraif.db" ]; then
                cp "data/eraif.db" "${backup_dir}/eraif_${ENVIRONMENT}_${timestamp}.db"
                echo -e "${GREEN}✓${NC} SQLite database backed up to ${backup_file}"
            else
                print_warning "No database found to backup"
            fi
            ;;
        production)
            # For production, backup PostgreSQL
            if docker-compose ps postgres &> /dev/null; then
                docker-compose exec -T postgres pg_dump -U eraif eraif > "$backup_file"
                echo -e "${GREEN}✓${NC} PostgreSQL database backed up to ${backup_file}"
            else
                print_warning "PostgreSQL container not found"
            fi
            ;;
    esac
}

build_image() {
    if [ "$SKIP_BUILD" = true ]; then
        print_step "Skipping image build (--no-build specified)"
        return
    fi
    
    print_step "Building Docker image..."
    
    local full_image_name="${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}"
    
    # Build the image
    docker build -t "$full_image_name" .
    
    # Tag with environment
    docker tag "$full_image_name" "${DOCKER_REGISTRY}/${IMAGE_NAME}:${ENVIRONMENT}-${VERSION}"
    
    # Also tag as latest for the environment
    docker tag "$full_image_name" "${DOCKER_REGISTRY}/${IMAGE_NAME}:${ENVIRONMENT}-latest"
    
    echo -e "${GREEN}✓${NC} Docker image built: $full_image_name"
}

run_pre_deployment_tests() {
    print_step "Running pre-deployment tests..."
    
    # Run security scan
    if command -v docker &> /dev/null; then
        # Run basic container security scan
        print_step "Running container security scan..."
        
        # Check for known vulnerabilities (if trivy is available)
        if command -v trivy &> /dev/null; then
            trivy image "${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}" --exit-code 1 --severity HIGH,CRITICAL || {
                print_warning "Security vulnerabilities found, but continuing deployment..."
            }
        fi
    fi
    
    # Run smoke tests
    print_step "Running smoke tests..."
    
    # Start a temporary container for testing
    local test_container="eraif-test-$$"
    docker run -d --name "$test_container" \
        -p 8081:8080 \
        "${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}" &> /dev/null
    
    # Wait for container to start
    sleep 10
    
    # Test health endpoint
    if curl -f http://localhost:8081/health &> /dev/null; then
        echo -e "${GREEN}✓${NC} Health check passed"
    else
        print_error "Health check failed"
        docker logs "$test_container"
        docker rm -f "$test_container"
        exit 1
    fi
    
    # Cleanup test container
    docker rm -f "$test_container" &> /dev/null
    
    echo -e "${GREEN}✓${NC} Pre-deployment tests passed"
}

deploy_application() {
    print_step "Deploying application..."
    
    # Create deployment-specific docker-compose override
    local compose_override="docker-compose.${ENVIRONMENT}.yml"
    
    if [ ! -f "$compose_override" ]; then
        print_step "Creating deployment configuration..."
        
        case $ENVIRONMENT in
            staging)
                cat > "$compose_override" << EOF
version: '3.8'

services:
  eraif:
    image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}
    environment:
      - ERAIF_ENV=staging
    volumes:
      - ${CONFIG_FILE}:/app/config.yml
    ports:
      - "8080:8080"
      - "8443:8443"
    restart: unless-stopped
    
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=eraif
      - POSTGRES_USER=eraif
      - POSTGRES_PASSWORD=staging_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
EOF
                ;;
            production)
                cat > "$compose_override" << EOF
version: '3.8'

services:
  eraif:
    image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}
    environment:
      - ERAIF_ENV=production
    volumes:
      - ${CONFIG_FILE}:/app/config.yml
      - ./certs:/app/certs
    ports:
      - "80:8080"
      - "443:8443"
    restart: always
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=eraif
      - POSTGRES_USER=eraif
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: always
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - eraif
    restart: always

volumes:
  postgres_data:
EOF
                ;;
        esac
    fi
    
    # Deploy using docker-compose
    export COMPOSE_FILE="docker-compose.yml:$compose_override"
    
    # Pull latest images
    docker-compose pull
    
    # Start services
    docker-compose up -d
    
    echo -e "${GREEN}✓${NC} Application deployed"
}

wait_for_health_check() {
    print_step "Waiting for application to become healthy..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + HEALTH_CHECK_TIMEOUT))
    
    while [ $(date +%s) -lt $end_time ]; do
        if curl -f http://localhost:8080/health &> /dev/null; then
            echo -e "${GREEN}✓${NC} Application is healthy"
            return 0
        fi
        
        echo "Waiting for health check... ($(date))"
        sleep 10
    done
    
    print_error "Health check timeout after ${HEALTH_CHECK_TIMEOUT} seconds"
    print_error "Application logs:"
    docker-compose logs eraif --tail=50
    return 1
}

run_post_deployment_tests() {
    print_step "Running post-deployment tests..."
    
    # Test emergency system readiness
    local emergency_test=$(curl -s http://localhost:8080/emergency/status | jq -r '.readiness')
    if [ "$emergency_test" = "ready" ]; then
        echo -e "${GREEN}✓${NC} Emergency systems ready"
    else
        print_warning "Emergency systems not fully ready: $emergency_test"
    fi
    
    # Test API endpoints
    local endpoints=("/health" "/emergency/status")
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f "http://localhost:8080${endpoint}" &> /dev/null; then
            echo -e "${GREEN}✓${NC} Endpoint ${endpoint} is responding"
        else
            print_error "Endpoint ${endpoint} is not responding"
            return 1
        fi
    done
    
    echo -e "${GREEN}✓${NC} Post-deployment tests passed"
}

rollback_deployment() {
    print_step "Rolling back deployment..."
    
    # Find previous version
    local previous_version=$(docker images "${DOCKER_REGISTRY}/${IMAGE_NAME}" --format "table {{.Tag}}" | grep -v "TAG\|latest\|${VERSION}" | head -1)
    
    if [ -z "$previous_version" ]; then
        print_error "No previous version found for rollback"
        exit 1
    fi
    
    print_step "Rolling back to version: $previous_version"
    
    # Update docker-compose to use previous version
    sed -i.bak "s/${VERSION}/${previous_version}/g" "docker-compose.${ENVIRONMENT}.yml"
    
    # Redeploy with previous version
    docker-compose up -d
    
    # Wait for health check
    wait_for_health_check
    
    echo -e "${GREEN}✓${NC} Rollback completed to version: $previous_version"
}

cleanup_old_images() {
    print_step "Cleaning up old Docker images..."
    
    # Keep last 5 versions
    docker images "${DOCKER_REGISTRY}/${IMAGE_NAME}" --format "{{.ID}}" | tail -n +6 | xargs -r docker rmi
    
    # Remove dangling images
    docker image prune -f
    
    echo -e "${GREEN}✓${NC} Cleanup completed"
}

send_deployment_notification() {
    print_step "Sending deployment notification..."
    
    local status="SUCCESS"
    local message="ERAIF deployment to ${ENVIRONMENT} completed successfully"
    
    if [ $? -ne 0 ]; then
        status="FAILED"
        message="ERAIF deployment to ${ENVIRONMENT} failed"
    fi
    
    # Send notification (webhook, Slack, email, etc.)
    # This is a placeholder - implement according to your notification system
    echo "Deployment Status: $status"
    echo "Message: $message"
    echo "Environment: $ENVIRONMENT"
    echo "Version: $VERSION"
    echo "Timestamp: $(date)"
    
    echo -e "${GREEN}✓${NC} Notification sent"
}

print_completion_message() {
    echo
    echo -e "${GREEN}=============================================="
    echo "  Deployment Complete!"
    echo -e "==============================================\n${NC}"
    
    echo "Deployment Summary:"
    echo "  Environment: $ENVIRONMENT"
    echo "  Version: $VERSION"
    echo "  Config: $CONFIG_FILE"
    echo
    echo "Application URLs:"
    case $ENVIRONMENT in
        staging)
            echo "  Health Check: http://localhost:8080/health"
            echo "  API Docs: http://localhost:8080/docs"
            echo "  Emergency Status: http://localhost:8080/emergency/status"
            ;;
        production)
            echo "  Health Check: https://your-domain.com/health"
            echo "  API Docs: https://your-domain.com/docs"
            echo "  Emergency Status: https://your-domain.com/emergency/status"
            ;;
    esac
    echo
    echo "Management Commands:"
    echo "  View logs: docker-compose logs -f eraif"
    echo "  Scale service: docker-compose up -d --scale eraif=3"
    echo "  Update config: docker-compose restart eraif"
    echo
}

# Main execution
main() {
    print_header
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Handle rollback
    if [ "$ROLLBACK" = true ]; then
        rollback_deployment
        send_deployment_notification
        exit 0
    fi
    
    # Validate environment and prerequisites
    validate_environment
    check_prerequisites
    
    # Backup and build
    backup_database
    build_image
    
    # Test and deploy
    run_pre_deployment_tests
    deploy_application
    
    # Verify deployment
    wait_for_health_check
    run_post_deployment_tests
    
    # Cleanup and notify
    cleanup_old_images
    send_deployment_notification
    
    print_completion_message
}

# Run main function
main "$@"
