from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api.auth import router as auth_router
from app.api.interviews import router as interviews_router
from app.api.inscriptions import router as inscriptions_router
from app.api.form_templates import router as templates_router
from app.api.candidates import router as candidates_router
from app.api.tasks import router as tasks_router
from app.api.media import router as media_router
from app.api.ads import router as ads_router
from app.api.job_posts import router as job_posts_router
from app.api.tiktok_streams import router as tiktok_streams_router

app = FastAPI(title="Kasper Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы — ПЕРВЫМ делом до роутеров
MEDIA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "media")
os.makedirs(MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

app.include_router(auth_router)
app.include_router(interviews_router)
app.include_router(inscriptions_router)
app.include_router(templates_router)
app.include_router(candidates_router)
app.include_router(tasks_router)
app.include_router(media_router)
app.include_router(ads_router)
app.include_router(job_posts_router)
app.include_router(tiktok_streams_router)

@app.get("/health")
def health():
    return {"status": "ok"}
