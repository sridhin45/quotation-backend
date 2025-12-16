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
from typing import List, Dict

import cloudinary.uploader
import backend.cloudinary_config  # loads config

from backend.database import get_db
from backend import crud, schemas

router = APIRouter(prefix="/quotations", tags=["Quotations"])


# ======================================================
# CREATE QUOTATION (JSON + IMAGES) — CLOUDINARY
# ======================================================
@router.post("/", response_model=schemas.QuotationResponse)
def create_quotation(
    data: str = Form(...),
    images: List[UploadFile] | None = File(None),
    db: Session = Depends(get_db)
):
    try:
        payload_dict = json.loads(data)
        quotation_data = schemas.QuotationCreate(**payload_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid quotation data: {e}")

    image_map: Dict[int, str] = {}

    # ✅ Upload images to Cloudinary
    if images:
        for index, image in enumerate(images):
            result = cloudinary.uploader.upload(
                image.file,
                folder="quotation/items"
            )
            image_map[index] = result["secure_url"]   # ✅ FULL URL

    # ---------- Validate & compute totals ----------
    for item in quotation_data.items:
        if not item.item_id and not item.item_name:
            raise HTTPException(
                status_code=400,
                detail="Each item must have either item_id or item_name"
            )

        if item.total is None:
            item.total = item.qty * item.price

    return crud.create_quotation(
        db=db,
        data=quotation_data,
        image_map=image_map
    )


# ======================================================
# UPDATE QUOTATION (JSON + IMAGES) — CLOUDINARY
# ======================================================
@router.patch("/{quotation_id}", response_model=schemas.QuotationResponse)
def edit_quotation(
    quotation_id: int,
    data: str = Form(...),
    images: List[UploadFile] | None = File(None),
    db: Session = Depends(get_db)
):
    try:
        payload_dict = json.loads(data)
        payload = schemas.QuotationUpdate(**payload_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid update data: {e}")

    image_map: Dict[int, str] = {}

    if images:
        for index, image in enumerate(images):
            result = cloudinary.uploader.upload(
                image.file,
                folder="quotation/items"
            )
            image_map[index] = result["secure_url"]   # ✅ FULL URL

    if payload.items:
        for item in payload.items:
            if not item.item_id and not item.item_name:
                raise HTTPException(
                    status_code=400,
                    detail="Each item must have either item_id or item_name"
                )

            if item.total is None:
                item.total = item.qty * item.price

    quotation = crud.update_quotation(
        db=db,
        quotation_id=quotation_id,
        data=payload,
        image_map=image_map
    )

    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    return quotation
