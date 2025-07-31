from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime

class MenuBase(BaseModel):
    """菜单基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="菜单名称")
    title: str = Field(..., min_length=1, max_length=100, description="菜单标题")
    path: Optional[str] = Field(None, max_length=255, description="路由路径")
    component: Optional[str] = Field(None, max_length=255, description="组件路径")
    redirect: Optional[str] = Field(None, max_length=255, description="重定向地址")
    
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    sort: int = Field(0, description="排序序号")
    level: int = Field(1, ge=1, le=5, description="菜单层级")
    
    menu_type: int = Field(1, ge=1, le=3, description="菜单类型: 1-目录 2-菜单 3-按钮")
    is_visible: bool = Field(True, description="是否显示")
    is_enabled: bool = Field(True, description="是否启用")
    is_cache: bool = Field(False, description="是否缓存")
    is_frame: bool = Field(False, description="是否为外链")
    
    icon: Optional[str] = Field(None, max_length=100, description="菜单图标")
    icon_type: int = Field(1, ge=1, le=2, description="图标类型")
    permission_code: Optional[str] = Field(None, max_length=100, description="权限标识码")
    
    meta: Optional[Dict[str, Any]] = Field(None, description="元数据配置")

class MenuCreate(MenuBase):
    """创建菜单模型"""
    pass

class MenuUpdate(BaseModel):
    """更新菜单模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    path: Optional[str] = Field(None, max_length=255)
    component: Optional[str] = Field(None, max_length=255)
    redirect: Optional[str] = Field(None, max_length=255)
    
    parent_id: Optional[int] = None
    sort: Optional[int] = None
    level: Optional[int] = Field(None, ge=1, le=5)
    
    menu_type: Optional[int] = Field(None, ge=1, le=3)
    is_visible: Optional[bool] = None
    is_enabled: Optional[bool] = None
    is_cache: Optional[bool] = None
    is_frame: Optional[bool] = None
    
    icon: Optional[str] = Field(None, max_length=100)
    icon_type: Optional[int] = Field(None, ge=1, le=2)
    permission_code: Optional[str] = Field(None, max_length=100)
    
    meta: Optional[Dict[str, Any]] = None

class MenuInDB(MenuBase):
    """数据库中的菜单模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Menu(MenuInDB):
    """菜单响应模型"""
    children: Optional[List['Menu']] = Field(default_factory=list, description="子菜单列表")
    
    class Config:
        from_attributes = True

# 用于解决循环引用
Menu.model_rebuild()

class MenuTree(BaseModel):
    """菜单树形结构"""
    id: int
    name: str
    title: str
    path: Optional[str]
    component: Optional[str]
    redirect: Optional[str]
    parent_id: Optional[int]
    sort: int
    level: int
    menu_type: int
    is_visible: bool
    is_enabled: bool
    is_cache: bool
    is_frame: bool
    icon: Optional[str]
    icon_type: int
    permission_code: Optional[str]
    meta: Optional[Dict[str, Any]]
    children: List['MenuTree'] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

# 解决循环引用
MenuTree.model_rebuild()

class MenuRoute(BaseModel):
    """前端路由格式的菜单"""
    name: str
    path: str
    component: Optional[str] = None
    redirect: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    children: Optional[List['MenuRoute']] = None

# 解决循环引用
MenuRoute.model_rebuild()

class UserMenuResponse(BaseModel):
    """用户菜单响应"""
    menus: List[MenuTree] = Field(description="菜单树")
    routes: List[MenuRoute] = Field(description="路由配置")
    permissions: List[str] = Field(description="权限代码列表") 