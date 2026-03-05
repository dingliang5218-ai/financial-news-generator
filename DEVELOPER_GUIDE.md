# 开发者指南

## 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Main Entry Point                      │
│                          (main.py)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Health Check System                     │
│                     (health_check.py)                        │
│  • Startup Check  • Runtime Check  • API Connection Test    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Scheduler System                        │
│                      (scheduler.py)                          │
│  • Daily News (8:00)  • Market Updates (Hourly)             │
│  • Weekly Summary (Sun 18:00)  • Health Check (6h)          │
└─────┬───────────────┬───────────────┬────────────────┬──────┘
      │               │               │                │
      ▼               ▼               ▼                ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│   Data   │   │ Analyzer │   │Generator │   │ Storage  │
│ Fetcher  │──▶│          │──▶│          │──▶│          │
│          │   │          │   │          │   │          │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
     │              │               │              │
     ▼              ▼               ▼              ▼
┌──────────────────────────────────────────────────────┐
│              Support Systems                          │
│  • Logger  • Error Handler  • Config                 │
└──────────────────────────────────────────────────────┘
```

### 数据流

```
1. Data Collection Flow:
   RSS Feeds → DataFetcher → Raw News → Storage (dedup)

2. Analysis Flow:
   Raw News → Analyzer (Claude AI) → Analyzed Data

3. Generation Flow:
   Analyzed Data → Generator (Claude AI) → Article → Storage

4. Scheduling Flow:
   Scheduler → Task Trigger → Data Flow (1→2→3)
```

## 核心组件详解

### 1. Config (config.py)

**职责**: 集中管理所有配置

**关键配置**:
```python
# API 配置
CLAUDE_API_KEY          # Claude API 密钥

# RSS 配置
RSS_FEEDS               # RSS 订阅源列表
MAX_NEWS_PER_SOURCE     # 每个源最大新闻数

# 生成参数
IMPORTANCE_THRESHOLD    # 重要性阈值
QUICK_NEWS_MIN_LENGTH   # 简报最小字数
DEEP_ANALYSIS_MIN_LENGTH # 深度分析最小字数

# 重试配置
MAX_RETRIES            # 最大重试次数
RETRY_DELAY_BASE       # 重试延迟基数
```

**扩展方法**:
```python
# 添加新配置项
class Config:
    NEW_FEATURE_ENABLED = os.getenv("NEW_FEATURE_ENABLED", "false").lower() == "true"
```

### 2. Logger (logger.py)

**职责**: 统一日志管理

**日志级别**:
- DEBUG: 详细调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

**日志文件**:
- `logs/app_YYYYMMDD.log` - 主日志
- `logs/errors_YYYYMMDD.log` - 错误日志

**使用示例**:
```python
from logger import Logger

logger = Logger.get_logger('my_module')
logger.info("Processing started")
logger.error("Failed to process", exc_info=True)
```

### 3. Error Handler (error_handler.py)

**错误类型**:

1. **RetryableError**: 可重试错误
   - 网络超时
   - API 限流
   - 临时性故障

2. **DegradableError**: 可降级错误
   - 部分数据源失败
   - 非关键功能失败

3. **FatalError**: 致命错误
   - 配置错误
   - 数据库损坏
   - API 认证失败

**装饰器使用**:

```python
# 简单重试
@retry_with_backoff(max_retries=3, base_delay=2)
def fetch_data():
    # 会自动重试 3 次，延迟 2, 4, 8 秒
    pass

# 带错误处理的重试
@handle_errors(max_retries=3, retry_delay=60)
def generate_article():
    # 失败后重试，最终失败返回 None
    pass
```

### 4. Storage (storage.py)

**数据表结构**:

```sql
-- 文章表
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_url TEXT,
    importance INTEGER,
    news_type TEXT,
    word_count INTEGER,
    created_at TIMESTAMP
);

-- 原始新闻表（去重）
CREATE TABLE raw_news (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE,
    fetched_at TIMESTAMP
);

