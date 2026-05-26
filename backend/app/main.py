from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import config
from .routes import agents, library, logs, network, notes, projects, settings, status
from .startup_checks import run_startup_checks

_startup_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    result = await run_startup_checks()
    _startup_state.update(result)
    yield


app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Local offline field assistant backend.",
    lifespan=lifespan,
)

# API routes
app.include_router(status.router, prefix="/api", tags=["status"])
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(logs.router, prefix="/api", tags=["logs"])
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(library.router, prefix="/api", tags=["library"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(network.router, prefix="/api", tags=["network"])
app.include_router(settings.router, prefix="/api", tags=["settings"])

# Static files (CSS, JS) — mounted at /static
if config.FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(config.FRONTEND_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def serve_dashboard() -> FileResponse:
    index = config.FRONTEND_DIR / "index.html"
    if not index.exists():
        from fastapi.responses import HTMLResponse
        return HTMLResponse(
            "<html><body><h1>Offline Field Assistant</h1>"
            "<p>Dashboard not found. Expected frontend/static/index.html</p>"
            "<p><a href='/api/status'>API Status</a></p></body></html>",
            status_code=200,
        )
    return FileResponse(str(index))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
    )
