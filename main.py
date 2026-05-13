from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database.db import engine
from models.models import Base
from routers import auth
from routers import apis

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Marketplace", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(apis.router)

@app.get("/")
def home():
    return {"message": "API Marketplace chal raha hai!"}

@app.get("/health")
def health():
    return {"status": "ok"}