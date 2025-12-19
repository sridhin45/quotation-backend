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
import backend.cloudinary_config

from backend.database import get_db
from backend import crud, schemas

router = APIRouter(prefix="/quotations", tags=["Quotations"])


# ======================================================
# CREATE QUOTATION
# ======================================================
@router.post("/", response_model=schemas.QuotationResponse)
def create_quotation(
    data: str = Form(...),
    images: List[UploadFile] | None = File(None),
    db: Session = Depends(get_db)
):
    payload = schemas.QuotationCreate(**json.loads(data))

    image_map: Dict[int, str] = {}
    image_index = 0

    if images:
        for idx, item in enumerate(payload.items):
            # upload ONLY for manually added items
            if not item.item_id:
                result = cloudinary.uploader.upload(
                    images[image_index].file,
                    folder="quotation/items"
                )
                image_map[idx] = result["secure_url"]
                image_index += 1

    for item in payload.items:
        if item.total is None:
            item.total = item.qty * item.price

    return crud.create_quotation(db, payload, image_map)


# ======================================================
# UPDATE QUOTATION
# ======================================================
@router.patch("/{quotation_id}", response_model=schemas.QuotationResponse)
def update_quotation(
    quotation_id: int,
    data: str = Form(...),
    images: List[UploadFile] | None = File(None),
    db: Session = Depends(get_db)
):
    payload = schemas.QuotationUpdate(**json.loads(data))

    image_map: Dict[int, str] = {}
    image_index = 0

    if images and payload.items:
        for idx, item in enumerate(payload.items):
            if not item.item_id:
                result = cloudinary.uploader.upload(
                    images[image_index].file,
                    folder="quotation/items"
                )
                image_map[idx] = result["secure_url"]
                image_index += 1

    quotation = crud.update_quotation(db, quotation_id, payload, image_map)

    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    return quotation


# ======================================================
# GET ALL
# ======================================================
@router.get("/", response_model=List[schemas.QuotationResponse])
def get_quotations(db: Session = Depends(get_db)):
    return crud.get_quotations(db)


# ======================================================
# GET BY ID
# ======================================================
@router.get("/{quotation_id}", response_model=schemas.QuotationResponse)
def get_quotation(quotation_id: int, db: Session = Depends(get_db)):
    quotation = crud.get_quotation_by_id(db, quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation


# ======================================================
# DELETE
# ======================================================
@router.delete("/{quotation_id}")
def delete_quotation(quotation_id: int, db: Session = Depends(get_db)):
    if not crud.delete_quotation(db, quotation_id):
        raise HTTPException(status_code=404, detail="Quotation not found")
    return {"message": "Quotation deleted"}
