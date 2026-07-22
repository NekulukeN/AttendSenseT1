import numpy as np
import json
import os
import shutil
from deepface import DeepFace

UPLOAD_DIR = "uploads/faces"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_image(file, user_id: int) -> str:
    """Save uploaded image to disk, return path."""
    path = f"{UPLOAD_DIR}/user_{user_id}.jpg"
    with open(path, "wb") as f:
        shutil.copyfileobj(file, f)
    return path

def generate_embedding(image_path: str) -> list:
    """Generate 128-d face embedding using DeepFace."""
    result = DeepFace.represent(
        img_path    = image_path,
        model_name  = "Facenet",   # fast + accurate for MVP
        enforce_detection = True   # raises error if no face found
    )
    return result[0]["embedding"]  # list of floats

def compare_embeddings(stored: str, new_embedding: list, threshold=10.0) -> bool:
    """Compare stored embedding (JSON string) against new embedding."""
    stored_list = json.loads(stored)
    stored_np   = np.array(stored_list)
    new_np      = np.array(new_embedding)
    distance    = np.linalg.norm(stored_np - new_np)  # Euclidean distance
    return distance < threshold   # True = same person