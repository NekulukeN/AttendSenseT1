from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.utils.jwt import decode_token
from app.utils.liveness import analyze_liveness

router      = APIRouter(prefix="/liveness", tags=["Liveness Detection"])
http_bearer = HTTPBearer()

# Supported probe actions
VALID_ACTIONS = ["blink", "smile", "turn_left", "turn_right"]


@router.post("/check/{action}")
async def liveness_check(
    action: str,
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    """
    Check liveness for a specific action.
    Actions: blink | smile | turn_left | turn_right
    """
    # Validate token
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token.")

    # Validate action
    if action not in VALID_ACTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Choose from: {VALID_ACTIONS}"
        )

    # Read image bytes
    image_bytes = await file.read()

    # Analyze liveness
    analysis = analyze_liveness(image_bytes)

    if not analysis.get("face_detected"):
        raise HTTPException(status_code=422, detail="No face detected in image.")

    # Check if action was performed
    passed = False

    if action == "blink":
        passed = analysis["eyes_closed"]

    elif action == "smile":
        passed = analysis["smiling"]

    elif action == "turn_left":
        passed = analysis["head_direction"] == "left"

    elif action == "turn_right":
        passed = analysis["head_direction"] == "right"

    return {
        "action"         : action,
        "passed"         : passed,
        "face_detected"  : analysis["face_detected"],
        "eyes_closed"    : analysis["eyes_closed"],
        "smiling"        : analysis["smiling"],
        "head_direction" : analysis["head_direction"],
        "ear_left"       : analysis["ear_left"],
        "ear_right"      : analysis["ear_right"],
        "mar"            : analysis["mar"],
        "message"        : f"Liveness check {'passed ✅' if passed else 'failed ❌'}"
    }


@router.post("/analyze")
async def analyze_face(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    """Raw analysis — returns all facial metrics without pass/fail."""
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token.")

    image_bytes = await file.read()
    analysis    = analyze_liveness(image_bytes)

    if not analysis.get("face_detected"):
        raise HTTPException(status_code=422, detail="No face detected.")

    return analysis