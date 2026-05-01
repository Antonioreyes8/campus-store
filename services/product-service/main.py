from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, database

# Create the tables (specifically the Product table)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"service": "Product Service", "status": "Online"}

@app.post("/products")
def create_product(name: str, price: float, db: Session = Depends(get_db)):
    new_product = models.Product(name=name, price=price)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    # The Order Service will call this endpoint to check if a product exists!
    return db.query(models.Product).filter(models.Product.id == product_id).first()