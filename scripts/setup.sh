#!/bin/bash

# ERAIF Setup Script
# This script sets up the ERAIF development and production environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.8"
REQUIRED_TOOLS=("docker" "docker-compose" "git")

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "  ERAIF Emergency Connector Setup Script"
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

check_python_version() {
    print_step "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        echo "Found Python $PYTHON_VERSION"
        
        # Compare versions
        if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
            echo -e "${GREEN}✓${NC} Python version is compatible"
        else
            print_error "Python $PYTHON_MIN_VERSION or higher is required"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

check_required_tools() {
    print_step "Checking required tools..."
    
    for tool in "${REQUIRED_TOOLS[@]}"; do
        if command -v "$tool" &> /dev/null; then
            echo -e "${GREEN}✓${NC} $tool is installed"
        else
            print_warning "$tool is not installed (optional for development)"
        fi
    done
}

setup_virtual_environment() {
    print_step "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} Virtual environment created"
    else
        echo "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    echo -e "${GREEN}✓${NC} pip upgraded"
}

install_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Install production dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo -e "${GREEN}✓${NC} Production dependencies installed"
    else
        print_warning "requirements.txt not found, creating basic dependencies..."
        cat > requirements.txt << EOF
# Core dependencies
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
python-multipart>=0.0.6
aiofiles>=23.2.1

# Medical imaging
pydicom>=2.4.3
pynetdicom>=2.0.2

# Database and storage
sqlalchemy>=2.0.23
alembic>=1.13.0
redis>=5.0.1

# Security and authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# Monitoring and logging
prometheus-client>=0.19.0
structlog>=23.2.0

# Configuration
pyyaml>=6.0.1
python-dotenv>=1.0.0

# Testing (dev dependencies)
pytest>=7.4.3
pytest-asyncio>=0.21.1
pytest-cov>=4.1.0
httpx>=0.25.2
EOF
        pip install -r requirements.txt
        echo -e "${GREEN}✓${NC} Basic dependencies installed"
    fi
    
    # Install development dependencies
    pip install pytest pytest-asyncio pytest-cov black flake8 mypy
    echo -e "${GREEN}✓${NC} Development dependencies installed"
}

setup_configuration() {
    print_step "Setting up configuration files..."
    
    # Create config directory
    mkdir -p config
    
    # Create default configuration if it doesn't exist
    if [ ! -f "config.yml" ]; then
        cat > config.yml << EOF
# ERAIF Configuration File
server:
  host: "0.0.0.0"
  port: 8080
  ssl_port: 8443
  workers: 4

emergency:
  mode: "normal"  # normal, disaster, hybrid
  fallback_timeout: 30
  auto_activation:
    network_failure_threshold: 5  # seconds
    system_overload_threshold: 90  # percent

security:
  secret_key: "change-this-in-production"
  ssl_cert: null
  ssl_key: null
  
database:
  url: "sqlite:///./eraif.db"
  # For production, use PostgreSQL:
  # url: "postgresql://user:password@localhost:5432/eraif"

logging:
  level: "INFO"
  format: "json"
  file: "logs/eraif.log"

integrations:
  dicom:
    ae_title: "ERAIF_EMERGENCY"
    port: 11112
    
  fhir:
    base_url: null
    auth_type: "none"
    
monitoring:
  enabled: true
  prometheus_port: 9090
  health_check_interval: 30
EOF
        echo -e "${GREEN}✓${NC} Default configuration created"
    else
        echo "Configuration file already exists"
    fi
    
    # Create environment file
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# ERAIF Environment Variables
ERAIF_ENV=development
ERAIF_SECRET_KEY=dev-secret-key-change-in-production
ERAIF_DATABASE_URL=sqlite:///./eraif.db
ERAIF_LOG_LEVEL=INFO
EOF
        echo -e "${GREEN}✓${NC} Environment file created"
    else
        echo "Environment file already exists"
    fi
}

setup_directories() {
    print_step "Creating directory structure..."
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data
    mkdir -p certs
    mkdir -p backups
    
    echo -e "${GREEN}✓${NC} Directory structure created"
}

