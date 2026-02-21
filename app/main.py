from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, database

# Create the database tables if they don't exist yet
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency to get a database session for each request
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. ROOT ENDPOINT: Returns a welcome message
@app.get("/")
def read_root():
    return {"message": "Welcome to the Campus Store Online API!"}

# 2. CREATE PRODUCT: Adds a new product to the database
@app.post("/products")
def create_product(name: str, price: float, db: Session = Depends(get_db)):
    new_product = models.Product(name=name, price=price)
    db.add(new_product)
    db.commit()
    db.refresh(new_product) # Get the generated ID back
    return new_product

# 3. GET ALL PRODUCTS: Retrieves everything stored
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products