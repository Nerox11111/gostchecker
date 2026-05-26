from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.auth import get_current_vk_user
from app.database import get_session


router = APIRouter()


@router.get("/download/{session_id}")
async def download(session_id: str, vk_user_id: int = Depends(get_current_vk_user)) -> FileResponse:
    session = await get_session(session_id, vk_user_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    filepath = Path(session["fixed_path"] or session["orig_path"])
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=filepath,
        media_type="application/octet-stream",
        filename=filepath.name,
    )

