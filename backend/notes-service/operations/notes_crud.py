# operations/notes_crud.py
from database import SessionLocal
from models import Note


def create_note(title: str, content: str):
    session = SessionLocal()
    try:
        note = Note(title=title, content=content)
        session.add(note)
        session.commit()
        session.refresh(note)
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
