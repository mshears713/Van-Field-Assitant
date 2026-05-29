from fastapi import APIRouter, Query

from ..config import config
from ..log_service import read_recent_logs

router = APIRouter()


@router.get("/logs/recent")
def get_recent_logs(limit: int = Query(default=50, ge=1, le=200)) -> dict:
    logs = read_recent_logs(config.LOGS_DIR, limit=limit)
    return {
        "ok": True,
        "count": len(logs),
        "logs": logs,
    }
