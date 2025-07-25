import logging
from app.database.session import Base, engine, SessionLocal
# from app.users.models import User  # 移到函数内部，避免循环 import
from app.core.security import get_password_hash
from loguru import logger

logger = logging.getLogger(__name__)

def drop_db() -> None:
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise

def init_db() -> None:
    from app.users.models import User, Role, Permission
    db = None
    try:
        # Drop existing tables
        drop_db()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        db = SessionLocal()
        
        try:
            # Create default permissions
            permissions = {
                "asset": ["read", "write", "delete"],
                "user": ["read", "write", "delete"],
                "role": ["read", "write", "delete"]
            }
            
            permission_objects = {}
            for resource, actions in permissions.items():
                for action in actions:
                    code = f"{resource}:{action}"
                    name = f"Can {action} {resource}"
                    permission = Permission(
                        name=name,
                        code=code,
                        description=f"Permission to {action} {resource}"
                    )
                    db.add(permission)
                    permission_objects[code] = permission
            
            # Create admin role
            admin_role = Role(
                name="admin",
                description="Administrator role with all permissions"
            )
            db.add(admin_role)
            db.flush()  # Get the role ID
            
            # Assign all permissions to admin role
            admin_role.permissions = list(permission_objects.values())
            
            # Create admin user
            admin = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrator",
                is_active=True,
                is_superuser=True
            )
            db.add(admin)
            db.flush()  # Get the user ID
            
            # Assign admin role to admin user
            admin.roles = [admin_role]
            
            db.commit()
            logger.info("Initial admin user and permissions created successfully")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating initial data: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        if db is not None:
            db.close()
