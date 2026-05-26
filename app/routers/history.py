from fastapi import APIRouter, Depends

from app.auth import get_current_vk_user
from app.database import list_sessions
from app.models import HistoryResponse


router = APIRouter()


@router.get("/history", response_model=HistoryResponse)
async def history(vk_user_id: int = Depends(get_current_vk_user)) -> HistoryResponse:
    return HistoryResponse(sessions=await list_sessions(vk_user_id))

