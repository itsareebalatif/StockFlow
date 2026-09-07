# StockFlow

# StockFlow

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.0+-e92063.svg)](https://docs.pydantic.dev/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![uv](https://img.shields.io/badge/uv-Astral-purple.svg)](https://docs.astral.sh/uv/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

Containerized with **Docker** and packaged with Astral's **`uv`**, the service provides fast cold starts, deterministic builds, and role-based access control (RBAC).

---

## Architecture & Relational Schema

StockFlow uses a 9-table normalized relational model designed to prevent split-brain inventory states and preserve immutable transaction ledgers:

```text
+------------------+       +-------------------------+       +--------------------+
|      USERS       |       |       CATEGORIES        |       |     SUPPLIERS      |
+------------------+       +-------------------------+       +--------------------+
| id (PK, UUID)    |       | id (PK, UUID)           |       | id (PK, UUID)      |
| email (Unique)   |       | name (Unique)           |       | name               |
| hashed_password  |       | description             |       | contact_name       |
| role (Enum)      |       | created_at, updated_at  |       | email, phone       |
| is_active (Bool) |       +-------------------------+       | address            |
| created_at       |                    |                    | created_at         |
+------------------+                    | 1:N                +--------------------+
     |          |                       v                              | 1:N
     | 1:N      | 1:N         +--------------------+                   |
     |          |             |      PRODUCTS      |                   v
     |          |             +--------------------+       +-------------------------+
     |          |             | id (PK, UUID)      |<------|     PURCHASE_ORDERS     |
     |          |             | category_id (FK)   |       +-------------------------+
     |          |             | name               |       | id (PK, UUID)           |
     |          |             | sku (Unique)       |       | supplier_id (FK)        |
     |          |             | description        |       | user_id (FK - Business) |
     |          |             | price (Numeric)    |       | status (Enum)           |
     |          |             | status (Enum)      |       | total_amount (Numeric)  |
     |          |             | created_at         |       | created_at, updated_at  |
     |          |             +--------------------+       +-------------------------+
     |          |               | 1:1        | 1:N                      | 1:N
     |          |               v            v                          v
     |          |      +-------------+  +-------------+    +-------------------------+
     |          |      |  INVENTORY  |  | ORDER_ITEMS |    |   PURCHASE_ORDER_ITEMS  |
     |          |      +-------------+  +-------------+    +-------------------------+
     |          |      | id (PK)     |  | id (PK)     |    | id (PK, UUID)           |
     |          |      | product_id  |  | order_id(FK)|    | purchase_order_id (FK)  |
     |          |      | quantity    |  | product_id  |    | product_id (FK)         |
     |          |      | updated_at  |  | quantity    |    | quantity (Int)          |
     |          |      +-------------+  | unit_price  |    | unit_cost (Numeric)     |
     |          |                       +-------------+    +-------------------------+
     |          v                              ^
     |   +-------------------------+           |
     +-->|         ORDERS          |-----------+ 1:N
         +-------------------------+
         | id (PK, UUID)           |
         | customer_id (FK - User) |
         | status (Enum)           |
         | total_amount (Numeric)  |
         | created_at, updated_at  |
         +-------------------------+


# Database Migration:
uv run alembic upgrade head

## To autogenerate a new revision after modifying models in app/models/:

uv run alembic revision --autogenerate -m "describe_migration_here"
uv run alembic upgrade head

#Build the Docker Image:
docker build -t stockflow-api 

#Run the Container:
docker run -d \
  --name stockflow \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  stockflow-api

  
