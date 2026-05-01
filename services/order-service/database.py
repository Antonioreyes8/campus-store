from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the location of the SQLite database file
SQLALCHEMY_DATABASE_URL = "postgresql://campusadmin:MyStrongPassword123!@campus-store-aurora.cluster-c123456.us-east-2.rds.amazonaws.com:5432/campus_store_db"

# Create the engine to talk to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# This creates a "Session" class - each instance will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the base class our database models will inherit from
Base = declarative_base()