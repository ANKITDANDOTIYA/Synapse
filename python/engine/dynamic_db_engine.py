import os
import chromadb


class DynamicDBEngine:
    def __init__(self):
        # Path fix (Windows/Linux compatible)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_dir = os.path.join(base_dir, "naina_memory_db")

        self.client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.client.get_or_create_collection("people_memory")

        print(f"🧠 [DB] Connected to: {db_dir}")
        count = self.collection.count()
        print(f"📊 [DB] Total Memories: {count}")

        # DEBUG: Startup pe check karo ki andar maal kya pada hai
        if count > 0:
            existing_data = self.collection.get()
            print(f"📂 [DEBUG] Existing IDs in DB: {existing_data['ids']}")

        # Auto-Seed agar DB khali ho ya developer missing ho
        # Note: Hum ID hamesha lowercase save karenge taaki match easy ho
        try:
            dev_check = self.collection.get(ids=["priyadarshan"])
            if not dev_check['ids']:
                print("🌱 [DB] Seeding Developer Data...")
                self.add_person("priyadarshan",
                                "Priyadarshan is the creator of this AI. He is a developer working on the Trinetra Vision Project.")
        except Exception as e:
            print(f"Seed Error: {e}")

    def add_person(self, name, info):
        # Hamesha Lowercase ID use karo
        clean_id = name.strip().lower()
        try:
            self.collection.upsert(
                ids=[clean_id],
                documents=[info],
                metadatas=[{"original_name": name}]
            )
            print(f"✅ [DB] Saved: {clean_id}")
            return True
        except Exception as e:
            print(f"❌ [DB] Save Error: {e}")
            return False

    def find_user(self, query):
        print(f"🕵️ [DB Search] Query: '{query}'")

        # STRATEGY 1: EXACT ID LOOKUP (Fastest)
        # Agar query hi naam hai (e.g. "priyadarshan"), to pehle ID check karo
        clean_id = query.strip().lower()

        try:
            id_result = self.collection.get(ids=[clean_id])
            if id_result['documents'] and len(id_result['documents']) > 0:
                print(f"🎯 [DB] Found via Exact ID Match: {clean_id}")
                return id_result['documents'][0]
        except:
            pass  # ID match fail hua to ro mat, aage badho

        # STRATEGY 2: SEMANTIC VECTOR SEARCH (The Real Magic)
        # Agar exact naam nahi mila, ya query complex hai (e.g. "Who created you?")
        try:
            print(f"🤖 [DB] Trying Vector Search for: '{query}'")
            results = self.collection.query(
                query_texts=[query],
                n_results=1
            )

            # Result validation
            if not results['documents'] or len(results['documents'][0]) == 0:
                print("❌ [DB] No semantic match found.")
                return None

            found_info = results['documents'][0][0]
            distance = results['distances'][0][0]

            print(f"✅ [DB] Semantic Match Found! (Distance: {distance}) -> {found_info}")

            # Distance Jitna kam, utna accurate.
            # 1.5 se neeche hai to matlab milta julta hai.
            if distance < 1.6:
                return found_info
            else:
                print("⚠️ [DB] Match too weak (Distance > 1.6). Ignoring.")
                return None

        except Exception as e:
            print(f"❌ [DB] Critical Search Error: {e}")
            return None


if __name__ == "__main__":
    db = DynamicDBEngine()
    # Test kar lo yahin pe
    print("\nTest 1 (Name):", db.find_user("priyadarshan"))
    print("\nTest 2 (Question):", db.find_user("Who is the developer?"))