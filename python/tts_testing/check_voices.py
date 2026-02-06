import numpy as np
from kokoro_onnx import Kokoro
import os

# --- FIX: Monkey Patching NumPy for Pickle ---
original_load = np.load
np.load = lambda *args, **kwargs: original_load(*args, **kwargs, allow_pickle=True)


def check_available_voices():
    # Check if files exist
    if not os.path.exists("kokoro-v0_19.onnx") or not os.path.exists("voices.bin"):
        print("❌ Error: 'kokoro-v0_19.onnx' ya 'voices.bin' missing hai!")
        print("Pehle TTS_Engine chalao taaki wo files download kar sake.")
        return

    try:
        print("🔍 Scanning voices.bin...")
        k = Kokoro("kokoro-v0_19.onnx", "voices.bin")

        print("\n=== ✅ AVAILABLE VOICES ===")
        found_voices = list(k.voices.keys())

        for name in found_voices:
            print(f"🎤 {name}")

        print("===========================")

        # Recommendation Logic
        if "af_heart" not in found_voices:
            print("\n⚠️ 'af_heart' nahi mili.")
            if "af_bella" in found_voices:
                print("💡 Suggestion: 'af_bella' use karo (Similar emotional depth).")
            elif "af_sarah" in found_voices:
                print("💡 Suggestion: 'af_sarah' use karo (Professional).")

    except Exception as e:
        print(f"❌ Error reading voices: {e}")

    finally:
        # Reset NumPy safety
        np.load = original_load


if __name__ == "__main__":
    check_available_voices()