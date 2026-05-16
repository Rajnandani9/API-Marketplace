import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import jwt, JWTError
import secrets
import razorpay

from database.db import get_db
from models.models import Subscription, API, User

router = APIRouter(prefix="/payments", tags=["Payments"])

SECRET_KEY = "marketplace-secret-key-2024"
ALGORITHM = "HS256"

security = HTTPBearer()

# Razorpay Test Keys
RAZORPAY_KEY_ID = "rzp_test_Sq52EQbN7ugcGz"
RAZORPAY_KEY_SECRET = "9xHLthVT3ujqOw0TK76RDyzQ"


# =========================
# AUTH USER
# =========================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user = db.query(User).filter(
            User.id == payload["user_id"]
        ).first()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# =========================
# REQUEST MODELS
# =========================
class CreateOrderInput(BaseModel):
    api_id: int


class VerifyPaymentInput(BaseModel):
    api_id: int
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


# =========================
# CREATE ORDER
# =========================
@router.post("/create-order")
def create_order(
    data: CreateOrderInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    api = db.query(API).filter(
        API.id == data.api_id,
        API.is_active == True
    ).first()

    if not api:
        raise HTTPException(
            status_code=404,
            detail="API not found"
        )

    try:
        client = razorpay.Client(
            auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
        )

        amount = int(api.price_monthly * 100)

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        return {
            "success": True,
            "order_id": order["id"],
            "amount": amount,
            "currency": "INR",
            "api_name": api.name,
            "key_id": RAZORPAY_KEY_ID
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Razorpay error: {str(e)}"
        )


# =========================
# VERIFY PAYMENT
# =========================
@router.post("/verify")
def verify_payment(
    data: VerifyPaymentInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:
        client = razorpay.Client(
            auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
        )

        client.utility.verify_payment_signature({
            "razorpay_order_id": data.razorpay_order_id,
            "razorpay_payment_id": data.razorpay_payment_id,
            "razorpay_signature": data.razorpay_signature
        })

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Payment verification failed"
        )

    # Already subscribed check
    existing = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.api_id == data.api_id,
        Subscription.is_active == True
    ).first()

    if existing:
        return {
            "message": "Already subscribed",
            "api_key": existing.api_key
        }

    # Generate API Key
    api_key = "mk_" + secrets.token_hex(16)

    new_subscription = Subscription(
        user_id=current_user.id,
        api_id=data.api_id,
        api_key=api_key
    )

    db.add(new_subscription)
    db.commit()

    return {
        "success": True,
        "message": "Payment successful!",
        "api_key": api_key
    }