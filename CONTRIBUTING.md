# 贡献指南

感谢你考虑为财经新闻自动生成系统做出贡献！

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性化的语言或图像
- 人身攻击或侮辱性评论
- 公开或私下骚扰
- 未经许可发布他人的私人信息
- 其他不道德或不专业的行为

## 如何贡献

### 报告 Bug

在提交 Bug 报告之前：

1. **检查文档** - 确保这不是预期行为
2. **搜索已有 Issue** - 避免重复报告
3. **使用最新版本** - Bug 可能已被修复

提交 Bug 报告时，请包含：

- **清晰的标题** - 简洁描述问题
- **详细描述** - 问题的详细说明
- **重现步骤** - 如何重现问题
- **预期行为** - 你期望发生什么
- **实际行为** - 实际发生了什么
- **环境信息** - 操作系统、Python 版本等
- **日志输出** - 相关的错误日志

示例：

```markdown
**Bug 描述**
数据采集时偶尔会超时

**重现步骤**
1. 配置 RSS_FEEDS 为 10 个源
2. 运行 `python main.py --run-once daily`
3. 观察日志输出

**预期行为**
所有 RSS 源都应该成功采集

**实际行为**
第 5 个源超时失败

**环境**
- OS: Ubuntu 20.04
- Python: 3.9.5
- 版本: 1.0.0

**日志**
```
2026-03-05 10:30:45 | ERROR | data_fetcher | Failed to fetch RSS feed: Connection timeout
```
```

### 提出新功能

在提交功能请求之前：

1. **检查路线图** - 功能可能已在计划中
2. **搜索已有 Issue** - 避免重复请求
3. **考虑通用性** - 功能是否对大多数用户有用

提交功能请求时，请包含：

- **功能描述** - 清晰描述新功能
- **使用场景** - 为什么需要这个功能
- **建议实现** - 如何实现（可选）
- **替代方案** - 考虑过的其他方案

示例：

```markdown
**功能描述**
添加邮件通知功能，在生成文章后发送邮件

**使用场景**
用户希望在文章生成后立即收到通知，而不是手动检查

**建议实现**
1. 添加 SMTP 配置到 .env
2. 在 generator.py 中添加邮件发送功能
3. 在 scheduler.py 中调用邮件通知

**替代方案**
- 使用 Webhook 通知
- 使用消息队列
```

### 提交代码

#### 开发流程

1. **Fork 项目**

```bash
# 在 GitHub 上 Fork 项目
# 克隆你的 Fork
git clone https://github.com/your-username/financial-news.git
cd financial-news
```

2. **创建分支**

```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 或修复分支
git checkout -b fix/your-bug-fix
```

分支命名规范：
- `feature/` - 新功能
- `fix/` - Bug 修复
- `docs/` - 文档更新
- `refactor/` - 代码重构
- `test/` - 测试相关
- `chore/` - 构建/工具相关

3. **开发和测试**

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python test_system.py

# 检查代码风格
flake8 *.py
black --check *.py
```

4. **提交更改**

```bash
# 添加更改
git add .

# 提交（遵循提交规范）
git commit -m "feat: add email notification feature"
```

提交信息规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型 (type)：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

示例：

```
feat(generator): add email notification

- Add SMTP configuration
- Implement email sending function
- Integrate with scheduler

Closes #123
```

5. **推送和创建 PR**

```bash
# 推送到你的 Fork
git push origin feature/your-feature-name

# 在 GitHub 上创建 Pull Request
```

#### Pull Request 指南

PR 标题应该：
- 清晰描述更改
- 遵循提交信息规范
- 引用相关 Issue

PR 描述应该包含：

```markdown
## 更改说明
简要描述这个 PR 做了什么

## 更改类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化

## 测试
- [ ] 添加了新测试
- [ ] 所有测试通过
- [ ] 手动测试通过

## 相关 Issue
Closes #123

