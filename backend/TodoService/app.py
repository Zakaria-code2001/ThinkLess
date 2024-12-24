from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.todos import router as todos_router
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Allow CORS from your frontend (Vite running on http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow only your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods, including OPTIONS
    allow_headers=["*"],  # Allow all headers
)

# Root endpoint to avoid 404 for '/'
@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo API"}

# Include the todos router
app.include_router(todos_router, prefix="/api/v1")

@app.get("/favicon.ico")
def favicon():
    # This points to the static directory inside the TodoService folder
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "favicon.ico"))
