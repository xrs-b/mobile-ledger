"""
数据库连接配置
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库路径
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.dirname(os.path.dirname(__file__))}/data/mobile_ledger.db"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "true").lower() == "true",  # 开发模式显示SQL
    connect_args={"check_same_thread": False},  # SQLite需要
)

# 创建SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 确保data目录存在
data_dir = os.path.dirname(DATABASE_URL.replace("sqlite:///", ""))
if data_dir and not os.path.exists(data_dir):
    os.makedirs(data_dir, exist_ok=True)
