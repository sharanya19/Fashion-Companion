from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from .. import models, schemas, database
from .auth import get_current_user
from ..services import wardrobe_logic, vision_service
from ..services.clothing_normalizer import normalize_category, normalize_text
from ..services.image_category_detector import detect_category_from_image

import os
import uuid
import json
import shutil
import re

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])

UPLOAD_DIR = "uploads/wardrobe"

ALLOWED_CATEGORIES = {
    "Top",
    "Bottom",
    "OnePiece",
    "Outerwear",
    "Footwear",
    "Accessory",
}


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def normalize_hex(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not re.fullmatch(r"#?[0-9a-fA-F]{6}", value):
        return None
    return value if value.startswith("#") else f"#{value}"


# -------------------------------------------------
# Upload wardrobe item
# -------------------------------------------------

@router.post("/", response_model=schemas.WardrobeItemResponse)
async def upload_wardrobe_item(
    file: UploadFile = File(...),
    category: str | None = Form(None),
    color_hex: str | None = Form(None),
    color_name: str | None = Form(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # ---------- Save image ----------
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ---------- AI Vision ----------
    try:
        ai_metadata = await vision_service.analyze_clothing_image(file_path)
    except Exception:
        ai_metadata = None

    # ---------- CATEGORY RESOLUTION ----------
    final_category = "Uncategorized"
    decision_meta = {}

    # 1️⃣ AI semantic (highest confidence)
    if ai_metadata:
        normalized = normalize_category(
            ai_metadata.get("category"),
            ai_metadata.get("subcategory"),
            ai_metadata.get("type"),
            ai_metadata.get("item_type"),
            ai_metadata.get("garment"),
            ai_metadata.get("description"),
        )
        if normalized in ALLOWED_CATEGORIES:
            final_category = normalized
            decision_meta = {
                "source": "ai_semantic",
                "confidence": "high",
            }

    # 2️⃣ Image heuristic
    if final_category == "Uncategorized":
        image_cat = detect_category_from_image(file_path)
        if image_cat in ALLOWED_CATEGORIES:
            final_category = image_cat
            decision_meta = {
                "source": "image_heuristic",
                "confidence": "medium",
            }

    # 3️⃣ Filename fallback
    if final_category == "Uncategorized":
        name_cat = normalize_category(file.filename)
        if name_cat in ALLOWED_CATEGORIES:
            final_category = name_cat
            decision_meta = {
                "source": "filename",
                "confidence": "low",
            }

    # 3.5️⃣ Fallback Classifier (last resort before giving up)
    if final_category == "Uncategorized":
        from ..services.fallback_classifier import fallback_classify
        fallback_cat = fallback_classify(file_path, file.filename)
        if fallback_cat and fallback_cat in ALLOWED_CATEGORIES:
            final_category = fallback_cat
            decision_meta = {
                "source": "fallback_heuristic",
                "confidence": "very_low",
            }

    # 4️⃣ Manual override (last)
    if final_category == "Uncategorized" and category in ALLOWED_CATEGORIES:
        final_category = category
        decision_meta = {
            "source": "user_input",
            "confidence": "low",
        }

    # ---------- COLOR ----------
    final_hex = normalize_hex(color_hex)
    if not final_hex and ai_metadata:
        final_hex = normalize_hex(ai_metadata.get("color_hex"))

    final_color_name = (
        color_name
        or (ai_metadata.get("color_primary") if ai_metadata else None)
        or "Unknown"
    )

    # ---------- METADATA ----------
    subcategory = normalize_text(
        ai_metadata.get("subcategory") if ai_metadata else None
    )
    item_type = normalize_text(ai_metadata.get("type")) if ai_metadata else None
    pattern = normalize_text(ai_metadata.get("pattern")) if ai_metadata else None
    fabric = normalize_text(ai_metadata.get("fabric")) if ai_metadata else None
    fit = normalize_text(ai_metadata.get("fit")) if ai_metadata else None

    seasonality = json.dumps(ai_metadata.get("seasonality", [])) if ai_metadata else "[]"
    occasions = json.dumps(ai_metadata.get("occasion_tags", [])) if ai_metadata else "[]"
    styles = json.dumps(ai_metadata.get("style_tags", [])) if ai_metadata else "[]"

    # ---------- MATCH LEVEL ----------
    match_level = "neutral"
    if current_user.style_analysis and final_hex:
        sa = current_user.style_analysis
        match_level = wardrobe_logic.determine_match_level(
            final_hex,
            json.loads(sa.best_colors),
            json.loads(sa.neutral_colors),
            json.loads(sa.worst_colors),
        )

    # ---------- SAVE ----------
    new_item = models.WardrobeItem(
        user_id=current_user.id,
        file_path=file_path,
        category=final_category,
        subcategory=subcategory,
        type=item_type,
        color_primary=final_hex,
        color_name=final_color_name,
        pattern=pattern,
        fabric=fabric,
        fit=fit,
        seasonality=seasonality,
        occasion_tags=occasions,
        style_tags=styles,
        match_level=match_level,
        ai_metadata=json.dumps({
            "ai": ai_metadata,
            "decision": decision_meta
        }) if ai_metadata else None,
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return schemas.WardrobeItemResponse(
        id=new_item.id,
        file_path=new_item.file_path.replace("\\", "/"),
        category=new_item.category,
        subcategory=new_item.subcategory,
        type=new_item.type,
        color_primary=new_item.color_primary,
        color_secondary=None,
        color_name=new_item.color_name,
        pattern=new_item.pattern,
        fabric=new_item.fabric,
        fit=new_item.fit,
        seasonality=json.loads(new_item.seasonality),
        occasion_tags=json.loads(new_item.occasion_tags),
        style_tags=json.loads(new_item.style_tags),
        match_level=new_item.match_level,
        ai_metadata=json.loads(new_item.ai_metadata) if new_item.ai_metadata else None,
    )


# -------------------------------------------------
# Get wardrobe
# -------------------------------------------------

@router.get("/", response_model=list[schemas.WardrobeItemResponse])
def get_wardrobe(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    return [
        schemas.WardrobeItemResponse(
            id=i.id,
            file_path=i.file_path.replace("\\", "/"),
            category=i.category,
            subcategory=i.subcategory,
            type=i.type,
            color_primary=i.color_primary,
            color_secondary=None,
            color_name=i.color_name,
            pattern=i.pattern,
            fabric=i.fabric,
            fit=i.fit,
            seasonality=json.loads(i.seasonality),
            occasion_tags=json.loads(i.occasion_tags),
            style_tags=json.loads(i.style_tags),
            match_level=i.match_level,
            ai_metadata=json.loads(i.ai_metadata) if i.ai_metadata else None,
        )
        for i in current_user.wardrobe_items
    ]


# -------------------------------------------------
# Delete item
# -------------------------------------------------

@router.delete("/{item_id}")
def delete_wardrobe_item(
    item_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = db.query(models.WardrobeItem).filter_by(id=item_id).first()

    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")

    if os.path.exists(item.file_path):
        os.remove(item.file_path)

    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
