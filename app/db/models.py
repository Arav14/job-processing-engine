from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class JobDB(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    priority = Column(Integer, default=0)
    status = Column(String, nullable=False)
    payload = Column(Text)
    result = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
