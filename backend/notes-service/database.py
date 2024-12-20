from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpass@db:5432/notesdb")
engine = create_engine(DATABASE_URL)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)
