from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException
from .event_handler import publish_inventory
from .redis_cache import distributed_cache

def create_Product(db : Session, product : schemas.ProductCreate):
    db_product = db.query(models.Product).filter(models.Product.name == product.name).first()
    if db_product:
        raise HTTPException(status_code=400, detail="Producto ya existe")

    new_product = models.Product(name = product.name, stock = product.stock, price = product.price)    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    publish_inventory(new_product)
    return new_product

@distributed_cache(key_pattern="product_{product_id}")
def get_Product(db : Session, product_id : int):
    product =  db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

def update_Product(db : Session, product_id : int, product : schemas.ProductUpdate):
    db_product = get_Product(db, product_id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="No se encontro producto")
    
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
        publish_inventory(db_product)
    return db_product
        
def delete_Product(db : Session, product_id: int):
    db_product = get_Product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product

def get_inventory(db : Session, store_id : str):
    product = db.query(models.Product).all()
    return product