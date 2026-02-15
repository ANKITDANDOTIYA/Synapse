import re
import ollama


class IdentityManager:
    def __init__(self, db_engine):
        self.db = db_engine
        self.current_user = "Unknown"  # Default
        self.user_memory_buffer = []  # Sirf current user ki batein

    def detect_user_change(self, text):
        """
        Check karega agar koi naya banda aaya hai.
        """
        system_prompt = """
        Analyze the sentence. Is someone introducing themselves?
        Return JSON: {"new_user": "Name"} or {"new_user": null}

        Examples:
        "Hi I am Ankit" -> {"new_user": "Ankit"}
        "This is Priya speaking" -> {"new_user": "Priya"}
        "Mera naam Rahul hai" -> {"new_user": "Rahul"}
        "What is the weather?" -> {"new_user": null}
        """

        try:
            # Fast check using regex first (Optimization)
            patterns = [
                r"i am (\w+)", r"my name is (\w+)", r"this is (\w+)", r"(\w+) here"
            ]
            for pat in patterns:
                match = re.search(pat, text.lower())
                if match:
                    name = match.group(1).capitalize()
                    # Common words filter karein taaki "I am happy" ko naam na maan le
                    if name not in ["Happy", "Sad", "Here", "Speaking", "Listening"]:
                        return name

            # Agar regex fail ho, tab LLM se pucho (More accurate)
            # (Optional: Isse skip kar sakte ho speed ke liye)
            return None

        except Exception:
            return None

    def switch_user(self, new_name):
        if new_name and new_name != self.current_user:
            print(f"🔄 Switching Context: {self.current_user} ➡️ {new_name}")

            # 1. Purane user ki memory save kar do jaane se pehle
            self.save_buffer_to_db()

            # 2. Naya user set karo
            self.current_user = new_name
            self.user_memory_buffer = []  # Buffer clear

            # 3. DB se naye user ka purana data laao
            existing_data = self.db.find_user(new_name)
            return existing_data  # Ye LLM ko context me denge

        return None

    def add_to_buffer(self, text):
        self.user_memory_buffer.append(text)

        # Agar buffer bada ho gaya (e.g. 5 lines), to DB me save kardo
        if len(self.user_memory_buffer) >= 3:
            self.save_buffer_to_db()

    def save_buffer_to_db(self):
        if not self.user_memory_buffer or self.current_user == "Unknown":
            return

        text_blob = " ".join(self.user_memory_buffer)

        # Extraction Logic
        prompt = f"""
        Extract facts about '{self.current_user}' from this text:
        "{text_blob}"
        Return a short summary sentence. If no facts, return 'None'.
        """
        try:
            res = ollama.generate(model='qwen2.5:3b-instruct', prompt=prompt)
            fact = res['response'].strip()

            if "None" not in fact and len(fact) > 5:
                print(f"💾 Saving Memory for {self.current_user}: {fact}")
                self.db.add_person(self.current_user, fact)
                self.user_memory_buffer = []  # Reset buffer
        except Exception as e:
            print(f"Save Error: {e}")