from fastapi import APIRouter

from ..config import config
from ..library_service import get_index

router = APIRouter()


@router.get("/library")
def get_library() -> dict:
    exports_dir = config.LIBRARY_DIR / "notion_exports"
    index_path = config.LIBRARY_DIR / "index.json"

    items = get_index(exports_dir, index_path)

    return {
        "ok": True,
        "implemented": len(items) > 0,
        "library_dir": str(config.LIBRARY_DIR),
        "notion_exports_dir": str(exports_dir),
        "index_path": str(index_path),
        "index_exists": index_path.exists(),
        "library_items": len(items),
        "items": items,
        "note": "No Notion API connection is used. Library content is copied manually from a trusted machine.",
    }
