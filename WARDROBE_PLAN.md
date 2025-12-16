# 🧥 Digital Wardrobe & AI Stylist Implementation Plan

## 🧭 Phase 1: Foundation (Data & Schema)
**Goal:** Upgrade the database to store richer metadata ("Smart Wardrobe").

### 1.1 Database Migration
Update `WardrobeItem` model (and DB table) to include:
- `subcategory` (String)
- `type` (String)
- `color_primary` (String, Hex)
- `color_secondary` (String, Hex)
- `pattern` (String)
- `fabric` (String)
- `fit` (String)
- `seasonality` (JSON List)
- `occasion_tags` (JSON List)
- `ai_metadata` (JSON Object) - for storing confidence scores and raw AI analysis

### 1.2 Pydantic Schemas
Create strict validation schemas (`schemas.py`) ensuring every item has the required fields before reaching the DB.

---

## 👁️ Phase 2: AI Vision Pipeline (Auto-Tagging)
**Goal:** User uploads a photo -> AI extracts all tags automatically.

### 2.1 Clothing CV Engine
Create `app/services/clothing_cv.py`.
- **Function:** `extract_dominant_colors(image_path)`
    - Uses K-Means clustering (like current engine) but optimized for clothing (masking background).
- **Function:** `analyze_clothing_attributes(image_path)`
    - *Option A (Lightweight):* Classification model (ResNet/EfficientNet) for basic attributes.
    - *Option B (Advanced):* Calls Gemini 1.5 Flash Vision API to get detailed JSON description (Fabric, Pattern, Collar Type). **(Recommended)**

### 2.2 Color Matching Logic
Upgrade `wardrobe_logic.py` to use the **CIE76/CIE2000** Delta E standard for color matching (more accurate than simple RGB distance).
- Compare extracted `color_primary` vs User's Season Palette.
- Return `ai_color_score` (Match Score 0-100, Season Fit).

---

## 🤖 Phase 3: AI Stylist (Outfit Generation)
**Goal:** "I need an outfit for brunch" -> AI returns a full look.

### 3.1 LLM Integration Service
Create `app/services/stylist_ai.py`.
- Integrates with Gemini 1.5 Pro / GPT-4.
- Implements the **MASTER PROMPT** you provided.
- **Workflow:**
    1. Fetch User's Wardrobe (filtered by Seasonality).
    2. Construct the Prompt with Wardrobe JSON + User Request.
    3. Send to LLM.
    4. Parse JSON response.

### 3.2 Outfit Endpoints
- `POST /outfits/generate`: Takes context `{occasion, weather, vibe}`. Returns generated outfit.
- `GET /outfits/history`: View past recommendations.

---

## 📅 Timeline & Execution Order

1.  **Step 1:** Modify Database Schema (SQLAlchemy Models).
2.  **Step 2:** Implement Gemini Vision for auto-tagging uploaded items.
3.  **Step 3:** Implement the "Master Prompt" Generator.
4.  **Step 4:** Build the API Endpoints.
5.  **Step 5:** Frontend "Wardrobe" & "Stylist" tab updates.

**Ready to proceed?** I will start with **Step 1: Database Migration.**
