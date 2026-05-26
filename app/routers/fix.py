import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_vk_user
from app.database import get_session, update_fixed_session
from app.engine.corrector import DocumentCorrector
from app.engine.validator import DocumentValidator
from app.ml.features import extract_features
from app.models import FixRequest, FixResponse


router = APIRouter()
corrector = DocumentCorrector()
validator = DocumentValidator()


@router.post("/fix", response_model=FixResponse)
async def fix_document(payload: FixRequest, vk_user_id: int = Depends(get_current_vk_user)) -> FixResponse:
    session = await get_session(payload.session_id, vk_user_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    orig_path = Path(session["orig_path"])
    if not orig_path.exists():
        raise HTTPException(status_code=404, detail="Original file not found")

    issues = json.loads(session["issues_json"] or "[]")
    rules = payload.apply_rules or [
        issue["rule_id"]
        for issue in issues
        if issue.get("auto_fixable")
    ]
    fixed_path = orig_path.with_name(orig_path.name.replace("_original.docx", "_fixed.docx"))
    patches = corrector.apply(orig_path, fixed_path, rules)

    features = extract_features(fixed_path)
    score_after, new_issues, _ = validator.validate(str(fixed_path), features, session["mode"])
    await update_fixed_session(
        session_id=payload.session_id,
        vk_user_id=vk_user_id,
        score_after=score_after,
        fixed_path=fixed_path,
        issues=[issue.model_dump() for issue in new_issues],
    )

    return FixResponse(
        session_id=payload.session_id,
        score_after=score_after,
        download_url=f"/api/download/{payload.session_id}",
        patches=patches,
    )

