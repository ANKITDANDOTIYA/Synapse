import json

import ollama


class LLM_Engine:
    def __init__(self):
        # Sarah System Prompt (Strict Language Enforcer)
        system_instructions = """
        You are Sarah, a witty and helpful AI Assistant.

        STRICT RULES:
        1. LANGUAGE: You must speak ONLY in English or Hindi (Hinglish).
        2. NO HALLUCINATIONS: If the user input is gibberish, random characters, or a language you don't understand, simply ask "Can you repeat that?"
        3. HINDI SUPPORT: If the user speaks Hindi, reply in Hinglish (Hindi written in English alphabet).
        4. Do NOT generate text in Spanish, French, Welsh, or any other language.
        5. Keep answers short and direct.
        """

        self.history = [
            {"role": "system", "content": system_instructions}
        ]

    def chat(self, text):
        # Debugging: Dekho ki Whisper kya bhej raha hai
        print(f"🧠 Brain Received: {text}")

        # Safety Check: Agar input khali ya garbage hai to LLM ko mat bhejo
        if not text or len(text.strip()) < 2:
            return "I didn't catch that."

        self.history.append({"role": "user", "content": text})

        try:
            # Temperature 0.3 kar diya taaki wo creative hone ke chakkar me bhasha na badle
            response = ollama.chat(
                model='qwen2.5:3b-instruct',
                messages=self.history,
                options={'temperature': 0.3}
            )

            reply = response['message']['content']
            self.history.append({"role": "assistant", "content": reply})
            return reply

        except Exception as e:
            print(f"Chat Error: {e}")
            return "My systems are recovering."

    def process_name_info(self, user_text):
        system_prompt = """
        You are a Data Extraction AI. You will receive a sentence about a person.
        You MUST return the output in VALID JSON format with keys: 'name' and 'info'.
        Rules:
        1. Extract the name.
        2. 'info': Summarize details into a short string.
        3. Return ONLY raw JSON. No markdown.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
        try:
            response = ollama.chat(model='qwen2.5:3b-instruct', messages=messages)
            content = response['message']['content']
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"JSON Error: {e}")
            return None

    def get_name(self, text):
        # DEBUG PRINT: Whisper output check karne ke liye
        print(f"🧠 Brain Input: '{text}'")

        system_prompt = """
        ROLE: You are an Entity Extraction Bot. 
        TASK: Extract the NAME of the person mentioned in the user's command.

        RULES:
        1. Return ONLY the name. Nothing else.
        2. Do NOT chat. Do NOT mention Bollywood or movies.
        3. If no name is found, return "None".
        4. Fix spelling if it looks like a common Indian name.

        User: "Who is Ankit?" Output: Ankit
        User: "Tell me about Priyadarshan Garg" Output: Priyadarshan Garg
        User: "What is the time?" Output: None
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        try:
            response = ollama.chat(model='qwen2.5:3b-instruct', messages=messages)
            content = response['message']['content'].strip()

            # --- CRITICAL FIX ---
            # Agar Qwen ne bola "None", to asli Python None return karo
            if "None" in content or content == "":
                return None

            # Agar Qwen ne galti se "Output: Ankit" likh diya, to saaf karo
            content = content.replace("Output:", "").strip()

            return content
        except Exception as e:
            print(f"Couldn't get the name: {e}")
            return None

    def generate_info(self, json_text, name):
        # 1. System Prompt (Strict Rules)
        system_prompt = f"""
                ROLE: You are Jarvis, an AI Assistant. 
                TASK: You are describing a person named '{name}' to the user based on the provided database info.

                CRITICAL RULES (Pronoun Correction):
                1. You are talking ABOUT {name}. Use "He", "She", or "They".
                2. NEVER refer to {name} as "I", "Me", or "My". 
                4. If there is "you" in sentence use "me" , like creator of you convert it to "creator of me"   
                3. If the data says "I am the admin", you MUST convert it to "{name} is the admin" or "He is the admin".
                4. Do not output JSON. Output a natural sentence.

                Example Input: {{ "name": "Rahul", "info": "I am a doctor" }}
                Example Output: Rahul is a doctor. (NOT "I am a doctor")
                """

        # 2. User Prompt (Wrapper trick)
        user_message = f"Tell me about {name} using this data: {json_text}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            response = ollama.chat(model='qwen2.5:3b-instruct', messages=messages)
            content = response['message']['content'].strip()

            # --- THE NUCLEAR OPTION (Python Fallback) ---
            if content.startswith('{') or "{" in content:
                print("⚠️ LLM failed (Gave JSON). Using Python fallback.")
                try:
                    data = json.loads(json_text.replace("'", '"'))
                    info_val = data.get('info', 'known person')
                    content = f"Yes, I know {name}. {info_val}."
                except:
                    content = f"Yes, I know {name}, but I cannot read the details right now."

            content = content.replace('"', '').replace("'", "")
            return content

        except Exception as e:
            print(f"Error in generate_info: {e}")
            return f"I know {name}."