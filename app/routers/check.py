import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.auth import get_current_vk_user
from app.config import settings
from app.database import create_session
from app.engine.validator import DocumentValidator
from app.ml.features import extract_features
from app.models import CheckResponse, ClassificationResponse


router = APIRouter()
validator = DocumentValidator()


def _validate_mode(mode: str) -> str:
    normalized = mode.upper()
    if normalized not in {"AUTO", "LIGHT", "MEDIUM", "HARD"}:
        raise HTTPException(status_code=422, detail="mode must be auto|light|medium|hard")
    return normalized


def _user_file_dir(vk_user_id: int) -> Path:
    path = settings.files_dir / str(vk_user_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


async def _save_docx(file: UploadFile, vk_user_id: int, session_id: str, suffix: str = "original") -> Path:
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=422, detail="Only .docx files are supported")
    dest = _user_file_dir(vk_user_id) / f"{session_id}_{suffix}.docx"
    size = 0
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_file_size_bytes:
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File is too large")
            out.write(chunk)
    return dest


@router.post("/check", response_model=CheckResponse)
async def check_document(
    request: Request,
    file: UploadFile = File(...),
    mode: str = Form("auto"),
    vk_user_id: int = Depends(get_current_vk_user),
) -> CheckResponse:
    normalized_mode = _validate_mode(mode)
    session_id = str(uuid4())
    orig_path = await _save_docx(file, vk_user_id, session_id)

    try:
        features = extract_features(orig_path)
        classification = request.app.state.classifier.predict(features)
        effective_mode = classification.mode if normalized_mode == "AUTO" else normalized_mode
        score, issues, _ = validator.validate(str(orig_path), features, effective_mode)
    except Exception as exc:
        orig_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Cannot process .docx: {exc}") from exc

    await create_session(
        session_id=session_id,
        vk_user_id=vk_user_id,
        doc_type=classification.doc_type,
        mode=effective_mode,
        score_before=score,
        orig_path=orig_path,
        issues=[issue.model_dump() for issue in issues],
    )
    return CheckResponse(
        score=score,
        doc_type=classification.doc_type,
        mode=effective_mode,
        session_id=session_id,
        issues=issues,
    )


@router.post("/classify", response_model=ClassificationResponse)
async def classify_document(
    request: Request,
    file: UploadFile = File(...),
    vk_user_id: int = Depends(get_current_vk_user),
) -> ClassificationResponse:
    session_id = str(uuid4())
    tmp_path = await _save_docx(file, vk_user_id, session_id, suffix="classify")
    try:
        features = extract_features(tmp_path)
        result = request.app.state.classifier.predict(features)
        return ClassificationResponse(**result.__dict__)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Cannot classify .docx: {exc}") from exc
    finally:
        tmp_path.unlink(missing_ok=True)

