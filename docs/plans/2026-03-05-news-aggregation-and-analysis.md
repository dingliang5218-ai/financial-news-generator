# 新闻聚合与多维分析系统 - 设计文档

## 项目概述

在现有财经新闻自动生成系统基础上，增加智能新闻聚合、综合评分排序和多维度影响分析功能。

## 核心需求

1. **智能新闻聚合**：识别同一事件的不同报道，将多个来源的新闻合并
2. **Top3 筛选**：每30分钟采集的新闻中，选出3条最重要的新闻
3. **多维度影响分析**：分析新闻对全球经济、美国经济、中国经济、美股、A股等的影响
4. **混合内容生成**：生成日报汇总 + 可选的独立深度文章

## 系统架构

### 整体流程

```
数据采集 → 新闻聚合 → 综合评分 → Top3筛选 → 多维分析 → 混合内容生成
   ↓           ↓           ↓          ↓          ↓            ↓
 4个RSS    AI识别同事件   评分排序    选前3     影响分析    日报+深度文章
```

### 核心模块

#### 1. NewsAggregator（新闻聚合器）

**职责：**
- 使用 Claude AI 识别同一事件的不同报道
- 将多个来源的新闻合并为一个"新闻事件"
- 保留所有来源的原始数据

**工作流程：**
1. 接收本次采集的所有新闻（去重后）
2. 使用 Claude 分析新闻之间的关联性
3. 将相关新闻聚合为 NewsEvent
4. 每个 NewsEvent 包含：
   - 主标题（综合各来源）
   - 所有来源的新闻列表
   - 报道数量（热度指标）
   - 最早发布时间

**Claude Prompt 策略：**
```
分析这批新闻，识别报道同一事件的新闻组：

[新闻列表]

返回 JSON 格式：
{
  "events": [
    {
      "event_id": "unique_id",
      "main_title": "事件主标题",
      "news_ids": [1, 3, 5],  // 属于该事件的新闻ID
      "event_summary": "事件简述"
    }
  ],
  "standalone_news": [2, 4]  // 独立新闻（未聚合）
}
```

#### 2. NewsRanker（新闻排序器）

**职责：**
- 对聚合后的新闻事件进行综合评分
- 选出 Top3 最重要的新闻事件

**评分公式：**
```
总分 = 重要性 × 0.6 + 热度 × 0.3 + 时效性 × 0.1
```

**评分维度：**

1. **重要性（1-5分）**
   - 来自 Claude 的原始重要性评分
   - 如果是聚合事件，取所有来源中的最高分

2. **热度（1-4分）**
   - 报道该事件的来源数量
   - 1个来源 = 1分，2个 = 2分，3个 = 3分，4个 = 4分

3. **时效性（0-1分）**
   - 发布时间距离现在的小时数
   - 1小时内 = 1.0分
   - 6小时内 = 0.8分
   - 12小时内 = 0.5分
   - 24小时内 = 0.3分
   - 超过24小时 = 0.1分

**排序逻辑：**
- 计算所有事件的总分
- 按总分降序排列
- 选取前3名

#### 3. ImpactAnalyzer（影响分析器）

**职责：**
- 对 Top3 新闻事件进行多维度影响分析
- 为每个维度评估影响程度和原因

**分析维度：**
1. 全球经济
2. 美国经济
3. 中国经济
4. 美国股市
5. 中国股市（A股）
6. 其他市场（欧洲、日本等）

**影响程度分级：**
- **高影响**：直接、重大、广泛的影响
- **中影响**：间接或局部的影响
- **低影响**：轻微或潜在的影响
- **无影响**：基本无关

**Claude Prompt 策略：**
```
分析这条新闻对各个市场的影响：

新闻事件：[标题 + 综合内容]

请从以下维度分析影响：
1. 全球经济
2. 美国经济
3. 中国经济
4. 美国股市
5. 中国股市（A股）
6. 其他市场

返回 JSON 格式：
{
  "global_economy": {
    "impact_level": "high/medium/low/none",
    "explanation": "影响说明（50字内）"
  },
  "us_economy": {...},
  "china_economy": {...},
  "us_stock": {...},
  "china_stock": {...},
  "other_markets": {...}
}
```

#### 4. ContentGenerator（内容生成器 - 扩展）

**职责：**
- 生成"今日财经要闻"汇总文章（必选）
- 为重要事件生成独立深度文章（可选）

**生成策略：**

