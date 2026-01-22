from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import shutil
import os

from utils import extract_amounts_pipeline

app = FastAPI(
    title="AI-Powered Amount Detection API",
    description="Extracts financial amounts from medical bills (text or image)",
    version="1.0",
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/extract-amounts")
async def extract_amounts(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    if not text and not file:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "reason": "Either text or image file is required",
            },
        )

    file_path = None

    try:
        if file:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        result = extract_amounts_pipeline(
            text=text,
            file=file_path,
        )

        return result

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "reason": str(e)},
        )

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
