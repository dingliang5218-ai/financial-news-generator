# 财经新闻自动生成系统

基于 Claude AI 的智能财经新闻自动生成系统，支持多源数据采集、智能分析和自动化内容生成。

## 功能特性

- **多源数据采集**：支持 RSS、财经 API 等多种数据源
- **智能内容分析**：使用 Claude AI 进行新闻分析和分类
- **智能新闻聚合**：自动识别同一事件的不同报道并聚合
- **Top3 筛选**：综合重要性、热度、时效性选出最重要的3条新闻
- **多维度影响分析**：分析新闻对全球经济、美国经济、中国经济、美股、A股等的影响
- **混合内容生成**：生成日报汇总 + 重要事件深度分析
- **定时任务调度**：支持每日新闻、市场更新、周报等定时生成
- **健康检查系统**：启动和运行时的全面健康检查
- **完善的错误处理**：自动重试和错误恢复机制

## 系统要求

- Python 3.8+
- Claude API Key
- 至少 100MB 可用磁盘空间

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
CLAUDE_API_KEY=your_api_key_here
DATA_DIR=./data
LOG_LEVEL=INFO
```

### 3. 运行健康检查

```bash
python main.py --health-check
```

### 4. 启动系统

```bash
# 启动调度器（后台运行）
python main.py

# 或者运行单次任务（测试用）
python main.py --run-once daily
```

## 使用说明

### 命令行选项

```bash
# 启动调度器（默认模式）
python main.py

# 运行单次任务
python main.py --run-once daily    # 生成每日新闻
python main.py --run-once market   # 生成市场更新
python main.py --run-once weekly   # 生成周报

# 仅运行健康检查
python main.py --health-check

# 跳过启动健康检查（不推荐）
python main.py --skip-health-check

# 显示版本信息
python main.py --version
```

### 定时任务说明

系统默认配置了以下定时任务：

- **每日新闻**：每天 8:00 AM 生成
- **市场更新**：工作日 9:00 AM - 5:00 PM 每小时生成
- **周报总结**：每周日 6:00 PM 生成
- **健康检查**：每 6 小时运行一次

### 测试系统

运行集成测试：

```bash
python test_system.py
```

## 项目结构

```
.
├── config.py           # 配置管理
├── logger.py           # 日志系统
├── error_handler.py    # 错误处理
├── storage.py          # 数据存储
├── data_fetcher.py     # 数据采集
├── analyzer.py         # 智能分析
├── generator.py        # 内容生成
├── health_check.py     # 健康检查
├── scheduler.py        # 任务调度
├── main.py             # 主程序入口
├── test_system.py      # 集成测试
├── requirements.txt    # 依赖列表
├── .env.example        # 环境变量示例
└── README.md           # 使用文档
```

## 数据目录结构

```
data/
├── news.db            # SQLite 数据库
├── backup/            # 数据备份
└── logs/              # 日志文件
    └── app_YYYYMMDD.log
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `CLAUDE_API_KEY` | Claude API 密钥 | 必填 |
| `DATA_DIR` | 数据目录路径 | `./data` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `MAX_RETRIES` | 最大重试次数 | `3` |
| `RETRY_DELAY` | 重试延迟（秒） | `60` |

### 数据源配置

在 `config.py` 中配置 RSS 源：

```python
RSS_FEEDS = [
    'https://example.com/rss/finance',
    'https://example.com/rss/market',
]
```

## 故障排除

### 常见问题

**1. API 连接失败**

```
✗ Claude API connection failed
```

解决方案：
- 检查 API Key 是否正确
- 检查网络连接
- 确认 API 配额是否充足

**2. 磁盘空间不足**

```
Insufficient disk space: XX.XMB free (minimum 100MB required)
```

解决方案：
- 清理数据目录
- 删除旧的备份文件
- 增加磁盘空间

**3. 数据库锁定**

```
Database check failed: database is locked
```

解决方案：
- 确保没有其他进程在使用数据库
- 重启系统

### 日志查看

日志文件位于 `data/logs/` 目录：

```bash
# 查看今天的日志
tail -f data/logs/app_$(date +%Y%m%d).log

# 搜索错误日志
grep ERROR data/logs/app_*.log
```

## 开发指南

### 添加新的数据源

1. 在 `data_fetcher.py` 中添加新的采集方法
2. 在 `config.py` 中配置数据源 URL
3. 更新 `fetch_all_sources()` 方法

### 自定义生成样式

在 `generator.py` 中修改 `STYLE_PROMPTS` 字典：

```python
STYLE_PROMPTS = {
    'custom': "你的自定义提示词...",
}
```

### 调整调度时间

在 `scheduler.py` 中修改 CronTrigger 参数：

```python
self.scheduler.add_job(
    self.generate_daily_news,
    CronTrigger(hour=9, minute=30),  # 改为 9:30 AM
    ...
)
```

## 性能优化

- 数据库定期备份（每周自动）
- 日志文件自动轮转（每天）
- 旧数据自动清理（保留 30 天）
- API 请求限流保护

## 安全建议

- 不要将 `.env` 文件提交到版本控制
- 定期更换 API Key
- 限制数据目录访问权限
- 定期备份数据库

## 许可证

MIT License

## 支持

如有问题或建议，请提交 Issue。
