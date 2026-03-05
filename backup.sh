#!/bin/bash
# Backup script for Financial News Auto-Generation System

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS="${RETENTION_DAYS:-7}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Financial News System Backup"
echo "=========================================="
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo -n "Backing up database... "
if [ -f "data/articles.db" ]; then
    cp data/articles.db "$BACKUP_DIR/articles_${DATE}.db"
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ Database not found${NC}"
fi

# Backup configuration
echo -n "Backing up configuration... "
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/env_${DATE}.backup"
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ .env not found${NC}"
fi

# Backup logs (last 7 days)
echo -n "Backing up recent logs... "
if [ -d "logs" ]; then
    tar czf "$BACKUP_DIR/logs_${DATE}.tar.gz" logs/*.log 2>/dev/null || true
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ Logs directory not found${NC}"
fi

# Create full backup archive
echo -n "Creating full backup archive... "
tar czf "$BACKUP_DIR/full_backup_${DATE}.tar.gz" \
    data/ \
    logs/ \
    .env 2>/dev/null || true
echo -e "${GREEN}✓${NC}"

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR/full_backup_${DATE}.tar.gz" | cut -f1)
echo ""
echo "Backup completed: full_backup_${DATE}.tar.gz ($BACKUP_SIZE)"

# Cleanup old backups
echo ""
echo "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "*.db" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.backup" -mtime +$RETENTION_DAYS -delete

# List recent backups
echo ""
echo "Recent backups:"
ls -lh "$BACKUP_DIR" | tail -5

echo ""
echo -e "${GREEN}Backup completed successfully!${NC}"
