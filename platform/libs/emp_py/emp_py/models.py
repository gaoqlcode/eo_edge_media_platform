"""
文件：emp_py/models.py
内容：ORM 模型，对应 migrations 中的核心表（教学简化版）
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text, BigInteger, ForeignKey
from sqlalchemy.types import JSON

from emp_py.db import Base


def _uuid():
    return str(uuid.uuid4())


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String(36), primary_key=True, default=_uuid)
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Device(Base):
    __tablename__ = "devices"
    id = Column(String(36), primary_key=True, default=_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    device_code = Column(String(64), nullable=False)
    name = Column(String(128), nullable=False)
    device_type = Column(String(32), default="edge")
    platform = Column(String(32), default="wsl")
    status = Column(String(32), default="offline")
    last_seen_at = Column(DateTime, nullable=True)
    meta_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Channel(Base):
    __tablename__ = "channels"
    id = Column(String(36), primary_key=True, default=_uuid)
    device_id = Column(String(36), ForeignKey("devices.id"), nullable=False)
    channel_code = Column(String(64), nullable=False)
    name = Column(String(128), nullable=False)
    media_kind = Column(String(32), default="video")
    enabled = Column(Boolean, default=True)
    config_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class RecordSession(Base):
    __tablename__ = "record_sessions"
    id = Column(String(36), primary_key=True, default=_uuid)
    device_id = Column(String(36), ForeignKey("devices.id"), nullable=False)
    session_code = Column(String(128), nullable=False)
    status = Column(String(32), default="created")
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    storage_root = Column(Text, nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MediaAsset(Base):
    __tablename__ = "media_assets"
    id = Column(String(36), primary_key=True, default=_uuid)
    session_id = Column(String(36), ForeignKey("record_sessions.id"), nullable=False)
    channel_id = Column(String(36), nullable=True)
    asset_type = Column(String(32), nullable=False)
    relative_path = Column(Text, nullable=False)
    byte_size = Column(BigInteger, default=0)
    duration_ms = Column(BigInteger, nullable=True)
    meta_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class AlarmEvent(Base):
    __tablename__ = "alarm_events"
    id = Column(String(36), primary_key=True, default=_uuid)
    device_id = Column(String(36), nullable=True)
    severity = Column(String(16), default="info")
    code = Column(String(64), nullable=False)
    message = Column(Text, nullable=False)
    payload_json = Column(JSON, default=dict)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    acked = Column(Boolean, default=False)


class CommandAudit(Base):
    __tablename__ = "command_audits"
    id = Column(String(36), primary_key=True, default=_uuid)
    device_id = Column(String(36), nullable=True)
    operator = Column(String(64), nullable=False, default="system")
    command = Column(String(64), nullable=False)
    request_json = Column(JSON, default=dict)
    result_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
