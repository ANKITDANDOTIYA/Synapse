import os
import librosa
import soundfile as sf
import numpy as np

# Folder jahan tune happy.wav, sad.wav rakhi hain
folder_path = r"E:\MyProjects\CPP\Trinetra_Vision\python\tts_testing"

print("🔧 Fixing Audio Sampling Rates to 24000Hz...")

for filename in os.listdir(folder_path):
    if filename.endswith(".wav"):
        file_path = os.path.join(folder_path, filename)

        try:
            # 1. Load file (librosa automatically resamples if we tell it to)
            # sr=24000 is CRITICAL here
            y, sr = librosa.load(file_path, sr=24000, mono=True)

            # 2. Trim silence (Start aur End ki khamoshi hata do)
            y, _ = librosa.effects.trim(y, top_db=20)

            # 3. Overwrite the file with corrected version
            sf.write(file_path, y, 24000)

            print(f"   ✅ Fixed: {filename} (Resampled to 24k Mono)")

        except Exception as e:
            print(f"   ❌ Error fixing {filename}: {e}")

print("\n🎉 Ab chala ke dekh, ladki hi bolegi!")