import cv2
import numpy as np

# Load OpenCV's built-in detectors
face_cascade  = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade   = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")


def analyze_liveness(image_bytes: bytes) -> dict:
    """
    Analyze an image for liveness indicators using OpenCV.
    Returns face detection, eye count, and smile detection.
    """
    result = {
        "face_detected" : False,
        "eyes_detected" : 0,
        "eyes_closed"   : False,
        "smiling"       : False,
        "head_direction": "center",
    }

    # Decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        return {"error": "Could not decode image."}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect face
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    if len(faces) == 0:
        return result

    result["face_detected"] = True

    # Use the largest face
    x, y, w, h = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
    face_gray  = gray[y:y+h, x:x+w]

    # Detect eyes inside face region
    eyes = eye_cascade.detectMultiScale(face_gray, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))
    result["eyes_detected"] = len(eyes)
    result["eyes_closed"]   = len(eyes) == 0   # no eyes detected = likely closed

    # Detect smile inside lower half of face
    lower_face = face_gray[h//2:, :]
    smiles = smile_cascade.detectMultiScale(lower_face, scaleFactor=1.8, minNeighbors=20, minSize=(25, 25))
    result["smiling"] = len(smiles) > 0

    # Estimate head direction from face position in full image
    img_w        = image.shape[1]
    face_center  = x + w // 2
    img_center   = img_w // 2
    offset_ratio = (face_center - img_center) / img_center

    if offset_ratio < -0.2:
        result["head_direction"] = "left"
    elif offset_ratio > 0.2:
        result["head_direction"] = "right"
    else:
        result["head_direction"] = "center"

    return result