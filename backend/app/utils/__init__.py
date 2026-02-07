"""
响应格式化工具
"""
from typing import Any, Dict, List, Optional
from datetime import date, datetime


class ResponseFormatter:
    """统一响应格式化"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功") -> Dict:
        """成功响应"""
        result = {
            "success": True,
            "message": message
        }
        if data is not None:
            result["data"] = data
        return result
    
    @staticmethod
    def paginated(
        items: List,
        total: int,
        page: int,
        page_size: int
    ) -> Dict:
        """分页响应"""
        return {
            "success": True,
            "data": {
                "items": items,
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size
                }
            }
        }
    
    @staticmethod
    def error(message: str, code: int = 400) -> Dict:
        """错误响应"""
        return {
            "success": False,
            "error": {
                "code": code,
                "message": message
            }
        }


def format_datetime(value: Optional[datetime]) -> Optional[str]:
    """格式化datetime为ISO字符串"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return value.isoformat()


def format_date(value: Optional[date]) -> Optional[str]:
    """格式化date为字符串"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return value.isoformat()


def round_number(value: float, decimals: int = 2) -> float:
    """四舍五入"""
    if value is None:
        return 0
    return round(float(value), decimals)
