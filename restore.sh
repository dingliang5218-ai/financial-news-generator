#!/bin/bash
# Restore script for Financial News Auto-Generation System

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Financial News System Restore"
echo "=========================================="
echo ""

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    echo ""
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh backups/*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Confirm restore
echo -e "${YELLOW}Warning: This will overwrite existing data!${NC}"
echo "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to restore? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Create backup of current data
echo ""
echo "Creating backup of current data..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p backups/pre-restore
tar czf "backups/pre-restore/backup_${TIMESTAMP}.tar.gz" data/ logs/ .env 2>/dev/null || true
echo -e "${GREEN}✓ Current data backed up${NC}"

# Extract backup
echo ""
echo "Restoring from backup..."
tar xzf "$BACKUP_FILE" -C .
echo -e "${GREEN}✓ Backup restored${NC}"

# Verify restoration
echo ""
echo "Verifying restoration..."
if [ -f "data/articles.db" ]; then
    echo -e "${GREEN}✓ Database restored${NC}"
else
    echo -e "${RED}✗ Database not found${NC}"
fi

if [ -f ".env" ]; then
    echo -e "${GREEN}✓ Configuration restored${NC}"
else
    echo -e "${YELLOW}⚠ Configuration not found${NC}"
fi

echo ""
echo -e "${GREEN}Restore completed successfully!${NC}"
echo ""
echo "Pre-restore backup saved to: backups/pre-restore/backup_${TIMESTAMP}.tar.gz"
