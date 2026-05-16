from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from database.db import get_db
from models.models import UsageLog, API, Subscription, User

router = APIRouter(prefix="/ai", tags=["AI Insights"])

SECRET_KEY = "marketplace-secret-key-2024"
ALGORITHM = "HS256"
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                     db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/insights")
def get_ai_insights(db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    apis = db.query(API).filter(API.developer_id == current_user.id).all()
    if not apis:
        raise HTTPException(status_code=404, detail="Koi API listed nahi hai")

    summary = []
    total_revenue = 0
    best_api = None
    best_subs = 0

    for api in apis:
        calls = db.query(UsageLog).filter(UsageLog.api_id == api.id).count()
        subs = db.query(Subscription).filter(
            Subscription.api_id == api.id,
            Subscription.is_active == True).count()
        revenue = subs * api.price_monthly
        total_revenue += revenue
        if subs > best_subs:
            best_subs = subs
            best_api = api.name
        summary.append({
            "api_name": api.name,
            "total_calls": calls,
            "subscribers": subs,
            "revenue": revenue
        })

    insights = []

    if best_api:
        insights.append(f"⭐ Sabse popular API: {best_api} ({best_subs} subscribers)")
    else:
        insights.append("⚠️ Abhi koi subscriber nahi hai — API price check karo")

    if total_revenue < 500:
        insights.append("💡 Revenue badhane ke liye: Aur APIs add karo ya price thoda kam karo")
    else:
        insights.append(f"✅ Total monthly revenue ₹{total_revenue} — acha chal raha hai!")

    insights.append("🚀 Next step: Premium plan add karo — zyada features, zyada price")
    insights.append("📊 Tip: API description aur documentation improve karo — subscribers badhenge")

    return {
        "insights": insights,
        "api_summary": summary,
        "total_revenue": total_revenue
    }