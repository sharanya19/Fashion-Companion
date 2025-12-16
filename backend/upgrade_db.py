import sqlite3

DB_PATH = "palette.db"

def upgrade_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # List of new columns to add
    new_columns = [
        ("subcategory", "TEXT"),
        ("type", "TEXT"),
        ("color_primary", "TEXT"),
        ("color_secondary", "TEXT"),
        ("fabric", "TEXT"),
        ("fit", "TEXT"),
        ("seasonality", "TEXT"),
        ("occasion_tags", "TEXT"),
        ("style_tags", "TEXT"),
        ("ai_metadata", "TEXT")
    ]
    
    print(f"📦 Upgrading database: {DB_PATH}")
    
    for col_name, col_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE wardrobe_items ADD COLUMN {col_name} {col_type}")
            print(f"   ✅ Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"   ⚠️ Column already exists: {col_name}")
            else:
                print(f"   ❌ Error adding {col_name}: {e}")

    # Optional: Migrate data from color_hex to color_primary if needed
    try:
        cursor.execute("UPDATE wardrobe_items SET color_primary = color_hex WHERE color_primary IS NULL AND color_hex IS NOT NULL")
        print("   ✅ Migrated color_hex -> color_primary")
    except Exception as e:
        print(f"   ⚠️ Migration skipped: {e}")

    conn.commit()
    conn.close()
    print("🎉 Database upgrade complete!")

if __name__ == "__main__":
    upgrade_database()
