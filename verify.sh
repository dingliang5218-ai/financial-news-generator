#!/bin/bash
# Project verification script - Check if all components are in place

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}项目完整性验证${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

TOTAL=0
PASSED=0
FAILED=0

check_file() {
    local file=$1
    local desc=$2
    TOTAL=$((TOTAL + 1))

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $desc"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $desc (缺失: $file)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

check_executable() {
    local file=$1
    local desc=$2
    TOTAL=$((TOTAL + 1))

    if [ -f "$file" ] && [ -x "$file" ]; then
        echo -e "${GREEN}✓${NC} $desc"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $desc (不可执行: $file)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Check core Python files
echo -e "${BLUE}核心代码文件:${NC}"
check_file "config.py" "配置管理"
check_file "logger.py" "日志系统"
check_file "error_handler.py" "错误处理"
check_file "storage.py" "数据存储"
check_file "data_fetcher.py" "数据采集"
check_file "analyzer.py" "智能分析"
check_file "generator.py" "内容生成"
check_file "health_check.py" "健康检查"
check_file "scheduler.py" "任务调度"
check_file "main.py" "主程序"
echo ""

# Check test files
echo -e "${BLUE}测试文件:${NC}"
check_file "test_system.py" "集成测试"
echo ""

# Check shell scripts
echo -e "${BLUE}工具脚本:${NC}"
check_executable "run.sh" "快速启动脚本"
check_executable "demo.sh" "演示脚本"
check_executable "status.sh" "状态检查脚本"
check_executable "backup.sh" "备份脚本"
check_executable "restore.sh" "恢复脚本"
echo ""

# Check configuration files
echo -e "${BLUE}配置文件:${NC}"
check_file "requirements.txt" "依赖列表"
check_file ".env.example" "环境变量模板"
check_file ".gitignore" "Git 忽略规则"
check_file ".dockerignore" "Docker 忽略规则"
echo ""

# Check deployment files
echo -e "${BLUE}部署文件:${NC}"
check_file "Dockerfile" "Docker 镜像配置"
check_file "docker-compose.yml" "Docker Compose 配置"
check_file "financial-news.service" "systemd 服务配置"
echo ""

# Check documentation
echo -e "${BLUE}文档文件:${NC}"
check_file "README.md" "用户文档"
check_file "DEVELOPER_GUIDE.md" "开发者指南"
check_file "API_REFERENCE.md" "API 参考"
check_file "DOCKER_GUIDE.md" "Docker 部署指南"
check_file "PROJECT_SUMMARY.md" "项目总结"
check_file "FINAL_REPORT.md" "项目完成报告"
check_file "CHANGELOG.md" "变更日志"
check_file "CONTRIBUTING.md" "贡献指南"
check_file "QUICK_REFERENCE.md" "快速参考"
check_file "INDEX.md" "文档索引"
check_file "CLAUDE.md" "项目说明"
check_file "LICENSE" "许可证"
check_file "PROJECT_COMPLETION.txt" "完成总结"
echo ""

# Check Python syntax
echo -e "${BLUE}Python 语法检查:${NC}"
TOTAL=$((TOTAL + 1))
if python3 -m py_compile *.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC} 所有 Python 文件语法正确"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗${NC} Python 文件存在语法错误"
    FAILED=$((FAILED + 1))
fi
echo ""

# Check Git repository
echo -e "${BLUE}Git 仓库检查:${NC}"
TOTAL=$((TOTAL + 1))
if [ -d ".git" ]; then
    echo -e "${GREEN}✓${NC} Git 仓库已初始化"
    PASSED=$((PASSED + 1))

    # Check commit count
    COMMIT_COUNT=$(git log --oneline | wc -l)
    echo "  提交数: $COMMIT_COUNT"

    # Check branch
    BRANCH=$(git branch --show-current)
    echo "  当前分支: $BRANCH"
else
    echo -e "${RED}✗${NC} Git 仓库未初始化"
    FAILED=$((FAILED + 1))
fi
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}验证结果${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "总检查项: $TOTAL"
echo -e "${GREEN}通过: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}失败: $FAILED${NC}"
fi
echo ""

# Calculate percentage
PERCENTAGE=$((PASSED * 100 / TOTAL))
echo "完整性: $PERCENTAGE%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 项目完整性验证通过！${NC}"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  发现 $FAILED 个问题，请检查${NC}"
    echo ""
    exit 1
fi
