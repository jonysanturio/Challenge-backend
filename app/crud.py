from . import schemas
from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models
from .event_handler import publish_inventory
from .redis_cache import distributed_cache
from .databases import redis_client

def create_Product(db: Session, product: schemas.ProductCreate):
    db_product = db.query(models.Product).filter(models.Product.name == product.name).first()
    if db_product:
        raise HTTPException(status_code=400, detail="Producto ya existe")

    new_product = models.Product(name=product.name, stock=product.stock, price=product.price)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    publish_inventory("create", new_product)
    return new_product


@distributed_cache(key_pattern="product_{product_id}")
def get_Product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

def update_Product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="No se encontro producto")

    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    try:
        redis_client.delete(f"product_{product_id}")
    except Exception:
        pass

    publish_inventory("update", db_product)
    return db_product

def delete_Product(db: Session, product_id: int):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(db_product)
    db.commit()

    try:
        redis_client.delete(f"product_{product_id}")
    except Exception:
        pass
    publish_inventory("delete", db_product)
    return db_product

def get_inventory(db: Session, store_id: str):
    return db.query(models.Product).all()