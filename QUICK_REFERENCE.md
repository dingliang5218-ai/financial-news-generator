# 快速参考卡片

## 一分钟快速开始

```bash
# 1. 配置环境
cp .env.example .env
# 编辑 .env，添加 CLAUDE_API_KEY

# 2. 快速启动
./run.sh

# 3. 运行系统
python main.py
```

## 常用命令

### 运行模式

```bash
# 启动调度器（后台运行）
python main.py

# 单次生成（测试）
python main.py --run-once daily    # 每日新闻
python main.py --run-once market   # 市场更新
python main.py --run-once weekly   # 周报

# 健康检查
python main.py --health-check

# 查看版本
python main.py --version
```

### 测试和检查

```bash
# 运行集成测试
python test_system.py

# 系统状态检查
./status.sh

# 查看日志
tail -f logs/app_$(date +%Y%m%d).log
```

### 备份和恢复

```bash
# 创建备份
./backup.sh

# 恢复数据
./restore.sh backups/full_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Docker 部署

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

## 配置速查

### 环境变量 (.env)

```bash
# 必需配置
CLAUDE_API_KEY=sk-ant-xxx          # Claude API 密钥
RSS_FEEDS=url1,url2,url3           # RSS 源（逗号分隔）

# 可选配置
MAX_NEWS_PER_SOURCE=20             # 每源最大新闻数
IMPORTANCE_THRESHOLD=3             # 重要性阈值
MAX_RETRIES=3                      # 最大重试次数
LOG_LEVEL=INFO                     # 日志级别
```

### 定时任务

| 任务 | 时间 | 说明 |
|------|------|------|
| 每日新闻 | 8:00 AM | 生成 5 篇综合文章 |
| 市场更新 | 工作日 9-17 点每小时 | 生成简报 |
| 周报 | 周日 18:00 | 生成周总结 |
| 健康检查 | 每 6 小时 | 系统检查 |

## 目录结构

```
daily/
├── *.py              # 核心代码（10 个文件）
├── *.sh              # 工具脚本（4 个）
├── *.md              # 文档（10 个）
├── data/             # 数据目录
│   ├── articles.db   # 数据库
│   └── backups/      # 备份
└── logs/             # 日志目录
```

## 故障排除

### 问题：API 连接失败

```bash
# 检查 API Key
grep CLAUDE_API_KEY .env

# 测试连接
python main.py --health-check
```

### 问题：磁盘空间不足

```bash
# 检查空间
df -h .

# 清理日志
find logs/ -name "*.log" -mtime +30 -delete

# 清理备份
find backups/ -name "*.tar.gz" -mtime +7 -delete
```

### 问题：数据库锁定

```bash
# 检查进程
ps aux | grep python

# 停止进程
pkill -f "python.*main.py"

# 重启
python main.py
```

## 性能参考

| 操作 | 时间 |
|------|------|
| RSS 采集 | 2-5 秒/源 |
| 新闻分析 | 3-5 秒/条 |
| 文章生成 | 10-20 秒/篇 |
| 数据库查询 | <100ms |

## 资源需求

| 资源 | 最小 | 推荐 |
|------|------|------|
| CPU | 1 核 | 2 核 |
| 内存 | 512MB | 1GB |
| 磁盘 | 5GB | 10GB |
| 网络 | 稳定连接 | 稳定连接 |

## 文档导航

| 文档 | 用途 |
|------|------|
| README.md | 用户指南 |
| DEVELOPER_GUIDE.md | 开发指南 |
| API_REFERENCE.md | API 文档 |
| DOCKER_GUIDE.md | Docker 部署 |
| CONTRIBUTING.md | 贡献指南 |
| CHANGELOG.md | 变更日志 |
| FINAL_REPORT.md | 项目报告 |

## 获取帮助

1. 查看文档
2. 运行 `./status.sh` 检查状态
3. 查看日志文件
4. 提交 GitHub Issue

## 版本信息

- **当前版本**: v1.0.0
- **发布日期**: 2026-03-05
- **Python 版本**: 3.8+
- **许可证**: MIT

---

**提示**: 将此文件打印或保存为书签，方便快速查阅！
