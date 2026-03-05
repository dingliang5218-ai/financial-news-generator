# API 参考文档

## 概述

本文档详细说明了财经新闻自动生成系统的所有 API 和接口。

## 核心类和方法

### Config

配置管理类，提供系统所有配置项。

#### 类属性

```python
class Config:
    # 版本信息
    VERSION: str = "1.0.0"

    # API 配置
    CLAUDE_API_KEY: str          # Claude API 密钥

    # RSS 配置
    RSS_FEEDS: List[str]         # RSS 订阅源列表
    MAX_NEWS_PER_SOURCE: int     # 每个源最大新闻数（默认：20）

    # 生成参数
    IMPORTANCE_THRESHOLD: int    # 重要性阈值（默认：3）
    QUICK_NEWS_MIN_LENGTH: int   # 简报最小字数（默认：500）
    QUICK_NEWS_MAX_LENGTH: int   # 简报最大字数（默认：800）
    DEEP_ANALYSIS_MIN_LENGTH: int # 深度分析最小字数（默认：1500）
    DEEP_ANALYSIS_MAX_LENGTH: int # 深度分析最大字数（默认：2500）

    # 调度配置
    FETCH_INTERVAL_MINUTES: int  # 采集间隔（默认：30）

    # 重试配置
    MAX_RETRIES: int             # 最大重试次数（默认：3）
    RETRY_DELAY_BASE: int        # 重试延迟基数（默认：2）

    # 日志配置
    LOG_LEVEL: str               # 日志级别（默认：INFO）
    LOG_RETENTION_DAYS: int      # 日志保留天数（默认：30）

    # 路径配置
    DATA_DIR: str                # 数据目录（默认：data）
    LOGS_DIR: str                # 日志目录（默认：logs）
    BACKUP_DIR: str              # 备份目录（默认：data/backups）
    DB_PATH: str                 # 数据库路径（默认：data/articles.db）
```

#### 方法

```python
@classmethod
def validate(cls) -> bool:
    """
    验证必需的配置项

    Returns:
        bool: 配置是否有效

    Raises:
        ValueError: 如果缺少必需配置
    """
```

---

### Logger

日志管理类，提供统一的日志记录功能。

#### 方法

```python
@classmethod
def get_logger(cls, name: str) -> logging.Logger:
    """
    获取或创建日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器实例
    """

@classmethod
def cleanup_old_logs(cls) -> None:
    """
    清理过期的日志文件

    删除超过 LOG_RETENTION_DAYS 天的日志文件
    """
```

#### 使用示例

```python
from logger import Logger

logger = Logger.get_logger('my_module')

logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

---

### Storage

数据存储类，管理 SQLite 数据库操作。

#### 方法

```python
def __init__(self):
    """初始化存储系统，创建数据库和表"""

def save_article(self, article: Dict) -> int:
    """
    保存生成的文章

    Args:
        article: 文章字典，包含以下字段：
            - title: str (必需) 文章标题
            - content: str (必需) 文章内容
            - source_url: str (可选) 来源 URL
            - importance: int (可选) 重要性评分
            - news_type: str (可选) 新闻类型
            - word_count: int (可选) 字数

    Returns:
        int: 文章 ID

    Raises:
        RetryableError: 数据库写入失败
    """

def get_article(self, article_id: int) -> Optional[Dict]:
    """
    根据 ID 获取文章

    Args:
        article_id: 文章 ID

    Returns:
        Optional[Dict]: 文章字典，如果不存在返回 None
    """

def get_recent_articles(self, limit: int = 10) -> List[Dict]:
    """
    获取最近的文章

    Args:
        limit: 返回数量限制

    Returns:
        List[Dict]: 文章列表
    """

def search_articles(self, query: str) -> List[Dict]:
    """
    搜索文章

    Args:
        query: 搜索关键词

    Returns:
        List[Dict]: 匹配的文章列表（最多 50 条）
    """

def get_articles_by_date_range(self, days: int = 7) -> List[Dict]:
    """
    获取指定天数内的文章

    Args:
        days: 天数

    Returns:
        List[Dict]: 文章列表
    """

def is_news_processed(self, url: str) -> bool:
    """
    检查新闻 URL 是否已处理

    Args:
        url: 新闻 URL

    Returns:
        bool: 是否已处理
    """

def mark_news_processed(self, title: str, url: str) -> None:
    """
    标记新闻为已处理

    Args:
        title: 新闻标题
        url: 新闻 URL
    """

def update_source_status(self, source_name: str, success: bool) -> None:
    """
    更新数据源状态

    Args:
        source_name: 数据源名称
        success: 是否成功
    """

def get_active_sources(self) -> List[str]:
    """
    获取活跃的数据源列表

    Returns:
        List[str]: 数据源名称列表
    """
