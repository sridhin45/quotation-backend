from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# =========================
# ITEM SCHEMAS (ITEM MASTER)
# =========================
class ItemBase(BaseModel):
    name: str
    unit_price: float


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    unit_price: Optional[float] = None


class Item(ItemBase):
    id: int
    image: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


# =========================
# QUOTATION ITEM (CREATE / EDIT)
# =========================
class QuotationItemAuto(BaseModel):
    item_id: Optional[int] = None
    item_name: Optional[str] = None
    qty: int
    price: float
    total: Optional[float] = None
    replace_image: Optional[bool] = False


# =========================
# QUOTATION CREATE
# =========================
class QuotationCreate(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    salesman_name: str
    tax: float = 0
    items: List[QuotationItemAuto]


# =========================
# QUOTATION UPDATE
# =========================
class QuotationUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    salesman_name: Optional[str] = None
    tax: Optional[float] = None
    items: Optional[List[QuotationItemAuto]] = None


# =========================
# RESPONSE SCHEMAS
# =========================
class QuotationItemResponse(BaseModel):
    id: int
    qty: int
    price: float
    total: float
    item: Item

    model_config = {
        "from_attributes": True
    }


class QuotationResponse(BaseModel):
    id: int
    quote_no: str
    customer_name: str
    customer_phone: Optional[str]
    salesman_name: str
    tax: float
    created_at: datetime
    items: List[QuotationItemResponse]

    model_config = {
        "from_attributes": True
    }


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = {
        "from_attributes": True
    }
