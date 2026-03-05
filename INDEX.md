# 文档索引

欢迎使用财经新闻自动生成系统！本文档索引帮助你快速找到所需信息。

## 📚 文档导航

### 🚀 快速开始

| 文档 | 描述 | 适合人群 |
|------|------|----------|
| [README.md](README.md) | 用户使用指南，包含快速开始、功能介绍、配置说明 | 所有用户 |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 快速参考卡片，常用命令和配置速查 | 所有用户 |
| [run.sh](run.sh) | 快速启动脚本，自动化环境配置 | 新用户 |
| [demo.sh](demo.sh) | 交互式演示脚本，展示系统功能 | 新用户 |

### 👨‍💻 开发文档

| 文档 | 描述 | 适合人群 |
|------|------|----------|
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | 开发者指南，系统架构、开发流程、代码规范 | 开发者 |
| [API_REFERENCE.md](API_REFERENCE.md) | API 参考文档，所有类和方法的详细说明 | 开发者 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南，如何参与项目开发 | 贡献者 |

### 🐳 部署文档

| 文档 | 描述 | 适合人群 |
|------|------|----------|
| [DOCKER_GUIDE.md](DOCKER_GUIDE.md) | Docker 部署指南，容器化部署完整教程 | 运维人员 |
| [Dockerfile](Dockerfile) | Docker 镜像构建文件 | 运维人员 |
| [docker-compose.yml](docker-compose.yml) | Docker Compose 编排配置 | 运维人员 |
| [financial-news.service](financial-news.service) | systemd 服务配置文件 | 运维人员 |

### 📊 项目信息

| 文档 | 描述 | 适合人群 |
|------|------|----------|
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 项目总结，任务清单、技术栈、核心功能 | 所有人 |
| [FINAL_REPORT.md](FINAL_REPORT.md) | 项目完成报告，详细的项目统计和成果 | 所有人 |
| [CHANGELOG.md](CHANGELOG.md) | 变更日志，版本历史和更新记录 | 所有人 |
| [LICENSE](LICENSE) | MIT 开源许可证 | 所有人 |

### 🛠️ 工具脚本

| 脚本 | 描述 | 用途 |
|------|------|------|
| [run.sh](run.sh) | 快速启动脚本 | 自动化环境配置和启动 |
| [demo.sh](demo.sh) | 演示脚本 | 展示系统功能 |
| [status.sh](status.sh) | 状态检查脚本 | 检查系统健康状态 |
| [backup.sh](backup.sh) | 备份脚本 | 创建数据备份 |
| [restore.sh](restore.sh) | 恢复脚本 | 恢复数据备份 |

---

## 🎯 按场景查找

### 场景 1: 我是新用户，想快速开始

1. 阅读 [README.md](README.md) 了解系统
2. 运行 `./run.sh` 快速启动
3. 查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 学习常用命令

### 场景 2: 我想了解系统架构

1. 阅读 [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) 的系统架构部分
2. 查看 [API_REFERENCE.md](API_REFERENCE.md) 了解各个组件
3. 阅读 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) 了解整体设计

### 场景 3: 我想部署到生产环境

1. 阅读 [DOCKER_GUIDE.md](DOCKER_GUIDE.md) 选择部署方式
2. 配置 `.env` 文件
3. 使用 `docker-compose up -d` 或 systemd 部署
4. 运行 `./status.sh` 检查状态

### 场景 4: 我想参与开发

1. 阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献流程
2. 阅读 [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) 了解开发规范
3. 查看 [API_REFERENCE.md](API_REFERENCE.md) 了解 API
4. Fork 项目并提交 PR

### 场景 5: 我遇到了问题

1. 查看 [README.md](README.md) 的故障排除部分
2. 运行 `./status.sh` 检查系统状态
3. 查看日志文件 `logs/app_*.log`
4. 搜索 [CHANGELOG.md](CHANGELOG.md) 看是否是已知问题
5. 提交 GitHub Issue

### 场景 6: 我想了解项目进展

1. 阅读 [FINAL_REPORT.md](FINAL_REPORT.md) 了解项目完成情况
2. 查看 [CHANGELOG.md](CHANGELOG.md) 了解版本历史
3. 阅读 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) 了解后续规划

---

## 📖 文档阅读顺序建议

### 新用户推荐阅读顺序

