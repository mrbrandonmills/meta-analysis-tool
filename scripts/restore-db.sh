#!/bin/bash
# Database Restore Script for Meta-Analysis Platform
# Usage: ./scripts/restore-db.sh <backup_file> [environment]
# Environment: production, staging, local (default)

set -e  # Exit on error
set -u  # Exit on undefined variable

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

# Check arguments
if [ $# -lt 1 ]; then
    error "Missing backup file argument"
    echo "Usage: $0 <backup_file> [environment]"
    echo "Example: $0 ./backups/production_backup_20250104_120000.sql.gz local"
    exit 1
fi

BACKUP_FILE="$1"
ENVIRONMENT="${2:-local}"

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

log "Starting database restore from: $BACKUP_FILE"
log "Target environment: $ENVIRONMENT"

# Safety check for production
if [ "$ENVIRONMENT" = "production" ]; then
    warn "⚠️  WARNING: You are about to restore to PRODUCTION!"
    warn "This will overwrite all current production data!"
    echo ""
    read -p "Type 'RESTORE PRODUCTION' to confirm: " confirmation

    if [ "$confirmation" != "RESTORE PRODUCTION" ]; then
        error "Restore cancelled"
        exit 1
    fi

    log "Production restore confirmed. Creating pre-restore backup..."
    ./scripts/backup-db.sh production
    log "Pre-restore backup complete"
fi

# Get database credentials based on environment
case $ENVIRONMENT in
    production)
        if command -v railway &> /dev/null; then
            DATABASE_URL=$(railway variables get DATABASE_URL --environment production 2>/dev/null || echo "")
        else
            error "Railway CLI not found"
            exit 1
        fi
        ;;

    staging)
        DATABASE_URL=$(railway variables get DATABASE_URL --environment staging 2>/dev/null || echo "")
        ;;

    local)
        DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/meta_analysis}"
        ;;

    *)
        error "Unknown environment: $ENVIRONMENT"
        exit 1
        ;;
esac

# Parse database URL
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

log "Database: $DB_NAME"
log "Host: $DB_HOST:$DB_PORT"

# Verify backup file integrity
log "Verifying backup file integrity..."
if gunzip -t "$BACKUP_FILE" 2>/dev/null; then
    log "Backup file verification successful"
else
    error "Backup file is corrupted"
    exit 1
fi

# Set password for psql
export PGPASSWORD="$DB_PASSWORD"

# Test database connection
log "Testing database connection..."
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c '\q' 2>/dev/null; then
    log "Database connection successful"
else
    error "Failed to connect to database"
    exit 1
fi

# Drop all connections to the target database (if local/staging)
if [ "$ENVIRONMENT" != "production" ]; then
    log "Terminating existing connections..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres << EOF
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DB_NAME'
  AND pid <> pg_backend_pid();
EOF
fi

# Restore database
log "Restoring database..."
if gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
    log "Database restore successful"
else
    error "Database restore failed"
    exit 1
fi

# Verify restore
log "Verifying restore..."
TABLE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

log "Tables restored: $TABLE_COUNT"

if [ "$TABLE_COUNT" -gt 0 ]; then
    log "✅ Restore verification successful"
else
    error "Restore verification failed - no tables found"
    exit 1
fi

# Run migrations (if needed)
if [ -f "backend/alembic.ini" ]; then
    log "Running database migrations..."
    cd backend
    alembic upgrade head
    cd ..
    log "Migrations complete"
fi

# Generate restore report
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cat > "./backups/restore_report_${TIMESTAMP}.txt" << EOF
Restore Report
==============
Environment: $ENVIRONMENT
Database: $DB_NAME
Backup File: $BACKUP_FILE
Timestamp: $(date)
Tables Restored: $TABLE_COUNT
Status: SUCCESS
EOF

log "Restore completed successfully!"
log "Tables in database: $TABLE_COUNT"

# Cleanup
unset PGPASSWORD
unset DATABASE_URL
