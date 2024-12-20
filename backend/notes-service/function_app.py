from flask import Flask, request, jsonify
from flasgger import Swagger
from operations.notes_crud import (
    create_note,
    get_all_notes,
    update_note,
    delete_note,
)
from database import init_db, engine

app = Flask(__name__)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Notes API",
        "description": "API per gestire le note",
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "tags": [{"name": "Notes", "description": "Operazioni sulle note"}],
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

init_db()


@app.route("/notes", methods=["POST"])
def create_note_handler():
    """
    Crea una nuova nota
    ---
    tags:
      - Notes
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            content:
              type: string
    responses:
      201:
        description: Nota creata con successo
        schema:
          type: object
          properties:
            id:
              type: integer
      500:
        description: Errore interno del server
    """
    try:
        data = request.get_json()
        note = create_note(data["title"], data["content"])
        return jsonify({"id": note.id}), 201
    except Exception as e:
        return str(e), 500


@app.route("/notes", methods=["GET"])
def get_all_notes_handler():
    """
    Ottiene tutte le note
    ---
    tags:
      - Notes
    responses:
      200:
        description: Lista delle note
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              content:
                type: string
              created_at:
                type: string
              updated_at:
                type: string
      500:
        description: Errore interno del server
    """
    try:
        notes = get_all_notes()
        return (
            jsonify(
                [
                    {
                        "id": note.id,
                        "title": note.title,
                        "content": note.content,
                        "created_at": note.created_at.isoformat(),
                        "updated_at": note.updated_at.isoformat(),
                    }
                    for note in notes
                ]
            ),
            200,
        )
    except Exception as e:
        return str(e), 500


@app.route("/notes/<int:id>", methods=["PUT"])
def update_note_handler(id):
    """
    Aggiorna una nota esistente
    ---
    tags:
      - Notes
    parameters:
      - in: path
        name: id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            content:
              type: string
    responses:
      200:
        description: Nota aggiornata con successo
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            content:
              type: string
      404:
        description: Nota non trovata
      500:
        description: Errore interno del server
    """
    try:
        data = request.get_json()
        note = update_note(id, data["title"], data["content"])
        if note:
            return (
                jsonify({"id": note.id, "title": note.title, "content": note.content}),
                200,
            )
        return "Note not found", 404
    except Exception as e:
        return str(e), 500


@app.route("/notes/<int:id>", methods=["DELETE"])
def delete_note_handler(id):
    """
    Elimina una nota
    ---
    tags:
      - Notes
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      204:
        description: Nota eliminata con successo
      404:
        description: Nota non trovata
      500:
        description: Errore interno del server
    """
    try:
        if delete_note(id):
            return "", 204
        return "Note not found", 404
    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7071)