```

---

### DataFetcher

数据采集类，负责从各种数据源获取新闻。

#### 方法

```python
def __init__(self):
    """初始化数据采集器"""

def fetch_rss_feed(self, feed_url: str) -> List[Dict]:
    """
    采集单个 RSS 源

    Args:
        feed_url: RSS 源 URL

    Returns:
        List[Dict]: 新闻项列表，每项包含：
            - title: str 标题
            - link: str 链接
            - summary: str 摘要
            - published: str 发布时间

    Raises:
        RetryableError: 采集失败
    """

def fetch_all_sources(self) -> List[Dict]:
    """
    采集所有配置的数据源

    Returns:
        List[Dict]: 所有新闻项列表
    """
```

---

### Analyzer

智能分析类，使用 Claude AI 分析新闻。

#### 方法

```python
def __init__(self):
    """初始化分析器"""

def analyze_news(self, news_item: Dict) -> Dict:
    """
    分析单条新闻

    Args:
        news_item: 新闻项字典

    Returns:
        Dict: 分析结果，包含：
            - importance: int (1-5) 重要性评分
            - category: str 新闻分类
            - keywords: List[str] 关键词列表
            - summary: str 摘要

    Raises:
        RetryableError: API 调用失败
    """

def analyze_batch(self, news_items: List[Dict]) -> Dict:
    """
    批量分析新闻

    Args:
        news_items: 新闻项列表

    Returns:
        Dict: 批量分析结果，包含：
            - priority_items: List[Dict] 按重要性排序的新闻
            - categories: Dict[str, int] 分类统计
            - total_analyzed: int 分析总数
    """
```

---

### Generator

内容生成类，使用 Claude AI 生成文章。

#### 方法

```python
def __init__(self):
    """初始化生成器"""

def generate_article(self, news_item: Dict, style: str = 'comprehensive') -> Dict:
    """
    生成文章

    Args:
        news_item: 新闻项字典
        style: 生成样式，可选值：
            - 'brief': 简报（500-800字）
            - 'comprehensive': 综合（1000-1500字）
            - 'deep': 深度（1500-2500字）

    Returns:
        Dict: 生成的文章，包含：
            - title: str 标题
            - content: str 内容
            - summary: str 摘要
            - category: str 分类
            - keywords: List[str] 关键词
            - source_urls: List[str] 来源链接
            - generated_at: str 生成时间

    Raises:
        RetryableError: 生成失败
    """

def generate_weekly_summary(self, articles: List[Dict]) -> Dict:
    """
    生成周报总结

    Args:
        articles: 文章列表

    Returns:
        Dict: 周报文章
    """
```

---

### HealthCheck

健康检查类，提供系统健康检查功能。

#### 方法

```python
@staticmethod
def startup_check() -> bool:
    """
    启动健康检查

    检查项目：
    - 配置验证
    - 依赖检查
    - 存储检查
    - API 连接测试

    Returns:
        bool: 检查是否通过

    Raises:
        FatalError: 检查失败
    """

@staticmethod
def runtime_check() -> bool:
    """
    运行时健康检查

    检查项目：
    - 磁盘空间
    - 数据库连接

    Returns:
        bool: 检查是否通过
    """
```

---

### NewsScheduler

任务调度类，管理定时任务。

#### 方法

```python
def __init__(self):
    """初始化调度器"""

def setup(self) -> None:
    """
    设置定时任务

    配置的任务：
    - 每日新闻：8:00 AM
    - 市场更新：工作日 9-17 点每小时
    - 周报：周日 18:00
    - 健康检查：每 6 小时
    """

def start(self) -> None:
    """
    启动调度器

    阻塞运行，直到收到中断信号
    """

def shutdown(self) -> None:
    """优雅关闭调度器"""

def run_once(self, task: str = 'daily') -> None:
    """
    运行单次任务（用于测试）

    Args:
        task: 任务类型，可选值：
            - 'daily': 每日新闻
            - 'market': 市场更新
            - 'weekly': 周报

    Raises:
        ValueError: 未知的任务类型
    """

def generate_daily_news(self) -> None:
    """生成每日新闻（内部方法）"""

def generate_market_update(self) -> None:
    """生成市场更新（内部方法）"""

def generate_weekly_summary(self) -> None:
    """生成周报（内部方法）"""
```

---

## 错误处理

### 异常类

```python
class RetryableError(Exception):
    """可重试的错误"""
    pass

class DegradableError(Exception):
    """可降级的错误"""
    pass

class FatalError(Exception):
    """致命错误"""
    pass
```

### 装饰器

```python
def retry_with_backoff(max_retries: int = None, base_delay: int = None):
    """
    指数退避重试装饰器

    Args:
        max_retries: 最大重试次数（默认：Config.MAX_RETRIES）
        base_delay: 基础延迟秒数（默认：Config.RETRY_DELAY_BASE）

    使用示例：
        @retry_with_backoff(max_retries=3, base_delay=2)
        def my_function():
            # 会重试 3 次，延迟 2, 4, 8 秒
            pass
    """

