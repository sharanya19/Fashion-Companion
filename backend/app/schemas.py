from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# User
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

# Profile
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender_expression: Optional[str] = None
    style_preferences: Optional[str] = None

class ProfileResponse(ProfileUpdate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# Analysis
class ColorItem(BaseModel):
    hex: str
    name: str
    category: Optional[str] = "General"  # Made optional for compatibility

class RecommendationItem(BaseModel):
    name: str
    description: Optional[str] = None

class AnalysisResponse(BaseModel):
    season: str
    season_subtype: Optional[str] = None
    undertone: Optional[str] = None
    
    # Features as Objects
    skin_tone: Optional[Dict[str, Any]] = None
    eye_color: Optional[Dict[str, Any]] = None
    hair_color: Optional[Dict[str, Any]] = None
    
    confidence_score: float = 0.0
    
    explanation: Optional[List[str]] = [] # NEW
    
    best_colors: List[ColorItem]
    neutral_colors: List[ColorItem]
    accent_colors: List[ColorItem] = [] # NEW
    luxury_colors: List[ColorItem] = [] # NEW
    worst_colors: List[ColorItem]
    complementary_colors: List[ColorItem]
    
    jewelry_metals: List[Any] # Can be str or dict
    jewelry_stones: List[Any]
    
    class Config:
        from_attributes = True

# Wardrobe
# Wardrobe
class WardrobeItemCreate(BaseModel):
    category: str
    subcategory: Optional[str] = None
    type: Optional[str] = None
    
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    pattern: Optional[str] = None
    fabric: Optional[str] = None
    fit: Optional[str] = None
    
    # We accept lists in API, but backend might serialize them
    seasonality: Optional[List[str]] = []
    occasion_tags: Optional[List[str]] = []
    style_tags: Optional[List[str]] = []

class WardrobeItemResponse(WardrobeItemCreate):
    id: int
    file_path: str
    match_level: str
    ai_metadata: Optional[Dict[str, Any]] = None # Return full AI analysis
    
    class Config:
        from_attributes = True

# Chat
class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int

# Outfits
class OutfitGenRequest(BaseModel):
    occasion: str
    weather: Optional[str] = "Neutral"
    vibe: Optional[str] = "Smart Casual"

class OutfitItem(BaseModel):
    item_id: int
    reason: str

class OutfitGenResponse(BaseModel):
    outfit_name: str
    items: List[OutfitItem]
    explanation: str
    missing_categories: Optional[List[str]] = []

