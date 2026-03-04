# 财经内容自动生成系统 - 设计文档

## 项目概述

开发一个轻量级的自动化财经内容生成系统，用于生成面向中文读者的美国财经资讯文章，支持发布到微信公众号、头条号等自媒体平台。

## 核心目标

- 自动采集美国财经新闻（RSS + API）
- 智能判断新闻重要性
- 生成高质量的中文财经文章
- 支持混合模式：日常定期资讯 + 突发重大事件
- 灵活的文章长度：根据重要性自动调整（500-2500字）

## 系统架构

### 整体设计

```
数据采集层 → 智能分析层 → 内容生成层 → 存储层
```

**核心原则：**
- 轻量级：纯 Python 实现，不依赖重量级框架
- 模块化：每层职责单一，易于维护和扩展
- 智能化：用 LLM 判断而非规则匹配

### 技术栈

**后端：**
- Python 3.10+
- feedparser（RSS 解析）
- anthropic（Claude API）
- APScheduler（定时任务）
- SQLite（数据存储）
- requests（HTTP 请求）

**数据源：**
- RSS 订阅（CNBC、Bloomberg、Reuters、MarketWatch）
- Yahoo Finance API（美股数据）
- FRED API（美国经济数据，可选）

## 核心模块设计

### 1. 数据采集层（data_fetcher.py）

**职责：**
- 从多个数据源获取美国财经新闻
- 数据清洗和去重
- 统一数据格式

**设计思路：**
- 使用简单的接口抽象（DataSource 基类）
- 每个数据源实现独立的 fetch 方法
- 易于添加新数据源

**数据源列表：**
- CNBC RSS Feed
- Bloomberg RSS Feed
- Reuters Business RSS Feed
- MarketWatch RSS Feed
- Yahoo Finance API（补充市场数据）

### 2. 智能分析层（analyzer.py）

**职责：**
- 使用 Claude 判断新闻重要性（1-5分）
- 分类新闻类型（市场行情/公司财报/政策变化/经济数据）
- 识别突发重大事件
- 提取关键信息摘要

**核心创新：**
- 不使用规则匹配，完全依赖 LLM 理解
- 更灵活，能适应各种新情况
- 减少维护成本

### 3. 内容生成层（generator.py）

**职责：**
- 根据重要性选择生成策略
- 翻译英文新闻为中文
- 改写和深度分析
- 输出符合自媒体风格的文章

**生成策略：**

**普通资讯（重要性 < 4）：**
- 长度：500-800字
- 风格：快讯
- 内容：翻译 + 简要解读
- 结构：事件概述 + 市场影响

**重大事件（重要性 >= 4）：**
- 长度：1500-2500字
- 风格：深度分析
- 内容：背景 + 分析 + 展望
- 结构：
  - 事件概述（200字）
  - 背景分析（400字）
  - 市场影响（600字）
  - 未来展望（300字）

### 4. 存储层（storage.py）

**职责：**
- 存储生成的文章
- 记录数据源和生成时间
- 提供查询接口

**数据库设计：**

```sql
-- 文章表
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

-- 原始新闻表（用于去重）
CREATE TABLE raw_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT UNIQUE,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. 定时任务（scheduler.py）

**职责：**
- 定时执行采集和生成任务
- 协调各个模块

**执行频率：**
- 主任务：每30分钟执行一次
- 流程：采集 → 分析 → 生成 → 存储

## 工作流程

### 主流程

1. **数据采集**
   - 从所有 RSS 源获取最新新闻
   - 调用 Yahoo Finance API 获取市场数据
   - 去重（基于 URL）

2. **智能分析**
   - 对每条新闻调用 Claude 进行分析
   - 获取重要性评分和分类
   - 过滤低重要性新闻（< 3分）

3. **内容生成**
   - 根据重要性选择生成策略
   - 调用 Claude 生成中文文章
   - 质量检查（字数、格式）

4. **存储**
   - 保存到 SQLite 数据库
   - 记录元数据

5. **查看**
   - 命令行工具查看生成的文章
   - 可导出为 Markdown 或 HTML

## MVP 功能范围

**第一版包含：**
- ✅ RSS 数据采集（3-5个源）
- ✅ Claude 智能分析
- ✅ 双策略内容生成（快讯/深度）
- ✅ SQLite 存储
- ✅ 命令行查看工具
- ✅ 定时任务（每30分钟）

**第一版不包含：**
- ❌ Web 管理界面
- ❌ 自动发布功能
- ❌ 复杂的事件检测
- ❌ 数据可视化

## 项目结构

```
financial-news-generator/
├── config.py              # 配置文件
├── data_fetcher.py        # 数据采集
├── analyzer.py            # 智能分析
├── generator.py           # 内容生成
├── storage.py             # 数据存储
├── scheduler.py           # 定时任务
├── cli.py                 # 命令行工具
├── requirements.txt       # 依赖
├── README.md             # 项目说明
└── data/
    └── articles.db        # SQLite 数据库
```

## 配置管理

**config.py 包含：**
- Claude API Key
- RSS 源列表
- Yahoo Finance API Key（可选）
- 生成参数（字数范围、重要性阈值等）
- 定时任务配置

## 扩展性考虑

**易于扩展的部分：**
1. **数据源** - 实现 DataSource 接口即可添加新源
2. **生成策略** - 修改 prompt 即可调整风格
3. **存储** - 可以轻松切换到 PostgreSQL 或 MySQL
4. **界面** - 后期可添加 Web 界面（Flask/FastAPI）

## 成本估算

**API 调用成本：**
- 假设每30分钟采集20条新闻
- 其中5条重要度 >= 3，需要生成文章
- 每条新闻分析：约 500 tokens
- 每篇文章生成：约 2000-4000 tokens
- 每天总计：约 200,000 tokens
- 使用 Claude Sonnet：约 $0.6/天

**服务器成本：**
- 本地 WSL 运行：$0
- 后期迁移到云端：约 $5-10/月（最低配置）

## 风险和挑战

**技术风险：**
1. RSS 源可能变更或失效 - 解决：多源冗余
2. API 限流 - 解决：控制调用频率，添加重试机制
3. Claude API 成本 - 解决：优化 prompt，减少不必要的调用

**内容风险：**
1. 翻译准确性 - 解决：人工审核机制
2. 事实错误 - 解决：保留原文链接，便于核查
3. 时效性 - 解决：30分钟更新频率已足够

## 后续迭代方向

**第二阶段（可选）：**
- 添加简单的 Web 界面
- 支持文章编辑和导出
- 添加更多数据源

**第三阶段（可选）：**
- 实现半自动发布功能
- 添加数据统计和分析
- 优化生成质量

## 成功标准

**MVP 成功标准：**
1. 能够稳定运行，每30分钟自动采集和生成
2. 每天生成 10-20 篇高质量文章
3. 文章翻译准确，语言流畅
4. 重要事件能够被正确识别
5. 系统运行成本可控（< $1/天）
