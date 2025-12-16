# 🏗️ Wardrobe Feature - Complete Architecture Documentation

**Last Updated:** December 16, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [Workflow Diagram](#workflow-diagram)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)
6. [API Endpoints](#api-endpoints)

---

## 🎯 Overview

The Wardrobe feature allows users to upload clothing items, automatically extract metadata (category, color, pattern, etc.), and match items against their personal color season palette.

### Key Capabilities

- **Image Upload** - Accepts clothing photos
- **Auto-Tagging** - Extracts category, color, pattern, fabric automatically
- **Color Matching** - Compares item colors to user's season palette
- **Smart Detection** - Multiple fallback mechanisms for reliability

---

## 📁 File Structure

### Core Router

```
backend/app/routers/wardrobe.py
```

**Purpose:** Main API endpoint handler for wardrobe operations
**Responsibilities:**

- Handle POST `/wardrobe/` - Upload new items
- Handle GET `/wardrobe/` - Retrieve user's wardrobe
- Handle DELETE `/wardrobe/{id}` - Remove items
- Orchestrate the upload workflow
- Format responses for frontend

**Key Functions:**

- `upload_wardrobe_item()` - Main upload handler
- `get_wardrobe()` - Retrieve items
- `delete_wardrobe_item()` - Delete items
- `get_detailed_color_name()` - Enhanced color naming

---

### Service Layer Files

#### 1. `backend/app/services/vision_service.py`

**Purpose:** AI-powered image analysis using Google Gemini Vision API
**Responsibilities:**

- Call Gemini API for clothing analysis
- Extract structured metadata (category, color, pattern, fabric, etc.)
- Fallback to local color extraction if API fails
- Handle timeouts and retries

**Key Functions:**

- `analyze_clothing_image(image_path)` - Main analysis function
- Returns: Dictionary with category, subcategory, color, pattern, fabric, tags

**Features:**

- Timeout: 3 seconds per attempt
- Retries: 1 attempt
- Fallback: Local color extraction if API unavailable

---

#### 2. `backend/app/services/image_category_detector.py`

**Purpose:** Image-based category detection (fallback when AI unavailable)
**Responsibilities:**

- Analyze image aspect ratio (tops vs pants)
- Detect visual patterns (legs vs torso)
- Distinguish between clothing types

**Key Functions:**

- `detect_category_from_image(image_path)` - Main detection function
- `detect_pants_vs_dress()` - Distinguish vertical items
- `detect_from_features()` - Analyze image features

**Detection Logic:**

- **Aspect Ratio Analysis:**
  - Wide (ratio > 1.3) → Top
  - Tall (ratio < 0.7) → Pants or Dress
  - Square (0.7-1.3) → Feature analysis
- **Visual Pattern Detection:**
  - Two leg areas → Pants
  - Uniform middle → Dress
  - Variation in top third → Top

---

#### 3. `backend/app/services/clothing_normalizer.py`

**Purpose:** Normalize and standardize category names
**Responsibilities:**

- Map various category names to standard format
- Repair incorrect categorizations
- Handle subcategory-based corrections

**Key Functions:**

- `normalize_category(raw_category, raw_subcategory)` - Main normalization
- `normalize_text(text)` - Text formatting

**Category Mapping:**

- "top", "shirt", "t-shirt", "blouse" → "Top"
- "jeans", "pants", "trousers", "skirt" → "Bottom"
- "dress", "jumpsuit", "romper" → "OnePiece"
- "shoe", "boot", "sandal" → "Footwear"
- "jacket", "coat", "blazer" → "Outerwear"

**Repair Rules:**

- If category is "Top" but subcategory is "Jeans" → Correct to "Bottom"
- If category is generic but subcategory is specific → Use subcategory

---

#### 4. `backend/app/services/wardrobe_logic.py`

**Purpose:** Color matching logic for season palette
**Responsibilities:**

- Compare item colors to user's season palette
- Determine match level (best/neutral/worst)
- Calculate color distance using weighted RGB formula

**Key Functions:**

- `determine_match_level(item_hex, best_colors, neutral_colors, worst_colors)` - Main matching
- `hex_to_rgb(hex_color)` - Color conversion
- `color_distance(c1, c2)` - Distance calculation

**Matching Logic:**

- Compares item hex color to user's palette colors
- Uses weighted RGB distance formula
- Threshold: 100 (adjustable)
- Returns: "best", "neutral", or "worst"

**Color Format Handling:**

- Supports both string hex (`"#FF0000"`) and dict format (`{"hex": "#FF0000"}`)

---

### Data Models

#### `backend/app/models.py` - WardrobeItem Model

**Purpose:** Database schema for wardrobe items
**Fields:**

```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key to User)
- file_path: String (Path to uploaded image)
- category: String (Top, Bottom, OnePiece, etc.)
- subcategory: String (T-Shirt, Jeans, etc.)
- type: String (Sleeveless, Skinny, etc.)
- color_primary: String (Hex code)
- color_secondary: String (Hex code)
- color_name: String (Human-readable name)
- pattern: String (Solid, Striped, etc.)
- fabric: String (Cotton, Silk, etc.)
- fit: String (Tight, Regular, etc.)
- seasonality: Text (JSON array: ["Spring", "Summer"])
- occasion_tags: Text (JSON array: ["Work", "Casual"])
- style_tags: Text (JSON array: ["Minimal", "Boho"])
- match_level: String (best, neutral, worst)
- ai_metadata: Text (Full AI analysis JSON)
- created_at: DateTime
```

---

### Schemas

#### `backend/app/schemas.py` - WardrobeItemResponse

**Purpose:** Pydantic schema for API responses
**Fields:** Same as model, but with parsed JSON arrays (not strings)

---

## 🔄 Workflow Diagram

```
User Uploads Image
       ↓
[1] wardrobe.py - upload_wardrobe_item()
       ↓
[2] Save File to Disk
       ↓
[3] AI Vision Analysis (5s timeout)
       ├─→ vision_service.py → Gemini API
       │   ├─ Success → Extract metadata
       │   └─ Fail/Timeout → Continue with fallback
       ↓
[4] Category Detection (Multi-tier)
       ├─→ AI Category (if available)
       ├─→ normalize_category() → clothing_normalizer.py
       ├─→ Image Detection → image_category_detector.py
       └─→ Filename Inference (last resort)
       ↓
[5] Color Extraction (Multi-tier)
       ├─→ AI Color (if available)
       ├─→ Local Hex Extraction (vision_service fallback)
       └─→ Enhanced Extraction (wardrobe.py fallback)
       ↓
[6] Color Naming
       └─→ get_detailed_color_name() → wardrobe.py
       ↓
[7] Color Matching
       └─→ wardrobe_logic.py → determine_match_level()
       ↓
[8] Save to Database
       └─→ models.WardrobeItem → SQLite
       ↓
[9] Format Response
       └─→ schemas.WardrobeItemResponse
       ↓
Return to Frontend
```

---

## 📊 Detailed Component Breakdown

### 1. Upload Workflow (`wardrobe.py`)

#### Step 1: File Handling

```python
# Create upload directory
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Generate unique filename
filename = f"{uuid.uuid4()}{file_extension}"
file_path = os.path.join(UPLOAD_DIR, filename)

# Save file
shutil.copyfileobj(file.file, buffer)
```

#### Step 2: AI Vision Analysis

```python
# Try Gemini API (5s timeout)
ai_metadata = await asyncio.wait_for(
    vision_service.analyze_clothing_image(file_path),
    timeout=5.0
)
```

**What vision_service does:**

1. Checks for Gemini API key
2. Encodes image to base64
3. Sends to Gemini API with structured prompt
4. Parses JSON response
5. Falls back to local color extraction if fails

#### Step 3: Category Detection (Multi-Tier)

**Tier 1: AI Category** (if available)

```python
ai_cat = ai_metadata.get("category")
final_category = normalize_category(ai_cat, ai_sub)
```

**Tier 2: Image-Based Detection** (if AI failed or default "Top")

```python
detected_category = detect_category_from_image(file_path)
```

**Tier 3: Filename Inference** (last resort)

```python
if "jean" in filename.lower():
    final_category = "Bottom"
```

#### Step 4: Color Extraction (Multi-Tier)

**Tier 1: User Input** (if provided)

```python
final_hex = color_hex  # From form
```

**Tier 2: AI Color** (if available)

```python
local_hex = ai_metadata.get("local_hex")
final_hex = local_hex
```

**Tier 3: Local Extraction** (fallback)

```python
# Use PIL to extract dominant color
img = Image.open(file_path).convert('RGB')
# Filter background pixels
# Get most common color
final_hex = "#{:02x}{:02x}{:02x}".format(*most_common_color)
```

#### Step 5: Color Naming

```python
final_name = get_detailed_color_name(most_common_color)
# Returns: "Dark Blue", "Light Blue", "Navy Blue", etc.
```

**Color Naming Logic:**

- Calculates brightness (0-255)
- Determines dominant channel (R, G, B)
- Classifies shade (dark/light/medium)
- Returns specific color name

#### Step 6: Color Matching

```python
match_level = wardrobe_logic.determine_match_level(
    final_hex,
    user.best_colors,      # From style analysis
    user.neutral_colors,
    user.worst_colors
)
```

**Matching Algorithm:**

1. Convert hex to RGB
2. Calculate weighted distance to each palette color
3. Check against thresholds:
   - Distance < 100 → Match found
   - Check best colors first
   - Then worst colors
   - Then neutral colors
4. Return match level

#### Step 7: Database Save

```python
new_item = models.WardrobeItem(
    user_id=current_user.id,
    file_path=file_path,
    category=final_category,
    color_primary=final_hex,
    color_name=final_name,
    match_level=match_level,
    # ... other fields
)
db.add(new_item)
db.commit()
```

---

## 🔌 API Endpoints

### POST `/wardrobe/`

**Purpose:** Upload new wardrobe item

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Body:
  - `file`: Image file (required)
  - `category`: String (optional, defaults to "Top")
  - `color_hex`: String (optional)
  - `color_name`: String (optional)

**Response:**

```json
{
  "id": 1,
  "file_path": "uploads/wardrobe/uuid.jpg",
  "category": "Bottom",
  "subcategory": "Jeans",
  "color_primary": "#4169E1",
  "color_name": "Light Blue",
  "match_level": "neutral",
  "seasonality": [],
  "occasion_tags": [],
  "style_tags": [],
  "ai_metadata": {...}
}
```

**Processing Time:** 3-5 seconds (with fallbacks)

---

### GET `/wardrobe/`

**Purpose:** Retrieve user's wardrobe items

**Request:**

- Method: GET
- Headers: Authorization: Bearer {token}

**Response:**

```json
[
  {
    "id": 1,
    "file_path": "uploads/wardrobe/uuid.jpg",
    "category": "Bottom",
    "color_name": "Light Blue",
    "match_level": "neutral",
    ...
  }
]
```

**Processing Time:** <100ms

---

### DELETE `/wardrobe/{item_id}`

**Purpose:** Delete wardrobe item

**Request:**

- Method: DELETE
- Path Parameter: `item_id` (integer)
- Headers: Authorization: Bearer {token}

**Response:**

```json
{
  "message": "Deleted"
}
```

**Processing Time:** <100ms

---

## 🔄 Data Flow Example

### Example: Uploading Blue Jeans

1. **User Action:** Uploads `jeans.jpg` via frontend

2. **File Save:**

   - Saved to `uploads/wardrobe/abc123-uuid.jpg`

3. **AI Vision Attempt:**

   - Calls Gemini API (if key available)
   - Timeout: 5 seconds
   - If fails → Continue with fallback

4. **Category Detection:**

   - AI says: "Top" (incorrect) or None
   - Normalize: "Top" → Still "Top"
   - Image detection: Analyzes aspect ratio → "Bottom" ✅
   - Result: `category = "Bottom"`

5. **Color Extraction:**

   - AI hex: None (API failed)
   - Local extraction: Analyzes pixels → `#4169E1`
   - Result: `color_primary = "#4169E1"`

6. **Color Naming:**

   - RGB: (65, 105, 225)
   - Brightness: 131.67
   - Dominant: Blue (b > r+20, b > g+20)
   - Brightness < 150 → "Blue"
   - Result: `color_name = "Blue"`

7. **Color Matching:**

   - User's palette: Autumn (warm colors)
   - Item color: Blue (cool)
   - Distance calculation → No close match
   - Result: `match_level = "neutral"`

8. **Database Save:**

   - Item saved with all metadata

9. **Response:**
   - Returns formatted JSON to frontend

---

## 🛠️ Dependencies

### Python Packages

- `fastapi` - Web framework
- `PIL/Pillow` - Image processing
- `numpy` - Numerical operations
- `httpx` - HTTP client for Gemini API
- `sqlalchemy` - Database ORM

### External Services

- **Google Gemini Vision API** (optional)
  - Used for AI-powered tagging
  - Falls back gracefully if unavailable
  - Requires `GEMINI_API_KEY` in `.env`

---

## 🎯 Key Design Decisions

### 1. Multi-Tier Fallbacks

**Why:** Ensures reliability even when AI services fail

- AI Vision → Image Detection → Filename Inference
- AI Color → Local Extraction → Enhanced Extraction

### 2. Fast Timeouts

**Why:** Better user experience

- 5s wrapper timeout
- 3s per API attempt
- 1 retry maximum
- Total max: ~5 seconds

### 3. Image-Based Category Detection

**Why:** Works without API keys

- Analyzes visual features
- Distinguishes pants from tops
- No external dependencies

### 4. Enhanced Color Naming

**Why:** Better user experience

- Specific names (Dark Blue vs just "Dark")
- Handles shades and brightness
- More informative than generic names

### 5. JSON Storage in Database

**Why:** Flexibility for complex data

- Arrays stored as JSON strings
- Parsed when retrieved
- Easy to extend with new fields

---

## 📈 Performance Characteristics

| Operation        | Time     | Notes                       |
| ---------------- | -------- | --------------------------- |
| File Save        | <100ms   | Disk I/O                    |
| AI Vision        | 0-5s     | Depends on API availability |
| Image Detection  | <200ms   | Local processing            |
| Color Extraction | <300ms   | PIL + NumPy                 |
| Color Matching   | <50ms    | Simple calculations         |
| Database Save    | <100ms   | SQLite                      |
| **Total**        | **3-5s** | With all fallbacks          |

---

## 🔍 Troubleshooting Guide

### Issue: Items showing as "Top"

**Check:**

1. Is image detection running? (Check logs for "Image-based category detected")
2. Is aspect ratio being calculated correctly?
3. Try uploading a clearly vertical item (pants)

### Issue: Colors showing as "neutral"

**Check:**

1. Is color extraction working? (Check logs for "Color Extracted")
2. Does user have style analysis? (Required for matching)
3. Is color hex valid? (Should be like "#4169E1")

### Issue: Uploads slow (>10s)

**Check:**

1. Is Gemini API timing out? (Check logs)
2. Is timeout set correctly? (Should be 5s)
3. Check network connectivity

---

## 📝 Summary

The Wardrobe feature is a **multi-layered system** with:

- **3-tier category detection** (AI → Image → Filename)
- **3-tier color extraction** (AI → Local → Enhanced)
- **Fast fallbacks** for reliability
- **Smart color naming** with shades
- **Season palette matching** for personalization

All components work together to provide a robust, fast, and accurate wardrobe management system.

---

**Files Involved:**

1. `backend/app/routers/wardrobe.py` - Main router
2. `backend/app/services/vision_service.py` - AI vision
3. `backend/app/services/image_category_detector.py` - Image detection
4. `backend/app/services/clothing_normalizer.py` - Category normalization
5. `backend/app/services/wardrobe_logic.py` - Color matching
6. `backend/app/models.py` - Database models
7. `backend/app/schemas.py` - API schemas
