#!/bin/bash
set -e

# ============================================================
# Kasper-management — Фаза 8 Backend
# Запускать на node-1 из папки проекта:
# cd /path/to/kasper-management && bash phase8_backend.sh
# ============================================================

BACKEND="./backend"

echo ""
echo "======================================================"
echo "  Kasper-management Phase 8 — Backend Setup"
echo "======================================================"
echo ""

# --------------------------------------------------------------
# ШАГ 1: Переименование роли manager → pult в модели user.py
# --------------------------------------------------------------
echo "[1/8] Обновляем модель User (manager → pult)..."

cat > "$BACKEND/app/models/user.py" << 'PYEOF'
from sqlalchemy import Column, Integer, String, Enum
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    pult = "pult"
    hr = "hr"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.hr)
    telegram_id = Column(String, nullable=True)
PYEOF

echo "    ✅ models/user.py обновлён"

# --------------------------------------------------------------
# ШАГ 2: Обновляем deps.py (require_manager_or_admin → require_pult_or_admin)
# --------------------------------------------------------------
echo "[2/8] Обновляем deps.py..."

cat > "$BACKEND/app/api/deps.py" << 'PYEOF'
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return current_user

def require_pult_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in [UserRole.admin, UserRole.pult]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return current_user
PYEOF

echo "    ✅ api/deps.py обновлён"

# --------------------------------------------------------------
# ШАГ 3: Обновляем все роутеры — manager → pult
# --------------------------------------------------------------
echo "[3/8] Обновляем роутеры (manager → pult)..."

# auth.py
cat > "$BACKEND/app/api/auth.py" << 'PYEOF'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin, UserOut, Token, UserCreate
from app.services.auth import verify_password, hash_password, create_access_token
from app.api.deps import get_current_user, require_admin, require_pult_or_admin

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/users", response_model=UserOut)
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email уже используется")
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        telegram_id=data.telegram_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/reset-password/{user_id}")
def reset_password(user_id: int, new_password: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.password_hash = hash_password(new_password)
    db.commit()
    return {"detail": "Пароль сброшен"}

@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(require_pult_or_admin)):
    return db.query(User).order_by(User.full_name).all()
PYEOF

# inscriptions.py
cat > "$BACKEND/app/api/inscriptions.py" << 'PYEOF'
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.database import get_db
from app.models.inscription import Inscription
from app.schemas.inscription import InscriptionCreate, InscriptionUpdate, InscriptionOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/inscriptions", tags=["inscriptions"])

@router.get("", response_model=List[InscriptionOut])
def list_inscriptions(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Inscription)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            Inscription.full_name.ilike(like),
            Inscription.username.ilike(like),
            Inscription.phone.ilike(like),
        ))
    return q.order_by(Inscription.created_at.desc()).all()

