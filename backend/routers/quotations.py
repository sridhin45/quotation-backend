from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException
)
from sqlalchemy.orm import Session
import json
import os
import shutil
import uuid

from backend.database import get_db
from backend import crud, schemas

router = APIRouter(prefix="/quotations", tags=["Quotations"])

UPLOAD_DIR = "backend/uploads/items"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ======================================================
# CREATE QUOTATION (JSON + IMAGES)
# ======================================================
@router.post("/", response_model=schemas.QuotationResponse)
def create_quotation(
    data: str = Form(...),
    images: list[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    # ---------- Parse JSON safely ----------
    try:
        payload_dict = json.loads(data)
        quotation_data = schemas.QuotationCreate(**payload_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid quotation data: {e}")

    # ---------- Save images ----------
    image_map: dict[str, str] = {}

    for index, image in enumerate(images):
        ext = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        image_map[str(index)] = filename  # ✅ ONLY filename

    return crud.create_quotation(
        db=db,
        data=quotation_data,
        image_map=image_map
    )

# ======================================================
# UPDATE QUOTATION (JSON + OPTIONAL IMAGES)
# ======================================================
@router.patch("/{quotation_id}", response_model=schemas.QuotationResponse)
def edit_quotation(
    quotation_id: int,
    data: str = Form(...),
    images: list[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    try:
        payload_dict = json.loads(data)
        payload = schemas.QuotationUpdate(**payload_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid update data: {e}")

    image_map: dict[str, str] = {}

    for index, image in enumerate(images):
        ext = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        image_map[str(index)] = filename

    quotation = crud.update_quotation(
        db=db,
        quotation_id=quotation_id,
        data=payload,
        image_map=image_map
    )

    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    return quotation

# ======================================================
# DELETE QUOTATION
# ======================================================
@router.delete("/{quotation_id}")
def delete_quotation(quotation_id: int, db: Session = Depends(get_db)):
    if not crud.delete_quotation(db, quotation_id):
        raise HTTPException(status_code=404, detail="Quotation not found")
    return {"message": "Quotation deleted successfully"}

# ======================================================
# GET ALL QUOTATIONS
# ======================================================
@router.get("/", response_model=list[schemas.QuotationResponse])
def get_quotations(db: Session = Depends(get_db)):
    return crud.get_quotations(db)

# ======================================================
# GET QUOTATION BY ID
# ======================================================
@router.get("/{quotation_id}", response_model=schemas.QuotationResponse)
def get_quotation_by_id(quotation_id: int, db: Session = Depends(get_db)):
    quotation = crud.get_quotation_by_id(db, quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation
