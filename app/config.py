"""Configuration settings for the Hospital Directory API."""

import os

# Application Settings
APP_NAME = "Hospital Directory API"
VERSION = "1.0.0"
DESCRIPTION = "A RESTful API for managing hospital directory information with batch processing capabilities."

# Server Settings
DEFAULT_PORT = 10000
HOST = "0.0.0.0"

# Business Logic Settings
MAX_BATCH_SIZE = 20
MAX_TOTAL_HOSPITALS = 10000

# Processing Settings
SLOW_TASK_DELAY_SECONDS = 5

# Rate Limiting Settings (requests per minute)
RATE_LIMITS = {
    "health_check": "100/minute",
    "create_hospital": "30/minute",
    "get_hospitals": "50/minute",
    "get_hospital_by_id": "50/minute",
    "update_hospital": "50/minute",
    "delete_hospital": "50/minute",
    "get_batch": "50/minute",
    "delete_batch": "50/minute",
    "activate_batch": "50/minute",
}

def get_port() -> int:
    """Get the port from environment variable or use default."""
    return int(os.getenv("PORT", DEFAULT_PORT))

def get_environment() -> str:
    """Get the current environment."""
    return os.getenv("ENVIRONMENT", "development")

def is_production() -> bool:
    """Check if running in production environment."""
    return get_environment().lower() == "production"

def is_testing() -> bool:
    """Check if running in test environment."""
    return get_environment().lower() == "test"