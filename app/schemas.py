from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    stock: int
    price: float

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    stock: Optional[int] = None
    price: Optional[float] = None
    version : int
    model_config = {"extra" : "forbid"}

class ProductResponse(ProductBase):
    id: int
    version : int
    model_config = {"from_attributes": True} 
