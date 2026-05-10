from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from jose import jwt, JWTError
from database.db import get_db
from models.models import UsageLog, API, Subscription, User

router = APIRouter(prefix="/analytics", tags=["Analytics"])

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

@router.get("/my-apis")
def my_api_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    apis = db.query(API).filter(API.developer_id == current_user.id).all()
    result = []
    for api in apis:
        total_calls = db.query(UsageLog).filter(UsageLog.api_id == api.id).count()
        success_calls = db.query(UsageLog).filter(
            UsageLog.api_id == api.id,
            UsageLog.status_code == 200
        ).count()
        avg_response = db.query(func.avg(UsageLog.response_time)).filter(
            UsageLog.api_id == api.id
        ).scalar()
        total_subscribers = db.query(Subscription).filter(
            Subscription.api_id == api.id,
            Subscription.is_active == True
        ).count()
        result.append({
            "api_name": api.name,
            "total_calls": total_calls,
            "success_calls": success_calls,
            "avg_response_time": round(avg_response or 0, 3),
            "total_subscribers": total_subscribers,
            "monthly_revenue": total_subscribers * api.price_monthly
        })
    return result

@router.get("/usage-logs/{api_id}")
def usage_logs(api_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = db.query(UsageLog).filter(
        UsageLog.api_id == api_id
    ).order_by(UsageLog.timestamp.desc()).limit(50).all()
    return [
        {
            "endpoint": l.endpoint,
            "status_code": l.status_code,
            "response_time": l.response_time,
            "timestamp": l.timestamp
        }
        for l in logs
    ]
    