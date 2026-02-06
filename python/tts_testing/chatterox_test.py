import sounddevice as sd
import soundfile as sf
import os
import numpy as np

# 1. Path set karo (Wahi purana wala)
folder_path = r"E:\MyProjects\CPP\Trinetra_Vision\python\tts_testing"
file_path = os.path.join(folder_path, "voice_ref.wav")

# Folder verify
os.makedirs(folder_path, exist_ok=True)

# 2. Recording Settings
fs = 24000  # Sample Rate (Chatterbox ke liye 24k best hai)
duration = 8  # 8 seconds recording

print(f"🎤 Recording shuru hone wali hai {duration} seconds ke liye...")
print("👉 Kuch bhi bolo: 'Hello, main Trinetra hoon. Yeh meri asli awaaz hai.'")
print("3... 2... 1... GO!")

# 3. Record
my_recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
sd.wait()  # Wait until recording is finished

print("✅ Recording Khatam!")

# 4. Save
sf.write(file_path, my_recording, fs)
print(f"📁 Asli awaaz save ho gayi hai yahan:\n{file_path}")
print("\n🔥 Ab wapas 'chatterox_test.py' chalao, ab BEEP nahi aayegi!")



