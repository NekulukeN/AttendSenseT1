import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.face_profile import FaceProfile
from app.utils.jwt import decode_token
from app.utils.face import save_image, generate_embedding

router     = APIRouter(prefix="/face", tags=["Face Enrollment"])
http_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db)
) -> User:
    """Reusable dependency — extracts user from JWT."""
    token   = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.post("/enroll")
def enroll_face(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a face photo to enroll. One profile per student."""

    # Check already enrolled
    existing = db.query(FaceProfile).filter(FaceProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Face already enrolled. Use /face/update to replace.")

    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only JPG or PNG images accepted.")

    # Save image to disk
    image_path = save_image(file.file, current_user.id)

    # Generate embedding
    try:
        embedding = generate_embedding(image_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"No face detected in image. Please use a clear photo. ({str(e)})")

    # Save to DB
    profile = FaceProfile(
        user_id    = current_user.id,
        embedding  = json.dumps(embedding),
        image_path = image_path,
    )
    db.add(profile)
    db.commit()

    return {
        "message"    : "Face enrolled successfully ✅",
        "user"       : current_user.full_name,
        "embedding_size": len(embedding)
    }


@router.get("/status")
def enrollment_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if current user has enrolled their face."""
    profile = db.query(FaceProfile).filter(FaceProfile.user_id == current_user.id).first()
    return {
        "enrolled"   : profile is not None,
        "user"       : current_user.full_name,
        "enrolled_at": profile.created_at if profile else None
    }