# 🚀 Mobile Ledger 部署教程

本教程将指导您在云服务器上部署 Mobile Ledger 记账应用。

## 📋 目录

- [快速开始](#快速开始)
- [手动部署](#手动部署)
- [Docker 部署](#docker-部署)
- [Nginx 配置](#nginx-配置)
- [域名配置](#域名配置)
- [HTTPS 配置](#https-配置)
- [常见问题](#常见问题)

---

## ⚡ 快速开始

### 方式一：一键部署（推荐）

```bash
# 下载一键部署脚本
curl -O https://raw.githubusercontent.com/xrs-b/mobile-ledger/main/deploy.sh

# 添加执行权限
chmod +x deploy.sh

# 运行部署脚本
sudo ./deploy.sh deploy
```

### 方式二：Docker 部署

```bash
# 克隆项目
git clone https://github.com/xrs-b/mobile-ledger.git
cd mobile-ledger

# 启动服务
docker-compose up -d
```

---

## 💻 服务器要求

| 配置 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 1 核 | 2 核 |
| 内存 | 1 GB | 2 GB |
| 硬盘 | 10 GB | 20 GB |
| 带宽 | 1 Mbps | 5 Mbps |
| 系统 | Ubuntu 20.04+ / CentOS 7+ | Ubuntu 22.04 LTS |

---

## 🐳 Docker 部署

### 1. 安装 Docker

**Ubuntu/Debian:**
```bash
# 更新软件包
sudo apt update

# 安装必要依赖
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
```

**CentOS/RHEL:**
```bash
# 安装必要依赖
sudo yum install -y yum-utils

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 安装 Docker Compose

```bash
# 下载最新版本
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 3. 克隆并部署项目

```bash
# 克隆项目
git clone https://github.com/xrs-b/mobile-ledger.git
cd mobile-ledger

# 创建数据目录
mkdir -p data logs

# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

---

## 🔧 手动部署

### 1. 安装 Python 环境

```bash
# 安装 Python 3.11+
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev

# 验证安装
python3 --version
```

### 2. 部署后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
cd scripts
python init_db.py
cd ..

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 部署前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 安装 serve（静态文件服务器）
npm install -g serve

# 启动服务
serve -s dist -l 3000
```

---

## 🌐 Nginx 配置

### 1. 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt install -y nginx

# CentOS/RHEL
sudo yum install -y nginx

# 启动并设置开机自启
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. 配置反向代理

创建配置文件 `/etc/nginx/conf.d/mobile-ledger.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名

    # 重定向到 HTTPS（可选）
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书配置（后续章节介绍）
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    add_header Strict-Transport-Security "max-age=63072000" always;

    # 前端静态文件
    location / {
        root /opt/mobile-ledger/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket 支持（可选）
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 日志配置
    access_log /var/log/nginx/mobile-ledger-access.log;
    error_log /var/log/nginx/mobile-ledger-error.log;
}
```

### 3. 测试并重载 Nginx

```bash
# 测试配置
sudo nginx -t

# 重载配置
sudo nginx -s reload
```

---

## 🔒 HTTPS 配置（Let's Encrypt）

### 1. 安装 Certbot

```bash
# Ubuntu/Debian
sudo apt install -y certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install -y certbot python3-certbot-nginx
```

### 2. 获取 SSL 证书

```bash
# 自动配置
sudo certbot --nginx -d your-domain.com

# 手动获取
sudo certbot certonly --nginx -d your-domain.com
```

### 3. 自动续期

```bash
# 测试续期
sudo certbot renew --dry-run

# 添加定时任务
echo "0 0,12 * * * root certbot renew --quiet" | sudo tee -a /etc/crontab
```

---

## 🔥 防火墙配置

### UFW（Ubuntu）

```bash
# 启用防火墙
sudo ufw enable

# 开放端口
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 查看状态
sudo ufw status
```

### firewalld（CentOS）

```bash
# 开放端口
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=22/tcp

# 重载配置
sudo firewall-cmd --reload

# 查看状态
sudo firewall-cmd --list-all
```

---

## 📊 服务管理

### 使用 Systemd 管理

创建服务文件 `/etc/systemd/system/mobile-ledger.service`:

```ini
[Unit]
Description=Mobile Ledger Backend Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/mobile-ledger/backend
Environment="PATH=/opt/mobile-ledger/backend/.venv/bin"
ExecStart=/opt/mobile-ledger/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

管理命令:

```bash
# 重新加载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start mobile-ledger

# 停止服务
sudo systemctl stop mobile-ledger

# 重启服务
sudo systemctl restart mobile-ledger

# 查看状态
sudo systemctl status mobile-ledger

# 开机自启
sudo systemctl enable mobile-ledger
```

---

## 📝 常用命令

### Docker 方式

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 更新并重启
docker-compose pull
docker-compose up -d

# 查看容器状态
docker-compose ps

# 进入容器
docker-compose exec backend bash
```

### 查看服务状态

```bash
# 检查端口监听
netstat -tlnp | grep -E ':(8000|3000|80)'

# 检查进程
ps aux | grep -E '(uvicorn|serve|nginx)'

# 检查磁盘空间
df -h

# 检查内存使用
free -h
```

---

## ❓ 常见问题

### Q1: 端口被占用怎么办？

```bash
# 查找占用端口的进程
sudo lsof -i :8000
sudo lsof -i :3000

# 或使用 kill 终止进程
sudo kill <PID>
```

### Q2: Docker 构建失败？

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

### Q3: 数据库初始化失败？

```bash
# 检查权限
sudo chmod -R 777 data/

# 重新初始化
cd backend/scripts
python init_db.py
```

### Q4: 前端静态文件 404？

```bash
# 检查构建目录
ls -la frontend/dist/

# 重新构建
cd frontend
npm run build
```

### Q5: API 无法访问？

```bash
# 检查后端日志
docker-compose logs backend

# 检查防火墙
sudo ufw status

# 检查 Nginx 代理
curl -v http://localhost/api/categories
```

---

## 🔒 安全建议

1. **修改默认密码**: 首次登录后立即修改 admin 密码
2. **环境变量**: 生产环境使用强 SECRET_KEY
3. **定期备份**: 使用 `scripts/backup.sh` 备份数据
4. **监控日志**: 定期检查 `/var/log/nginx/` 和 `docker-compose logs`
5. **更新依赖**: 定期更新 Docker 镜像和系统包

---

## 📞 获取帮助

- 项目地址: https://github.com/xrs-b/mobile-ledger
- Issues: https://github.com/xrs-b/mobile-ledger/issues

---

**祝您部署顺利！ 🎉**
