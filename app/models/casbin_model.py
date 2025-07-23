from sqlalchemy import Column, Integer, Text
from app.database.session import Base

class CasbinModel(Base):
    __tablename__ = "casbin_model"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False, comment="Casbin模型内容")
