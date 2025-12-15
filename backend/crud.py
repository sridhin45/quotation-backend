from sqlalchemy.orm import Session
from datetime import datetime

from backend import models, schemas


# =========================
# ITEM HELPERS
# =========================
def get_item_by_id(db: Session, item_id: int):
    return db.query(models.ItemMaster).filter(
        models.ItemMaster.id == item_id
    ).first()


def get_item_by_name(db: Session, name: str):
    return db.query(models.ItemMaster).filter(
        models.ItemMaster.name.ilike(name)
    ).first()


def get_items(db: Session):
    return db.query(models.ItemMaster).order_by(
        models.ItemMaster.name
    ).all()


def create_item(
    db: Session,
    name: str,
    unit_price: float,
    image: str | None = None
):
    item = models.ItemMaster(
        name=name,
        unit_price=unit_price,
        image=image
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# =========================
# CREATE QUOTATION
# =========================
def create_quotation(
    db: Session,
    data: schemas.QuotationCreate,
    image_map: dict
):
    quote_no = f"Q-{int(datetime.utcnow().timestamp())}"

    quotation = models.Quotation(
        quote_no=quote_no,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        salesman_name=data.salesman_name,
        tax=data.tax
    )
    db.add(quotation)
    db.commit()
    db.refresh(quotation)

    for index, q_item in enumerate(data.items):
        image_path = image_map.get(index)  # ✅ int key

        # Calculate total safely
        item_total = (
            q_item.total
            if q_item.total is not None
            else q_item.qty * q_item.price
        )

        # EXISTING ITEM
        if q_item.item_id:
            item = get_item_by_id(db, q_item.item_id)
            if not item:
                raise ValueError(f"Item ID {q_item.item_id} not found")

        # NEW ITEM
        else:
            item = get_item_by_name(db, q_item.item_name)
            if not item:
                item = create_item(
                    db=db,
                    name=q_item.item_name,
                    unit_price=q_item.price,
                    image=image_path
                )

        qi = models.QuotationItem(
            quotation_id=quotation.id,
            item_id=item.id,
            qty=q_item.qty,
            price=q_item.price,
            total=item_total
        )
        db.add(qi)

    db.commit()
    db.refresh(quotation)
    return quotation


# =========================
# UPDATE QUOTATION
# =========================
def update_quotation(
    db: Session,
    quotation_id: int,
    data: schemas.QuotationUpdate,
    image_map: dict
):
    quotation = get_quotation_by_id(db, quotation_id)
    if not quotation:
        return None

    # Update header
    for field, value in data.dict(
        exclude_unset=True,
        exclude={"items"}
    ).items():
        setattr(quotation, field, value)

    # Replace items
    if data.items is not None:
        db.query(models.QuotationItem).filter(
            models.QuotationItem.quotation_id == quotation.id
        ).delete()

        for index, q_item in enumerate(data.items):
            image_path = image_map.get(index)

            item_total = (
                q_item.total
                if q_item.total is not None
                else q_item.qty * q_item.price
            )

            if q_item.item_id:
                item = get_item_by_id(db, q_item.item_id)
                if not item:
                    raise ValueError(f"Item ID {q_item.item_id} not found")

                if q_item.replace_image and image_path:
                    item.image = image_path
                    item.unit_price = q_item.price

            else:
                item = get_item_by_name(db, q_item.item_name)
                if not item:
                    item = create_item(
                        db=db,
                        name=q_item.item_name,
                        unit_price=q_item.price,
                        image=image_path
                    )

            qi = models.QuotationItem(
                quotation_id=quotation.id,
                item_id=item.id,
                qty=q_item.qty,
                price=q_item.price,
                total=item_total
            )
            db.add(qi)

    db.commit()
    db.refresh(quotation)
    return quotation


# =========================
# GET QUOTATIONS
# =========================
def get_quotations(db: Session):
    return (
        db.query(models.Quotation)
        .order_by(models.Quotation.id.desc())
        .all()
    )


def get_quotation_by_id(db: Session, quotation_id: int):
    return (
        db.query(models.Quotation)
        .filter(models.Quotation.id == quotation_id)
        .first()
    )


# =========================
# DELETE QUOTATION
# =========================
def delete_quotation(db: Session, quotation_id: int):
    quotation = get_quotation_by_id(db, quotation_id)
    if not quotation:
        return None

    db.delete(quotation)
    db.commit()
    return True
# =========================
# DELETE ITEM
# =========================
def delete_item(db: Session, item_id: int):
    item = get_item_by_id(db, item_id)
    if not item:
        return None

    # Check if item is still used in quotation items
    used = db.query(models.QuotationItem).filter(
        models.QuotationItem.item_id == item_id
    ).first()

    if used:
        raise ValueError("Item used in quotation")

    db.delete(item)
    db.commit()
    return True
