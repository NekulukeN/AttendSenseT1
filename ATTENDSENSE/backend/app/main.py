from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from app.database import Base, engine
from app.routers import auth
from app.routers import auth, face, attendance,liveness, probe, reports, audit
from app.utils.probe_scheduler import start_scheduler, stop_scheduler

# Auto-create tables on startup
Base.metadata.create_all(bind=engine)

security = HTTPBearer()

app = FastAPI(
    title="AttendSense API",
    description="Secure Face-Based Attendance with Randomized Probing",
    version="1.0.0",
)

# CORS — allow React dashboard and Android app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict to real domains in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(face.router)
app.include_router(attendance.router)
app.include_router(liveness.router)
app.include_router(probe.router)
app.include_router(reports.router)
app.include_router(audit.router)

@app.get("/", tags=["Health"])
def root():
    return {"message": "AttendSense API is running ✅"}