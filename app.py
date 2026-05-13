import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from server.db import db


@asynccontextmanager
async def lifespan(application: FastAPI):
    await db.initialize_schema()
    yield


app = FastAPI(title="BPA - Benefit Plan Administration", lifespan=lifespan)

from server.routes import upload, extract, documents, export, sync, volume, config

app.include_router(upload.router, prefix="/api")
app.include_router(extract.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(sync.router, prefix="/api")
app.include_router(volume.router, prefix="/api")
app.include_router(config.router, prefix="/api")

frontend_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if os.path.exists(frontend_dir):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(frontend_dir, "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dir, "index.html"))
