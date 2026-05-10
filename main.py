from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database.db import engine
from models.models import Base
from routers import auth, apis, subscriptions, gateway, analytics, payments, ai_insights

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Marketplace", version="1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                  allow_methods=["*"], allow_headers=["*"])

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(apis.router)
app.include_router(subscriptions.router)
app.include_router(gateway.router)
app.include_router(analytics.router)
app.include_router(payments.router)
app.include_router(ai_insights.router)

@app.get("/")
def home():
    return FileResponse("templates/index.html")

@app.get("/health")
def health():
    return {"status": "ok"}