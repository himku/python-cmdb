import casbin
from casbin_sqlalchemy_adapter import Adapter
import os
from app.core.config import get_settings

settings = get_settings()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "casbin_model.conf")

# 使用 SQLAlchemyAdapter 连接 MySQL 存储 Casbin 策略
adapter = Adapter(settings.SQLALCHEMY_DATABASE_URI)

# 单例模式，避免重复加载
_enforcer = None

def get_enforcer():
    global _enforcer
    if _enforcer is None:
        _enforcer = casbin.Enforcer(MODEL_PATH, adapter)
    return _enforcer

def check_permission(sub: str, obj: str, act: str) -> bool:
    """
    检查用户(sub)对资源(obj)的操作(act)是否被允许
    """
    enforcer = get_enforcer()
    return enforcer.enforce(sub, obj, act)

def add_policy(sub: str, obj: str, act: str) -> bool:
    """
    添加一条策略
    """
    enforcer = get_enforcer()
    return enforcer.add_permission_for_user(sub, obj, act)

def remove_policy(sub: str, obj: str, act: str) -> bool:
    """
    删除一条策略
    """
    enforcer = get_enforcer()
    return enforcer.delete_permission_for_user(sub, obj, act)

def get_policies():
    """
    获取所有策略
    """
    enforcer = get_enforcer()
    return enforcer.get_policy()

def get_user_policies(username: str):
    """
    获取指定用户的所有权限策略
    """
    enforcer = get_enforcer()
    return enforcer.get_permissions_for_user(username)
