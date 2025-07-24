# .env.example - Copy to .env and modify as needed
# Environment Configuration for Bible App

# =============================================================================
# Application Settings
# =============================================================================
APP_NAME="Bible App"
APP_VERSION="1.0.0"
APP_DESCRIPTION="A Bible application built with FastAPI"

# =============================================================================
# Environment (development, production, test)
# =============================================================================
ENVIRONMENT=development

# =============================================================================
# Database Configuration
# =============================================================================

# SQLite (default - no setup required)
DATABASE_URL=sqlite:///./bible.db

# PostgreSQL (uncomment and configure for production)
# DATABASE_URL=postgresql://username:password@localhost:5432/bible_db

# MySQL (uncomment and configure if needed)
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/bible_db

# =============================================================================
# Server Configuration
# =============================================================================
HOST=0.0.0.0
PORT=8080
DEBUG=true
RELOAD=true

# =============================================================================
# API Configuration
# =============================================================================
API_V1_PREFIX=/api/v1

# =============================================================================
# CORS Settings (for frontend applications)
# =============================================================================
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:8080

# =============================================================================
# Security Settings (for future authentication features)
# =============================================================================
SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=30

# =============================================================================
# Pagination and Search Settings
# =============================================================================
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
SEARCH_LIMIT=50
MIN_SEARCH_LENGTH=3

# =============================================================================
# Production Database Examples
# =============================================================================

# PostgreSQL Production Example:
# DATABASE_URL=postgresql://bible_user:secure_password@localhost:5432/bible_production
# 
# To create PostgreSQL database:
# sudo -u postgres createuser -P bible_user
# sudo -u postgres createdb -O bible_user bible_production

# MySQL Production Example:
# DATABASE_URL=mysql+pymysql://bible_user:secure_password@localhost:3306/bible_production
#
# To create MySQL database:
# mysql -u root -p
# CREATE DATABASE bible_production;
# CREATE USER 'bible_user'@'localhost' IDENTIFIED BY 'secure_password';
# GRANT ALL PRIVILEGES ON bible_production.* TO 'bible_user'@'localhost';
# FLUSH PRIVILEGES;

# =============================================================================
# Docker Configuration (if using Docker)
# =============================================================================
DOCKER_PORT=8080

# =============================================================================
# Logging Configuration
# =============================================================================
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# =============================================================================
# Development vs Production Examples
# =============================================================================

# Development Settings:
# ENVIRONMENT=development
# DEBUG=true
# RELOAD=true
# DATABASE_URL=sqlite:///./bible_dev.db

# Production Settings:
# ENVIRONMENT=production
# DEBUG=false
# RELOAD=false
# DATABASE_URL=postgresql://bible_user:secure_password@localhost:5432/bible_production
# SECRET_KEY=generate-with-openssl-rand-hex-32

# Test Settings:
# ENVIRONMENT=test
# DATABASE_URL=sqlite:///./bible_test.db