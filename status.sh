#!/bin/bash
# System status check script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Financial News System Status Check"
echo "=========================================="
echo ""

# Check Python version
echo -n "Python version: "
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}$PYTHON_VERSION${NC}"

# Check if virtual environment exists
echo -n "Virtual environment: "
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${YELLOW}⚠ Not found${NC}"
fi

# Check dependencies
echo -n "Dependencies: "
if pip list | grep -q "anthropic"; then
    echo -e "${GREEN}✓ Installed${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
fi

# Check configuration
echo ""
echo "Configuration:"
echo -n "  .env file: "
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ Exists${NC}"

    # Check API key
    echo -n "  API key: "
    if grep -q "CLAUDE_API_KEY=sk-" .env 2>/dev/null; then
        echo -e "${GREEN}✓ Configured${NC}"
    else
        echo -e "${YELLOW}⚠ Not configured${NC}"
    fi

    # Check RSS feeds
    echo -n "  RSS feeds: "
    if grep -q "RSS_FEEDS=" .env 2>/dev/null; then
        FEED_COUNT=$(grep "RSS_FEEDS=" .env | tr ',' '\n' | wc -l)
        echo -e "${GREEN}✓ $FEED_COUNT configured${NC}"
    else
        echo -e "${YELLOW}⚠ Not configured${NC}"
    fi
else
    echo -e "${RED}✗ Not found${NC}"
fi

# Check data directory
echo ""
echo "Data directories:"
for dir in data logs data/backups; do
    echo -n "  $dir: "
    if [ -d "$dir" ]; then
        SIZE=$(du -sh "$dir" 2>/dev/null | cut -f1)
        echo -e "${GREEN}✓ Exists ($SIZE)${NC}"
    else
        echo -e "${YELLOW}⚠ Not found${NC}"
    fi
done

# Check database
echo ""
echo -n "Database: "
if [ -f "data/articles.db" ]; then
    DB_SIZE=$(du -sh data/articles.db | cut -f1)
    ARTICLE_COUNT=$(sqlite3 data/articles.db "SELECT COUNT(*) FROM articles" 2>/dev/null || echo "0")
    echo -e "${GREEN}✓ Exists ($DB_SIZE, $ARTICLE_COUNT articles)${NC}"
else
    echo -e "${YELLOW}⚠ Not found${NC}"
fi

# Check disk space
echo ""
echo -n "Disk space: "
DISK_FREE=$(df -h . | tail -1 | awk '{print $4}')
echo -e "${GREEN}$DISK_FREE available${NC}"

# Check running processes
echo ""
echo -n "Running processes: "
if pgrep -f "python.*main.py" > /dev/null; then
    PID=$(pgrep -f "python.*main.py")
    echo -e "${GREEN}✓ Running (PID: $PID)${NC}"
else
    echo -e "${YELLOW}⚠ Not running${NC}"
fi

# Check recent logs
echo ""
echo "Recent logs:"
if [ -d "logs" ]; then
    LATEST_LOG=$(ls -t logs/*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo "  Latest: $LATEST_LOG"
        echo -n "  Last error: "
        LAST_ERROR=$(grep "ERROR" "$LATEST_LOG" 2>/dev/null | tail -1 | cut -d'|' -f1,4)
        if [ -n "$LAST_ERROR" ]; then
            echo -e "${YELLOW}$LAST_ERROR${NC}"
        else
            echo -e "${GREEN}None${NC}"
        fi
    else
        echo -e "  ${YELLOW}No logs found${NC}"
    fi
else
    echo -e "  ${YELLOW}Logs directory not found${NC}"
fi

# Check backups
echo ""
echo -n "Backups: "
if [ -d "backups" ]; then
    BACKUP_COUNT=$(ls backups/*.tar.gz 2>/dev/null | wc -l)
    if [ $BACKUP_COUNT -gt 0 ]; then
        LATEST_BACKUP=$(ls -t backups/*.tar.gz 2>/dev/null | head -1)
        BACKUP_DATE=$(stat -c %y "$LATEST_BACKUP" 2>/dev/null | cut -d' ' -f1)
        echo -e "${GREEN}✓ $BACKUP_COUNT backups (latest: $BACKUP_DATE)${NC}"
    else
        echo -e "${YELLOW}⚠ No backups found${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Backup directory not found${NC}"
fi

# System health check
echo ""
echo "Running health check..."
if python3 main.py --health-check > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo "Status Summary"
echo "=========================================="

# Count issues
ISSUES=0

[ ! -f ".env" ] && ISSUES=$((ISSUES+1))
[ ! -d "data" ] && ISSUES=$((ISSUES+1))
[ ! -f "data/articles.db" ] && ISSUES=$((ISSUES+1))

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ System is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Found $ISSUES issue(s)${NC}"
    echo ""
    echo "Recommendations:"
    [ ! -f ".env" ] && echo "  - Create .env file from .env.example"
    [ ! -d "data" ] && echo "  - Run the system once to initialize data directory"
    [ ! -f "data/articles.db" ] && echo "  - Run the system once to initialize database"
fi

echo ""
