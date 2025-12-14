from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException
)
from sqlalchemy.orm import Session
import os
import shutil
import uuid

from backend.database import get_db
from backend import crud, schemas

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)

# =========================
# UPLOAD DIRECTORY
# =========================
UPLOAD_DIR = "backend/uploads/items"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =========================
# CREATE ITEM (WITH IMAGE)
# =========================
@router.post("/", response_model=schemas.Item)
def create_item(
    name: str = Form(...),
    unit_price: float = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    image_filename = None

    if image:
        # generate unique filename
        ext = image.filename.split(".")[-1]
        image_filename = f"{uuid.uuid4()}.{ext}"

        file_path = os.path.join(UPLOAD_DIR, image_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    return crud.create_item(
        db=db,
        name=name,
        unit_price=unit_price,
        image=image_filename
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
def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    item = crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# =========================
# UPDATE ITEM
# =========================
@router.patch("/{item_id}", response_model=schemas.Item)
def update_item(
    item_id: int,
    name: str | None = Form(None),
    unit_price: float | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    image_filename = None

    if image:
        ext = image.filename.split(".")[-1]
        image_filename = f"{uuid.uuid4()}.{ext}"

        file_path = os.path.join(UPLOAD_DIR, image_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    item = crud.update_item(
        db=db,
        item_id=item_id,
        item_update=schemas.ItemUpdate(
            name=name,
            unit_price=unit_price
        ),
        image=image_filename
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item

# =========================
# DELETE ITEM
# =========================
@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = crud.delete_item(db, item_id)
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
