
# Product Inventory Management API

A REST API built with FastAPI, SQLAlchemy ORM, Pydantic, and SQLite.

## Features

- Category CRUD operations
- Product CRUD operations
- SQLAlchemy one-to-many relationships
- Pydantic request validation
- Duplicate category detection
- Product category reference validation
- Product filtering by category and price
- Product name search
- Category-specific product listing
- Total inventory value calculation
- Proper HTTP errors and status codes
- Swagger UI and Postman collection
- Automated tests with pytest

## Requirements

- Python 3.10 or later
- pip

## Installation

Open CMD in the project root.

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run the application

```cmd
uvicorn app.main:app --reload
```

The SQLite database file `inventory.db` is created automatically
in the project root when the application starts.

## API documentation

Swagger UI:
http://127.0.0.1:8000/docs

ReDoc:
http://127.0.0.1:8000/redoc

Health check:
http://127.0.0.1:8000/health

## Category APIs

| Method | Endpoint |
|---|---|
| POST | /categories |
| GET | /categories |
| GET | /categories/{category_id} |
| PUT | /categories/{category_id} |
| DELETE | /categories/{category_id} |
| GET | /categories/{category_id}/products |

## Product APIs

| Method | Endpoint |
|---|---|
| POST | /products |
| GET | /products |
| GET | /products/{product_id} |
| PUT | /products/{product_id} |
| DELETE | /products/{product_id} |
| GET | /products/inventory-value |

## Product filtering examples

Filter by category:
`GET /products?category_id=1`

Filter by price:
`GET /products?min_price=100&max_price=1000`

Search by name:
`GET /products?search=laptop`

Combine filters:
`GET /products?category_id=1&min_price=100&max_price=1000&search=laptop`

## Sample category request

POST /categories

```json
{
  "name": "Electronics",
  "description": "Electronic products"
}
```

## Sample product request

POST /products

```json
{
  "name": "Laptop",
  "description": "Business laptop",
  "category_id": 1,
  "price": 750,
  "quantity": 10
}
```

## Inventory calculation

Inventory value is calculated as:

`SUM(product.price * product.quantity)`

GET /products/inventory-value

Example response:

```json
{
  "total_inventory_value": 7500.0,
  "product_count": 1
}
```

## HTTP status codes

- 200: Request successful
- 201: Resource created
- 204: Resource deleted
- 400: Database constraint error
- 404: Resource or category not found
- 409: Duplicate category or category has products
- 422: Request validation error

## Run automated tests

```cmd
python -m pytest -v
```

## Postman

Import `postman_collection.json` into Postman.
Start the API before executing the collection.

## Database design

`categories.id` is the primary key.

`products.category_id` is a foreign key referencing
`categories.id`.

One category can contain many products. A category with
existing products cannot be deleted.

## Notes

SQLAlchemy ORM is used for all application data operations.
SQLite is used for persistent storage. The database tables
are created automatically during application startup.
