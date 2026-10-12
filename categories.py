
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Product
from app.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ProductResponse,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.scalar(
        select(Category).where(Category.name == payload.name)
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="A category with this name already exists",
        )

    category = Category(**payload.model_dump())
    db.add(category)

    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A category with this name already exists",
        )

    return category


@router.get("", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.scalars(
        select(Category).order_by(Category.id)
    ).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    changes = payload.model_dump(exclude_unset=True)

    # Null values do not clear the category name.
    if changes.get("name") is None:
        changes.pop("name", None)

    if "name" in changes:
        duplicate = db.scalar(
            select(Category).where(
                Category.name == changes["name"],
                Category.id != category_id,
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="A category with this name already exists",
            )

    for field, value in changes.items():
        setattr(category, field, value)

    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not update category due to a constraint conflict",
        )

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    has_products = db.scalar(
        select(Product.id)
        .where(Product.category_id == category_id)
        .limit(1)
    )
    if has_products is not None:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a category that contains products",
        )

    db.delete(category)
    db.commit()
    return None


@router.get(
    "/{category_id}/products",
    response_model=list[ProductResponse],
)
def get_category_products(
    category_id: int,
    db: Session = Depends(get_db),
):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return db.scalars(
        select(Product)
        .where(Product.category_id == category_id)
        .order_by(Product.id)
    ).all()