def handle_errors(max_retries: int = None,
                 retry_delay: int = None,
                 error_type: str = ErrorType.RECOVERABLE):
    """
    错误处理装饰器

    Args:
        max_retries: 最大重试次数
        retry_delay: 重试延迟
        error_type: 错误类型

    使用示例：
        @handle_errors(max_retries=3, retry_delay=60)
        def my_function():
            # 失败后重试，最终失败返回 None
            pass
    """
```

---

## 命令行接口

### main.py

```bash
# 启动调度器（默认）
python main.py

# 运行单次任务
python main.py --run-once daily   # 生成每日新闻
python main.py --run-once market  # 生成市场更新
python main.py --run-once weekly  # 生成周报

# 仅运行健康检查
python main.py --health-check

# 跳过启动健康检查（不推荐）
python main.py --skip-health-check

# 显示版本
python main.py --version
```

### test_system.py

```bash
# 运行所有集成测试
python test_system.py
```

---

## 数据结构

### 新闻项 (News Item)

```python
{
    "title": str,        # 标题
    "link": str,         # 链接
    "summary": str,      # 摘要
    "published": str     # 发布时间
}
```

### 分析结果 (Analysis Result)

```python
{
    "importance": int,      # 重要性 (1-5)
    "category": str,        # 分类
    "keywords": List[str],  # 关键词
    "summary": str          # 摘要
}
```

### 文章 (Article)

```python
{
    "title": str,              # 标题
    "content": str,            # 内容
    "summary": str,            # 摘要
    "category": str,           # 分类
    "keywords": List[str],     # 关键词
    "source_urls": List[str],  # 来源链接
    "generated_at": str,       # 生成时间 (ISO 8601)
    "importance": int,         # 重要性 (可选)
    "news_type": str,          # 新闻类型 (可选)
    "word_count": int          # 字数 (可选)
}
```

---

## 配置文件格式

### .env

```bash
# Claude API
CLAUDE_API_KEY=your_api_key_here

# RSS Feeds (逗号分隔)
RSS_FEEDS=https://example.com/rss1,https://example.com/rss2

# Generation Parameters
MAX_NEWS_PER_SOURCE=20
IMPORTANCE_THRESHOLD=3
QUICK_NEWS_MIN_LENGTH=500
QUICK_NEWS_MAX_LENGTH=800
DEEP_ANALYSIS_MIN_LENGTH=1500
DEEP_ANALYSIS_MAX_LENGTH=2500

# Scheduler
FETCH_INTERVAL_MINUTES=30

# Retry Configuration
MAX_RETRIES=3
RETRY_DELAY_BASE=2

# Logging
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30
```

---

## 数据库架构

### articles 表

```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_url TEXT,
    importance INTEGER,
    news_type TEXT,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### raw_news 表

```sql
CREATE TABLE raw_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT UNIQUE,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### data_source_status 表

```sql
CREATE TABLE data_source_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT UNIQUE NOT NULL,
    consecutive_failures INTEGER DEFAULT 0,
    last_success TIMESTAMP,
    last_failure TIMESTAMP,
    is_active INTEGER DEFAULT 1
);
```

---

## 日志格式

```
YYYY-MM-DD HH:MM:SS | LEVEL | MODULE | MESSAGE
```

示例：
```
2026-03-05 10:30:45 | INFO | scheduler | Starting daily news generation...
2026-03-05 10:30:46 | ERROR | data_fetcher | Failed to fetch RSS feed: Connection timeout
```

---

## 性能指标

### 推荐配置

- **CPU**: 2 核心
- **内存**: 1GB
- **磁盘**: 10GB（包含日志和数据）
- **网络**: 稳定的互联网连接

### 性能数据

- RSS 采集：~2-5 秒/源
- 新闻分析：~3-5 秒/条
- 文章生成：~10-20 秒/篇
- 数据库查询：<100ms

---

## 限制和约束

1. **API 限制**
   - Claude API 有速率限制
   - 建议配置合理的重试延迟

2. **存储限制**
   - SQLite 单文件最大 281TB
   - 实际受磁盘空间限制

3. **并发限制**
   - 调度器任务串行执行
   - max_instances=1 防止重复执行

4. **内容长度**
   - 简报：500-800 字
   - 综合：1000-1500 字
   - 深度：1500-2500 字

---

## 版本历史

### v1.0.0 (2026-03-05)

- 初始版本发布
- 支持 RSS 数据采集
- 支持 Claude AI 分析和生成
- 支持定时任务调度
- 完整的错误处理和日志系统
- 健康检查系统
- Docker 部署支持

---

## 支持和反馈

如有问题或建议，请提交 Issue 或 Pull Request。
