from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the location of the SQLite database file
# This uses a local file instead of a remote AWS server
SQLALCHEMY_DATABASE_URL = "sqlite:///./campus_store.db"

# Create the engine to talk to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# This creates a "Session" class - each instance will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the base class our database models will inherit from
Base = declarative_base()