-- 数据源状态表
CREATE TABLE data_source_status (
    id INTEGER PRIMARY KEY,
    source_name TEXT UNIQUE,
    consecutive_failures INTEGER,
    last_success TIMESTAMP,
    last_failure TIMESTAMP,
    is_active INTEGER
);
```

**核心方法**:
```python
storage = Storage()

# 保存文章
article_id = storage.save_article(article_dict)

# 获取文章
article = storage.get_article(article_id)

# 搜索文章
results = storage.search_articles("关键词")

# 检查去重
if not storage.is_news_processed(url):
    storage.mark_news_processed(title, url)
```

### 5. Data Fetcher (data_fetcher.py)

**数据采集流程**:

```python
fetcher = DataFetcher()

# 1. 采集单个源
news_items = fetcher.fetch_rss_feed(feed_url)

# 2. 采集所有源
all_news = fetcher.fetch_all_sources()

# 3. 自动去重和错误处理
```

**扩展新数据源**:

```python
class DataFetcher:
    def fetch_api_source(self, api_url):
        """添加 API 数据源"""
        try:
            response = requests.get(api_url)
            data = response.json()
            return self._parse_api_data(data)
        except Exception as e:
            logger.error(f"API fetch failed: {e}")
            raise RetryableError(f"API error: {e}")

    def fetch_all_sources(self):
        """更新以包含新数据源"""
        all_news = []

        # RSS 源
        for feed in Config.RSS_FEEDS:
            all_news.extend(self.fetch_rss_feed(feed))

        # API 源（新增）
        for api in Config.API_SOURCES:
            all_news.extend(self.fetch_api_source(api))

        return all_news
```

### 6. Analyzer (analyzer.py)

**分析流程**:

```python
analyzer = Analyzer()

# 1. 单条分析
analysis = analyzer.analyze_news(news_item)
# 返回: {
#     'importance': 4,
#     'category': '股市',
#     'keywords': ['A股', '上涨'],
#     'summary': '...'
# }

# 2. 批量分析
batch_analysis = analyzer.analyze_batch(news_items)
# 返回: {
#     'priority_items': [...],  # 按重要性排序
#     'categories': {...},      # 分类统计
#     'total_analyzed': 10
# }
```

**自定义分析提示词**:

```python
ANALYSIS_PROMPT = """
你的自定义分析要求...

额外要求：
- 识别情感倾向
- 提取数字数据
- 关联历史事件
"""
```

### 7. Generator (generator.py)

**生成样式**:

1. **brief** (简报): 500-800 字
   - 快速概述
   - 关键信息
   - 适合市场更新

2. **comprehensive** (综合): 1000-1500 字
   - 详细分析
   - 背景介绍
   - 适合每日新闻

3. **deep** (深度): 1500-2500 字
   - 深入解读
   - 多角度分析
   - 适合专题报道

**使用示例**:

```python
generator = Generator()

# 生成文章
article = generator.generate_article(
    news_item,
    style='comprehensive'
)

# 生成周报
summary = generator.generate_weekly_summary(articles)
```

**自定义样式**:

```python
STYLE_PROMPTS = {
    'custom': """
    你的自定义生成要求...

    格式要求：
    - 标题：吸引眼球
    - 导语：概括核心
    - 正文：详细展开
    - 结语：总结展望
    """
}
```

### 8. Health Check (health_check.py)

**检查项目**:

1. **启动检查** (startup_check):
   - 配置验证
   - 依赖检查
   - 存储检查
   - API 连接测试

2. **运行时检查** (runtime_check):
   - 磁盘空间
   - 数据库连接

**自定义检查**:

```python
class HealthCheck:
    @staticmethod
    def _check_custom_service():
        """添加自定义服务检查"""
        try:
            # 检查逻辑
            return True
        except Exception as e:
            logger.error(f"Custom check failed: {e}")
            return False

    @staticmethod
    def startup_check():
        checks = {
            'config': HealthCheck._check_config(),
            'custom': HealthCheck._check_custom_service(),  # 新增
            # ...
        }
        # ...
```

### 9. Scheduler (scheduler.py)

**定时任务配置**:

```python
from apscheduler.triggers.cron import CronTrigger