1. **README.md** - 了解系统基本信息
2. **QUICK_REFERENCE.md** - 学习常用操作
3. **demo.sh** - 运行演示了解功能
4. 根据需要查阅其他文档

### 开发者推荐阅读顺序

1. **README.md** - 了解系统概况
2. **PROJECT_SUMMARY.md** - 了解项目结构
3. **DEVELOPER_GUIDE.md** - 学习开发规范
4. **API_REFERENCE.md** - 查阅 API 文档
5. **CONTRIBUTING.md** - 了解贡献流程

### 运维人员推荐阅读顺序

1. **README.md** - 了解系统功能
2. **DOCKER_GUIDE.md** - 学习部署方法
3. **QUICK_REFERENCE.md** - 学习运维命令
4. 根据需要查阅其他文档

---

## 🔍 快速查找

### 配置相关

- 环境变量配置: [README.md](README.md#配置说明)
- 配置文件示例: [.env.example](.env.example)
- 配置验证: [config.py](config.py)

### 部署相关

- Docker 部署: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- systemd 部署: [financial-news.service](financial-news.service)
- 快速启动: [run.sh](run.sh)

### 开发相关

- 系统架构: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#系统架构)
- API 文档: [API_REFERENCE.md](API_REFERENCE.md)
- 代码规范: [CONTRIBUTING.md](CONTRIBUTING.md#代码规范)

### 运维相关

- 状态检查: [status.sh](status.sh)
- 备份恢复: [backup.sh](backup.sh), [restore.sh](restore.sh)
- 日志查看: [README.md](README.md#日志查看)

### 故障排除

- 常见问题: [README.md](README.md#故障排除)
- Docker 问题: [DOCKER_GUIDE.md](DOCKER_GUIDE.md#故障排除)
- 开发问题: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#常见问题)

---

## 📝 核心代码文件

| 文件 | 描述 | 文档参考 |
|------|------|----------|
| [config.py](config.py) | 配置管理 | [API_REFERENCE.md](API_REFERENCE.md#config) |
| [logger.py](logger.py) | 日志系统 | [API_REFERENCE.md](API_REFERENCE.md#logger) |
| [error_handler.py](error_handler.py) | 错误处理 | [API_REFERENCE.md](API_REFERENCE.md#错误处理) |
| [storage.py](storage.py) | 数据存储 | [API_REFERENCE.md](API_REFERENCE.md#storage) |
| [data_fetcher.py](data_fetcher.py) | 数据采集 | [API_REFERENCE.md](API_REFERENCE.md#datafetcher) |
| [analyzer.py](analyzer.py) | 智能分析 | [API_REFERENCE.md](API_REFERENCE.md#analyzer) |
| [generator.py](generator.py) | 内容生成 | [API_REFERENCE.md](API_REFERENCE.md#generator) |
| [health_check.py](health_check.py) | 健康检查 | [API_REFERENCE.md](API_REFERENCE.md#healthcheck) |
| [scheduler.py](scheduler.py) | 任务调度 | [API_REFERENCE.md](API_REFERENCE.md#newsscheduler) |
| [main.py](main.py) | 主程序 | [README.md](README.md#使用说明) |
| [test_system.py](test_system.py) | 集成测试 | [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#测试指南) |

---

## 🆘 获取帮助

### 在线资源

- **项目文档**: 查看本目录下的 `.md` 文件
- **代码注释**: 查看源代码中的文档字符串
- **演示脚本**: 运行 `./demo.sh` 查看功能演示

### 命令行帮助

```bash
# 查看主程序帮助
python main.py --help

# 查看系统状态
./status.sh

# 运行演示
./demo.sh
```

### 问题反馈

1. 查看现有文档
2. 搜索已有 Issue
3. 创建新 Issue
4. 提交 Pull Request

---

## 📌 重要提示

- 📖 **首次使用**: 请先阅读 [README.md](README.md)
- 🔧 **配置系统**: 复制 `.env.example` 到 `.env` 并配置
- ✅ **运行测试**: 使用 `python test_system.py` 验证安装
- 🚀 **快速启动**: 使用 `./run.sh` 自动化配置
- 📚 **查阅文档**: 遇到问题先查看相关文档

---

## 📞 联系方式

- **GitHub Issues**: 提交问题和建议
- **Pull Requests**: 贡献代码
- **Discussions**: 一般讨论和问答

---

**最后更新**: 2026-03-05
**版本**: v1.0.0
