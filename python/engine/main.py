from stt_engine import STT_Engine
from tts_engine import TTS_Engine
from llm_engine import LLM_Engine

from vision_pro import Vision_Pro
import colorama

colorama.init(autoreset=True)


class Synapse:
    def __init__(self):
        print(colorama.Fore.CYAN + f"Initializing Synapse AI Engine...")

        self.vision = Vision_Pro()
        self.mouth = TTS_Engine()
        self.ear = STT_Engine()
        self.brain = LLM_Engine()
        self.mouth.speak("Hi there")

    def check_exit(self, text):
        exit_phrases = ["exit", "quit", "stop", "terminate", "bye", "adios"]
        if any(phrase in text.lower() for phrase in exit_phrases):
            return True
        return False

    def start(self):
        while True:
            command = self.ear.listen()
            if command:
                # Exit Check
                if self.check_exit(command.lower()):
                    self.mouth.speak("Goodbye!")
                    break

                # 1. PEHLE NAAM CHECK KARO (DB Lookup).
                detected_name_input = self.brain.get_name(command)

                if detected_name_input:
                    print(f"🔍 Checking DB for input: {detected_name_input}")

                    # 2. Step: Vision se Correct Name + Info mango
                    result = self.vision.get_info(detected_name_input)

                    if result:
                        # 3. Step: UNPACK TUPLE (Correct Name ko alag karo)
                        correct_name, info_data = result

                        natural_sentence = self.brain.generate_info(str(info_data), correct_name)
                        self.mouth.speak(natural_sentence)

                    else:
                        # Agar DB me match nahi mila
                        self.mouth.speak(f"I heard {detected_name_input}, but I don't have their details.")

                    continue

                    # 2. AGAR NAAM NAHI HAI, TO VISION TRIGGERS CHECK KARO (Camera Scan)
                vision_triggers = ["who is this", "who is that", "identify", "scan", "what do you see", "do you know me", "who am I"]

                # .lower() lagana zaroori hai case matching ke liye
                if any(trigger in command.lower() for trigger in vision_triggers):
                    print("📷 Scanning Scene...")
                    detected_people = self.vision.scan_scene()

                    if "Camera Error" in detected_people:
                        self.mouth.speak("My camera is malfunctioned.")

                    elif "Unknown" in detected_people:
                        # Registration flow (agar unknown banda hai)
                        self.handle_registration_flow()

                    else:
                        # Known log dikhe (jo frame me abhi hain)
                        names_str = ", ".join(detected_people)
                        self.mouth.speak(f"I can see {names_str}.")

                    continue

                # 3. FINAL FALLBACK (General Chat)
                # Agar na Naam mila, na Camera trigger mila, tabhi baat karo
                print("💬 General Chat Mode")
                ai_response = self.brain.chat(command)
                self.mouth.speak(ai_response)


    def handle_registration_flow(self):
        self.mouth.speak("I see someone new here, do you want me to remember them? (yes or no)")

        response = self.ear.listen()
        if not response or "yes" not in response.lower():
            self.mouth.speak("Okay, I will ignore them.")
            return

        ret, frame = self.vision.cap.read()
        if not ret:
            self.mouth.speak("I cannot see you, please try again later.")
            return

        self.mouth.speak("Okay, tell me their name and some details about them.")
        name_info = self.ear.listen()

        if not name_info:
            self.mouth.speak("I didn't hear anything. Cancelling.")
            return

        person_data = self.brain.process_name_info(name_info)

        if not person_data:
            self.mouth.speak("I could not understand the details. Please try again.")
            return

        name = person_data.get("name", "Unknown")
        info_string = person_data.get("info", "No details")

        info_dict = {
            "details": info_string,
            "added_on": "Today"
        }

        success = self.vision.register_face(frame, name, info_dict, self.mouth)

        if success:
            self.mouth.speak(f"Done. I've remembered {name}. Details: {info_string}.")
        else:
            self.mouth.speak("Could not see the face clearly. Try again.")


if __name__ == "__main__":
    try:
        app = Synapse()
        app.start()
    except KeyboardInterrupt:
        print(f"Interrupted by user")
