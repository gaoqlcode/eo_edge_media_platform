"""
文件：emp_py/db.py
内容：SQLAlchemy 引擎与会话工厂；兼容 PostgreSQL 与 SQLite 自测
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

from emp_py.config import settings

# SQLite 需要 check_same_thread=False 才能在 FastAPI 多线程下用
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """FastAPI 依赖：获取并关闭一个 DB 会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建全部 ORM 表（自测/首次启动用；生产以 SQL 迁移为准）。"""
    from emp_py import models  # noqa: F401
    from sqlalchemy.exc import OperationalError

    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError:
        # 多进程并发 create_all 时 SQLite 可能报 already exists，可安全忽略
        pass
