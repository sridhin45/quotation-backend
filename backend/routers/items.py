from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException
)
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import crud, schemas

import cloudinary.uploader
import backend.cloudinary_config  # loads Cloudinary config


router = APIRouter(
    prefix="/items",
    tags=["Items"]
)


# =========================
# CREATE ITEM (CLOUDINARY)
# =========================
@router.post("/", response_model=schemas.Item)
def create_item(
    name: str = Form(...),
    unit_price: float = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    image_url = None

    if image:
        try:
            result = cloudinary.uploader.upload(
                image.file,
                folder="quotation/items"
            )
            image_url = result["secure_url"]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Cloudinary upload failed: {e}"
            )

    return crud.create_item(
        db=db,
        name=name,
        unit_price=unit_price,
        image=image_url
    )


# =========================
# GET ALL ITEMS
# =========================
@router.get("/", response_model=list[schemas.Item])
def get_items(db: Session = Depends(get_db)):
    return crud.get_items(db)


# =========================
# GET SINGLE ITEM
# =========================
@router.get("/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# =========================
# UPDATE ITEM (CLOUDINARY)
# =========================
@router.patch("/{item_id}", response_model=schemas.Item)
def update_item(
    item_id: int,
    name: str | None = Form(None),
    unit_price: float | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    image_url = None

    if image:
        try:
            result = cloudinary.uploader.upload(
                image.file,
                folder="quotation/items"
            )
            image_url = result["secure_url"]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Cloudinary upload failed: {e}"
            )

    item = crud.update_item(
        db=db,
        item_id=item_id,
        item_data=schemas.ItemUpdate(
            name=name,
            unit_price=unit_price
        ),
        image=image_url
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


# =========================
# DELETE ITEM
# =========================
@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    try:
        result = crud.delete_item(db, item_id)
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")

        return {"message": "Item deleted successfully"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
