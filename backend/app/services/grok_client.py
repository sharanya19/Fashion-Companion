import httpx
from ..config import settings

async def get_chat_completion(messages: list) -> str:
    if not settings.XAI_API_KEY:
        return "Grok API Key is missing. Please check your .env file."
        
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.XAI_API_KEY}"
    }
    
    payload = {
        "model": settings.XAI_MODEL,
        "messages": messages,
        "stream": False
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error calling Grok: {e}")
            return "Sorry, I'm having trouble connecting to the stylist brain right now."
