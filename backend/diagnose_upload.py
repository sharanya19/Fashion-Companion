from app.database import SessionLocal
from app.models import WardrobeItem, User
import json

def diagnose():
    db = SessionLocal()
    try:
        print("Checking DB Connection...")
        # Get user
        user = db.query(User).filter(User.email == "test@example.com").first()
        if not user:
            print("Test user not found.")
            return

        print(f"Attempting to add WardrobeItem for user {user.id}...")
        
        item = WardrobeItem(
            user_id=user.id,
            file_path="dummy_path.jpg",
            category="Top",
            subcategory="T-Shirt", # New field
            color_primary="#FF0000",
            seasonality=json.dumps(["Summer"]),
            ai_metadata=json.dumps({"test": "data"})
        )
        
        db.add(item)
        db.commit()
        print("✅ Successfully added item to DB directly. Schema is correct.")
        
        # Verify read
        db.refresh(item)
        print(f"Read back subcategory: {item.subcategory}")
        
    except Exception as e:
        print(f"❌ DB Diagnosis Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
