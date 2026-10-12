
from math import isfinite

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Product
from app.schemas import (
    InventoryValueResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    category = db.get(Category, payload.category_id)
    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found. Create the category first.",
        )

    product = Product(**payload.model_dump())
    db.add(product)

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Could not create product because of a database constraint",
        )

    return product


@router.get("", response_model=list[ProductResponse])
def get_products(
    category_id: int | None = Query(default=None, gt=0),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    search: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
):
    if min_price is not None and not isfinite(min_price):
        raise HTTPException(status_code=422, detail="min_price must be finite")
    if max_price is not None and not isfinite(max_price):
        raise HTTPException(status_code=422, detail="max_price must be finite")
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=422,
            detail="min_price cannot be greater than max_price",
        )

    statement = select(Product)

    if category_id is not None:
        statement = statement.where(Product.category_id == category_id)

    if min_price is not None:
        statement = statement.where(Product.price >= min_price)

    if max_price is not None:
        statement = statement.where(Product.price <= max_price)

    if search is not None:
        # Treat %, _ and backslash as literal search characters.
        escaped_search = (
            search.strip()
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        if not escaped_search:
            raise HTTPException(
                status_code=422,
                detail="Search text cannot be empty",
            )
        statement = statement.where(
            Product.name.ilike(f"%{escaped_search}%", escape="\\")
        )

    return db.scalars(statement.order_by(Product.id)).all()


@router.get(
    "/inventory-value",
    response_model=InventoryValueResponse,
)
def get_inventory_value(db: Session = Depends(get_db)):
    total = db.scalar(
        select(
            func.coalesce(
                func.sum(Product.price * Product.quantity), 0.0
            )
        )
    )
    count = db.scalar(select(func.count(Product.id)))

    return {
        "total_inventory_value": round(float(total), 2),
        "product_count": count or 0,
    }


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    changes = payload.model_dump(exclude_unset=True)

    # Treat explicitly supplied nulls as unchanged for required fields.
    for field in ("name", "category_id", "price", "quantity"):
        if field in changes and changes[field] is None:
            changes.pop(field)

    if "category_id" in changes:
        category = db.get(Category, changes["category_id"])
        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found. Product category was not updated.",
            )

    for field, value in changes.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Could not update product due to a database constraint",
        )

    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return None
