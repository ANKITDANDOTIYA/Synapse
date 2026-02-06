import pyaudio
import pygame

from python.engine.music_engine import MusicEngine
from python.engine.weather_system import Wheather_Engine
from stt_engine import STT_Engine
from tts_engine import TTS_Engine
from llm_engine import LLM_Engine

import os

import threading
import numpy as np

from openwakeword import Model

from vision_pro import Vision_Pro
import colorama
import time

colorama.init(autoreset=True)


class Synapse:
    def __init__(self):
        print(colorama.Fore.CYAN + f"Initializing Synapse AI Engine...")

        self.vision = Vision_Pro()
        self.mouth = TTS_Engine()
        self.ear = STT_Engine()
        self.brain = LLM_Engine()
        self.music = MusicEngine()
        self.weather =  Wheather_Engine()
        self.MIC_INDEX = 1
        self.manual_music_mode = False
        models_path = r"E:\MyProjects\CPP\Trinetra_Vision\src\hey_jarvis.onnx"
        self.model = Model(wakeword_models=[models_path])
        self.mouth.speak("Hi there")

    def check_exit(self, text):
        if any(word in text for word in ["music", "song", "gana", "playing"]):
            return False
        exit_phrases = ["exit", "quit", "stop", "terminate", "bye", "adios", "chal thik hai", "milte hai"]
        if any(phrase in text.lower() for phrase in exit_phrases):
            return True
        return False

    def start(self):


        # ... baki imports ...

        while True:
            try:
                command = None  # Har baar reset karo
                audio = None

                # --- STEP 1: STATUS CHECK ---
                hardware_status = self.music.check_status()

                # Agar hardware bajne laga, to manual flag hata do (Auto-sync)
                if hardware_status:
                    self.manual_music_mode = False

                # Decision: Kya Music Mode chalana hai?
                is_music_mode = hardware_status or self.manual_music_mode

                # --- STEP 2: LISTENING MODES ---

                # MODE A: MUSIC PLAYING (Wake Word)
                if is_music_mode:
                    if not hasattr(self, 'stream_music_mode'):
                        import pyaudio
                        self.p_audio = pyaudio.PyAudio()
                        self.stream_music_mode = self.p_audio.open(
                            format=pyaudio.paInt16,
                            channels=1,
                            rate=16000,
                            input=True,
                            frames_per_buffer=1280,
                            input_device_index= self.MIC_INDEX
                        )

                    try:
                        # 1. Read Audio Chunk
                        raw_audio = self.stream_music_mode.read(1280, exception_on_overflow=False)
                        audio_np = np.frombuffer(raw_audio, dtype=np.int16)

                        # 2. Predict
                        prediction = self.model.predict(audio_np)

                        # 3. Key Matching
                        max_score = 0.0
                        for key, score in prediction.items():
                            if "jarvis" in key.lower() or "sarah" in key.lower():
                                max_score = score
                                break

                        # 4. Action
                        if max_score > 0.5:
                            print(f"🚨 Wake Word Detected! (Score: {max_score:.2f})")

                            try:
                                pygame.mixer.music.set_volume(0.1)  # Direct 0.1 bhejo
                            except:
                                pass

                            # CRITICAL: Mic Free Karo
                            self.stream_music_mode.stop_stream()
                            self.stream_music_mode.close()
                            self.p_audio.terminate()
                            del self.stream_music_mode
                            del self.p_audio

                            time.sleep(0.5)

                            # Google Listen
                            print("👂 Listening for command...")
                            try:
                                _, command = self.ear.listen()
                            except Exception as e:
                                command = None

                            self.music.restore_volume()

                            # Agar command nahi mili to wapas loop me
                            if not command:
                                continue

                        else:
                            continue  # Wake word nahi mila, loop continue

                    except Exception as e:
                        continue

                # MODE B: NORMAL LISTENING (Jab Music Band Ho)
                else:
                    # Cleanup: Agar galti se stream khuli reh gayi
                    if hasattr(self, 'stream_music_mode'):
                        try:
                            self.stream_music_mode.close()
                            self.p_audio.terminate()
                            del self.stream_music_mode
                            del self.p_audio
                        except:
                            pass

                    # Normal Listen
                    try:
                        audio, command = self.ear.listen()
                    except:
                        command = None

                # --- STEP 3: PROCESSING PHASE ---

                if command:
                    print(f"🎤 Heard: {command}")
                    command_lower = command.lower()

                    if "stop" in command_lower and ("music" in command_lower or "song" in command_lower):
                        print("🛑 Stopping Music...")
                        self.music.stop()  # Ensure MusicEngine me 'stop()' function ho
                        self.mouth.speak("Stopping the music.")

                        # Important: Music Mode ko False kar do taaki loop wapas Normal Mode me chala jaye
                        self.manual_music_mode = False
                        continue

                    # 1. EXIT CHECK
                    if self.check_exit(command_lower):
                        self.vision.close_camera()
                        self.mouth.speak("Goodbye!")
                        print("Stopping Synapse...")
                        os._exit(0)

                    # 2. MUSIC TRIGGERS
                    music_triggers = ["play", "bajao", "sunao", "song", "music", "gana"]
                    if any(trigger in command_lower for trigger in music_triggers):
                        song_name = self.brain.play_music(command_lower)

                        if song_name and song_name.lower() not in ["unknown", "none"]:
                            print(f"🎵 Extracting Song: {song_name}")
                            self.mouth.speak(f"Sure, playing {song_name}.")

                            # Flag ON karo taaki agle loop me Music Mode me jaye
                            self.manual_music_mode = True

                            t = threading.Thread(target=self.music.play, args=(song_name,))
                            t.start()

                            print("[System] Waiting for music to start...")
                            time.sleep(2)
                            continue
                        else:
                            self.mouth.speak("I couldn't understand the song name.")
                        continue
                    city = self.brain.get_weather_city(command_lower)
                    # if city is not None:
                    #

                    # 3. REGISTRATION TRIGGERS
                    registration_triggers = ["remember this person", "add a new person", "remember me"]
                    if any(trigger in command_lower for trigger in registration_triggers):
                        print("📝 Switching to Registration Mode...")
                        self.handle_registration_flow()
                        continue

                    # 4. VISION TRIGGERS
                    vision_triggers = ["who is this", "what do you see", "scan"]
                    if any(trigger in command_lower for trigger in vision_triggers):
                        print("📷 Scanning Scene...")
                        detected_people = self.vision.scan_scene()

                        if not detected_people:
                            self.mouth.speak("I don't see anyone.")
                        elif "Unknown" in detected_people:
                            self.mouth.speak("I see someone, but I don't know them.")
                        else:
                            names_str = ", ".join(detected_people)
                            self.mouth.speak(f"I can see {names_str}.")
                        continue

                    # 5. DB NAME LOOKUP
                    detected_name_input = self.brain.get_name(command)
                    if detected_name_input:
                        result = self.vision.get_info(detected_name_input)
                        if result:
                            correct_name, info_data = result
                            natural_sentence = self.brain.generate_info(str(info_data), correct_name)
                            self.mouth.speak(natural_sentence)
                        else:
                            self.mouth.speak(f"I don't have details for {detected_name_input}.")
                        continue

                    # 6. GENERAL CHAT (Fallback)
                    print(f"💬 General Chat: {command}")
                    ai_response = self.brain.chat(command)
                    self.mouth.speak(ai_response)

            except KeyboardInterrupt:
                print("\nStopping Synapse...")
                break
            except Exception as e:
                print(f"Critical Error in Main Loop: {e}")
                time.sleep(1)

    def handle_registration_flow(self, auto_trigger=False):

        def wait_for_sarah():
            time.sleep(0.5)
            while self.mouth._is_speaking:
                time.sleep(0.1)

        #  CONTEXT CHECK (Unknown Face Trigger)
        if auto_trigger:
            self.mouth.speak("I see someone new. Do you want me to remember them?")
            wait_for_sarah()

            # Jab tak Haan/Na nahi milta, yahi rukenge
            print("[System] Waiting for User Decision (Yes/No)...")
            decision_made = False

            # 3 Attempts denge user ko
            for _ in range(3):
                response = self.ear.listen()

                if not response:
                    continue  # Kuch nahi suna, fir se suno

                if any(w in response.lower() for w in ["yes", "haan", "yep", "sure", "ok"]):
                    decision_made = True
                    break
                elif any(w in response.lower() for w in ["no", "nah", "nahi", "cancel"]):
                    self.mouth.speak("Okay, ignoring.")
                    return  # Exit function

            # Agar 3 baar sunne ke baad bhi koi jawab nahi
            if not decision_made:
                self.mouth.speak("No response. Ignoring for now.")
                return

        # NAME GATHERING
        self.mouth.speak("Okay, tell me their name.")
        wait_for_sarah()

        final_name = None
        final_info = ""
        attempts = 0

        while attempts < 3:
            print(f"[System] Listening for Name (Attempt {attempts + 1})...")
            user_input = self.ear.listen()

            if not user_input:
                self.mouth.speak("I didn't hear anything. Please say the name.")
                wait_for_sarah()
                continue

            if "cancel" in user_input.lower():
                self.mouth.speak("Registration cancelled.")
                return

            # Brain se Name extract karo
            person_data = self.brain.process_name_info(user_input)
            extracted_name = person_data.get("name", user_input)
            extracted_info = person_data.get("info", "")

            if extracted_name == "Unknown":
                self.mouth.speak("I couldn't understand the name. Please try again.")
                wait_for_sarah()
                continue

            # SMART CONFIRMATION
            self.mouth.speak(f"I heard {extracted_name}. Is that correct?")
            wait_for_sarah()

            confirm = self.ear.listen()

            if confirm and any(w in confirm.lower() for w in ["yes", "haan", "sahi", "right", "correct"]):
                final_name = extracted_name
                if len(extracted_info) > 2:
                    final_info = extracted_info
                break
            else:
                self.mouth.speak("Sorry. Please say the name again.")
                wait_for_sarah()

            attempts += 1

        if not final_name:
            self.mouth.speak("I am struggling to hear. Let's try later.")
            return

        # EXISTING USER CHECK (Ye Naya Logic Hai)
        # Vision engine se poocho kya ye banda pehle se hai?
        existing_info = self.vision.check_person_exists(final_name)

        if existing_info:
            current_details = existing_info.get("details", "No details provided")
            self.mouth.speak(f"Wait, I already know {final_name}. You told me: {current_details}.")
            wait_for_sarah()

            self.mouth.speak("Do you want to update this information?")
            wait_for_sarah()

            update_response = self.ear.listen()

            # Agar user bole "Yes" ya "Update"
            if update_response and any(w in update_response.lower() for w in ["yes", "haan", "update", "change"]):
                self.mouth.speak(f"Okay, tell me, who is {final_name} now?")
                wait_for_sarah()

                new_details = self.ear.listen()
                if new_details:
                    new_info_dict = {"details": new_details, "added_on": time.strftime("%Y-%m-%d"), "updated": True}

                    # DB Update Call
                    if self.vision.update_person_info(final_name, new_info_dict):
                        self.mouth.speak(f"Done. I have updated the information for {final_name}.")
                    else:
                        self.mouth.speak("Failed to update database.")
                else:
                    self.mouth.speak("I didn't hear anything. Keeping old info.")
            else:
                self.mouth.speak("Okay, keeping the existing information.")

            return  # (Photo lene ki zaroorat nahi hai)

        # MANDATORY INFO (Sirf New Users Ke Liye)
        if len(final_info) < 5:
            self.mouth.speak(
                f"Got it, {final_name}. Now, tell me, who is he? What do you want me to remember about him?")
            wait_for_sarah()

            details_input = self.ear.listen()

            if details_input and len(details_input) > 2:
                final_info = details_input
            else:
                final_info = "Just a friend."  # Fallback default
                self.mouth.speak("Okay, I'll just remember him as a friend.")
                wait_for_sarah()

        # STEP 5: VISION REGISTRATION (Photo Session)
        self.mouth.speak(f"Registering {final_name}. Look at the camera.")
        wait_for_sarah()

        ret, frame = self.vision.cap.read()
        if ret:
            info_dict = {"details": final_info, "added_on": time.strftime("%Y-%m-%d")}
            success = self.vision.register_face(frame, final_name, info_dict, self.mouth)

            if not success:
                self.mouth.speak("Face capture failed.")
        else:
            self.mouth.speak("Camera error.")


if __name__ == "__main__":
    try:
        app = Synapse()
        app.start()
    except KeyboardInterrupt:
        print(f"Interrupted by user")
