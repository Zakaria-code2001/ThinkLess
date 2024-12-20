import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database import engine, Base
from models.note import Note

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def create_note(title: str, content: str):
    session = SessionLocal()
    try:
        note = Note(title=title, content=content)
        session.add(note)
        session.commit()
        session.refresh(note)  # Aggiorna l’oggetto con l’ID dal DB
        return note
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_note(note_id: int):
    session = SessionLocal()
    try:
        return session.query(Note).filter(Note.id == note_id).first()
    finally:
        session.close()


def get_all_notes():
    session = SessionLocal()
    try:
        return session.query(Note).all()
    finally:
        session.close()


def update_note(note_id: int, title: str, content: str):
    session = SessionLocal()
    try:
        note = session.query(Note).filter(Note.id == note_id).first()
        if note:
            note.title = title
            note.content = content
            session.commit()
        return note
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_note(note_id: int):
    session = SessionLocal()
    try:
        note = session.query(Note).filter(Note.id == note_id).first()
        if note:
            session.delete(note)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
