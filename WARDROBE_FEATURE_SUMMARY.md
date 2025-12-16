# 🧥 Digital Wardrobe & AI Stylist - Feature Guide

**Status:** Backend Implementation Complete ✅

## ✨ New Capabilities

### 1. Smart Upload (Auto-Tagging) 👁️
When you upload a clothing item to `/wardrobe/`, the system now automatically calls **Google Gemini Vision**.
- **Categorization:** Automatically detects "Top > T-Shirt".
- **Attributes:** Detects "Cotton", "Striped", "V-Neck".
- **Tags:** Assigns seasonality ("Summer") and Occasion ("Casual").
- **Color:** Extracts dominant color name.

### 2. AI Stylist Engine 🤖
New endpoint `/outfits/generate` creates entire looks.
- **Input:** Occasion ("Date Night"), Weather ("Chilly"), Vibe ("Romantic").
- **Logic:**
    - Scans your digital wardrobe.
    - Filters by your **Season** (e.g. Deep Autumn).
    - Checks weather appropriateness.
    - Matches items using color theory.
- **Output:**
    - "Outfit Name" (e.g. "Autumn Romance").
    - List of items to wear.
    - Explanation of why it works.
    - Alerts if items are missing (e.g., "You need brown boots").

## ⚙️ Setup Required
To enable the AI features, you must add your Google Gemini API Key.

1. Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey) (It's free).
2. Open `.env` file.
3. Add: `GEMINI_API_KEY=your_key_here`
4. Restart the backend.

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/wardrobe/` | Upload photo. **Now Auto-Tags item.** |
| `POST` | `/outfits/generate` | JSON Body: `{ "occasion": "...", "weather": "..." }` |

## 🧪 Testing
1. Upload a shirt image.
2. Check the response -> `ai_metadata` should be populated.
3. Call `/outfits/generate` to see the magic.
