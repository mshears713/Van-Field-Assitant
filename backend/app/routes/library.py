from fastapi import APIRouter

from ..config import config

router = APIRouter()


@router.get("/library")
def get_library() -> dict:
    index_path = config.LIBRARY_DIR / "index.json"
    return {
        "ok": True,
        "implemented": False,
        "message": (
            "Local library browsing is scaffolded but not fully implemented yet. "
            "Copy Notion exports (Markdown/HTML/CSV) into library/notion_exports/. "
            "A future index builder will scan those files and populate library/index.json."
        ),
        "library_dir": str(config.LIBRARY_DIR),
        "notion_exports_dir": str(config.LIBRARY_DIR / "notion_exports"),
        "index_path": str(index_path),
        "index_exists": index_path.exists(),
        "library_items": 0,
        "items": [],
        "note": "No Notion API connection is used. Library content is copied manually from a trusted machine.",
    }
