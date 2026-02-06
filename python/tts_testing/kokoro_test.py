import threading
import pygame
import io
import soundfile as sf
from kokoro_onnx import Kokoro
import re
import os
import urllib.request
import time
import numpy as np  # Numpy import zaroori hai fix ke liye



class TTS_Engine:
    _is_speaking = False
    _stop_event = threading.Event()
    _current_thread = None
    _kokoro = None

    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # 1. Sahi files download karo (.bin NOT .json)
        self._ensure_models_exist()

        if TTS_Engine._kokoro is None:
            print("Loading Kokoro ONNX Model...")

            # --- THE FIX: MONKEY PATCHING NUMPY ---
            # Hum np.load ko temporary hack kar rahe hain taaki wo pickle allow kare
            # Kyunki kokoro ki voices file pickled format me hai
            original_load = np.load
            np.load = lambda *args, **kwargs: original_load(*args, **kwargs, allow_pickle=True)

            try:
                # Dhyan de: Yahan 'voices.bin' pass karna hai, json nahi
                TTS_Engine._kokoro = Kokoro("kokoro-v0_19.onnx", "voices.bin")
                print("Kokoro Loaded Successfully.")
            finally:
                # Wapas original state me lao (Safety first)
                np.load = original_load

        # Voice Settings
        self.hindi_voice = "af_sarah"
        self.english_voice = "af_sarah"

    def _ensure_models_exist(self):
        """Auto-download correct .bin files"""
        # Note: File name changed to voices.bin
        files = ["kokoro-v0_19.onnx", "voices.bin"]
        base_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/"

        for file in files:
            if not os.path.exists(file):
                print(f"Downloading {file}...")
                try:
                    urllib.request.urlretrieve(base_url + file, file)
                    print(f"Downloaded {file}")
                except Exception as e:
                    print(f"Failed to download {file}: {e}")

    @classmethod
    def stop(cls):
        cls._is_speaking = False
        cls._stop_event.set()

        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

    def speak(self, text):
        TTS_Engine.stop()
        TTS_Engine._stop_event.clear()
        TTS_Engine._is_speaking = True

        TTS_Engine._current_thread = threading.Thread(
            target=self._run_speech_generation,
            args=(text,)
        )
        TTS_Engine._current_thread.start()

    def _run_speech_generation(self, text):
        try:
            lang = self.detect_language(text)
            voice_name = self.hindi_voice if lang == "hi" else self.english_voice
            print(f"[AI - Kokoro ({voice_name})]: {text}")

            if TTS_Engine._stop_event.is_set(): return

            # Speed adjustment
            speed = 0.9 if lang == "hi" else 1.0

            # Generate Audio
            samples, sample_rate = TTS_Engine._kokoro.create(
                text,
                voice=voice_name,
                speed=speed,
                lang="en-us"
            )

            if TTS_Engine._stop_event.is_set(): return

            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, samples, sample_rate, format='WAV')
            audio_buffer.seek(0)

            if TTS_Engine._stop_event.is_set(): return

            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy() and TTS_Engine._is_speaking:
                if TTS_Engine._stop_event.is_set():
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)

        except Exception as e:
            print(f"Kokoro Error: {e}")
        finally:
            TTS_Engine._is_speaking = False

    def detect_language(self, text):
        text_lower = text.lower()
        if re.search(r'[\u0900-\u097F]', text): return "hi"

        hinglish_triggers = [
            "hai", "hian", "kya", "nahi", "nahin", "main", "tum", "aap", "hum",
            "bhai", "yaar", "arre", "are", "kaise", "thik", "theek", "acha",
            "bohot", "bahut", "samajh", "lekin", "magar", "kyunki", "kaun",
            "kaha", "kab", "kuch", "matlab", "shukriya", "dhanyavad", "namaste"
        ]

        for word in hinglish_triggers:
            if re.search(r'\b' + word + r'\b', text_lower): return "hi"
        return "en"


if __name__ == "__main__":
    tts = TTS_Engine()

    print("Test 1: Hindi (Immersive)")
    # Wahi deep script jo tune maangi thi
    tts.speak("मैं हमेशा से अपने सपनों को सच करने के लिए मेहनत करती आई हूँ। बचपन से ही मुझे पढ़ाई और नई चीज़ें सीखने का शौक रहा है। जब लोग कहते थे कि यह काम लड़कियों के लिए मुश्किल है, तो मैं और भी दृढ़ निश्चय के साथ आगे बढ़ती थी। मुझे लगता है कि एक स्त्री के लिए आत्मनिर्भर होना सबसे बड़ी ताकत है। आज मैं अपने पैरों पर खड़ी हूँ, अपने फैसले खुद लेती हूँ और अपने परिवार का सहारा बनी हूँ। जीवन में चुनौतियाँ आईं, लेकिन हर बार मैंने उन्हें एक नए अवसर की तरह अपनाया। मुझे गर्व है कि मैं अपनी पहचान खुद बना रही हूँ और दूसरों के लिए प्रेरणा बन रही हूँ।")
    time.sleep(2)
    # tts.speak("I could feel the rain soaking through my sweater, but I didn’t care. Each drop seemed to wash away a little of the heaviness I’d been carrying all week. People hurried past me with umbrellas and frowns, but I just stood there, letting the cold seep into my skin. Maybe it was foolish, maybe even reckless, but in that moment, I felt strangely alive—like the world had finally slowed down enough for me to breathe.")

    # Wait loop taaki main thread band na ho jaye
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tts.stop()