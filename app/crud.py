from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException

def create_Product(db : Session, product : schemas.ProductCreate):
    db_product = db.query(models.Product).filter(models.Product.name == product.name).first()
    if db_product:
        raise HTTPException(status_code=404, detail="Producto ya existe")

    new_product = models.Product(name = product.name, stock = product.stock, price = product.price)    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

def get_Product(db : Session, product_id : int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def update_Product(db : Session, product_id : int, product : schemas.ProductUpdate):
    db_product = get_Product(db, product_id)
    if db_product:
        db_product.stock = product.stock
        db_product.price = product.price
        db.commit()
        db.refresh(db_product)
    return db_product
        
def delete_Product(db : Session, product_id: int):
    db_product = get_Product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product

    