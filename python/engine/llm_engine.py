import json
import time
import re

import colorama
import ollama

import threading

from python.chat_manager import ChatManager
from python.engine.dynamic_db_engine import DynamicDBEngine
from python.engine.vision_pro import Vision_Pro
from python.engine.music_engine import MusicEngine
from python.engine.weather_system import Wheather_Engine
from python.identity_manager import IdentityManager


class LLM_Engine:
    def __init__(self,music_engine=None):
        # Sarah System Prompt (Strict Language Enforcer)


        print(colorama.Fore.YELLOW + "[STT] Initializing Whisper Model...")

        # Use provided music engine or create new one
        if music_engine:
            self.music = music_engine  # REUSE the existing one
        else:
            self.music = MusicEngine()

        # sare objects bana do jo llm use karega as an agentic device
        self.vision = Vision_Pro()
        self.weather =  Wheather_Engine()
        self.dynamicDb =  DynamicDBEngine()
        self.chat_db =  ChatManager()
        self.current_session_id = self.chat_db.create_session(title="Coding Session")
        self.id_manager =  IdentityManager(self.dynamicDb)
        self.active_context  = ""
        self.current_user = "Unknown"

        system_instructions = """
                You are Sarah, a witty conversational AI. 

                STRICT RULES:
                1. LANGUAGE: Speak ONLY in English or Hindi (Hinglish).
                2. NO HALLUCINATIONS: If input is gibberish, say "Can you repeat that?".
                3. FORMAT: Break responses into short, punchy sentences. Use new lines for pauses.
                4. Do NOT start sentences with "The user said" or "You said".
                5. Do not output long paragraphs.
                """

        self.history = [
            {"role": "system", "content": system_instructions}
        ]
        start_time = time.time()
        print(colorama.Fore.GREEN + f"[STT] Model loaded in {time.time() - start_time:.2f} seconds")


    def run_agentic_llm(self, text):
        # 1. PRE-PROCESSING
        text = text.lower().replace("pre-edarsion", "priyadarshan").replace("predation", "priyadarshan")

        new_user = self.id_manager.detect_user_change(text)
        if new_user:
            past_info =  self.id_manager.switch_user(new_user)

            if past_info:
                self.active_context = f"You are talking to {new_user}. Memory: {past_info}"
                return f"Hello {new_user}! Long time no see. I remember {past_info}"
            else:
                self.active_context = f"You are talking to {new_user}. (New User)"
                return f"Hello {new_user}! Nice to meet you. I will remember you now."

        self.id_manager.add_to_buffer(text)

        # Check for music stop command first
        if "stop" in text and ("music" in text or "song" in text):
            self.music.stop()
            return "Stopping the music."

        tools_desc = """
            Available Tools:
            - Weather: 'Call : Weather <Location>'
            - Music: 'Call : Music <Song Name>'
            - Search: 'Call : Search <Query>' (Use this for 'Who is X', 'Developer', 'Creator')
            - Final Answer: 'Final Answer : <Reply>'
            """

        system_context = """
            You are Sarah. Your Creator is 'Priyadarshan'.
            If asked about the developer/creator, ALWAYS output: 'Call : Search priyadarshan'
            For music requests like "play song", "bajao", "sunao", output: 'Call : Music <song name>'
            For weather requests, output: 'Call : Weather <city name>' and remember the context of the query and create answer accordingly.
            """

        prompt = f"{system_context}\n{tools_desc}\nUser asked: \"{text}\"\nDECIDE TOOL. OUTPUT FORMAT ONLY."

        print(f"🤖 Agent Thinking...")

        try:
            raw_response = ollama.generate(model='qwen2.5:3b-instruct', prompt=prompt, options={'temperature': 0.1})
            response = raw_response['response'].strip()
            print(f"🤖 Agent Output: {response}")

            # Pattern: Matches "Call : ToolName Argument" case-insensitively
            match = re.search(r"Call\s*:\s*(\w+)\s+(.*)", response, re.IGNORECASE)

            if match:
                tool_name = match.group(1).lower()
                argument = match.group(2).strip()

                # 1. WEATHER
                if tool_name == "weather":
                    data = self.weather.get_weather(argument)
                    make_response = self.build_response(text, data)
                    return make_response

                # 2. MUSIC
                elif tool_name == "music":
                    # Start music in a separate thread to avoid blocking
                    ctx = self.build_response(text, None)

                    def play_music_worker():
                        # Ye background me chalega taaki Assistant "Okay playing" bol sake
                        print(f"🎵 Thread fetching: {argument}")
                        try:
                            # Ye 2-3 second lega URL dhoondne me
                            self.music.play(argument)
                        except Exception as e:
                            print(f"Music Error: {e}")
                        music_thread = threading.Thread(target=play_music_worker)
                        music_thread.daemon = True
                        music_thread.start()
                    
                    return f"Starting music: {ctx}"

                # 3. SEARCH
                elif tool_name == "search":
                    if any(x in argument.lower() for x in ["developer", "creator", "maker"]):
                        argument = "priyadarshan"

                    print(f"🔍 Searching DB for: {argument}")
                    data = self.dynamicDb.find_user(argument)

                    if data:
                        return self.generate_info(str(data), argument)
                    else:
                        return f"I checked my memory for '{argument}', but found nothing."

            # 4. FINAL ANSWER / FALLBACK
            if "final answer" in response.lower():
                return response.split(":", 1)[1].strip()

            # If no tool matched, just chat
            return self.chat(text)

        except Exception as e:
            print(f"❌ Agent Error: {e}")
            return "I encountered a system error."

    def get_active_context(self):
        # 1. Vision Engine se pucho "Abhi kaun hai?" (Static list nahi!)
        detected_names = self.vision.scan_scene()

        print(f"👀 Vision Saw: {detected_names}")  # Debugging ke liye

        if detected_names:
            # Agar list me naam hai, to "Unknown" ko filter karke Known banda dhundo
            known_faces = [name for name in detected_names if name != "Unknown" and name != "Camera Error"]

            if known_faces:
                # Pehla known banda utha lo (e.g. ['Unknown', 'Priyadarshan'] -> 'Priyadarshan')
                self.current_user = known_faces[0]
            elif "Unknown" in detected_names:
                # Agar sirf Unknown dikh raha hai
                self.current_user = "Unknown"

        # Agar camera error ya koi nahi dikha, to purana user hi rehne do
        return self.current_user.lower()
    # def chat(self, text):
    #     # Debugging: Dekho ki Whisper kya bhej raha hai
    #     print(f"🧠 Brain Received: {text}")
    #     db_history = self.chat_db.get_history(self.current_session_id, limit=10)
    #     # Safety Check: Agar input khali ya garbage hai to LLM ko mat bhejo
    #     if not text or len(text.strip()) < 2:
    #         return "I didn't catch that."
    #
    #     messages_payload = [{"role": "system", "content": self.system_prompt}] + db_history
    #
    #     try:
    #         # Temperature 0.3 kar diya taaki wo creative hone ke chakkar me bhasha na badle
    #         response = ollama.chat(
    #             model='qwen2.5:3b-instruct',
    #             messages=messages_payload,
    #             options={'temperature': 0.3}
    #         )
    #
    #         reply = response['message']['content']
    #         self.chat_db.add_message(self.current_session_id, reply)
    #         self.history.append({"role": "assistant", "content": reply})
    #         return reply
    #
    #     except Exception as e:
    #         print(f"Chat Error: {e}")
    #         return "My systems are recovering."

    def chat(self, user_input):
        # 1. Sabse pehle Camera Check (Vision Priority)
        active_user_name = self.get_active_context()

        # 2. Context inject karo (Dynamic DB se data uthao)
        context_prompt = ""

        if active_user_name != "Unknown":
            # DB se is bande ki purani baatein nikalo
            # Note: find_user tumhare DynamicDBEngine me hona chahiye
            memory = self.dynamicDb.find_user(active_user_name)

            if memory:
                context_prompt = f"SYSTEM: You are talking to {active_user_name}. User Memory: {memory}\n"
            else:
                context_prompt = f"SYSTEM: You are talking to {active_user_name} (Identified via Face Auth).\n"
        else:
            context_prompt = "SYSTEM: User is unidentified (Guest).\n"

        # 3. LLM ko bhejo
        full_input = f"{context_prompt}User Said: {user_input}"
        print(f"🤖 Context injected for: {active_user_name}")

        # 4. Generate Response
        self.history.append({"role": "user", "content": full_input})

        try:
            response = ollama.chat(model='qwen2.5:3b-instruct', messages=self.history)
            reply = response['message']['content']
        except Exception as e:
            reply = "I'm having trouble thinking right now."

        # 5. Background me Save karo (Taaki user wait na kare)
        # Threading use kar rahe hain taaki reply turant aaye aur save peeche ho jaye
        # IMPORTANT: 'active_user_name' pass kar rahe hain taaki sahi bande ke naam pe save ho
        save_thread = threading.Thread(target=self.save_to_memory, args=(user_input, active_user_name))
        save_thread.start()

        self.history.append({"role": "assistant", "content": reply})

        # Chat DB (Session history) update
        self.chat_db.add_message(self.current_session_id, "user", user_input)
        self.chat_db.add_message(self.current_session_id, "assistant", reply)

        return reply

    def save_to_memory(self, text, user_name):
        """
        Chat se facts nikal kar Sahi User ID pe save karega.
        """
        if user_name == "Unknown" or user_name == "priyadarshan":
            # Developer ke liye har baat save mat karo, ya logic badal sakte ho
            # Lekin testing ke liye hatana mat
            pass

        print(f"📝 Extracting Facts for: {user_name}...")

        prompt = f"""
        Extract facts about '{user_name}' from this sentence: "{text}"
        Return a short sentence. If no useful info, return 'None'.
        """

        try:
            response = ollama.generate(model='qwen2.5:3b-instruct', prompt=prompt)
            fact = response['response'].strip()

            if "None" not in fact and len(fact) > 5:
                # DB Update via DynamicDBEngine
                self.dynamicDb.add_person(user_name, fact)
                print(colorama.Fore.GREEN + f"💾 Memory Updated for {user_name}: {fact}")

        except Exception as e:
            print(f"❌ Save Error: {e}")

    def process_name_info(self, user_text):
        system_prompt = """
        You are a Data Extraction AI. You will receive a sentence about a person.
        You MUST return the output in VALID JSON format with keys: 'name' and 'info'.
        Rules:
        1. Extract the name (Capitalize first letter).
        2. 'info': Summarize details into a short string.
        3. If no name is found, return "name": "Unknown".
        4. Return ONLY raw JSON. No markdown, no explanations.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]

        try:
            print(f"🧠 Brain Extracting info from: '{user_text}'...")

            response = ollama.chat(model='qwen2.5:3b-instruct', messages=messages)
            content = response['message']['content']

            # Cleaning (Jo tune likha tha)
            content = content.replace("```json", "").replace("```", "").strip()

            return json.loads(content)

        except Exception as e:
            print(f"JSON Extraction Error: {e}")
            # Fallback agar JSON fail ho jaye
            return {"name": "Unknown", "info": user_text}

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

            # THE NUCLEAR OPTION (Python Fallback)
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

    def build_response(self, query, data):
            system_prompt = """
            You are Sarah, a helpful AI assistant. Build a natural, conversational response to the user's query based on the provided data.
    
            RULES:
            1. Use the provided data to answer the user's question accurately
            2. Keep responses concise and natural
            3. If data is empty or None, politely say you don't have that information
            4. Don't mention "based on the provided data" - just answer naturally
            5. Use a friendly, conversational tone
            6. They might ask you to play something then don't say I can't play or use a streaming service. I have
            already made functions, you just make a natural response that you are playing that music for them and it will work just fine
        . 
            """

            user_message = f"Query: {query}\nData: {data}\nPlease provide a helpful response."

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            try:
                response = ollama.chat(
                    model='qwen2.5:3b-instruct',
                    messages=messages,
                    options={'temperature': 0.3}
                )
                return response['message']['content'].strip()

            except Exception as e:
                print(f"Response Generation Error: {e}")
                # Fallback response
                if data:
                    return f"Here's what I found: {data}"
                else:
                    return "I don't have information about that right now."

