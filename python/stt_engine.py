
from faster_whisper.transcribe import Segment
import speech_recognition as sr
from faster_whisper import WhisperModel
import os

import time


Model_Size = "medium"
Device = "cuda"
Compute_type = "float16"

start_time = time.time()

model =WhisperModel(Model_Size, device=Device, compute_type=Compute_type)
print(f"Model loaded in {time.time() - start_time} seconds")

def  listen_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            audio_raw_data = audio.get_wav_data()
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_raw_data)
            Segments, info = model.transcribe("temp_audio.wav", beam_size=5)
            text = " ".join([Segment.text for Segment in Segments])

            if text.strip():
                print(text)
                return text
            else:
                  print(f"Couldn't process audio properly")
                  return None
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

if __name__ == "__main__":
    try:
        while True:
            text = listen_and_transcribe()
            if text and "exit" in text.lower():
                print("Exiting...")
                break
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        if os.path.exists("temp_audio.wav"):
            os.remove("temp_audio.wav")