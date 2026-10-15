from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from app import models  # noqa
from app.deps import get_current_user
from app.routers import auth as auth_router
from app.routers import chat as chat_router
from app.routers import approvals as approvals_router
from app import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlowPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(approvals_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/me", response_model=schemas.UserResponse)
def me(user: models.User = Depends(get_current_user)):
    return user
