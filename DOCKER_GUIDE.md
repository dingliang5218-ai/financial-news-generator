# Docker 部署指南

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加 CLAUDE_API_KEY 等配置

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### 使用 Docker

```bash
# 1. 构建镜像
docker build -t financial-news:latest .

# 2. 运行容器
docker run -d \
  --name financial-news \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  financial-news:latest

# 3. 查看日志
docker logs -f financial-news

# 4. 停止容器
docker stop financial-news
docker rm financial-news
```

## 常用命令

### 容器管理

```bash
# 查看运行状态
docker-compose ps

# 重启服务
docker-compose restart

# 查看资源使用
docker stats financial-news

# 进入容器
docker exec -it financial-news bash
```

### 日志管理

```bash
# 查看实时日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100

# 查看特定时间的日志
docker-compose logs --since 2026-03-05T10:00:00
```

### 数据管理

```bash
# 备份数据
docker exec financial-news tar czf /tmp/backup.tar.gz /app/data
docker cp financial-news:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz

# 恢复数据
docker cp ./backup.tar.gz financial-news:/tmp/
docker exec financial-news tar xzf /tmp/backup.tar.gz -C /
docker-compose restart
```

## 健康检查

```bash
# 手动运行健康检查
docker exec financial-news python main.py --health-check

# 查看健康状态
docker inspect --format='{{.State.Health.Status}}' financial-news
```

## 故障排除

### 容器无法启动

```bash
# 查看详细错误
docker-compose logs

# 检查配置
docker-compose config

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 性能问题

```bash
# 查看资源使用
docker stats financial-news

# 限制资源使用
docker-compose.yml 中添加：
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

### 数据持久化问题

```bash
# 检查挂载点
docker inspect financial-news | grep Mounts -A 20

# 确保目录权限正确
chmod -R 755 data logs
```

## 生产环境建议

### 1. 使用环境变量文件

```bash
# 不要将 .env 提交到版本控制
echo ".env" >> .gitignore

# 生产环境使用单独的配置
cp .env.example .env.production
# 编辑 .env.production
docker-compose --env-file .env.production up -d
```

### 2. 配置日志轮转

```yaml
# docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "5"
```

### 3. 设置自动重启

```yaml
# docker-compose.yml
restart: unless-stopped
```

### 4. 监控和告警

```bash
# 使用 Watchtower 自动更新
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  financial-news
```

## 多环境部署

### 开发环境

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  financial-news:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env.dev
    volumes:
      - .:/app  # 挂载源码，支持热更新
    command: python main.py --run-once daily
```

```bash
docker-compose -f docker-compose.dev.yml up
```

### 生产环境

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  financial-news:
    image: financial-news:1.0.0
    env_file:
      - .env.prod
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
```

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 安全建议

1. **不要在镜像中包含敏感信息**
   - 使用环境变量或 secrets
   - 不要提交 .env 文件

2. **使用非 root 用户运行**
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

3. **限制容器权限**
   ```yaml
   security_opt:
     - no-new-privileges:true
   cap_drop:
     - ALL
   ```

4. **定期更新基础镜像**
   ```bash
   docker pull python:3.9-slim
   docker-compose build --no-cache
   ```

## 性能优化

### 1. 多阶段构建

```dockerfile
# 构建阶段
FROM python:3.9 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 运行阶段
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "main.py"]
```

### 2. 使用 .dockerignore

```
# .dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.git
.gitignore
.env
data/
logs/
venv/
*.md
```

### 3. 缓存优化

```dockerfile
# 先复制 requirements.txt，利用缓存
COPY requirements.txt .
RUN pip install -r requirements.txt

# 再复制代码
COPY . .
```

## 监控集成

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  financial-news:
    # ... 主服务配置

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 备份策略

### 自动备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
docker exec financial-news sqlite3 /app/data/articles.db ".backup /tmp/backup_${DATE}.db"
docker cp financial-news:/tmp/backup_${DATE}.db ${BACKUP_DIR}/

# 清理旧备份（保留 7 天）
find ${BACKUP_DIR} -name "backup_*.db" -mtime +7 -delete

echo "Backup completed: backup_${DATE}.db"
```

### 定时备份（crontab）

```bash
# 每天凌晨 2 点备份
0 2 * * * /path/to/backup.sh >> /var/log/financial-news-backup.log 2>&1
```

## 常见问题

### Q: 如何查看容器内的文件？

```bash
docker exec financial-news ls -la /app/data
```

### Q: 如何更新代码？

```bash
git pull
docker-compose build
docker-compose up -d
```

### Q: 如何清理 Docker 资源？

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune

# 清理所有未使用的资源
docker system prune -a
```

### Q: 如何调试容器？

```bash
# 进入容器
docker exec -it financial-news bash

# 查看进程
docker top financial-news

# 查看资源使用
docker stats financial-news
```
