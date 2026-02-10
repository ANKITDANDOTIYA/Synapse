import threading
import time

class AssistantState:
    def __init__(self, music_engine):
        self.music = music_engine
        self.is_listening = False
        self.is_speaking = False
        self.is_processing = False

    def enter_listening_mode(self):
        """Jab mic on ho"""
        self.is_listening = True
        # 🔥 MAGIC: Music dheema karo taaki mic music na sune
        if self.music.is_playing:
            self.music.duck_volume()  # Ye method humne pichle code me banaya tha

    def exit_listening_mode(self):
        """Jab sun liya ho"""
        self.is_listening = False
        # Note: Volume abhi full mat karo, abhi Processing hogi

    def enter_speaking_mode(self):
        """Jab TTS bol raha ho"""
        self.is_speaking = True
        # Music abhi bhi slow rehna chahiye
        if self.music.is_playing:
            self.music.duck_volume()

    def exit_speaking_mode(self):
        """Jab TTS chup ho jaye"""
        self.is_speaking = False
        # 🔥 MAGIC: Ab wapas music tez karo
        if self.music.is_playing and not self.is_listening:
            self.music.restore_volume()