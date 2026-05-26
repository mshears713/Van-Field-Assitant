from fastapi import APIRouter

from ..config import config

router = APIRouter()


@router.get("/notes")
async def get_notes() -> dict:
    return {
        "ok": True,
        "implemented": False,
        "message": (
            "Notes list is scaffolded but not fully implemented yet. "
            "The planned pipeline: record audio on phone -> upload to dashboard -> "
            "save raw audio -> transcribe with local Whisper -> classify with Capture Agent -> "
            "generate Notion-ready prompt -> copy to trusted machine for final import."
        ),
        "notes_dir": str(config.NOTES_DIR),
        "inbox": str(config.NOTES_DIR / "inbox"),
        "processed": str(config.NOTES_DIR / "processed"),
        "ready_for_notion": str(config.NOTES_DIR / "ready_for_notion"),
        "archived": str(config.NOTES_DIR / "archived"),
        "items": [],
    }
