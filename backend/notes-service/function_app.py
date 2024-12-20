from database import init_db
from flask import Flask, request, jsonify # type: ignore
from operations.notes_crud import (
    create_note,
    get_all_notes,
    update_note,
    delete_note,
)

app = Flask(__name__)

init_db()

@app.route("/notes", methods=["POST"])
def create_note_handler():
    try:
        data = request.get_json()
        note = create_note(data["title"], data["content"])
        return jsonify({"id": note.id}), 201
    except Exception as e:
        return str(e), 500

@app.route("/notes", methods=["GET"])
def get_all_notes_handler():
    try:
        notes = get_all_notes()
        return jsonify([{
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        } for note in notes]), 200
    except Exception as e:
        return str(e), 500

@app.route("/notes/<int:id>", methods=["PUT"])
def update_note_handler(id):
    try:
        data = request.get_json()
        note = update_note(id, data["title"], data["content"])
        if note:
            return jsonify({
                "id": note.id,
                "title": note.title,
                "content": note.content
            }), 200
        return "Note not found", 404
    except Exception as e:
        return str(e), 500

@app.route("/notes/<int:id>", methods=["DELETE"])
def delete_note_handler(id):
    try:
        if delete_note(id):
            return "", 204
        return "Note not found", 404
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7071)
