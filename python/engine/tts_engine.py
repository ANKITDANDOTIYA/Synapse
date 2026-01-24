import edge_tts
import pygame
import asyncio
import io
import time
import re


class TTS_Engine:
    def __init__(self):
        pygame.mixer.init()

        # Voice Settings
        # Note: Hinglish ke liye Swara/Madhur best hain, bhale hi script english ho.
        self.hindi_voice = "hi-IN-SwaraNeural"
        self.english_voice = "en-US-AriaNeural" # english bolegi

    def detect_language(self, text):
        """
        Modified Logic:
        1. Check Devanagari (Proper Hindi)
        2. Check Hinglish Keywords (Latin Script Hindi)
        """
        text_lower = text.lower()

        #  Check Devanagari script (अ, आ, क...)
        if re.search(r'[\u0900-\u097F]', text):
            return "hi"

        #  Check Hinglish Keywords
        # Ye common shabd hain jo english sentences mein nahi hote
        hinglish_triggers = [
            "hai", "hian", "kya", "nahi", "nahin", "main", "tum", "aap", "hum",
            "bhai", "yaar", "arre", "are", "kaise", "thik", "theek", "acha",
            "bohot", "bahut", "samajh", "lekin", "magar", "kyunki", "kaun",
            "kaha", "kab", "kuch", "matlab", "shukriya", "dhanyavad", "namaste"
        ]

        # Check if any trigger word exists in text
        # 'space' check zaroori hai taaki "main" (hindi) aur "main" (english) confuse na ho,

        for word in hinglish_triggers:
            # Word boundary check (\b) taaki "that" mein "ha" match na ho jaye
            if re.search(r'\b' + word + r'\b', text_lower):
                return "hi"

        return "en"

    def determine_emotion(self, text):
        rate = "+0%"
        pitch = "+0Hz"

        if "!" in text:
            rate = "+10%"
            pitch = "+5Hz"
        elif "..." in text or "sad" in text.lower():
            rate = "-10%"
            pitch = "-5Hz"
        elif "?" in text:
            pitch = "+2Hz"

        return rate, pitch

    async def _generate_audio(self, text, voice, rate, pitch):
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        audio_data = io.BytesIO()

        async for chunk in communicate.stream():
            if chunk['type'] == 'audio':
                audio_data.write(chunk['data'])

        audio_data.seek(0)
        return audio_data

    def speak(self, text):
        # 1. Detect Language
        lang = self.detect_language(text)

        if lang == "hi":
            selected_voice = self.hindi_voice
            print(f"[AI - Hindi ({selected_voice})]: {text}")
        else:
            selected_voice = self.english_voice
            print(f"[AI - English ({selected_voice})]: {text}")

        # 2. Emotion
        rate, pitch = self.determine_emotion(text)

        # 3. Async & Play
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        mp3_fp = loop.run_until_complete(self._generate_audio(text, selected_voice, rate, pitch))

        pygame.mixer.music.load(mp3_fp)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)


if __name__ == "__main__":
    tts = TTS_Engine()

    try:
      # trigger Swara
        tts.speak("Arre yaar! Ye code finally chal gaya! Maza aa gaya bhai!")
        time.sleep(1)

        # trigger Swara
        tts.speak("Lekin... abhi bhi ek error aa raha hai... samajh nahi aa raha kya karun.")
        time.sleep(1)

        # Should trigger Aria
        tts.speak("System initialization complete. Switching to English mode.")
        time.sleep(1)

        #  trigger Swara
        tts.speak("नमस्ते, सब ठीक है?")

    except KeyboardInterrupt:
        print("\nStopped.")