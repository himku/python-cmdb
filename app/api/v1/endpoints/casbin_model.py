from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services.casbin_model_service import get_model_content, set_model_content
from app.database.session import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ModelContentIn(BaseModel):
    content: str

@router.get("/model", summary="获取 Casbin 模型内容")
def get_model(db: Session = Depends(get_db)):
    content = get_model_content(db)
    if not content:
        raise HTTPException(status_code=404, detail="模型内容不存在")
    return {"content": content}

@router.post("/model", summary="设置 Casbin 模型内容")
def set_model(data: ModelContentIn, db: Session = Depends(get_db)):
    model = set_model_content(db, data.content)
    return {"msg": "保存成功", "id": model.id}
