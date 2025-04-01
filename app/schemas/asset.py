from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AssetBase(BaseModel):
    name: str
    asset_type: str
    status: str
    description: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    cpu_info: Optional[Dict[str, Any]] = None
    memory_info: Optional[Dict[str, Any]] = None
    disk_info: Optional[Dict[str, Any]] = None
    network_info: Optional[Dict[str, Any]] = None

class AssetCreate(AssetBase):
    owner_id: int

class AssetUpdate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 