
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app import models  # Import models before create_all
from app.routers import categories, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Product Inventory Management API",
    description=(
        "REST API for categories and products using FastAPI, "
        "SQLAlchemy ORM, and SQLite."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(categories.router)
app.include_router(products.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Product Inventory Management API is running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
