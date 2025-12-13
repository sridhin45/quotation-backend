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

from backend.database import get_db
from backend import crud, schemas

router = APIRouter(
    prefix="/quotations",
    tags=["Quotations"]
)

UPLOAD_DIR = "backend/uploads/items"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ======================================================
# CREATE QUOTATION (JSON + IMAGES FOR NEW ITEMS)
# ======================================================
@router.post("/", response_model=schemas.QuotationResponse)
def create_quotation(
    data: str = Form(...),                # JSON as string
    images: list[UploadFile] = File([]),  # optional images
    db: Session = Depends(get_db)
):
    quotation_data = schemas.QuotationCreate(**json.loads(data))

    image_map: dict[str, str] = {}

    for index, image in enumerate(images):
        path = os.path.join(UPLOAD_DIR, image.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_map[str(index)] = path

    return crud.create_quotation(db, quotation_data, image_map)


# ======================================================
# EDIT QUOTATION (JSON ONLY – SAFE, NO IMAGES)
# ======================================================
@router.patch("/{quotation_id}", response_model=schemas.QuotationResponse)
def edit_quotation(
    quotation_id: int,
    payload: schemas.QuotationUpdate,
    db: Session = Depends(get_db)
):
    quotation = crud.update_quotation(
        db=db,
        quotation_id=quotation_id,
        data=payload,
        image_map={}
    )

    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    return quotation


# ======================================================
# EDIT QUOTATION WITH IMAGE REPLACEMENT
# ======================================================
@router.patch("/{quotation_id}/images", response_model=schemas.QuotationResponse)
def edit_quotation_with_images(
    quotation_id: int,
    data: str = Form(...),
    images: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    # -------------------------
    # Validate JSON payload
    # -------------------------
    if not data.strip():
        raise HTTPException(
            status_code=400,
            detail="JSON data is required when uploading images"
        )

    try:
        payload_dict = json.loads(data)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format in data field"
        )

    payload = schemas.QuotationUpdate(**payload_dict)

    # -------------------------
    # Save images
    # -------------------------
    image_map: dict[str, str] = {}

    for index, image in enumerate(images):
        path = os.path.join(UPLOAD_DIR, image.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_map[str(index)] = path

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
def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db)
):
    success = crud.delete_quotation(db, quotation_id)
    if not success:
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
def get_quotation_by_id(
    quotation_id: int,
    db: Session = Depends(get_db)
):
    quotation = crud.get_quotation_by_id(db, quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation
