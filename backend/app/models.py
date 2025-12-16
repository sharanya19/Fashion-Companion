from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime, Float
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    style_analysis = relationship("UserStyleAnalysis", back_populates="user", uselist=False)
    wardrobe_items = relationship("WardrobeItem", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String)
    age = Column(Integer, nullable=True)
    gender_expression = Column(String, nullable=True)
    style_preferences = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="profile")

class UserStyleAnalysis(Base):
    __tablename__ = "user_style_analysis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    season = Column(String) # Spring, Summer, Autumn, Winter
    season_subtype = Column(String, nullable=True)
    skin_tone = Column(String, nullable=True)
    undertone = Column(String, nullable=True)
    
    confidence_score = Column(Float, default=0.85)
    
    # JSON columns
    best_colors = Column(Text) 
    neutral_colors = Column(Text)
    worst_colors = Column(Text)
    complementary_colors = Column(Text)
    
    eye_color = Column(String, nullable=True)
    hair_color = Column(String, nullable=True)
    
    jewelry_metals = Column(Text) # JSON list
    jewelry_stones = Column(Text) # JSON list
    
    face_shape = Column(String, nullable=True)
    
    user = relationship("User", back_populates="style_analysis")

class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String)
    
    # Core Classification
    category = Column(String) # Top, Bottom, etc.
    subcategory = Column(String, nullable=True) # Shirt, Jeans, Dress
    type = Column(String, nullable=True) # Sleeveless, Maxi, etc.
    
    # Attributes
    color_primary = Column(String, nullable=True) # Hex
    color_secondary = Column(String, nullable=True) # Hex
    color_name = Column(String, nullable=True) # Human readable name
    pattern = Column(String, nullable=True)
    fabric = Column(String, nullable=True)
    fit = Column(String, nullable=True)
    
    # Analysis & Tags (Stored as JSON Strings)
    seasonality = Column(Text, nullable=True) # ["Spring", "Autumn"]
    occasion_tags = Column(Text, nullable=True) # ["Work", "Party"]
    style_tags = Column(Text, nullable=True) # ["Casual", "Boho"]
    
    # AI Scoring
    match_level = Column(String, default="neutral") # best, neutral, worst
    ai_metadata = Column(Text, nullable=True) # Validated JSON from Vision AI
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="wardrobe_items")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String) # user, assistant, system
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")
