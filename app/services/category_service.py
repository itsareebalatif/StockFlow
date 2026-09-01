import uuid
from fastapi import HTTPException,status,status
from sqlalchemy import delete
from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

def get_categories(db: Session) -> list[Category]:
    return db.query(Category).all()

def get_category_by_id(db:Session, category_id:uuid.UUID)-> Category:
    category = db.query(Category).filter(category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )    
    return category

def create_category(db: Session,data: CategoryCreate) -> Category:
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already existed"
        )
    category= Category(name=data.name, description=data.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def update_category(
    db:Session,category_id:uuid.UUID, data:CategoryUpdate)-> Category:
    category=get_category_by_id(db, category_id)
    if data.name is not None:
        category.name = data.name
    if data.description is not None:
        category.description= data.description

    db.commit()
    db.refresh(category)
    return category

def delete_category(db: Session, category_id: uuid.UUID)->None:
    category = get_category_by_id(db, category_id)
    db.delete(category)
    db.commit()
