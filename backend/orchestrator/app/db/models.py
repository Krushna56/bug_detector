from sqlalchemy import Column, String, Integer, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from .database import Base
import enum

class ScanStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"

class Scan(Base):
    __tablename__ = "scans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo = Column(String, nullable=False)
    pr_number = Column(Integer)
    commit_sha = Column(String)
    scan_type = Column(String)
    artifact_url = Column(String)
    status = Column(Enum(ScanStatus), default=ScanStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Finding(Base):
    __tablename__ = "findings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    file_path = Column(String)
    start_line = Column(Integer)
    end_line = Column(Integer)
    rule_id = Column(String)
    message = Column(String)
    severity = Column(String)
    raw = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())