**A. 日报汇总文章（必选）**
- 触发条件：每次有 Top3 新闻
- 字数：1500-2000字
- 结构：
  ```
  【今日财经要闻】

  一、开篇总览（200字）
  - 今日三大要闻概述
  - 市场整体情绪

  二、要闻一：[标题]（400-500字）
  - 事件概述
  - 多维度影响分析
  - 关键数据

  三、要闻二：[标题]（400-500字）

  四、要闻三：[标题]（400-500字）

  五、综合点评（200-300字）
  - 三大新闻的关联性
  - 对投资者的启示
  ```

**B. 独立深度文章（可选）**
- 触发条件：新闻事件重要性 ≥ 4分 且 热度 ≥ 3
- 字数：1500-2500字
- 结构：
  ```
  【深度】[事件标题]

  一、事件全景（300字）
  - 综合所有来源的报道
  - 事件时间线

  二、背景分析（400字）
  - 历史背景
  - 相关政策/数据

  三、多维度影响分析（600-800字）
  - 全球经济影响
  - 美国市场影响
  - 中国市场影响
  - 其他市场影响

  四、未来展望（300-400字）
  - 短期影响预测
  - 长期趋势判断
  - 投资建议
  ```

## 数据结构设计

### NewsEvent（新闻事件）

```python
class NewsEvent:
    def __init__(self):
        self.event_id: str          # 事件唯一ID
        self.main_title: str        # 主标题
        self.event_summary: str     # 事件简述
        self.news_items: List[NewsItem]  # 所有来源的新闻
        self.source_count: int      # 报道来源数量
        self.earliest_time: str     # 最早发布时间
        self.importance: int        # 重要性（1-5）
        self.hotness: int          # 热度（1-4）
        self.timeliness: float     # 时效性（0-1）
        self.total_score: float    # 综合评分
```

### ImpactAnalysis（影响分析）

```python
class ImpactAnalysis:
    def __init__(self):
        self.event_id: str
        self.global_economy: Dict   # {"impact_level": "high", "explanation": "..."}
        self.us_economy: Dict
        self.china_economy: Dict
        self.us_stock: Dict
        self.china_stock: Dict
        self.other_markets: Dict
```

### 数据库扩展

```sql
-- 新闻事件表
CREATE TABLE news_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    main_title TEXT NOT NULL,
    event_summary TEXT,
    source_count INTEGER,
    earliest_time TIMESTAMP,
    importance INTEGER,
    hotness INTEGER,
    timeliness REAL,
    total_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 事件-新闻关联表
CREATE TABLE event_news_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    news_url TEXT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES news_events(event_id)
);

-- 影响分析表
CREATE TABLE impact_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    dimension TEXT NOT NULL,  -- global_economy, us_economy, etc.
    impact_level TEXT,        -- high, medium, low, none
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES news_events(event_id)
);

-- 扩展 articles 表
ALTER TABLE articles ADD COLUMN article_type TEXT;  -- 'daily_summary' or 'deep_analysis'
ALTER TABLE articles ADD COLUMN event_id TEXT;      -- 关联的事件ID
```

## 工作流程

### 完整流程

```
1. 数据采集（每30分钟）
   ↓
2. 基础分析（现有功能）
   - 对每条新闻进行重要性评分
   - 过滤低重要性新闻（< 3分）
   ↓
3. 新闻聚合（新增）
   - 使用 Claude 识别同一事件
   - 创建 NewsEvent 对象
   ↓
4. 综合评分（新增）
   - 计算每个事件的总分
   - 排序并选出 Top3
   ↓
5. 影响分析（新增）
   - 对 Top3 进行多维度分析
   ↓
6. 内容生成（扩展）
   - 必选：生成日报汇总
   - 可选：生成深度文章（重要性≥4 且 热度≥3）
   ↓
7. 存储
   - 保存事件、分析、文章到数据库
```

### 时间估算

- 数据采集：30秒
- 基础分析：1-2分钟（20条新闻 × 3-6秒）
- 新闻聚合：30-45秒（1次 Claude 调用）
- 综合评分：< 1秒（本地计算）
- 影响分析：1-1.5分钟（3次 Claude 调用 × 20-30秒）
- 内容生成：2-4分钟（1篇日报 + 0-3篇深度）

**总计：约 5-9 分钟/次**

## 成本估算

### API 调用增加

**现有成本（每30分钟）：**
- 新闻分析：20条 × 500 tokens = 10,000 tokens
- 内容生成：5篇 × 2,500 tokens = 12,500 tokens
- 小计：22,500 tokens

**新增成本（每30分钟）：**
- 新闻聚合：1次 × 3,000 tokens = 3,000 tokens
- 影响分析：3次 × 1,000 tokens = 3,000 tokens
- 日报汇总：1次 × 4,000 tokens = 4,000 tokens
- 深度文章：平均1篇 × 5,000 tokens = 5,000 tokens
- 小计：15,000 tokens

