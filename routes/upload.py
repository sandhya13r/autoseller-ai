# routes/upload.py
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Item, User
from agent.orchestrator import start_pipeline
from utils.logger import log
import shutil, os, uuid

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_item(
    file:        UploadFile = File(...),
    seller_id:   str        = Form(...),
    description: str        = Form(""),
    db:          Session    = Depends(get_db)
):
    """
    Upload item image and start AI analysis pipeline.
    """
    try:
        # save uploaded image
        item_id   = str(uuid.uuid4())[:8].upper()
        ext       = file.filename.split(".")[-1]
        filename  = f"{item_id}.{ext}"
        filepath  = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)

        log("upload", f"Image saved: {filepath}")

        # start agent pipeline
        result = start_pipeline(item_id, filepath)

        if not result["success"]:
            return JSONResponse(
                status_code=500,
                content={"error": result.get("error")}
            )

        # save to database
        item = Item(
            id              = item_id,
            seller_id       = seller_id,
            image_url       = filepath,
            title           = result["item_data"].get("title"),
            category        = result["item_data"].get("category"),
            condition       = result["item_data"].get("condition"),
            estimated_price = result["asking_price"],
            min_price       = result["min_price"],
            agent_state     = result["state"],
            ai_analysis     = result["item_data"]
        )
        db.add(item)
        db.commit()

        return {
            "success":      True,
            "item_id":      item_id,
            "item_data":    result["item_data"],
            "listing_data": result["listing_data"],
            "platform":     result["platform"],
            "asking_price": result["asking_price"],
            "state":        result["state"]
        }

    except Exception as e:
        log("upload", f"❌ Upload failed: {e}", "ERROR")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )