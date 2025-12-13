from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil

from backend.database import get_db
from backend import crud, schemas

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)

UPLOAD_DIR = "backend/uploads/items"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================
# CREATE ITEM (WITH IMAGE)
# =========================
@router.post("/", response_model=schemas.Item)
def create_item(
    name: str,
    unit_price: float,
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    image_path = None

    if image:
        file_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = file_path

    # ✅ UPDATED CALL (matches new crud.create_item signature)
    return crud.create_item(
        db=db,
        name=name,
        unit_price=unit_price,
        image=image_path
    )


# =========================
# GET ALL ITEMS
# =========================
@router.get("/", response_model=list[schemas.Item])
def get_items(db: Session = Depends(get_db)):
    return crud.get_items(db)


@router.patch("/{item_id}", response_model=schemas.Item)
def edit_item(
    item_id: int,
    name: str | None = None,
    unit_price: float | None = None,
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    image_path = None

    if image:
        file_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = file_path

    item = crud.update_item(
        db,
        item_id,
        schemas.ItemUpdate(name=name, unit_price=unit_price),
        image=image_path
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item
from fastapi import HTTPException

from fastapi import HTTPException

@router.get("/{item_id}", response_model=schemas.Item)
def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    item = crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    try:
        result = crud.delete_item(db, item_id)
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
