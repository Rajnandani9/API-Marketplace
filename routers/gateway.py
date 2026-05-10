from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx
import time
from database.db import get_db
from models.models import Subscription, UsageLog, API

router = APIRouter(prefix="/gateway", tags=["Gateway"])

@router.api_route("/{api_id}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(api_id: int, path: str, api_key: str, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(
        Subscription.api_key == api_key,
        Subscription.api_id == api_id,
        Subscription.is_active == True
    ).first()
    if not sub:
        raise HTTPException(status_code=403, detail="Invalid API key or not subscribed")

    api = db.query(API).filter(API.id == api_id).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    url = f"{api.base_url}/{path}"
    start_time = time.time()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            status_code = response.status_code
            result = response.json()
    except Exception:
        status_code = 500
        result = {"error": "Could not reach target API"}

    response_time = time.time() - start_time

    log = UsageLog(
        api_id=api_id,
        api_key=api_key,
        endpoint=path,
        status_code=status_code,
        response_time=round(response_time, 3)
    )
    db.add(log)
    db.commit()

    return {
        "status_code": status_code,
        "response_time": response_time,
        "data": result
    }