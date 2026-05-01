import requests # This is how services talk to each other!
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# URL of your other service (Use the public Render/AWS URL or Docker service name)
PRODUCT_SERVICE_URL = "http://product-service:8001" 
LAMBDA_URL = "https://your-lambda-url.aws.com/default/order-logger"

def get_db():
    db = database.SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/orders")
def create_order(product_id: int, quantity: int, db: Session = Depends(get_db)):
    # STEP 1: Call Product Service to see if the product exists
    response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
    
    if response.status_code != 200 or not response.json():
        raise HTTPException(status_code=404, detail="Product not found in Product Service")

    product_data = response.json()

    # STEP 2: Save the order to the Order Service database
    new_order = models.Order(product_id=product_id, quantity=quantity, total_price=product_data['price'] * quantity)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # STEP 3: Trigger Serverless Function (Event-Driven)
    # We "fire and forget" this message to our Lambda function
    try:
        requests.post(LAMBDA_URL, json={"order_id": new_order.id, "msg": "New Order Created!"})
    except:
        print("Lambda trigger failed, but order was still saved.")

    return {"message": "Order successful!", "order_details": new_order}