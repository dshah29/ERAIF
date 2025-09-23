"""
ERAIF Configuration Management

This module handles configuration for the Emergency Radiology AI 
Interoperability Framework, including AI/ML settings.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import yaml
import json
from enum import Enum


logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DeploymentMode(str, Enum):
    """Deployment modes."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    EMERGENCY = "emergency"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "eraif"
    username: str = "eraif_user"
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30


@dataclass
class RedisConfig:
    """Redis configuration."""
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    database: int = 0
    ssl: bool = False
    pool_size: int = 10


@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    ssl_cert_path: str = ""
    ssl_key_path: str = ""
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = 100
    enable_audit_logging: bool = True


@dataclass
class AIConfig:
    """AI/ML configuration."""
    # LLM Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 2000
    
    # LangGraph Configuration
    langgraph_checkpoint_backend: str = "memory"  # memory, postgres, redis
    langgraph_thread_timeout: int = 300
    
    # Model Configuration
    model_cache_dir: str = "./models"
    enable_gpu: bool = True
    gpu_memory_limit: Optional[int] = None
    batch_size: int = 8
    max_concurrent_inferences: int = 4
    
    # Medical Imaging AI
    imaging_model_path: str = "./models/imaging"
    enable_ct_analysis: bool = True
    enable_xray_analysis: bool = True
    enable_mri_analysis: bool = True
    enable_ultrasound_analysis: bool = True
    
    # Confidence Thresholds
    min_confidence_threshold: float = 0.5
    critical_finding_threshold: float = 0.8
    auto_alert_threshold: float = 0.9
    
    # Training Configuration
    enable_model_training: bool = False
    training_data_path: str = "./training_data"
    model_update_interval_hours: int = 24
    enable_federated_learning: bool = False


@dataclass
class EmergencyConfig:
    """Emergency mode configuration."""
    auto_activation_enabled: bool = True
    network_failure_threshold_seconds: int = 30
    cpu_threshold_percent: int = 90
    memory_threshold_percent: int = 85
    disk_threshold_percent: int = 95
    
    # Emergency modes
    disaster_mode_compression: bool = True
    disaster_mode_priority_filter: List[str] = field(
        default_factory=lambda: ["CRITICAL", "HIGH"]
    )
    disaster_mode_batch_size: int = 5
    disaster_mode_timeout_seconds: int = 15
    
    # Failover configuration
    enable_offline_mode: bool = True
    offline_cache_size_mb: int = 1000
    sync_retry_attempts: int = 5
    sync_retry_delay_seconds: int = 60


