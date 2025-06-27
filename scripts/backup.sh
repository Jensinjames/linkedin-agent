#!/bin/bash
# Backup script for LinkedIn Agent
# Handles database, job files, and Redis data backup

set -euo pipefail

# Configuration
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
DATA_DIR="./data"
STORAGE_DIR="./storage"
LOG_FILE="$BACKUP_DIR/backup.log"
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log_info "Starting backup process..."
log_info "Backup directory: $BACKUP_DIR"

# Function to check if Docker containers are running
check_containers() {
    if ! docker ps --format "table {{.Names}}" | grep -q "linkedin-agent"; then
        log_warn "LinkedIn Agent containers not running. Some backups may be incomplete."
        return 1
    fi
    return 0
}

# Function to backup SQLite database
backup_database() {
    log_info "Backing up SQLite database..."
    
    if [ -f "$DATA_DIR/jobs.db" ]; then
        # Create a copy of the database
        cp "$DATA_DIR/jobs.db" "$BACKUP_DIR/jobs.db"
        
        # Create SQL dump for better portability
        if command -v sqlite3 >/dev/null 2>&1; then
            sqlite3 "$DATA_DIR/jobs.db" ".dump" > "$BACKUP_DIR/jobs.sql"
            log_info "Database backup completed: jobs.db and jobs.sql"
        else
            log_warn "sqlite3 not found, only binary backup created"
        fi
    else
        log_warn "Database file not found: $DATA_DIR/jobs.db"
    fi
}

# Function to backup job files
backup_jobs() {
    log_info "Backing up job files..."
    
    if [ -d "$DATA_DIR/jobs" ]; then
        # Create tar archive of job files
        tar -czf "$BACKUP_DIR/jobs.tar.gz" -C "$DATA_DIR" jobs/
        
        # Count job directories
        job_count=$(find "$DATA_DIR/jobs" -maxdepth 1 -type d -name "job_*" | wc -l)
        log_info "Job files backup completed: $job_count job directories"
    else
        log_warn "Jobs directory not found: $DATA_DIR/jobs"
    fi
}

# Function to backup Redis data
backup_redis() {
    log_info "Backing up Redis data..."
    
    if check_containers; then
        # Trigger Redis BGSAVE
        if docker exec linkedin-agent-redis redis-cli BGSAVE >/dev/null 2>&1; then
            # Wait for BGSAVE to complete
            sleep 5
            
            # Copy Redis dump file
            redis_dump_path=$(docker exec linkedin-agent-redis redis-cli CONFIG GET dir | tail -n 1)
            if [ -n "$redis_dump_path" ]; then
                docker cp "linkedin-agent-redis:$redis_dump_path/dump.rdb" "$BACKUP_DIR/redis_dump.rdb"
                log_info "Redis backup completed: redis_dump.rdb"
            else
                log_warn "Could not determine Redis dump path"
            fi
        else
            log_warn "Failed to trigger Redis BGSAVE"
        fi
    else
        log_warn "Redis container not running, skipping Redis backup"
    fi
}

# Function to backup storage directory
backup_storage() {
    log_info "Backing up storage directory..."
    
    if [ -d "$STORAGE_DIR" ]; then
        tar -czf "$BACKUP_DIR/storage.tar.gz" -C . storage/
        log_info "Storage backup completed: storage.tar.gz"
    else
        log_warn "Storage directory not found: $STORAGE_DIR"
    fi
}

# Function to create backup manifest
create_manifest() {
    log_info "Creating backup manifest..."
    
    cat > "$BACKUP_DIR/manifest.txt" << EOF
LinkedIn Agent Backup Manifest
Generated: $(date)
Backup ID: $(basename "$BACKUP_DIR")

Files included:
$(ls -la "$BACKUP_DIR" | grep -v manifest.txt)

System information:
- Hostname: $(hostname)
- Date: $(date)
- Disk usage: $(df -h . | tail -1)

Database information:
$(if [ -f "$DATA_DIR/jobs.db" ]; then
    echo "- Database size: $(du -h "$DATA_DIR/jobs.db" | cut -f1)"
    if command -v sqlite3 >/dev/null 2>&1; then
        echo "- Total jobs: $(sqlite3 "$DATA_DIR/jobs.db" "SELECT COUNT(*) FROM jobs;" 2>/dev/null || echo "unknown")"
    fi
fi)

Job files information:
$(if [ -d "$DATA_DIR/jobs" ]; then
    echo "- Job directories: $(find "$DATA_DIR/jobs" -maxdepth 1 -type d -name "job_*" | wc -l)"
    echo "- Total job files size: $(du -sh "$DATA_DIR/jobs" 2>/dev/null | cut -f1 || echo "unknown")"
fi)
EOF

    log_info "Manifest created: manifest.txt"
}

# Function to clean old backups
cleanup_old_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."
    
    find ./backups -maxdepth 1 -type d -name "backup_*" -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    backup_count=$(find ./backups -maxdepth 1 -type d -name "backup_*" | wc -l)
    log_info "Remaining backups: $backup_count"
}

# Function to verify backup integrity
verify_backup() {
    log_info "Verifying backup integrity..."
    
    local errors=0
    
    # Check if backup files exist
    if [ ! -f "$BACKUP_DIR/jobs.db" ] && [ ! -f "$BACKUP_DIR/jobs.sql" ]; then
        log_error "Database backup verification failed"
        ((errors++))
    fi
    
    if [ ! -f "$BACKUP_DIR/jobs.tar.gz" ]; then
        log_error "Job files backup verification failed"
        ((errors++))
    fi
    
    if [ ! -f "$BACKUP_DIR/manifest.txt" ]; then
        log_error "Manifest verification failed"
        ((errors++))
    fi
    
    # Test tar archive integrity
    if [ -f "$BACKUP_DIR/jobs.tar.gz" ]; then
        if ! tar -tzf "$BACKUP_DIR/jobs.tar.gz" >/dev/null 2>&1; then
            log_error "Job files archive is corrupted"
            ((errors++))
        fi
    fi
    
    if [ $errors -eq 0 ]; then
        log_info "Backup verification completed successfully"
        return 0
    else
        log_error "Backup verification failed with $errors errors"
        return 1
    fi
}

# Main backup process
main() {
    local start_time=$(date +%s)
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Run backup operations
    backup_database
    backup_jobs
    backup_redis
    backup_storage
    create_manifest
    
    # Verify backup
    if verify_backup; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log_info "Backup completed successfully in ${duration} seconds"
        log_info "Backup location: $BACKUP_DIR"
        
        # Clean up old backups
        cleanup_old_backups
        
        # Create symlink to latest backup
        ln -sfn "$BACKUP_DIR" "./backups/latest"
        
        exit 0
    else
        log_error "Backup verification failed"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--help|--verify|--cleanup]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --verify       Verify latest backup integrity"
        echo "  --cleanup      Clean up old backups only"
        exit 0
        ;;
    --verify)
        if [ -L "./backups/latest" ]; then
            BACKUP_DIR=$(readlink -f "./backups/latest")
            verify_backup
        else
            log_error "No latest backup found"
            exit 1
        fi
        ;;
    --cleanup)
        cleanup_old_backups
        exit 0
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        exit 1
        ;;
esac