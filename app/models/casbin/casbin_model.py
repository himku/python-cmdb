from sqlalchemy import Column, Integer, Text
from app.database.session import Base
from sqlalchemy.schema import CreateTable

class CasbinModel(Base):
    __tablename__ = "casbin_model"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False, comment="Casbin模型内容")

    def __repr__(self):
        return f"<CasbinModel(id={self.id}, content={self.content[:20]}...)>"
    