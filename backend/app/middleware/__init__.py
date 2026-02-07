"""
中间件集合
"""
import time
import logging
from typing import Callable
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """请求计时中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 添加响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            # 日志记录
            logger.info(
                f"{request.method} {request.url.path} - "
                f"{response.status_code} - {process_time:.4f}s"
            )
            
            return response
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"{request.method} {request.url.path} - "
                f"ERROR: {exc} - {process_time:.4f}s"
            )
            raise


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """全局错误处理中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": exc.status_code,
                        "message": exc.detail
                    }
                }
            )
        except ValueError as exc:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": {
                        "code": 400,
                        "message": str(exc) or "无效的请求参数"
                    }
                }
            )
        except Exception as exc:
            logger.exception(f"未处理的异常: {exc}")
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


class CacheControlMiddleware(BaseHTTPMiddleware):
    """缓存控制中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # 对GET请求添加缓存头
        if request.method == "GET" and not request.url.path.startswith("/api/v1/statistics"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        
        return response