# 每天特定时间
CronTrigger(hour=8, minute=0)

# 工作日特定时间段
CronTrigger(day_of_week='mon-fri', hour='9-17', minute=0)

# 每周特定时间
CronTrigger(day_of_week='sun', hour=18, minute=0)

# 每隔 N 小时
CronTrigger(hour='*/6')
```

**添加新任务**:

```python
class NewsScheduler:
    def setup(self):
        # 添加新任务
        self.scheduler.add_job(
            self.custom_task,
            CronTrigger(hour=12, minute=0),  # 每天中午
            id='custom_task',
            name='Custom Task',
            max_instances=1
        )

    @handle_errors(max_retries=3, retry_delay=300)
    def custom_task(self):
        """自定义任务"""
        logger.info("Running custom task...")
        # 任务逻辑
```

## 开发工作流

### 1. 添加新功能

```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发功能
# 编辑相关文件...

# 3. 测试
python test_system.py

# 4. 提交
git add .
git commit -m "feat: add new feature"

# 5. 合并
git checkout main
git merge feature/new-feature
```

### 2. 调试技巧

```python
# 启用详细日志
# 在 .env 中设置
LOG_LEVEL=DEBUG

# 单步测试
python main.py --run-once daily

# 查看日志
tail -f logs/app_$(date +%Y%m%d).log
```

### 3. 性能优化

```python
# 1. 使用批量操作
# 不好
for item in items:
    storage.save_article(item)

# 好
storage.save_articles_batch(items)

# 2. 缓存结果
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_operation(param):
    # 耗时操作
    pass

# 3. 异步处理
import asyncio

async def fetch_multiple_sources():
    tasks = [fetch_source(url) for url in urls]
    return await asyncio.gather(*tasks)
```

## 测试指南

### 单元测试

```python
# test_custom.py
import unittest
from my_module import MyClass

class TestMyClass(unittest.TestCase):
    def setUp(self):
        self.obj = MyClass()

    def test_method(self):
        result = self.obj.method()
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
```

### 集成测试

```python
# 使用现有的 test_system.py
class SystemTest:
    def test_new_feature(self):
        """测试新功能"""
        # 测试逻辑
        assert result == expected
        logger.info("✓ New feature test passed")
```

## 部署指南

### 开发环境

```bash
# 1. 克隆项目
git clone <repo-url>
cd daily

# 2. 配置环境
cp .env.example .env
# 编辑 .env

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行测试
python test_system.py

# 5. 启动
python main.py
```

### 生产环境

```bash
# 1. 使用虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
# 使用生产环境的 API Key 和配置

# 4. 使用 systemd 管理服务
sudo cp financial-news.service /etc/systemd/system/
sudo systemctl enable financial-news
sudo systemctl start financial-news

# 5. 监控日志
journalctl -u financial-news -f
```

### Docker 部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```bash
# 构建和运行
docker build -t financial-news .
docker run -d --name financial-news \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  financial-news
```

## 常见问题

### Q1: 如何修改生成频率？

编辑 `scheduler.py` 中的 CronTrigger 参数。

### Q2: 如何添加新的 RSS 源？

在 `.env` 文件中的 `RSS_FEEDS` 添加新 URL（逗号分隔）。

### Q3: 如何自定义文章格式？

修改 `generator.py` 中的 `STYLE_PROMPTS` 字典。

### Q4: 如何处理 API 限流？

调整 `config.py` 中的 `MAX_RETRIES` 和 `RETRY_DELAY_BASE`。

### Q5: 如何备份数据？

```bash
# 手动备份
cp data/articles.db data/backups/articles_$(date +%Y%m%d).db

# 自动备份（添加到 crontab）
0 2 * * * cp /path/to/data/articles.db /path/to/backups/articles_$(date +\%Y\%m\%d).db
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 代码规范

- 遵循 PEP 8
- 使用类型提示
- 编写文档字符串
- 添加单元测试
- 保持函数简洁（< 50 行）

## 许可证

MIT License
