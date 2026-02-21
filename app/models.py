from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Product(Base):
    __tablename__ = "products" # The name of the table in SQLite

    id = Column(Integer, primary_key=True, index=True) # Unique ID for each product
    name = Column(String)                             # Name of the product
    price = Column(Float)                              # Price as a decimal/float