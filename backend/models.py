from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database import Base


# =========================
# ITEM MASTER
# =========================
class ItemMaster(Base):
    __tablename__ = "item_master"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    unit_price = Column(Float, nullable=False)
    image = Column(String, nullable=True)

    # ❌ NO CASCADE HERE
    quotation_items = relationship(
        "QuotationItem",
        back_populates="item"
    )


# =========================
# QUOTATION
# =========================
class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(Integer, primary_key=True, index=True)
    quote_no = Column(String, unique=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=True)
    salesman_name = Column(String, nullable=False)
    tax = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ DELETE QUOTATION → DELETE ITEMS
    items = relationship(
        "QuotationItem",
        back_populates="quotation",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


# =========================
# QUOTATION ITEMS
# =========================
class QuotationItem(Base):
    __tablename__ = "quotation_items"

    id = Column(Integer, primary_key=True, index=True)

    # ✅ CASCADE ONLY FROM QUOTATION
    quotation_id = Column(
        Integer,
        ForeignKey("quotations.id", ondelete="CASCADE"),
        nullable=False
    )

    # ❌ DO NOT CASCADE FROM ITEM
    item_id = Column(
        Integer,
        ForeignKey("item_master.id"),
        nullable=False
    )

    qty = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    quotation = relationship("Quotation", back_populates="items")
    item = relationship("ItemMaster", back_populates="quotation_items")
