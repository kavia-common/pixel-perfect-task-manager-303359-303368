from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.db import init_engine
from src.api.models import Base  # ensures models are registered
from src.api.routes.tasks import router as tasks_router

openapi_tags = [
    {
        "name": "Health",
        "description": "Service health and basic diagnostics.",
    },
    {
        "name": "Tasks",
        "description": "CRUD operations for tasks.",
    },
]

app = FastAPI(
    title="Pixel Perfect Task Manager API",
    description="FastAPI backend providing task CRUD endpoints backed by PostgreSQL.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# Allow the frontend container (web) to call this API.
# The user requested allowing frontend on port 3000.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # In hosted environments, the frontend may be served from a different origin;
        # expand as needed through a reverse proxy / config.
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """
    Initialize DB engine and create tables if they don't exist.

    This supports environments where migrations are not yet set up and
    the database container starts empty.
    """
    engine = init_engine()
    Base.metadata.create_all(bind=engine)


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Basic service health check endpoint.",
    operation_id="health_check",
)
def health_check():
    """Return a simple health status payload."""
    return {"message": "Healthy"}


app.include_router(tasks_router)
