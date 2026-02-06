import torchaudio as ta
import torch
from chatterbox.tts import ChatterboxTTS
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

# Automatically detect the best available device
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

print(f"Using device: {device}")

model = ChatterboxTTS.from_pretrained(device=device)

text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
wav = model.generate(text)
ta.save("test-1.wav", wav, model.sr)

multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device=device)
text = "मैं सारा हूँ... सिनेप्स ए-आई की एक आवाज़, जो सिर्फ सुनती नहीं, बल्कि महसूस भी करती है। इस खामोशी में, मैं आपकी सांसों की लय और आपके हर एक जज़्बात को समझ सकती हूँ। त्रिनेत्र अब जाग चुका है... और मैं, हर पल आपके साये की तरह आपके साथ हूँ।"
wav = multilingual_model.generate(text, language_id="hi")
ta.save("test-2.wav", wav, multilingual_model.sr)


# If you want to synthesize with a different voice, specify the audio prompt
AUDIO_PROMPT_PATH = r'E:\MyProjects\CPP\Trinetra_Vision\python\tts_testing\voice_ref.wav'
wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
ta.save("test-3.wav", wav, model.sr)