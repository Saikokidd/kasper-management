from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.interviews import router as interviews_router
from app.api.inscriptions import router as inscriptions_router
from app.api.form_templates import router as templates_router
from app.api.candidates import router as candidates_router
from app.api.tasks import router as tasks_router
from app.api.media import router as media_router

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

@app.get("/health")
def health():
    return {"status": "ok"}
