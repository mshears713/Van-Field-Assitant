from fastapi import APIRouter

from ..config import config

router = APIRouter()


@router.get("/projects")
async def get_projects() -> dict:
    return {
        "ok": True,
        "implemented": False,
        "message": (
            "Project workspace browsing is scaffolded but not fully implemented yet. "
            "Clone public repos into workspace/repos/ to get started. "
            "A future version will list and inspect repos from this endpoint."
        ),
        "workspace_dir": str(config.WORKSPACE_DIR / "repos"),
        "items": [],
    }
