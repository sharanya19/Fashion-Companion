from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
from .auth import get_current_user
from ..services import grok_client
import json

router = APIRouter(prefix="/stylist", tags=["Stylist Chat"])

SYSTEM_PROMPT = """You are Palette, a personal stylist. 
Your goal is to help the user with their fashion choices based on their seasonal color analysis and wardrobe.
Be friendly, encouraging, and professional. 
Give shorter, concise advice unless asked for detail.
"""

@router.post("/chat", response_model=schemas.ChatResponse)
async def chat(chat_req: schemas.ChatRequest, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    # Get or create conversation
    if chat_req.conversation_id:
        conversation = db.query(models.Conversation).filter(models.Conversation.id == chat_req.conversation_id, models.Conversation.user_id == current_user.id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = models.Conversation(user_id=current_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Save user message
    user_msg = models.ChatMessage(conversation_id=conversation.id, role="user", content=chat_req.message)
    db.add(user_msg)
    
    # Prepare messages for Grok
    # Fetch history (limit to last 10 messages for context window)
    history = db.query(models.ChatMessage).filter(models.ChatMessage.conversation_id == conversation.id).order_by(models.ChatMessage.created_at.desc()).limit(10).all()
    history.reverse()
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add user context (Style Analysis)
    if current_user.style_analysis:
        analysis = current_user.style_analysis
        context = f"User is a {analysis.season} ({analysis.season_subtype}). Best colors: {analysis.best_colors}. Worst: {analysis.worst_colors}."
        messages.append({"role": "system", "content": context})
        
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
        
    # Call Grok
    response_content = await grok_client.get_chat_completion(messages)
    
    # Save assistant message
    asst_msg = models.ChatMessage(conversation_id=conversation.id, role="assistant", content=response_content)
    db.add(asst_msg)
    db.commit()
    
    return {"response": response_content, "conversation_id": conversation.id}
