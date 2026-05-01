from sqlalchemy import Column, Integer, Float, String
from .database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)  # Reference to the Product ID from the other service
    quantity = Column(Integer)
    total_price = Column(Float)