from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import secrets
from jose import jwt, JWTError
from database.db import get_db
from models.models import Subscription, API, User

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

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

@router.post("/{api_id}")
def subscribe(api_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    api = db.query(API).filter(API.id == api_id, API.is_active == True).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")
    existing = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.api_id == api_id,
        Subscription.is_active == True
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already subscribed")
    api_key = "mk_" + secrets.token_hex(16)
    subscription = Subscription(
        user_id=current_user.id,
        api_id=api_id,
        api_key=api_key
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return {
        "message": "Subscribed successfully",
        "api_key": api_key,
        "api_name": api.name
    }

@router.get("/my")
def my_subscriptions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subs = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True
    ).all()
    return [
        {
            "api_name": s.api.name,
            "api_key": s.api_key,
            "subscribed_at": s.created_at
        }
        for s in subs
    ]

@router.delete("/{api_id}")
def unsubscribe(api_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.api_id == api_id,
        Subscription.is_active == True
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    sub.is_active = False
    db.commit()
    return {"message": "Unsubscribed successfully"}