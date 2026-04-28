from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os, shutil, uuid
from app.database import get_db
from app.models.media_file import MediaFile
from app.schemas.media_file import MediaFileOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/media", tags=["media"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEDIA_DIR = os.path.join(BASE_DIR, "media")

@router.post("/upload", response_model=MediaFileOut)
async def upload_file(
    entity_type: str = Query(...),
    entity_id: int = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.manager:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    os.makedirs(MEDIA_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, unique_name)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    size = os.path.getsize(file_path)
    media = MediaFile(
        uploaded_by_id=current_user.id,
        entity_type=entity_type,
        entity_id=entity_id,
        filename=file.filename,
        path=unique_name,
        size=size,
        available=True
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media

@router.get("", response_model=List[MediaFileOut])
def list_files(
    entity_type: str = Query(...),
    entity_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(MediaFile).filter(
        MediaFile.entity_type == entity_type,
        MediaFile.entity_id == entity_id
    ).order_by(MediaFile.uploaded_at.desc()).all()

@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    media = db.query(MediaFile).filter(MediaFile.id == file_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Файл не найден")
    file_path = os.path.join(MEDIA_DIR, media.path)
    if not os.path.exists(file_path):
        media.available = False
        db.commit()
        raise HTTPException(status_code=404, detail="Файл недоступен")
    return FileResponse(file_path, filename=media.filename)

@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.manager:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    media = db.query(MediaFile).filter(MediaFile.id == file_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Не найдено")
    file_path = os.path.join(MEDIA_DIR, media.path)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.delete(media)
    db.commit()
    return {"detail": "Удалено"}
