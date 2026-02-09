# seed_db.py
from python.engine.dynamic_db_engine import DynamicDBEngine

# Engine initialize karo
db = DynamicDBEngine()

print("🌱 Seeding Database...")

# 1. Developer ka data daalo (Ye zaroori hai)
success = db.add_user_info(
    "Priyadarshan",
    "Priyadarshan is the lead developer and creator of this AI, Sarah. He is a skilled programmer working on the Trinetra Vision project."
)

if success:
    print("✅ Priyadarshan added to memory.")
else:
    print("❌ Failed to add Priyadarshan.")

# 2. Test karo ki data gaya ya nahi
print("\n🔎 Testing Search...")
result = db.find_user("Who is the developer?")
print(f"Result: {result}")