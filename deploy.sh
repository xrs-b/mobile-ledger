#!/bin/bash

# ============================================
# Mobile Ledger 一键部署脚本
# 支持 Ubuntu/CentOS/Debian
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PROJECT_NAME="mobile-ledger"
PROJECT_DIR="/opt/${PROJECT_NAME}"
BACKUP_DIR="/opt/backups"
LOG_FILE="/var/log/${PROJECT_NAME}.log"

# 输出函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a ${LOG_FILE}
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a ${LOG_FILE}
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a ${LOG_FILE}
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a ${LOG_FILE}
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "请使用 root 用户运行此脚本"
        exit 1
    fi
}

# 检查操作系统
check_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS_NAME=${NAME}
        OS_VERSION=${VERSION}
        log_info "检测到操作系统: ${OS_NAME} ${OS_VERSION}"
    else
        log_error "无法检测操作系统"
        exit 1
    fi
}

# 安装 Docker
install_docker() {
    log_info "检查 Docker 安装状态..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker 已安装: $(docker --version)"
    else
        log_info "正在安装 Docker..."
        
        if [[ ${OS_NAME} == "Ubuntu" ]] || [[ ${OS_NAME} == "Debian" ]]; then
            apt-get update
            apt-get install -y apt-transport-https ca-certificates curl software-properties-common
            curl -fsSL https://download.docker.com/linux/${OS,,}/gpg | apt-key add -
            add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/${OS,,} ${VERSION_CODENAME} stable"
            apt-get update
            apt-get install -y docker-ce docker-ce-cli containerd.io
        elif [[ ${OS_NAME} == "CentOS" ]] || [[ ${OS_NAME} == "Red Hat Enterprise Linux" ]] || [[ ${OS_NAME} == "Amazon Linux" ]]; then
            yum install -y yum-utils
            yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            yum install -y docker-ce docker-ce-cli containerd.io
            systemctl start docker
            systemctl enable docker
        fi
        
        # 添加当前用户到 docker 组
        if [[ -n $SUDO_USER ]]; then
            usermod -aG docker $SUDO_USER
        fi
        
        log_success "Docker 安装完成: $(docker --version)"
    fi
    
    # 启动 Docker 服务
    systemctl start docker 2>/dev/null || true
}

# 安装 Docker Compose
install_docker_compose() {
    log_info "检查 Docker Compose 安装状态..."
    
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose 已安装: $(docker-compose --version)"
    else
        log_info "正在安装 Docker Compose..."
        
        # 获取最新版本
        COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
        
        if [[ -z ${COMPOSE_VERSION} ]]; then
            COMPOSE_VERSION="v2.24.0"
        fi
        
        # 安装
        curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
        
        log_success "Docker Compose 安装完成: $(docker-compose --version)"
    fi
}

# 安装 Git
install_git() {
    log_info "检查 Git 安装状态..."
    
    if command -v git &> /dev/null; then
        log_success "Git 已安装: $(git --version)"
    else
        log_info "正在安装 Git..."
        
        if [[ ${OS_NAME} == "Ubuntu" ]] || [[ ${OS_NAME} == "Debian" ]]; then
            apt-get update
            apt-get install -y git
        elif [[ ${OS_NAME} == "CentOS" ]] || [[ ${OS_NAME} == "Red Hat Enterprise Linux" ]] || [[ ${OS_NAME} == "Amazon Linux" ]]; then
            yum install -y git
        fi
        
        log_success "Git 安装完成: $(git --version)"
    fi
}

# 克隆项目
clone_project() {
    log_info "检查项目目录..."
    
    if [[ -d ${PROJECT_DIR} ]]; then
        log_warning "项目目录已存在，正在备份..."
        backup_project
        rm -rf ${PROJECT_DIR}
    fi
    
    log_info "正在克隆项目..."
    cd /opt
    git clone https://github.com/xrs-b/mobile-ledger.git ${PROJECT_NAME}
    
    log_success "项目克隆完成"
}

# 备份项目
backup_project() {
    mkdir -p ${BACKUP_DIR}
    BACKUP_NAME="${PROJECT_NAME}_$(date '+%Y%m%d_%H%M%S')"
    tar -czf ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz ${PROJECT_DIR}
    log_info "备份已创建: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
}

# 配置环境变量
setup_env() {
    log_info "配置环境变量..."
    
    cat > ${PROJECT_DIR}/.env << EOF
# Mobile Ledger 环境配置

# 数据库配置
DATABASE_URL=sqlite:///./data/ledger.db

# JWT 配置（生产环境请修改）
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 时区配置
TIMEZONE=Asia/Shanghai

# 服务配置
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000
EOF
    
    log_success "环境变量已配置"
}

# 创建数据目录
setup_data_dir() {
    log_info "创建数据目录..."
    
    mkdir -p ${PROJECT_DIR}/data
    mkdir -p ${PROJECT_DIR}/logs
    
    # 设置权限
    chmod -R 755 ${PROJECT_DIR}/data
    chmod -R 755 ${PROJECT_DIR}/logs
    
    log_success "数据目录已创建"
}

