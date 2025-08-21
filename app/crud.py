from sqlalchemy.orm import Session
from sqlalchemy import update
from fastapi import HTTPException
from . import models, schemas
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
    data = product.model_dump(exclude_unset=True)
    expected_version = data.pop("version", None)
    if expected_version is None:
        raise HTTPException(status_code=400, detail="Falta 'version' en el cuerpo")
    allowed = {k: v for k, v in data.items() if k in {"stock", "price"}}
    if not allowed:
        obj = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return obj
    lock = None
    try:
        try:
            lock = redis_client.lock(
                f"product:{product_id}:lock", timeout=5, blocking_timeout=1
            )
            if not lock.acquire(blocking=True):
                raise HTTPException(status_code=423, detail="Reintentar: recurso bloqueado")
        except Exception:
            lock = None
        stmt = (
            update(models.Product)
            .where(models.Product.id == product_id, models.Product.version == expected_version)
            .values(**allowed, version=models.Product.version + 1)
            .execution_options(synchronize_session=False)
        )
        result = db.execute(stmt)
        if result.rowcount == 0:
            db.rollback()
            exists = db.query(models.Product.id).filter(models.Product.id == product_id).first()
            if not exists:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            raise HTTPException(status_code=409, detail="Conflicto de versión. Refrescar y reintentar.")
        db.commit()
        obj = db.query(models.Product).filter(models.Product.id == product_id).first()
        try:
            redis_client.delete(f"product_{product_id}")
        except Exception:
            pass
        publish_inventory("update", obj)
        return obj
    finally:
        if lock:
            try:
                lock.release()
            except Exception:
                pass

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