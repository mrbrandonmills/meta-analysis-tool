#!/bin/bash
# Database Backup Script for Meta-Analysis Platform
# Usage: ./scripts/backup-db.sh [environment]
# Environment: production (default), staging, local

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
ENVIRONMENT="${1:-production}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

log "Starting database backup for environment: $ENVIRONMENT"

# Get database credentials based on environment
case $ENVIRONMENT in
    production)
        # For Railway, use railway CLI
        if command -v railway &> /dev/null; then
            log "Using Railway CLI for production backup"

            # Get database URL from Railway
            DATABASE_URL=$(railway variables get DATABASE_URL --environment production 2>/dev/null || echo "")

            if [ -z "$DATABASE_URL" ]; then
                error "Failed to get DATABASE_URL from Railway"
                exit 1
            fi
        else
            error "Railway CLI not found. Install it or set DATABASE_URL manually."
            exit 1
        fi
        BACKUP_NAME="production_backup_${TIMESTAMP}.sql.gz"
        ;;

    staging)
        DATABASE_URL=$(railway variables get DATABASE_URL --environment staging 2>/dev/null || echo "")
        BACKUP_NAME="staging_backup_${TIMESTAMP}.sql.gz"
        ;;

    local)
        DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/meta_analysis}"
        BACKUP_NAME="local_backup_${TIMESTAMP}.sql.gz"
        ;;

    *)
        error "Unknown environment: $ENVIRONMENT"
        echo "Usage: $0 [production|staging|local]"
        exit 1
        ;;
esac

# Parse database URL
# Format: postgresql://user:password@host:port/database
if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASSWORD="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    error "Invalid DATABASE_URL format"
    exit 1
fi

BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

log "Database: $DB_NAME"
log "Host: $DB_HOST:$DB_PORT"
log "Backup file: $BACKUP_PATH"

# Perform backup
log "Creating backup..."
export PGPASSWORD="$DB_PASSWORD"

if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --format=plain \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    | gzip > "$BACKUP_PATH"; then

    log "Backup created successfully"

    # Get backup size
    BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
    log "Backup size: $BACKUP_SIZE"

    # Verify backup
    log "Verifying backup integrity..."
    if gunzip -t "$BACKUP_PATH" 2>/dev/null; then
        log "Backup verification successful"
    else
        error "Backup verification failed"
        exit 1
    fi

else
    error "Backup failed"
    exit 1
fi

# Clean up old backups
log "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "*_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
log "Cleanup complete"

# Upload to cloud storage (optional)
if [ "${UPLOAD_TO_S3:-false}" = "true" ]; then
    if command -v aws &> /dev/null; then
        S3_BUCKET="${S3_BACKUP_BUCKET:-meta-analysis-backups}"
        log "Uploading to S3: s3://$S3_BUCKET/$BACKUP_NAME"

        if aws s3 cp "$BACKUP_PATH" "s3://$S3_BUCKET/$BACKUP_NAME"; then
            log "S3 upload successful"
        else
            warn "S3 upload failed (continuing anyway)"
        fi
    else
        warn "AWS CLI not found. Skipping S3 upload."
    fi
fi

# Generate backup report
cat > "$BACKUP_DIR/backup_report_${TIMESTAMP}.txt" << EOF
Backup Report
=============
Environment: $ENVIRONMENT
Database: $DB_NAME
Timestamp: $(date)
Backup File: $BACKUP_NAME
Backup Size: $BACKUP_SIZE
Status: SUCCESS
EOF

log "Backup completed successfully!"
log "Backup location: $BACKUP_PATH"

# Cleanup sensitive variables
unset PGPASSWORD
unset DATABASE_URL
