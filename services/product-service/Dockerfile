# Use a slim Python image to keep the container lightweight
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# We do this before copying the rest of the code to cache the layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual service code (including __init__.py, main.py, etc.)
COPY . .

# Expose the port the Product Service runs on
EXPOSE 8001

# Command to run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]