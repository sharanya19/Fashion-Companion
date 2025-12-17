# Fashion Companion (Local Dev Version)

A local, AI-powered personal stylist application.

## Overview
This application performs:
- **Season & Color Analysis**: Determines your seasonal palette (Spring/Summer/Autumn/Winter).
- **Wardrobe Digitization**: Upload clothes and get matches based on your palette.
- **Stylist Chat**: Chat with "Palette", your AI stylist (powered by Grok).

## Tech Stack
- **Frontend**: React (Vite) + TypeScript + Vanilla CSS (Premium Dark Theme)
- **Backend**: FastAPI (Python)
- **Database**: SQLite (Local file `palette.db`)
- **Storage**: Local filesystem (`backend/uploads`)

## Prerequisites
- Node.js (v18+)
- Python (v3.9+)

## Setup & Running

### 1. Backend
The backend handles API requests, database, and business logic.
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```
Runs on: `http://localhost:8000`

### 2. Frontend
The frontend is the user interface.
```bash
cd frontend
npm install
npm run dev
```
Runs on: `http://localhost:5173`

## Features Implemented
1. **Authentication**: Sign up & Login (JWT based).
2. **Onboarding Analysis**: Automatically assigns a Season based on email hash (Demo Logic).
3. **Dashboard**: View your Season, Best Colors, and Neutrals.
4. **Wardrobe**: Upload images. Items are tagged as "Best", "Neutral", or "Worst" match automatically.
5. **Chat**: Talk to the style assistant.

## Environment Variables
Create a `backend/.env` file to configure API keys (never commit this file!):
```
# Grok API (XAI) - Required for stylist chat
XAI_API_KEY=your_grok_api_key_here

# Google Gemini API - Required for wardrobe auto-tagging
GEMINI_API_KEY=your_gemini_api_key_here
```

**Security Note:** API keys are loaded from environment variables. The application will work without them, but some features (AI tagging, stylist chat) will be limited. Never commit actual API keys to version control!
