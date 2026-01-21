from stt_engine import STT_Engine
from tts_engine import TTS_Engine
from llm_engine import LLM_Engine
from vision_pro import Vision_Pro
import colorama

colorama.init(autoreset=True)


class Synapse:
    def __init__(self):
        print(colorama.Fore.CYAN + f"Initializing Synapse AI Engine...")

        self.ear = STT_Engine()
        self.mouth = TTS_Engine()
        self.brain = LLM_Engine()
        self.vision = Vision_Pro()
        self.mouth.speak("System Online. Ready for commands, hi my name is sarah how may I help you")

    def check_exit(self, text):
        exit_phrases = ["exit", "quit", "stop", "terminate", "bye", "adios"]
        if any(phrase in text.lower() for phrase in exit_phrases):
            return True
        return False

    def start(self):
        while True:
            command = self.ear.listen()
            if command:
                command = command.lower()
                if self.check_exit(command):
                    self.mouth.speak("Goodbye, see you latter !")
                    break
                vision_triggers = ["who is this", "who is that", "identify", "do you know", "scan this"]
                if any(trigger in command for trigger in vision_triggers):

                    # 1. Class name nahi, Object use karo (self.vision)
                    detected_people = self.vision.scan_scene()

                    # 2. Result handle karo (List aayegi)
                    if not detected_people:
                        self.mouth.speak("I cannot see anyone.")

                    elif "Camera Error" in detected_people:
                        self.mouth.speak("My camera is not working.")


                    else:

                        names_str = ", ".join(detected_people)

                        if "Unknown" in detected_people:
                                self.handle_registration_flow()

                        else:

                            self.mouth.speak(f"I can see {names_str}.")
                else:
                    ai_response = self.brain.chat(command)
                    self.mouth.speak(ai_response)

    def handle_registration_flow(self):
        self.mouth.speak("I see someone new here, please register yourself.")

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

        success = self.vision.register_face(frame, name, info_dict)

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
