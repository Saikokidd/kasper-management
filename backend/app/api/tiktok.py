from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.api.deps import get_current_user, require_admin
from app.models.user import User
from app.models.tiktok_token import TiktokToken
import httpx, secrets

router = APIRouter(prefix="/api/tiktok", tags=["tiktok"])

TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_VIDEOS_URL = "https://open.tiktokapis.com/v2/video/list/"

@router.get("/auth")
def tiktok_auth(current_user: User = Depends(require_admin)):
    state = secrets.token_hex(16)
    params = (
        f"?client_key={settings.TIKTOK_CLIENT_KEY}"
        f"&scope=user.info.basic,video.list"
        f"&response_type=code"
        f"&redirect_uri={settings.TIKTOK_REDIRECT_URI}"
        f"&state={state}"
    )
    return {"auth_url": TIKTOK_AUTH_URL + params}

@router.get("/callback")
async def tiktok_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db)
):
    async with httpx.AsyncClient() as client:
        resp = await client.post(TIKTOK_TOKEN_URL, data={
            "client_key": settings.TIKTOK_CLIENT_KEY,
            "client_secret": settings.TIKTOK_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.TIKTOK_REDIRECT_URI,
        })
    data = resp.json()
    if "access_token" not in data:
        raise HTTPException(status_code=400, detail=f"TikTok OAuth error: {data}")

    token = db.query(TiktokToken).first()
    if not token:
        token = TiktokToken()
        db.add(token)
    token.access_token = data["access_token"]
    token.refresh_token = data.get("refresh_token", "")
    token.open_id = data.get("open_id", "")
    db.commit()

    return RedirectResponse(url="https://kasper-management.duckdns.org/tiktok?connected=1")

@router.get("/videos")
async def get_videos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    token = db.query(TiktokToken).first()
    if not token or not token.access_token:
        return {"connected": False, "videos": []}

    all_videos = []
    cursor = None
    fields = "id,title,cover_image_url,share_url,view_count,like_count,comment_count,share_count,create_time"

    async with httpx.AsyncClient() as client:
        while True:
            body = {"max_count": 20}
            if cursor:
                body["cursor"] = cursor

            resp = await client.post(
                TIKTOK_VIDEOS_URL,
                headers={"Authorization": f"Bearer {token.access_token}"},
                params={"fields": fields},
                json=body
            )
            data = resp.json()
            videos = data.get("data", {}).get("videos", [])
            all_videos.extend(videos)

            has_more = data.get("data", {}).get("has_more", False)
            cursor = data.get("data", {}).get("cursor")
            if not has_more or not cursor:
                break

    return {"connected": True, "videos": all_videos}

@router.get("/status")
def tiktok_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    token = db.query(TiktokToken).first()
    return {"connected": bool(token and token.access_token)}
