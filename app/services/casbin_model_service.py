from sqlalchemy.orm import Session
from app.models.casbin_model import CasbinModel

def get_model_content(db: Session) -> str:
    model = db.query(CasbinModel).order_by(CasbinModel.id.desc()).first()
    return model.content if model else None

def set_model_content(db: Session, content: str) -> CasbinModel:
    model = db.query(CasbinModel).order_by(CasbinModel.id.desc()).first()
    if model:
        model.content = content
    else:
        model = CasbinModel(content=content)
        db.add(model)
    db.commit()
    db.refresh(model)
    return model
