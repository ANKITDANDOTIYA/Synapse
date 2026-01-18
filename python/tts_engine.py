
import edge_tts
import asyncio
import pygame
import io

import pygame.mixer

voice ="en-US-AriaNeural"
def speak(text) :
       try :
           loop = asyncio.get_event_loop()
       except RuntimeError as e:
            loop = asyncio.new_event_loop() 
            asyncio.set_event_loop(loop)
       mp3_fp = loop.run_until_complete(get_audio(text))
       pygame.mixer.init()
       pygame.mixer.music.load(mp3_fp)
       pygame.mixer.music.play()

       while pygame.mixer.music.get_busy():
           pygame.time.Clock().tick(10)



async def get_audio(text):
    """Text se Audio file generate karta hai"""
    communicate = edge_tts.Communicate(text, voice)
    auido_data = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk['type'] == 'audio':
            auido_data.write(chunk['data'])
    auido_data.seek(0)
    return auido_data


text = "Hello, this is a test of the text to speech engine."
speak(text)