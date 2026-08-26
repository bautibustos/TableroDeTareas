import os
from fastapi import APIRouter

router = APIRouter()

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
GALLERY_DIR = os.path.join("static", "src")


@router.get("/backgrounds")
async def get_backgrounds():
    if not os.path.isdir(GALLERY_DIR):
        return []

    files = sorted(
        f for f in os.listdir(GALLERY_DIR)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    )
    return [f"/static/src/{f}" for f in files]
