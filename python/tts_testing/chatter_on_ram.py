# ============================================================
# 🔥 TRINETRA TTS — FINAL ACTUALLY-CORRECT VERSION
# ============================================================

import os

# ---- HARD DISABLE SDPA (GLOBAL) ----
os.environ["PYTORCH_SDP_DISABLE"] = "1"
os.environ["TORCH_CUDNN_V8_API_ENABLED"] = "1"

import torch

if torch.cuda.is_available():
    torch.backends.cuda.enable_flash_sdp(False)
    torch.backends.cuda.enable_mem_efficient_sdp(False)
    torch.backends.cuda.enable_math_sdp(True)

# ----------------------------------

import threading
import queue
import numpy as np
import sounddevice as sd
import gradio as gr
import time
import re

from chatterbox.mtl_tts import ChatterboxMultilingualTTS

# =========================
# 1. LOAD MODEL
# =========================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading Model on {device} (FINAL FIX MODE)...")

multiModel = ChatterboxMultilingualTTS.from_pretrained(device=device)
# ❌ NO .config ACCESS HERE — IT DOES NOT EXIST

# =========================
# 2. VOICE FILE
# =========================
VOICE_FILE = "videoplayback.wav"
if not os.path.exists(VOICE_FILE):
    raise FileNotFoundError(f"{VOICE_FILE} not found")
print(f"✅ Reference Voice Found: {VOICE_FILE}")

# =========================
# 3. QUEUES
# =========================
audio_queue = queue.Queue()
stop_event = threading.Event()

# =========================
# 4. SPEAKER
# =========================
class SimpleTrinetra:
    def __init__(self, model, ref_file):
        self.model = model
        self.ref_file = ref_file
        self.voice_loaded = False

    def speak(self, text, out_q, stop_event):
        text = re.sub(r"\[.*?\]", "", text).strip()
        sentences = re.split(r'(?<=[.!?।])\s+', text)

        print(f"\n🔹 Processing: {text[:60]}")

        for sent in sentences:
            if stop_event.is_set():
                break
            sent = sent.strip()
            if not sent:
                continue

            lang_id = "hi" if any(w in sent.lower() for w in
                                  ["hai","main","tum","kya","nahi","hoon"]) else "en"

            prompt = None
            if not self.voice_loaded:
                print("🔄 Loading Voice into RAM (once)")
                prompt = self.ref_file
                self.voice_loaded = True

            with torch.no_grad(), torch.backends.cuda.sdp_kernel(enable_flash=False,
                                                                 enable_mem_efficient=False,
                                                                 enable_math=True):
                wav = self.model.generate(
                    sent,
                    audio_prompt_path=prompt,
                    language_id=lang_id,
                    cfg_weight=0.0,
                    temperature=0.3,
                    repetition_penalty=1.1,
                )

            audio = wav.squeeze(0).detach().cpu().numpy().astype(np.float32)
            out_q.put(audio)

# =========================
# 5. AUDIO THREADS
# =========================
def audio_consumer():
    while not stop_event.is_set():
        try:
            audio = audio_queue.get(timeout=0.5)
            sd.play(audio, samplerate=24000)
            sd.wait()
        except queue.Empty:
            continue

def audio_producer(text):
    trinetra.speak(text, audio_queue, stop_event)

# =========================
# 6. UI
# =========================
trinetra = SimpleTrinetra(multiModel, VOICE_FILE)

def start_playback(text):
    stop_event.clear()
    while not audio_queue.empty():
        audio_queue.get_nowait()

    t1 = threading.Thread(target=audio_producer, args=(text,))
    t2 = threading.Thread(target=audio_consumer)

    t1.start()
    t2.start()
    t1.join()

    stop_event.set()
    t2.join()

    return "Done ✅"

iface = gr.Interface(
    fn=start_playback,
    inputs=gr.Textbox(lines=5, label="Input Text"),
    outputs=gr.Textbox(label="Status"),
    title="Trinetra TTS — Stable",
)

if __name__ == "__main__":
    iface.launch()
