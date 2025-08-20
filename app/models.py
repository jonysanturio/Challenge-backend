from sqlalchemy import Integer, String, Column, Float
from .databases import base

class Product(base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    stock = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)



