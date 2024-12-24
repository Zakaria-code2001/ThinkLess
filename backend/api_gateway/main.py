from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

# Set the base URLs of the TodoService and NotesService
TODO_SERVICE_URL = "http://localhost:8001"  # Update with actual URL if different
NOTES_SERVICE_URL = "http://localhost:8002"  # Update with actual URL if different

@app.get("/todos")
async def get_todos():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TODO_SERVICE_URL}/api/v1/todos")
        return JSONResponse(content=response.json())

@app.get("/notes")
async def get_notes():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{NOTES_SERVICE_URL}/api/v1/notes")
        return JSONResponse(content=response.json())
