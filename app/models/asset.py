from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    asset_type = Column(String(50), nullable=False)  # server, network, storage, etc.
    status = Column(String(20), default="active")  # active, inactive, maintenance
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    mac_address = Column(String(17), nullable=True)  # MAC address format
    location = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    owner_id = Column(Integer, ForeignKey("users.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="assets", foreign_keys=[owner_id])
    creator = relationship("User", back_populates="created_assets", foreign_keys=[creator_id])