setup_database() {
    print_step "Setting up database..."
    
    # For now, just ensure the database directory exists
    mkdir -p data
    
    # In a full implementation, this would run database migrations
    echo -e "${GREEN}✓${NC} Database setup complete"
}

generate_ssl_certificates() {
    print_step "Generating self-signed SSL certificates for development..."
    
    if [ ! -f "certs/server.crt" ] || [ ! -f "certs/server.key" ]; then
        # Generate private key
        openssl genrsa -out certs/server.key 2048 2>/dev/null
        
        # Generate certificate signing request
        openssl req -new -key certs/server.key -out certs/server.csr -subj "/C=US/ST=State/L=City/O=ERAIF/CN=localhost" 2>/dev/null
        
        # Generate self-signed certificate
        openssl x509 -req -days 365 -in certs/server.csr -signkey certs/server.key -out certs/server.crt 2>/dev/null
        
        # Clean up CSR
        rm certs/server.csr
        
        echo -e "${GREEN}✓${NC} Self-signed SSL certificates generated"
        print_warning "These are self-signed certificates for development only!"
        print_warning "Use proper certificates from a CA in production!"
    else
        echo "SSL certificates already exist"
    fi
}

setup_docker() {
    print_step "Setting up Docker configuration..."
    
    # Create Dockerfile if it doesn't exist
    if [ ! -f "Dockerfile" ]; then
        cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ERAIF_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash eraif
RUN chown -R eraif:eraif /app
USER eraif

# Expose ports
EXPOSE 8080 8443

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python", "-m", "src.main"]
EOF
        echo -e "${GREEN}✓${NC} Dockerfile created"
    else
        echo "Dockerfile already exists"
    fi
    
    # Create docker-compose.yml if it doesn't exist
    if [ ! -f "docker-compose.yml" ]; then
        cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  eraif:
    build: .
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - ./config.yml:/app/config.yml
      - ./logs:/app/logs
      - ./data:/app/data
      - ./certs:/app/certs
    environment:
      - ERAIF_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped

volumes:
  redis_data:
  prometheus_data:
EOF
        echo -e "${GREEN}✓${NC} docker-compose.yml created"
    else
        echo "docker-compose.yml already exists"
    fi
}

run_tests() {
    print_step "Running initial tests..."
    
    # Run basic tests to ensure setup is working
    if command -v pytest &> /dev/null; then
        python -m pytest tests/ -v --tb=short || {
            print_warning "Some tests failed, but setup continues..."
        }
    else
        print_warning "pytest not available, skipping tests"
    fi
}

print_completion_message() {
    echo
    echo -e "${GREEN}=============================================="
    echo "  ERAIF Setup Complete!"
    echo -e "==============================================\n${NC}"
    
    echo "Next steps:"
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo
    echo "2. Start the development server:"
    echo "   python -m src.main"
    echo
    echo "3. Or use Docker:"
    echo "   docker-compose up"
    echo
    echo "4. Access the API documentation:"
    echo "   http://localhost:8080/docs"
    echo
    echo "5. Test emergency activation:"
    echo "   curl -X POST http://localhost:8080/emergency/test"
    echo
    echo -e "${YELLOW}Important:${NC}"
    echo "- Review and update config.yml for your environment"
    echo "- Replace default SSL certificates in production"
    echo "- Change default secret keys and passwords"
    echo "- Configure proper database connection for production"
    echo
}

# Main execution
main() {
    print_header
    
    # Check prerequisites
    check_python_version
    check_required_tools
    
    # Setup environment
    setup_virtual_environment
    install_dependencies
    
    # Configure application
    setup_configuration
    setup_directories
    setup_database
    
    # Security setup
    if command -v openssl &> /dev/null; then
        generate_ssl_certificates
    else
        print_warning "OpenSSL not found, skipping SSL certificate generation"
    fi
    
    # Docker setup
    setup_docker
    
    # Final verification
    run_tests
    
    print_completion_message
}

# Run main function
main "$@"