@router.post("", response_model=InscriptionOut)
def create_inscription(
    data: InscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    inscription = Inscription(**data.model_dump(), created_by_id=current_user.id)
    db.add(inscription)
    db.commit()
    db.refresh(inscription)
    return inscription

@router.patch("/{inscription_id}", response_model=InscriptionOut)
def update_inscription(
    inscription_id: int,
    data: InscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    inscription = db.query(Inscription).filter(Inscription.id == inscription_id).first()
    if not inscription:
        raise HTTPException(status_code=404, detail="Не найдено")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(inscription, field, value)
    db.commit()
    db.refresh(inscription)
    return inscription

@router.delete("/{inscription_id}")
def delete_inscription(
    inscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    inscription = db.query(Inscription).filter(Inscription.id == inscription_id).first()
    if not inscription:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(inscription)
    db.commit()
    return {"detail": "Удалено"}
PYEOF

# candidates.py
cat > "$BACKEND/app/api/candidates.py" << 'PYEOF'
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.database import get_db
from app.models.candidate import Candidate
from app.models.form_template import FormTemplate
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/candidates", tags=["candidates"])

@router.get("", response_model=List[CandidateOut])
def list_candidates(
    search: Optional[str] = Query(None),
    template_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Candidate)
    if search:
        q = q.filter(Candidate.full_name.ilike(f"%{search}%"))
    if template_id:
        q = q.filter(Candidate.template_id == template_id)
    return q.order_by(Candidate.created_at.desc()).all()

@router.post("", response_model=CandidateOut)
def create_candidate(
    data: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    template = db.query(FormTemplate).filter(FormTemplate.id == data.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    candidate = Candidate(
        full_name=data.full_name,
        template_id=data.template_id,
        fields=data.fields,
        created_by_id=current_user.id
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate

@router.get("/{candidate_id}", response_model=CandidateOut)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Не найдено")
    return candidate

@router.patch("/{candidate_id}", response_model=CandidateOut)
def update_candidate(
    candidate_id: int,
    data: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Не найдено")
    if data.full_name is not None:
        candidate.full_name = data.full_name
    if data.fields is not None:
        candidate.fields = data.fields
    db.commit()
    db.refresh(candidate)
    return candidate

@router.delete("/{candidate_id}")
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(candidate)
    db.commit()
    return {"detail": "Удалено"}
PYEOF

# form_templates.py
cat > "$BACKEND/app/api/form_templates.py" << 'PYEOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.form_template import FormTemplate
from app.schemas.form_template import FormTemplateCreate, FormTemplateUpdate, FormTemplateOut
from app.api.deps import get_current_user, require_pult_or_admin
from app.models.user import User

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.get("", response_model=List[FormTemplateOut])
def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(FormTemplate).order_by(FormTemplate.id.desc()).all()

@router.post("", response_model=FormTemplateOut)
def create_template(
    data: FormTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    template = FormTemplate(
        name=data.name,
        fields=[f.model_dump() for f in data.fields],
        created_by_id=current_user.id
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.get("/{template_id}", response_model=FormTemplateOut)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Не найдено")
    return template

@router.patch("/{template_id}", response_model=FormTemplateOut)
def update_template(
    template_id: int,
    data: FormTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Не найдено")
    if data.name is not None:
        template.name = data.name
    if data.fields is not None:
        template.fields = [f.model_dump() for f in data.fields]
    db.commit()
    db.refresh(template)
    return template

@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(template)
    db.commit()
    return {"detail": "Удалено"}
PYEOF

# tasks.py
cat > "$BACKEND/app/api/tasks.py" << 'PYEOF'
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.task import Task, TaskTemplate, TaskStatus
from app.models.user import User, UserRole
from app.schemas.task import TaskCreate, TaskComplete, TaskOut, TaskTemplateCreate, TaskTemplateOut
from app.api.deps import get_current_user, require_pult_or_admin

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/templates", response_model=List[TaskTemplateOut])
def list_task_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(TaskTemplate).order_by(TaskTemplate.id.desc()).all()

@router.post("/templates", response_model=TaskTemplateOut)
def create_task_template(
    data: TaskTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    tmpl = TaskTemplate(**data.model_dump(), created_by_id=current_user.id)
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return tmpl

@router.delete("/templates/{tmpl_id}")
def delete_task_template(
    tmpl_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    tmpl = db.query(TaskTemplate).filter(TaskTemplate.id == tmpl_id).first()
    if not tmpl:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(tmpl)
    db.commit()
    return {"detail": "Удалено"}

@router.get("", response_model=List[TaskOut])
def list_tasks(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Task)
    if current_user.role == UserRole.hr:
        q = q.filter(Task.assigned_to_id == current_user.id)
    if type:
        q = q.filter(Task.type == type)
    if status:
        q = q.filter(Task.status == status)
    return q.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).all()

@router.post("", response_model=TaskOut)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    assigned = db.query(User).filter(User.id == data.assigned_to_id).first()
    if not assigned:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    task = Task(**data.model_dump(), created_by_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.post("/{task_id}/complete", response_model=TaskOut)
def complete_task(
    task_id: int,
    data: TaskComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Не найдено")
    if current_user.role == UserRole.hr and task.assigned_to_id != current_user.id:
        raise HTTPException(status_code=403, detail="Не ваша задача")
    task.status = TaskStatus.done
    task.completion_comment = data.completion_comment
    db.commit()
    db.refresh(task)
    return task

@router.post("/{task_id}/reopen", response_model=TaskOut)
def reopen_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Не найдено")
    task.status = TaskStatus.pending
    task.completion_comment = None
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(task)
    db.commit()
    return {"detail": "Удалено"}
PYEOF

# media.py
cat > "$BACKEND/app/api/media.py" << 'PYEOF'
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
    if current_user.role == UserRole.pult:
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
    if current_user.role == UserRole.pult:
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
PYEOF

echo "    ✅ Все роутеры обновлены (manager → pult)"

# --------------------------------------------------------------
# ШАГ 4: Новые модели — Ad и JobPost
# --------------------------------------------------------------
echo "[4/8] Создаём модели Ad и JobPost..."

cat > "$BACKEND/app/models/ad.py" << 'PYEOF'
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class AdPlatform(str, enum.Enum):
    telegram = "telegram"
    facebook = "facebook"
    instagram = "instagram"
    tiktok = "tiktok"

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    platform = Column(Enum(AdPlatform), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")
PYEOF

cat > "$BACKEND/app/models/job_post.py" << 'PYEOF'
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class JobPlatform(str, enum.Enum):
    olx = "olx"
    workua = "workua"

class JobPostStatus(str, enum.Enum):
    active = "active"
    blocked = "blocked"

class JobPost(Base):
    __tablename__ = "job_posts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    platform = Column(Enum(JobPlatform), nullable=False)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    responses = Column(Integer, default=0)
    comment = Column(Text, nullable=True)
    status = Column(Enum(JobPostStatus), nullable=False, default=JobPostStatus.active)
    block_reason = Column(Text, nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")
PYEOF

echo "    ✅ models/ad.py и models/job_post.py созданы"

# --------------------------------------------------------------
# ШАГ 5: Новые схемы
# --------------------------------------------------------------
echo "[5/8] Создаём схемы..."

cat > "$BACKEND/app/schemas/ad.py" << 'PYEOF'
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.ad import AdPlatform
from app.schemas.user import UserOut

class AdCreate(BaseModel):
    platform: AdPlatform
    published_at: Optional[datetime] = None

class AdUpdate(BaseModel):
    published_at: Optional[datetime] = None

class AdOut(BaseModel):
    id: int
    created_at: datetime
    platform: AdPlatform
    published_at: Optional[datetime]
    created_by: UserOut

    class Config:
        from_attributes = True
PYEOF

cat > "$BACKEND/app/schemas/job_post.py" << 'PYEOF'
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.job_post import JobPlatform, JobPostStatus
from app.schemas.user import UserOut

class JobPostCreate(BaseModel):
    platform: JobPlatform
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    responses: int = 0
    comment: Optional[str] = None
    status: JobPostStatus = JobPostStatus.active
    block_reason: Optional[str] = None

class JobPostUpdate(BaseModel):
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    responses: Optional[int] = None
    comment: Optional[str] = None
    status: Optional[JobPostStatus] = None
    block_reason: Optional[str] = None

class JobPostOut(BaseModel):
    id: int
    created_at: datetime
    platform: JobPlatform
    content: Optional[str]
    published_at: Optional[datetime]
    responses: int
    comment: Optional[str]
    status: JobPostStatus
    block_reason: Optional[str]
    created_by: UserOut

    class Config:
        from_attributes = True
PYEOF

echo "    ✅ schemas/ad.py и schemas/job_post.py созданы"

# --------------------------------------------------------------
# ШАГ 6: Новые роутеры
# --------------------------------------------------------------
echo "[6/8] Создаём роутеры ads.py и job_posts.py..."

cat > "$BACKEND/app/api/ads.py" << 'PYEOF'
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.ad import Ad, AdPlatform
from app.schemas.ad import AdCreate, AdUpdate, AdOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/ads", tags=["ads"])

@router.get("", response_model=List[AdOut])
def list_ads(
    platform: Optional[AdPlatform] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Ad)
    if platform:
        q = q.filter(Ad.platform == platform)
    return q.order_by(Ad.published_at.desc().nullslast()).all()

@router.post("", response_model=AdOut)
def create_ad(
    data: AdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    ad = Ad(**data.model_dump(), created_by_id=current_user.id)
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad

@router.patch("/{ad_id}", response_model=AdOut)
def update_ad(
    ad_id: int,
    data: AdUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Не найдено")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ad, field, value)
    db.commit()
    db.refresh(ad)
    return ad

@router.delete("/{ad_id}")
def delete_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(ad)
    db.commit()
    return {"detail": "Удалено"}
PYEOF

cat > "$BACKEND/app/api/job_posts.py" << 'PYEOF'
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.job_post import JobPost, JobPlatform
from app.schemas.job_post import JobPostCreate, JobPostUpdate, JobPostOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/job-posts", tags=["job_posts"])

@router.get("", response_model=List[JobPostOut])
def list_job_posts(
    platform: Optional[JobPlatform] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(JobPost)
    if platform:
        q = q.filter(JobPost.platform == platform)
    return q.order_by(JobPost.created_at.desc()).all()

@router.post("", response_model=JobPostOut)
def create_job_post(
    data: JobPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    post = JobPost(**data.model_dump(), created_by_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.patch("/{post_id}", response_model=JobPostOut)
def update_job_post(
    post_id: int,
    data: JobPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    post = db.query(JobPost).filter(JobPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Не найдено")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post

@router.delete("/{post_id}")
def delete_job_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    post = db.query(JobPost).filter(JobPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(post)
    db.commit()
    return {"detail": "Удалено"}
PYEOF

echo "    ✅ api/ads.py и api/job_posts.py созданы"

# --------------------------------------------------------------
# ШАГ 7: Обновляем models/__init__.py и main.py
# --------------------------------------------------------------
echo "[7/8] Обновляем __init__.py и main.py..."

cat > "$BACKEND/app/models/__init__.py" << 'PYEOF'
from .user import User
from .interview import Interview
from .inscription import Inscription
from .form_template import FormTemplate
from .candidate import Candidate
from .task import Task, TaskTemplate
from .media_file import MediaFile
from .ad import Ad
from .job_post import JobPost
PYEOF

cat > "$BACKEND/app/main.py" << 'PYEOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.interviews import router as interviews_router
from app.api.inscriptions import router as inscriptions_router
from app.api.form_templates import router as templates_router
from app.api.candidates import router as candidates_router
from app.api.tasks import router as tasks_router
from app.api.media import router as media_router
from app.api.ads import router as ads_router
from app.api.job_posts import router as job_posts_router

app = FastAPI(title="Kasper Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(interviews_router)
app.include_router(inscriptions_router)
app.include_router(templates_router)
app.include_router(candidates_router)
app.include_router(tasks_router)
app.include_router(media_router)
app.include_router(ads_router)
app.include_router(job_posts_router)

@app.get("/health")
def health():
    return {"status": "ok"}
PYEOF

echo "    ✅ __init__.py и main.py обновлены"

# --------------------------------------------------------------
# ШАГ 8: Миграции Alembic
# --------------------------------------------------------------
echo "[8/8] Запускаем миграции..."

cd "$BACKEND"

# Миграция 1: переименование ENUM manager → pult (вручную)
MIGRATION_FILE=$(python -c "
import uuid, datetime
stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
rev = uuid.uuid4().hex[:12]
print(f'migrations/versions/{stamp}_{rev}_rename_manager_to_pult.py')
")

cat > "$MIGRATION_FILE" << 'PYEOF'
"""rename manager to pult

Revision ID: rename_mgr_pult
Revises: ad933b7f0ee9
Create Date: 2026-04-29

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'rename_mgr_pult'
down_revision: Union[str, None] = 'ad933b7f0ee9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("ALTER TYPE userrole RENAME VALUE 'manager' TO 'pult'")

def downgrade() -> None:
    op.execute("ALTER TYPE userrole RENAME VALUE 'pult' TO 'manager'")
PYEOF

echo "    ✅ Миграция rename_manager_to_pult создана: $MIGRATION_FILE"

# Применяем миграцию переименования
alembic upgrade rename_mgr_pult
echo "    ✅ ENUM manager → pult применён"

# Миграция 2: создание таблиц ads и job_posts
alembic revision --autogenerate -m "create_ads_and_job_posts"
alembic upgrade head
echo "    ✅ Таблицы ads и job_posts созданы"

cd ../..

echo ""
echo "======================================================"
echo "  ✅ Фаза 8 Backend — ГОТОВО"
echo "======================================================"
echo ""
echo "  Что сделано:"
echo "  • UserRole: manager → pult (ENUM + модель + все роутеры)"
echo "  • Новые модели: Ad, JobPost"
echo "  • Новые схемы: AdOut, JobPostOut"
echo "  • Новые роутеры: /api/ads, /api/job-posts"
echo "  • Миграции применены"
echo ""
echo "  Следующий шаг: перезапустить FastAPI контейнер"
echo "  docker compose restart  (или как у тебя запущен бэкенд)"
echo ""
