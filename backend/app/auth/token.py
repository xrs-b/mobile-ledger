"""
JWT Token工具
"""
import os
from datetime import datetime, timedelta
from typing import Optional
import jwt
from pydantic import BaseModel


# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 默认24小时


class TokenData(BaseModel):
    """Token数据"""
    user_id: int
    username: str
    is_admin: bool = False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT Token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": int(expire.timestamp())})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """解析JWT Token"""
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_sub": False}
        )
        user_id: int = payload.get("sub")
        username: str = payload.get("username")
        is_admin: bool = payload.get("is_admin", False)
        
        if user_id is None:
            return None
        
        return TokenData(user_id=user_id, username=username, is_admin=is_admin)
    
    except jwt.PyJWTError:
        return None
