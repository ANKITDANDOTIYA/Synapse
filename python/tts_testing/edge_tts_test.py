import asyncio
import edge_tts

# --- JARVIS SETTINGS ---
VOICE = "hi-IN-SwaraNeural"  # Best Indian Male Voice
OUTPUT_FILE = "jarvis_edge.mp3"


async def speak_with_emotion(text, mood="neutral"):
    """
    Moods:
    - neutral: Normal
    - angry: Fast & High Pitch
    - sad: Slow & Low Pitch
    - excited: Fast & Very High Pitch
    """

    # 1. Default Settings
    rate = "+0%"
    pitch = "+0Hz"
    volume = "+0%"

    # 2. Mood Logic (Jugaad for Emotions)
    if mood == "angry":
        rate = "+20%"  # Gusse mein tez bolte hain
        pitch = "+10Hz"  # Thoda chilla ke
        volume = "+20%"  # Zor se

    elif mood == "sad":
        rate = "-15%"  # Dheere
        pitch = "-10Hz"  # Awaaz bhari/girayi hui
        volume = "-10%"  # Dheere se

    elif mood == "excited":
        rate = "+10%"
        pitch = "+15Hz"  # Khushi mein awaaz patli/unchi hoti hai

    # 3. SSML Construction (Ye hai magic)
    # Is format ko Edge TTS samajhta hai
    ssml_text = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
        <voice name='{VOICE}'>
            <prosody rate='{rate}' pitch='{pitch}' volume='{volume}'>
                {text}
            </prosody>
        </voice>
    </speak>
    """

    # 4. Generate
    communicate = edge_tts.Communicate(text,
                                       VOICE)  # Note: Plain text pass karte hain usually, but communicate object ssml bhi le leta hai agar sahi se handle karein

    # *FIX*: Edge TTS library directly SSML text nahi leti 'text' parameter mein agar wo communicate object hai.
    # Hume communicate object ko thoda alag tarah se call karna hoga ya raw SSML use karna hoga.
    # Edge TTS ka best tarika hai simple text bhejo aur options set karo.

    # Let's use the parameters directly provided by library (Better method)
    communicate = edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch, volume=volume)

    await communicate.save(OUTPUT_FILE)
    print(f"✅ Audio Saved ({mood}): {OUTPUT_FILE}")


# --- TEST ---
text_angry = "Arre yaar! Tum meri baat kyun nahi sunte? Dimag kharab kar diya hai!"
text_sad = "Main thak gaya hoon boss. Koi model sahi se nahi chal raha."
text_happy = "Maza aa gaya bhai! Edge TTS hi sabse badhiya hai."

# Run
loop = asyncio.get_event_loop_policy().get_event_loop()
try:
    loop.run_until_complete(speak_with_emotion(text_angry, mood="angry"))
finally:
    pass