## 截图（如适用）
添加截图说明更改

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 添加了必要的文档
- [ ] 更新了 CHANGELOG.md
- [ ] 没有引入新的警告
```

#### 代码审查

PR 提交后：

1. **自动检查** - CI 会运行测试和代码检查
2. **代码审查** - 维护者会审查你的代码
3. **修改建议** - 根据反馈修改代码
4. **合并** - 审查通过后合并到主分支

## 开发规范

### 代码风格

遵循 PEP 8 规范：

```python
# 好的示例
def fetch_news_items(source_url: str, max_items: int = 20) -> List[Dict]:
    """
    从指定源获取新闻项

    Args:
        source_url: RSS 源 URL
        max_items: 最大获取数量

    Returns:
        新闻项列表
    """
    items = []
    # 实现逻辑
    return items


# 不好的示例
def fetchNews(url,max=20):
    items=[]
    #实现逻辑
    return items
```

使用工具检查：

```bash
# 安装工具
pip install flake8 black isort

# 检查代码风格
flake8 *.py

# 自动格式化
black *.py

# 排序导入
isort *.py
```

### 文档规范

#### 代码注释

```python
class NewsAnalyzer:
    """新闻分析器

    使用 Claude AI 分析新闻内容，评估重要性和分类。

    Attributes:
        client: Claude API 客户端
        cache: 分析结果缓存
    """

    def analyze_news(self, news_item: Dict) -> Dict:
        """分析单条新闻

        Args:
            news_item: 新闻项字典，包含 title, content 等字段

        Returns:
            分析结果字典，包含 importance, category, keywords

        Raises:
            RetryableError: API 调用失败时

        Example:
            >>> analyzer = NewsAnalyzer()
            >>> result = analyzer.analyze_news({"title": "..."})
            >>> print(result['importance'])
            4
        """
        pass
```

#### 文档更新

更改代码时，同步更新：

- README.md - 用户文档
- DEVELOPER_GUIDE.md - 开发者指南
- API_REFERENCE.md - API 文档
- CHANGELOG.md - 变更日志

### 测试规范

#### 单元测试

```python
import unittest
from my_module import MyClass

class TestMyClass(unittest.TestCase):
    """MyClass 测试套件"""

    def setUp(self):
        """测试前准备"""
        self.obj = MyClass()

    def tearDown(self):
        """测试后清理"""
        pass

    def test_method_success(self):
        """测试方法成功情况"""
        result = self.obj.method("input")
        self.assertEqual(result, "expected")

    def test_method_failure(self):
        """测试方法失败情况"""
        with self.assertRaises(ValueError):
            self.obj.method("invalid")
```

#### 集成测试

添加到 `test_system.py`：

```python
def test_new_feature(self):
    """测试新功能"""
    # 准备
    setup_data()

    # 执行
    result = new_feature()

    # 验证
    assert result is not None
    assert result['status'] == 'success'

    # 清理
    cleanup_data()

    logger.info("✓ New feature test passed")
```

### Git 工作流

#### 分支策略

```
main (生产分支)
  ├── develop (开发分支)
  │   ├── feature/feature-1
  │   ├── feature/feature-2
  │   └── fix/bug-1
  └── hotfix/critical-bug
```

#### 提交频率

- 小步提交，频繁提交
- 每个提交应该是一个逻辑单元
- 提交前运行测试

#### 合并策略

- 使用 Pull Request
- 需要至少一个审查者批准
- 通过所有 CI 检查
- 解决所有冲突

## 社区

### 沟通渠道

- **GitHub Issues** - Bug 报告和功能请求
- **GitHub Discussions** - 一般讨论和问答
- **Pull Requests** - 代码审查和讨论

### 获取帮助

遇到问题时：

1. 查看文档
2. 搜索已有 Issue
3. 在 Discussions 提问
4. 创建新 Issue

### 成为维护者

活跃贡献者可以申请成为维护者：

- 持续贡献高质量代码
- 帮助审查 PR
- 回答社区问题
- 维护文档

## 许可证

贡献代码即表示你同意：

- 代码使用 MIT 许可证
- 你拥有代码的版权
- 你授权项目使用你的代码

## 致谢

感谢所有贡献者的付出！

你的贡献将被记录在：
- CHANGELOG.md
- 项目 README.md
- GitHub Contributors 页面

---

再次感谢你的贡献！🎉
