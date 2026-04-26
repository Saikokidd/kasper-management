from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.interviews import router as interviews_router
from app.api.inscriptions import router as inscriptions_router

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

@app.get("/health")
def health():
    return {"status": "ok"}
