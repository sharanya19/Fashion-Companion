from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import auth, profile, wardrobe, stylist_chat, outfits
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fashion Companion Local API")

# CORS
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads
os.makedirs("uploads/wardrobe", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(wardrobe.router)
app.include_router(stylist_chat.router)
app.include_router(outfits.router)

@app.get("/")
def read_root():
    return {"message": "Fashion Companion Local API Running"}
