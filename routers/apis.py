from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import jwt, JWTError
from database.db import get_db
from models.models import API, User

router = APIRouter(prefix="/apis", tags=["APIs"])

SECRET_KEY = "marketplace-secret-key-2024"
ALGORITHM = "HS256"
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class APIInput(BaseModel):
    name: str
    description: str
    base_url: str
    price_monthly: float = 0.0

@router.get("/")
def list_apis(db: Session = Depends(get_db)):
    apis = db.query(API).filter(API.is_active == True).all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "price_monthly": a.price_monthly,
            "developer": a.developer.name
        }
        for a in apis
    ]

@router.post("/")
def create_api(data: APIInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "developer":
        raise HTTPException(status_code=403, detail="Only developers can list APIs")
    api = API(
        name=data.name,
        description=data.description,
        base_url=data.base_url,
        price_monthly=data.price_monthly,
        developer_id=current_user.id
    )
    db.add(api)
    db.commit()
    db.refresh(api)
    return {"message": "API listed successfully", "api_id": api.id}

@router.get("/{api_id}")
def get_api(api_id: int, db: Session = Depends(get_db)):
    api = db.query(API).filter(API.id == api_id).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")
    return {
        "id": api.id,
        "name": api.name,
        "description": api.description,
        "base_url": api.base_url,
        "price_monthly": api.price_monthly,
        "developer": api.developer.name
    }

@router.delete("/{api_id}")
def delete_api(api_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    api = db.query(API).filter(API.id == api_id, API.developer_id == current_user.id).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found or not yours")
    api.is_active = False
    db.commit()
    return {"message": "API removed successfully"}