# 构建和启动容器
deploy() {
    log_info "开始构建和启动服务..."
    
    cd ${PROJECT_DIR}
    
    # 构建镜像
    log_info "构建 Docker 镜像..."
    docker-compose build
    
    # 启动服务
    log_info "启动服务..."
    docker-compose up -d
    
    log_success "服务启动完成"
}

# 配置防火墙
configure_firewall() {
    log_info "检查防火墙状态..."
    
    # 检查 firewalld
    if systemctl is-active --quiet firewalld; then
        log_info "配置 firewalld..."
        firewall-cmd --permanent --add-port=8000/tcp
        firewall-cmd --permanent --add-port=3000/tcp
        firewall-cmd --reload
        log_success "firewalld 配置完成"
    fi
    
    # 检查 ufw
    if command -v ufw &> /dev/null; then
        if ufw status | grep -q "Status: active"; then
            log_info "配置 UFW..."
            ufw allow 8000/tcp
            ufw allow 3000/tcp
            ufw reload
            log_success "UFW 配置完成"
        fi
    fi
}

# 配置 Nginx（可选）
install_nginx() {
    log_info "检查 Nginx 安装状态..."
    
    if command -v nginx &> /dev/null; then
        log_success "Nginx 已安装"
    else
        log_info "正在安装 Nginx..."
        
        if [[ ${OS_NAME} == "Ubuntu" ]] || [[ ${OS_NAME} == "Debian" ]]; then
            apt-get update
            apt-get install -y nginx
        elif [[ ${OS_NAME} == "CentOS" ]] || [[ ${OS_NAME} == "Red Hat Enterprise Linux" ]] || [[ ${OS_NAME} == "Amazon Linux" ]]; then
            yum install -y nginx
        fi
        
        log_success "Nginx 安装完成"
    fi
    
    # 配置反向代理
    cat > /etc/nginx/conf.d/${PROJECT_NAME}.conf << EOF
server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location / {
        root ${PROJECT_DIR}/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF
    
    # 启动 Nginx
    systemctl start nginx
    systemctl enable nginx
    
    log_success "Nginx 配置完成"
}

# 检查服务状态
check_status() {
    log_info "检查服务状态..."
    
    cd ${PROJECT_DIR}
    
    echo ""
    echo "========================================"
    echo "         服务状态"
    echo "========================================"
    docker-compose ps
    echo ""
    echo "========================================"
    echo "         端口监听"
    echo "========================================"
    netstat -tlnp 2>/dev/null | grep -E ':(8000|3000|80)' || ss -tlnp | grep -E ':(8000|3000|80)'
    echo ""
    echo "========================================"
    echo "         访问地址"
    echo "========================================"
    echo "前端: http://localhost:3000"
    echo "后端: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
    echo "========================================"
}

# 查看日志
show_logs() {
    cd ${PROJECT_DIR}
    docker-compose logs -f ${1:-}
}

# 停止服务
stop() {
    log_info "停止服务..."
    cd ${PROJECT_DIR}
    docker-compose down
    log_success "服务已停止"
}

# 重启服务
restart() {
    log_info "重启服务..."
    cd ${PROJECT_DIR}
    docker-compose restart
    log_success "服务已重启"
}

# 更新项目
update() {
    log_info "更新项目..."
    
    cd ${PROJECT_DIR}
    
    # 备份
    backup_project
    
    # 拉取最新代码
    git pull
    
    # 重新构建
    docker-compose build
    docker-compose up -d
    
    log_success "更新完成"
}

# 显示帮助信息
show_help() {
    echo ""
    echo "========================================"
    echo "    Mobile Ledger 一键部署脚本"
    echo "========================================"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  install     安装所有依赖（Docker、Docker Compose、Git）"
    echo "  deploy      部署项目"
    echo "  update      更新项目"
    echo "  stop       停止服务"
    echo "  restart    重启服务"
    echo "  status     查看状态"
    echo "  logs       查看日志"
    echo "  backup     备份项目"
    echo "  nginx      安装并配置 Nginx"
    echo "  help       显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 install    # 安装依赖"
    echo "  $0 deploy    # 部署项目"
    echo "  $0 status    # 查看状态"
    echo ""
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p /var/log
    
    echo ""
    echo "========================================"
    echo "    Mobile Ledger 一键部署脚本"
    echo "========================================"
    echo ""
    
    # 检查系统
    check_root
    check_os
    
    # 解析命令
    case ${1:-deploy} in
        install)
            install_docker
            install_docker_compose
            install_git
            ;;
        deploy)
            install_docker
            install_docker_compose
            install_git
            clone_project
            setup_env
            setup_data_dir
            deploy
            configure_firewall
            check_status
            ;;
        update)
            update
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs ${2:-}
            ;;
        backup)
            backup_project
            ;;
        nginx)
            install_nginx
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