@dataclass
class IntegrationConfig:
    """Integration configuration for external systems."""
    # PACS Integration
    pacs_servers: List[Dict[str, Any]] = field(default_factory=list)
    pacs_timeout_seconds: int = 30
    pacs_retry_attempts: int = 3
    
    # HL7/FHIR Integration
    fhir_servers: List[Dict[str, Any]] = field(default_factory=list)
    fhir_version: str = "R4"
    fhir_timeout_seconds: int = 30
    
    # External AI Services
    external_ai_services: List[Dict[str, Any]] = field(default_factory=list)
    
    # Notification Systems
    email_config: Dict[str, Any] = field(default_factory=dict)
    sms_config: Dict[str, Any] = field(default_factory=dict)
    slack_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    enable_metrics: bool = True
    metrics_port: int = 9090
    enable_tracing: bool = True
    tracing_endpoint: str = ""
    enable_health_checks: bool = True
    health_check_interval_seconds: int = 30
    
    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "json"
    log_file_path: str = "./logs/eraif.log"
    log_rotation_size_mb: int = 100
    log_retention_days: int = 30
    
    # Alerting
    enable_alerting: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ["email"])
    alert_thresholds: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ERAIFConfig:
    """Main ERAIF configuration class."""
    # Basic configuration
    app_name: str = "ERAIF"
    version: str = "1.0.0"
    deployment_mode: DeploymentMode = DeploymentMode.DEVELOPMENT
    debug: bool = False
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8080
    ssl_port: int = 8443
    workers: int = 4
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    emergency: EmergencyConfig = field(default_factory=EmergencyConfig)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'ERAIFConfig':
        """Load configuration from file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            return cls()
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
            
            return cls.from_dict(data)
            
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {str(e)}")
            logger.warning("Using default configuration")
            return cls()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ERAIFConfig':
        """Create configuration from dictionary."""
        try:
            config = cls()
            
            # Update basic fields
            for field_name in ['app_name', 'version', 'deployment_mode', 'debug', 
                              'host', 'port', 'ssl_port', 'workers']:
                if field_name in data:
                    setattr(config, field_name, data[field_name])
            
            # Update component configurations
            if 'database' in data:
                config.database = DatabaseConfig(**data['database'])
            
            if 'redis' in data:
                config.redis = RedisConfig(**data['redis'])
            
            if 'security' in data:
                config.security = SecurityConfig(**data['security'])
            
            if 'ai' in data:
                config.ai = AIConfig(**data['ai'])
            
            if 'emergency' in data:
                config.emergency = EmergencyConfig(**data['emergency'])
            
            if 'integrations' in data:
                config.integrations = IntegrationConfig(**data['integrations'])
            
            if 'monitoring' in data:
                config.monitoring = MonitoringConfig(**data['monitoring'])
            
            if 'custom_settings' in data:
                config.custom_settings = data['custom_settings']
            
            return config
            
        except Exception as e:
            logger.error(f"Error creating config from dict: {str(e)}")
            return cls()
    
    @classmethod
    def from_env(cls) -> 'ERAIFConfig':
        """Load configuration from environment variables."""
        config = cls()
        
        # Basic configuration
        config.app_name = os.getenv('ERAIF_APP_NAME', config.app_name)
        config.version = os.getenv('ERAIF_VERSION', config.version)
        config.deployment_mode = DeploymentMode(
            os.getenv('ERAIF_DEPLOYMENT_MODE', config.deployment_mode.value)
        )
        config.debug = os.getenv('ERAIF_DEBUG', str(config.debug)).lower() == 'true'
        config.host = os.getenv('ERAIF_HOST', config.host)
        config.port = int(os.getenv('ERAIF_PORT', str(config.port)))
        config.ssl_port = int(os.getenv('ERAIF_SSL_PORT', str(config.ssl_port)))
        config.workers = int(os.getenv('ERAIF_WORKERS', str(config.workers)))
        
        # Database configuration
        config.database.host = os.getenv('ERAIF_DB_HOST', config.database.host)
        config.database.port = int(os.getenv('ERAIF_DB_PORT', str(config.database.port)))
        config.database.database = os.getenv('ERAIF_DB_NAME', config.database.database)
        config.database.username = os.getenv('ERAIF_DB_USER', config.database.username)
        config.database.password = os.getenv('ERAIF_DB_PASSWORD', config.database.password)
        
        # Redis configuration
        config.redis.host = os.getenv('ERAIF_REDIS_HOST', config.redis.host)
        config.redis.port = int(os.getenv('ERAIF_REDIS_PORT', str(config.redis.port)))
        config.redis.password = os.getenv('ERAIF_REDIS_PASSWORD', config.redis.password)
        
        # Security configuration
        config.security.secret_key = os.getenv('ERAIF_SECRET_KEY', config.security.secret_key)
        config.security.ssl_cert_path = os.getenv('ERAIF_SSL_CERT', config.security.ssl_cert_path)
        config.security.ssl_key_path = os.getenv('ERAIF_SSL_KEY', config.security.ssl_key_path)
        
        # AI configuration
        config.ai.openai_api_key = os.getenv('OPENAI_API_KEY', config.ai.openai_api_key)
        config.ai.openai_model = os.getenv('ERAIF_AI_MODEL', config.ai.openai_model)
        config.ai.model_cache_dir = os.getenv('ERAIF_MODEL_CACHE_DIR', config.ai.model_cache_dir)
        config.ai.enable_gpu = os.getenv('ERAIF_ENABLE_GPU', str(config.ai.enable_gpu)).lower() == 'true'
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'app_name': self.app_name,
            'version': self.version,
            'deployment_mode': self.deployment_mode.value,
            'debug': self.debug,
            'host': self.host,
            'port': self.port,
            'ssl_port': self.ssl_port,
            'workers': self.workers,
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'database': self.database.database,
                'username': self.database.username,
                'ssl_mode': self.database.ssl_mode,
                'pool_size': self.database.pool_size,
                'max_overflow': self.database.max_overflow,
                'pool_timeout': self.database.pool_timeout
            },
            'redis': {
                'host': self.redis.host,
                'port': self.redis.port,
                'database': self.redis.database,
                'ssl': self.redis.ssl,
                'pool_size': self.redis.pool_size
            },
            'security': {
                'jwt_algorithm': self.security.jwt_algorithm,
                'jwt_expiration_hours': self.security.jwt_expiration_hours,
                'ssl_cert_path': self.security.ssl_cert_path,
                'ssl_key_path': self.security.ssl_key_path,
                'enable_cors': self.security.enable_cors,
                'cors_origins': self.security.cors_origins,
                'rate_limit_per_minute': self.security.rate_limit_per_minute,
                'enable_audit_logging': self.security.enable_audit_logging
            },
            'ai': {
                'openai_model': self.ai.openai_model,
                'openai_temperature': self.ai.openai_temperature,
                'openai_max_tokens': self.ai.openai_max_tokens,
                'langgraph_checkpoint_backend': self.ai.langgraph_checkpoint_backend,
                'langgraph_thread_timeout': self.ai.langgraph_thread_timeout,
                'model_cache_dir': self.ai.model_cache_dir,
                'enable_gpu': self.ai.enable_gpu,
                'gpu_memory_limit': self.ai.gpu_memory_limit,
                'batch_size': self.ai.batch_size,
                'max_concurrent_inferences': self.ai.max_concurrent_inferences,
                'imaging_model_path': self.ai.imaging_model_path,
                'enable_ct_analysis': self.ai.enable_ct_analysis,
                'enable_xray_analysis': self.ai.enable_xray_analysis,
                'enable_mri_analysis': self.ai.enable_mri_analysis,
                'enable_ultrasound_analysis': self.ai.enable_ultrasound_analysis,
                'min_confidence_threshold': self.ai.min_confidence_threshold,
                'critical_finding_threshold': self.ai.critical_finding_threshold,
                'auto_alert_threshold': self.ai.auto_alert_threshold,
                'enable_model_training': self.ai.enable_model_training,
                'training_data_path': self.ai.training_data_path,
                'model_update_interval_hours': self.ai.model_update_interval_hours,
                'enable_federated_learning': self.ai.enable_federated_learning
            },
            'emergency': {
                'auto_activation_enabled': self.emergency.auto_activation_enabled,
                'network_failure_threshold_seconds': self.emergency.network_failure_threshold_seconds,
                'cpu_threshold_percent': self.emergency.cpu_threshold_percent,
                'memory_threshold_percent': self.emergency.memory_threshold_percent,
                'disk_threshold_percent': self.emergency.disk_threshold_percent,
                'disaster_mode_compression': self.emergency.disaster_mode_compression,
                'disaster_mode_priority_filter': self.emergency.disaster_mode_priority_filter,
                'disaster_mode_batch_size': self.emergency.disaster_mode_batch_size,
                'disaster_mode_timeout_seconds': self.emergency.disaster_mode_timeout_seconds,
                'enable_offline_mode': self.emergency.enable_offline_mode,
                'offline_cache_size_mb': self.emergency.offline_cache_size_mb,
                'sync_retry_attempts': self.emergency.sync_retry_attempts,
                'sync_retry_delay_seconds': self.emergency.sync_retry_delay_seconds
            },
            'integrations': {
                'pacs_servers': self.integrations.pacs_servers,
                'pacs_timeout_seconds': self.integrations.pacs_timeout_seconds,
                'pacs_retry_attempts': self.integrations.pacs_retry_attempts,
                'fhir_servers': self.integrations.fhir_servers,
                'fhir_version': self.integrations.fhir_version,
                'fhir_timeout_seconds': self.integrations.fhir_timeout_seconds,
                'external_ai_services': self.integrations.external_ai_services,
                'email_config': self.integrations.email_config,
                'sms_config': self.integrations.sms_config,
                'slack_config': self.integrations.slack_config
            },
            'monitoring': {
                'enable_metrics': self.monitoring.enable_metrics,
                'metrics_port': self.monitoring.metrics_port,
                'enable_tracing': self.monitoring.enable_tracing,
                'tracing_endpoint': self.monitoring.tracing_endpoint,
                'enable_health_checks': self.monitoring.enable_health_checks,
                'health_check_interval_seconds': self.monitoring.health_check_interval_seconds,
                'log_level': self.monitoring.log_level.value,
                'log_format': self.monitoring.log_format,
                'log_file_path': self.monitoring.log_file_path,
                'log_rotation_size_mb': self.monitoring.log_rotation_size_mb,
                'log_retention_days': self.monitoring.log_retention_days,
                'enable_alerting': self.monitoring.enable_alerting,
                'alert_channels': self.monitoring.alert_channels,
                'alert_thresholds': self.monitoring.alert_thresholds
            },
            'custom_settings': self.custom_settings
        }
    
    def save_to_file(self, config_path: Union[str, Path]):
        """Save configuration to file."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.to_dict()
        
        try:
            with open(config_path, 'w') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.safe_dump(data, f, default_flow_style=False, indent=2)
                elif config_path.suffix.lower() == '.json':
                    json.dump(data, f, indent=2)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
            
            logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"Error saving config to {config_path}: {str(e)}")
            raise
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Validate required fields
        if not self.security.secret_key and self.deployment_mode == DeploymentMode.PRODUCTION:
            issues.append("Secret key is required for production deployment")
        
        if not self.ai.openai_api_key:
            issues.append("OpenAI API key is required for AI functionality")
        
        if self.ai.enable_gpu and not self.ai.model_cache_dir:
            issues.append("Model cache directory is required when GPU is enabled")
        
        # Validate paths
        if self.ai.model_cache_dir and not Path(self.ai.model_cache_dir).exists():
            issues.append(f"Model cache directory does not exist: {self.ai.model_cache_dir}")
        
        if self.security.ssl_cert_path and not Path(self.security.ssl_cert_path).exists():
            issues.append(f"SSL certificate file does not exist: {self.security.ssl_cert_path}")
        
        if self.security.ssl_key_path and not Path(self.security.ssl_key_path).exists():
            issues.append(f"SSL key file does not exist: {self.security.ssl_key_path}")
        
        # Validate thresholds
        if not 0 <= self.ai.min_confidence_threshold <= 1:
            issues.append("AI confidence threshold must be between 0 and 1")
        
        if not 0 <= self.ai.critical_finding_threshold <= 1:
            issues.append("Critical finding threshold must be between 0 and 1")
        
        if not 0 <= self.ai.auto_alert_threshold <= 1:
            issues.append("Auto alert threshold must be between 0 and 1")
        
        return issues
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.deployment_mode == DeploymentMode.PRODUCTION
    
    @property
    def is_emergency_mode(self) -> bool:
        """Check if running in emergency mode."""
        return self.deployment_mode == DeploymentMode.EMERGENCY
    
    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key (for compatibility)."""
        return self.ai.openai_api_key


def load_config(config_path: Optional[Union[str, Path]] = None) -> ERAIFConfig:
    """
    Load ERAIF configuration from various sources.
    
    Priority order:
    1. Specified config file
    2. Environment variables
    3. Default config file locations
    4. Default configuration
    """
    if config_path:
        return ERAIFConfig.from_file(config_path)
    
    # Try default locations
    default_paths = [
        Path("config.yml"),
        Path("config.yaml"),
        Path("config.json"),
        Path("eraif.yml"),
        Path("eraif.yaml"),
        Path("eraif.json"),
        Path("/etc/eraif/config.yml"),
        Path("~/.eraif/config.yml").expanduser()
    ]
    
    for path in default_paths:
        if path.exists():
            logger.info(f"Loading configuration from {path}")
            return ERAIFConfig.from_file(path)
    
    # Load from environment
    logger.info("Loading configuration from environment variables")
    return ERAIFConfig.from_env()
