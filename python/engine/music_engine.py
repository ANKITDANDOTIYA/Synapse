import pygame
import yt_dlp
import os
import tempfile
import time


class MusicEngine:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100)
        self.current = 1.0


        self._volume = 1.0  #  ISKO 0.5 SE 1.0 KAR DO
        self.current_file = None

    def play(self, song_name):
        """
        Searches, Downloads, and Plays the song using native yt-dlp (No subprocess).
        """
        self.stop()  # Stop previous song if any

        print(f"🔎 Searching & Downloading: {song_name}...")

        # Temp directory aur filename setup
        temp_dir = tempfile.gettempdir()
        filename = f"synapse_music_{int(time.time())}"
        save_path = os.path.join(temp_dir, filename)

        # YT-DLP CONFIGURATION
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': save_path + '.%(ext)s',  # Temp path template
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,

            # FOR 403 FORBIDDEN ERROR
            # Hum YouTube ko bolenge hum 'Android App' hain, Bot nahi.
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                }
            },

            # Audio Convert to MP3 (Requires FFmpeg)
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 1. Search & Download directly (Faster than separating them)
                # "ytsearch1:" ka matlab pehla result download karo
                info = ydl.extract_info(f"ytsearch1:{song_name}", download=True)

                # Title nikalo display ke liye
                if 'entries' in info:
                    title = info['entries'][0]['title']
                else:
                    title = info['title']

                print(f"🎵 Ready to Play: {title}")

                # yt-dlp file convert karke .mp3 extension laga deta hai
                final_path = save_path + ".mp3"

                if os.path.exists(final_path):
                    self.current_file = final_path

                    # 2. Pygame Play
                    pygame.mixer.music.load(self.current_file)
                    pygame.mixer.music.set_volume(self._volume)
                    pygame.mixer.music.play()
                    self.is_playing = True
                else:
                    print("❌ Download Error: File not found after download.")

        except Exception as e:
            print(f"❌ Music Error: {e}")
            self.stop()

    def pause(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False

    def resume(self):
        if not self.is_playing:
            pygame.mixer.music.unpause()
            self.is_playing = True

    def stop(self):
        """Stops music and cleans up temp files safely."""
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except:
            pass

        self.is_playing = False

        # Temp file delete karne se pehle thoda wait karo taaki file free ho jaye
        if self.current_file and os.path.exists(self.current_file):
            try:
                time.sleep(0.1)
                os.remove(self.current_file)
            except Exception:
                pass  # Agar delete na ho paye to ignore karo (Windows lock issue)
            self.current_file = None

    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        self._volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._volume)

    def check_status(self):
        try:
            return pygame.mixer.music.get_busy()
        except:
            return False

    def duck_volume(self):
        """Music dheema karo (Wake Word sunte waqt)"""
        print("⬇️ Ducking Volume...")
        self.set_volume(10)  # 10% Volume (Ab ye 0.1 banega, jo sahi hai)

    def restore_volume(self):
        """Music wapas tez karo"""
        print("⬆️ Restoring Volume...")
        self.set_volume(100)  # 100% Volume (1.0)