# app.py
import sys
import os
from fastapi import FastAPI
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi.staticfiles import StaticFiles
app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from config import validate_config
from database.db import init_db
from routes import upload, agent, chat, delivery, payment
from utils.logger import log

# ──────────────────────────────────────────
# LIFESPAN
# ──────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── startup
    log("app", "🚀 AutoSeller AI starting up...")
    validate_config()
    init_db()
    log("app", "✅ Ready!", "SUCCESS")
    yield
    # ── shutdown
    log("app", "👋 AutoSeller AI shutting down")

# ──────────────────────────────────────────
# APP INIT
# ──────────────────────────────────────────
app = FastAPI(
    title       = "AutoSeller AI",
    description = "Autonomous commerce agent — From Snapshot to Settlement",
    version     = "1.0.0",
    lifespan    = lifespan
)

# ── CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Static files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# ── Templates
templates = Jinja2Templates(directory="templates")

# ──────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────
app.include_router(upload.router)
app.include_router(agent.router)
app.include_router(chat.router)
app.include_router(delivery.router)
app.include_router(payment.router)

# ──────────────────────────────────────────
# PAGE ROUTES
# ──────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/dashboard/{item_id}", response_class=HTMLResponse)
async def dashboard(request: Request, item_id: str):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "item_id": item_id}
    )

@app.get("/marketplace/{item_id}", response_class=HTMLResponse)
async def marketplace(request: Request, item_id: str):
    return templates.TemplateResponse(
        "marketplace.html",
        {"request": request, "item_id": item_id}
    )

@app.get("/chat/{item_id}", response_class=HTMLResponse)
async def chat_page(request: Request, item_id: str):
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "item_id": item_id, "role": "buyer"}
    )

@app.get("/tracking/{item_id}", response_class=HTMLResponse)
async def tracking(request: Request, item_id: str):
    return templates.TemplateResponse(
        "tracking.html",
        {"request": request, "item_id": item_id}
    )

# ──────────────────────────────────────────
# HEALTH CHECK
# ──────────────────────────────────────────
@app.get("/health")
async def health():
    """Quick health check endpoint."""
    import config
    return {
        "status":  "healthy",
        "mode":    config.APP_MODE,
        "version": "1.0.0"
    }

# ──────────────────────────────────────────
# RUN
# ──────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host   = "0.0.0.0",
        port   = 8000,
        reload = True
    )
    # app.py

@app.get("/")
async def read_index():
    # This serves your initial upload page
    return FileResponse("templates/index.html")