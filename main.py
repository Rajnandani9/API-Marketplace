<<<<<<< HEAD
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from database.db import engine
from models.models import Base
from routers import auth, apis, subscriptions, gateway, analytics, payments, ai_insights

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Marketplace", version="1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                  allow_methods=["*"], allow_headers=["*"])

# Static files — only mount if directory exists
if os.path.exists("static"):
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
    if os.path.exists("templates/index.html"):
        return FileResponse("templates/index.html")
    return HTMLResponse("<h1>API Marketplace Running!</h1>")

@app.get("/health")
def health():
    return {"status": "ok"}
=======
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
>>>>>>> 68175c670b8e573bfef8f6f0beca6246581e9c68
