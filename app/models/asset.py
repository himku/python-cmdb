from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    asset_type = Column(String, index=True)
    status = Column(String, index=True)
    description = Column(String)
    ip_address = Column(String)
    mac_address = Column(String)
    os_type = Column(String)
    os_version = Column(String)
    cpu_info = Column(JSON)
    memory_info = Column(JSON)
    disk_info = Column(JSON)
    network_info = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="assets")
    
class AutoAsset(Base):
    __tablename__ = "auto_assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    asset_type = Column(String, index=True)
    status = Column(String, index=True)
    