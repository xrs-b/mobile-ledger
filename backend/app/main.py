"""
移动账本后端 - FastAPI入口
"""
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 数据库初始化
from app.database import engine, Base

# 路由导入
from app.routers import auth, category, record, project, statistics, budget, invitation, admin


async def log_requests_middleware(request: Request, call_next: Callable):
    """记录请求日志"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 添加处理时间头
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        # 日志
        print(
            f"{datetime.now().isoformat()} | "
            f"{request.method} {request.url.path} | "
            f"{response.status_code} | "
            f"{process_time:.4f}s"
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        print(
            f"{datetime.now().isoformat()} | "
            f"{request.method} {request.url.path} | "
            f"ERROR: {str(e)} | "
            f"{process_time:.4f}s"
        )
        raise


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "服务器内部错误，请稍后重试"
            }
        }
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")
    yield
    # 关闭时：清理资源
    print("👋 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title="移动账本 API",
    description="个人记账系统后端服务",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 添加中间件
app.middleware("http")(log_requests_middleware)

# CORS配置
origins = [
    "http://localhost:5173",  # Vue开发服务器
    "http://localhost:3000",  # 其他本地服务
    "http://127.0.0.1:5173",
    "*",  # 开发环境允许所有，生产环境请修改
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(category.router, prefix="/api/v1")
app.include_router(record.router, prefix="/api/v1")
app.include_router(project.router, prefix="/api/v1")
app.include_router(statistics.router, prefix="/api/v1")
app.include_router(budget.router, prefix="/api/v1")
app.include_router(invitation.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


# 健康检查接口
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "message": "服务运行正常",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """详细健康检查"""
    import sqlite3
    from app.database import DATABASE_URL
    
    health_status = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # 检查数据库
    try:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()
        health_status["services"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "移动账本 API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量读取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("DEBUG", "true").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
    )
