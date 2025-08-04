import os
import casbin
from casbin_sqlalchemy_adapter import Adapter
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, create_engine
from app.users.models import User
from app.core.config import get_settings

# 添加日志
from app.core.logging import get_logger, log_casbin, log_permission, log_error

settings = get_settings()
logger = get_logger("casbin")

class CasbinService:
    _enforcer: Optional[casbin.Enforcer] = None
    _adapter: Optional[Adapter] = None
    
    @classmethod
    def get_adapter(cls) -> Adapter:
        """获取数据库适配器实例"""
        if cls._adapter is None:
            logger.info("🔧 初始化Casbin数据库适配器")
            # 创建同步数据库连接用于 Casbin 适配器
            sync_url = settings.SQLALCHEMY_DATABASE_URI.replace('+aiomysql', '+pymysql')
            logger.debug(f"📡 数据库连接: {sync_url.split('@')[0]}@***")
            cls._adapter = Adapter(sync_url)
            logger.info("✅ Casbin数据库适配器初始化完成")
        return cls._adapter
    
    @classmethod
    def get_enforcer(cls) -> casbin.Enforcer:
        """获取Casbin执行器实例"""
        if cls._enforcer is None:
            logger.info("🚀 初始化Casbin执行器")
            
            # 获取模型配置文件路径
            model_path = os.path.join(os.path.dirname(__file__), '../core/rbac_model.conf')
            logger.debug(f"📋 模型配置文件: {model_path}")
            
            # 创建执行器
            adapter = cls.get_adapter()
            cls._enforcer = casbin.Enforcer(model_path, adapter)
            
            # 加载策略
            cls._enforcer.load_policy()
            logger.info("✅ Casbin执行器初始化完成")
            
            # 记录当前策略统计
            policies = cls._enforcer.get_policy()
            groupings = cls._enforcer.get_grouping_policy()
            logger.info(f"📊 已加载策略: {len(policies)} 个权限策略, {len(groupings)} 个角色分配")
            
        return cls._enforcer
    
    @classmethod
    def check_permission(cls, username: str, resource: str, action: str) -> bool:
        """检查用户权限"""
        enforcer = cls.get_enforcer()
        result = enforcer.enforce(username, resource, action)
        
        log_permission(username, resource, action, result)
        return result
    
    @classmethod
    def add_policy(cls, role: str, resource: str, action: str) -> bool:
        """添加策略"""
        enforcer = cls.get_enforcer()
        
        # 检查策略是否已存在
        if enforcer.has_policy(role, resource, action):
            logger.debug(f"📝 策略已存在: {role} {resource} {action}")
            return False
        
        result = enforcer.add_policy(role, resource, action)
        if result:
            enforcer.save_policy()
            log_casbin("添加策略", f"{role} -> {resource} {action}")
        else:
            logger.warning(f"⚠️ 策略添加失败: {role} {resource} {action}")
            
        return result
    
    @classmethod
    def remove_policy(cls, role: str, resource: str, action: str) -> bool:
        """删除策略"""
        enforcer = cls.get_enforcer()
        result = enforcer.remove_policy(role, resource, action)
        
        if result:
            enforcer.save_policy()
            log_casbin("删除策略", f"{role} -> {resource} {action}")
        else:
            logger.warning(f"⚠️ 策略删除失败: {role} {resource} {action}")
            
        return result
    
    @classmethod
    def add_role_for_user(cls, username: str, role: str) -> bool:
        """为用户分配角色"""
        enforcer = cls.get_enforcer()
        
        # 检查角色分配是否已存在
        if enforcer.has_role_for_user(username, role):
            logger.debug(f"👤 角色分配已存在: {username} -> {role}")
            return False
        
        result = enforcer.add_role_for_user(username, role)
        if result:
            enforcer.save_policy()
            log_casbin("分配角色", f"{username} -> {role}")
        else:
            logger.warning(f"⚠️ 角色分配失败: {username} -> {role}")
            
        return result
    
    @classmethod
    def delete_role_for_user(cls, username: str, role: str) -> bool:
        """删除用户角色"""
        enforcer = cls.get_enforcer()
        result = enforcer.delete_role_for_user(username, role)
        
        if result:
            enforcer.save_policy()
            log_casbin("移除角色", f"{username} <- {role}")
        else:
            logger.warning(f"⚠️ 角色移除失败: {username} <- {role}")
            
        return result
    
    @classmethod
    def get_roles_for_user(cls, username: str) -> List[str]:
        """获取用户的所有角色"""
        enforcer = cls.get_enforcer()
        roles = enforcer.get_roles_for_user(username)
        logger.debug(f"👤 {username} 的角色: {roles}")
        return roles
    
    @classmethod
    def get_users_for_role(cls, role: str) -> List[str]:
        """获取拥有指定角色的所有用户"""
        enforcer = cls.get_enforcer()
        users = enforcer.get_users_for_role(role)
        logger.debug(f"👥 角色 {role} 的用户: {users}")
        return users
    
    @classmethod
    def get_permissions_for_user(cls, username: str) -> List[List[str]]:
        """获取用户的所有权限"""
        enforcer = cls.get_enforcer()
        permissions = enforcer.get_permissions_for_user(username)
        logger.debug(f"🔐 {username} 的权限: {len(permissions)} 个")
        return permissions
    
    @classmethod
    def save_policy(cls) -> bool:
        """保存策略到数据库"""
        enforcer = cls.get_enforcer()
        result = enforcer.save_policy()
        if result:
            log_casbin("保存策略", "策略已同步到数据库")
        else:
            logger.error("💥 策略保存失败")
        return result
    
    @classmethod
    def load_policy(cls) -> bool:
        """从数据库加载策略"""
        enforcer = cls.get_enforcer()
        result = enforcer.load_policy()
        if result:
            policies = enforcer.get_policy()
            groupings = enforcer.get_grouping_policy()
            log_casbin("加载策略", f"从数据库加载 {len(policies)} 个策略, {len(groupings)} 个角色分配")
        else:
            logger.error("💥 策略加载失败")
        return result
    
    @classmethod
    def get_all_policies(cls) -> List[List[str]]:
        """获取所有策略"""
        enforcer = cls.get_enforcer()
        policies = enforcer.get_policy()
        logger.debug(f"📊 当前策略总数: {len(policies)}")
        return policies
    
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
        
        role_list = list(roles)
        logger.debug(f"👥 当前角色总数: {len(role_list)} - {role_list}")
        return role_list
    
    @classmethod
    def initialize_default_policies(cls):
        """初始化默认策略"""
        logger.info("🔧 开始初始化默认策略")
        
        # 检查是否已有策略
        policies = cls.get_all_policies()
        if policies:
            logger.info(f"📋 发现现有策略 {len(policies)} 个，跳过初始化")
            return
        
        # 从CSV文件导入策略
        csv_path = os.path.join(os.path.dirname(__file__), '../core/rbac_policy.csv')
        if not os.path.exists(csv_path):
            logger.warning(f"⚠️ 策略文件不存在: {csv_path}")
            return
        
        logger.info(f"📁 从文件导入策略: {csv_path}")
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            policy_count = 0
            group_count = 0
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = [part.strip() for part in line.split(',')]
                
                if parts[0] == 'p' and len(parts) >= 4:
                    # 策略规则
                    result = cls.add_policy(parts[1], parts[2], parts[3])
                    if result:
                        policy_count += 1
                        
                elif parts[0] == 'g' and len(parts) >= 3:
                    # 角色分配
                    result = cls.add_role_for_user(parts[1], parts[2])
                    if result:
                        group_count += 1
            
            log_casbin("初始化完成", f"导入 {policy_count} 个策略, {group_count} 个角色分配")
            
        except Exception as e:
            logger.error(f"💥 初始化策略失败: {e}")
            log_error(e, "策略初始化") 