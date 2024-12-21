from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.todos import router as todos_router
from fastapi.responses import FileResponse

app = FastAPI()

# Allow all origins, or replace '*' with specific domains like 'http://localhost:3000' if you want to restrict it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with specific domains for security
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
    # You can provide your own favicon.ico file path
    return FileResponse("/path/to/your/favicon.ico")
