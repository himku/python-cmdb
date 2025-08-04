import os
import casbin
from casbin_sqlalchemy_adapter import Adapter
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, create_engine
from app.users.models import User
from app.core.config import get_settings

settings = get_settings()

class CasbinService:
    _enforcer: Optional[casbin.Enforcer] = None
    _adapter: Optional[Adapter] = None
    
    @classmethod
    def get_adapter(cls) -> Adapter:
        """获取数据库适配器实例"""
        if cls._adapter is None:
            # 创建同步数据库连接用于 Casbin 适配器
            # 注意：casbin-sqlalchemy-adapter 目前不支持异步
            database_url = settings.SQLALCHEMY_DATABASE_URI
            if database_url and database_url.startswith("mysql+aiomysql://"):
                # 将异步URL转换为同步URL
                database_url = database_url.replace("mysql+aiomysql://", "mysql+pymysql://")
            elif database_url and database_url.startswith("mysql+pymysql://"):
                # 已经是同步URL，直接使用
                pass
            
            cls._adapter = Adapter(database_url)
        return cls._adapter
    
    @classmethod
    def get_enforcer(cls) -> casbin.Enforcer:
        """获取 Casbin enforcer 实例（单例模式）"""
        if cls._enforcer is None:
            # 获取配置文件路径
            model_path = os.path.join(os.path.dirname(__file__), "../core/rbac_model.conf")
            
            # 创建数据库适配器
            adapter = cls.get_adapter()
            
            # 创建 enforcer
            cls._enforcer = casbin.Enforcer(model_path, adapter)
            
            # 加载策略
            cls._enforcer.load_policy()
            
        return cls._enforcer
    
    @classmethod
    def check_permission(cls, user: str, obj: str, act: str) -> bool:
        """检查用户权限"""
        enforcer = cls.get_enforcer()
        return enforcer.enforce(user, obj, act)
    
    @classmethod
    def add_policy(cls, role: str, obj: str, act: str) -> bool:
        """添加策略"""
        enforcer = cls.get_enforcer()
        result = enforcer.add_policy(role, obj, act)
        if result:
            enforcer.save_policy()
        return result
    
    @classmethod
    def remove_policy(cls, role: str, obj: str, act: str) -> bool:
        """移除策略"""
        enforcer = cls.get_enforcer()
        result = enforcer.remove_policy(role, obj, act)
        if result:
            enforcer.save_policy()
        return result
    
    @classmethod
    def add_role_for_user(cls, user: str, role: str) -> bool:
        """为用户添加角色"""
        enforcer = cls.get_enforcer()
        result = enforcer.add_role_for_user(user, role)
        if result:
            enforcer.save_policy()
        return result
    
    @classmethod
    def delete_role_for_user(cls, user: str, role: str) -> bool:
        """删除用户角色"""
        enforcer = cls.get_enforcer()
        result = enforcer.delete_role_for_user(user, role)
        if result:
            enforcer.save_policy()
        return result
    
    @classmethod
    def get_roles_for_user(cls, user: str) -> List[str]:
        """获取用户的所有角色"""
        enforcer = cls.get_enforcer()
        return enforcer.get_roles_for_user(user)
    
    @classmethod
    def get_users_for_role(cls, role: str) -> List[str]:
        """获取拥有指定角色的所有用户"""
        enforcer = cls.get_enforcer()
        return enforcer.get_users_for_role(role)
    
    @classmethod
    def get_permissions_for_user(cls, user: str) -> List[List[str]]:
        """获取用户的所有权限"""
        enforcer = cls.get_enforcer()
        return enforcer.get_permissions_for_user(user)
    
    @classmethod
    def get_all_policies(cls) -> List[List[str]]:
        """获取所有策略"""
        enforcer = cls.get_enforcer()
        return enforcer.get_policy()
    
    @classmethod
    def get_all_roles(cls) -> List[str]:
        """获取所有角色"""
        enforcer = cls.get_enforcer()
        roles = set()
        
        # 从策略中提取角色
        for policy in enforcer.get_policy():
            if len(policy) > 0:
                roles.add(policy[0])
        
        # 从角色分配中提取角色
        for group in enforcer.get_grouping_policy():
            if len(group) > 1:
                roles.add(group[1])
        
        return list(roles)
    
    @classmethod
    def save_policy(cls) -> bool:
        """保存策略到数据库"""
        enforcer = cls.get_enforcer()
        return enforcer.save_policy()
    
    @classmethod
    def load_policy(cls) -> bool:
        """从数据库加载策略"""
        enforcer = cls.get_enforcer()
        return enforcer.load_policy()
    
    @classmethod
    def initialize_default_policies(cls):
        """初始化默认策略（仅在表为空时执行）"""
        enforcer = cls.get_enforcer()
        
        # 检查是否已有策略
        existing_policies = enforcer.get_policy()
        if existing_policies:
            print(f"策略表已有 {len(existing_policies)} 条记录，跳过初始化")
            return
        
        # 默认策略
        default_policies = [
            # 管理员权限
            ("admin", "/api/v1/admin/*", "*"),
            ("admin", "/api/v1/users/*", "*"),
            
            # 用户管理员权限
            ("user_manager", "/api/v1/users/*", "GET"),
            ("user_manager", "/api/v1/users/*", "POST"),
            ("user_manager", "/api/v1/users/*", "PUT"),
            
            # 查看者权限
            ("viewer", "/api/v1/users/*", "GET"),
            
            # 匿名用户权限
            ("anonymous", "/docs", "GET"),
            ("anonymous", "/redoc", "GET"),
            ("anonymous", "/openapi.json", "GET"),
            ("anonymous", "/health", "GET"),
            ("anonymous", "/auth/*", "*"),
        ]
        
        # 默认角色分配
        default_role_assignments = [
            ("alice", "admin"),
            ("bob", "user_manager"),
            ("charlie", "viewer"),
        ]
        
        print("正在初始化默认策略...")
        
        # 添加策略
        for role, obj, act in default_policies:
            if enforcer.add_policy(role, obj, act):
                print(f"✅ 添加策略: {role} -> {obj} [{act}]")
        
        # 添加角色分配
        for user, role in default_role_assignments:
            if enforcer.add_role_for_user(user, role):
                print(f"✅ 分配角色: {user} -> {role}")
        
        # 保存策略
        enforcer.save_policy()
        print("✅ 默认策略初始化完成") 