import base64
import hashlib
import hmac
from urllib.parse import parse_qsl, urlencode

from fastapi import Header, HTTPException

from app.config import settings


def _vk_sign_payload(raw_query: str) -> tuple[str, dict[str, str]]:
    params = dict(parse_qsl(raw_query.lstrip("?"), keep_blank_values=True))
    provided_sign = params.pop("sign", "")
    params.pop("hash", None)
    vk_params = {k: v for k, v in params.items() if k.startswith("vk_")}
    return provided_sign, vk_params


def verify_vk_sign(raw_query: str) -> int:
    if not raw_query:
        raise HTTPException(status_code=401, detail="Missing X-VK-Sign header")
    if not settings.vk_secret_key:
        raise HTTPException(status_code=500, detail="VK_SECRET_KEY is not configured")
    if settings.vk_app_id <= 0:
        raise HTTPException(status_code=500, detail="VK_APP_ID is not configured")

    provided_sign, vk_params = _vk_sign_payload(raw_query)
    if not provided_sign or not vk_params:
        raise HTTPException(status_code=401, detail="Invalid VK launch params")
    if vk_params.get("vk_app_id") != str(settings.vk_app_id):
        raise HTTPException(status_code=401, detail="Invalid VK app id")

    ordered = urlencode(sorted(vk_params.items()))
    digest = hmac.new(
        settings.vk_secret_key.encode("utf-8"),
        ordered.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    expected = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    if not hmac.compare_digest(expected, provided_sign):
        raise HTTPException(status_code=401, detail="Invalid VK signature")

    user_id = vk_params.get("vk_user_id") or vk_params.get("vk_viewer_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="VK user id is missing")
    return int(user_id)


async def get_current_vk_user(x_vk_sign: str | None = Header(default=None)) -> int:
    return verify_vk_sign(x_vk_sign or "")