**总成本：**
- 每30分钟：37,500 tokens
- 每天（48次）：1,800,000 tokens
- 使用 Claude Sonnet：约 $0.9-1.2/天

**成本增加：约 50-60%**

## 配置参数

```python
# 聚合配置
AGGREGATION_ENABLED = True
MIN_SIMILARITY_SCORE = 0.7  # 新闻相似度阈值

# 排序配置
IMPORTANCE_WEIGHT = 0.6
HOTNESS_WEIGHT = 0.3
TIMELINESS_WEIGHT = 0.1
TOP_N_NEWS = 3

# 影响分析配置
IMPACT_DIMENSIONS = [
    'global_economy',
    'us_economy',
    'china_economy',
    'us_stock',
    'china_stock',
    'other_markets'
]

# 内容生成配置
DAILY_SUMMARY_ENABLED = True
DAILY_SUMMARY_MIN_LENGTH = 1500
DAILY_SUMMARY_MAX_LENGTH = 2000

DEEP_ANALYSIS_ENABLED = True
DEEP_ANALYSIS_IMPORTANCE_THRESHOLD = 4
DEEP_ANALYSIS_HOTNESS_THRESHOLD = 3
```

## 错误处理

### 聚合失败
- 如果 Claude 聚合失败，将所有新闻视为独立事件
- 记录警告日志，继续后续流程

### 影响分析失败
- 如果某个维度分析失败，标记为"分析失败"
- 不影响其他维度和内容生成

### 内容生成失败
- 日报汇总失败：重试3次，仍失败则跳过本次
- 深度文章失败：记录日志，不影响日报

## 扩展性考虑

### 易于扩展的部分

1. **分析维度**：在配置中添加新维度即可
2. **评分权重**：可调整重要性、热度、时效性的权重
3. **生成策略**：可添加更多文章类型（周报、月报等）
4. **数据源**：现有架构支持添加更多 RSS 源

### 未来优化方向

1. **用户反馈学习**：根据文章阅读量调整评分权重
2. **个性化推荐**：根据用户兴趣调整 Top3 选择
3. **实时监控**：重大事件实时推送（不等30分钟）
4. **多语言支持**：生成英文版本

## 成功标准

1. **聚合准确率**：同一事件的新闻聚合准确率 > 90%
2. **Top3 质量**：人工评估 Top3 选择合理性 > 85%
3. **影响分析准确性**：专业人士评估准确率 > 80%
4. **内容质量**：日报和深度文章可读性和专业性达标
5. **系统稳定性**：每天48次运行，成功率 > 95%
6. **成本控制**：每天 API 成本 < $1.5

## 风险和挑战

### 技术风险

1. **聚合准确性**：AI 可能误判新闻关联性
   - 缓解：设置相似度阈值，人工抽查

2. **API 成本**：成本增加 50-60%
   - 缓解：优化 prompt，减少 token 消耗

3. **处理时间**：从 2-3 分钟增加到 5-9 分钟
   - 缓解：可接受范围，不影响30分钟周期

### 内容风险

1. **影响分析偏差**：AI 可能对某些市场理解不准确
   - 缓解：添加免责声明，建议人工审核

2. **深度文章质量**：自动生成可能不够深入
   - 缓解：设置高阈值（重要性≥4 且 热度≥3）

## 项目结构变化

```
financial-news-generator/
├── config.py              # 添加新配置参数
├── data_fetcher.py        # 保持不变
├── analyzer.py            # 保持不变
├── aggregator.py          # 新增：新闻聚合器
├── ranker.py              # 新增：新闻排序器
├── impact_analyzer.py     # 新增：影响分析器
├── generator.py           # 扩展：添加混合生成策略
├── storage.py             # 扩展：添加新表操作
├── scheduler.py           # 修改：调整工作流程
├── main.py                # 保持不变
└── ...
```

## 实施计划

### Phase 1：核心功能（1-2天）
- 实现 NewsAggregator
- 实现 NewsRanker
- 扩展数据库表

### Phase 2：影响分析（1天）
- 实现 ImpactAnalyzer
- 测试多维度分析准确性

### Phase 3：内容生成（1天）
- 扩展 ContentGenerator
- 实现日报汇总和深度文章生成

### Phase 4：集成测试（1天）
- 端到端测试
- 性能优化
- 成本评估

### Phase 5：文档和部署（0.5天）
- 更新文档
- 部署到生产环境
