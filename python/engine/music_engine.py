
import subprocess
import threading
import time
import pygame
import yt_dlp
import os
import tempfile

class MusicEngine:
    def __init__(self):
        """Initialize the MusicEngine."""
        # Initialize pygame mixer
        pygame.mixer.init()
        self.process = None
        self.is_playing = False
        self._volume = 0.5
        self.current_file = None
        
    def search_and_get_stream(self, song_name):
        """
        Search for a song on YouTube and return the streaming URL.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch1',
            'noplaylist': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch1:{song_name}", download=False)
                if 'entries' in info:
                    video = info['entries'][0]
                else:
                    video = info
                    
                return video.get('webpage_url'), video.get('title')
            except Exception as e:
                print(f"Error searching for song: {e}")
                return None, None

    def play(self, song_name):
        """
        Download to temp file and play.
        """
        self.stop() # Stop any current playback
        
        stream_url, title = self.search_and_get_stream(song_name)
        if not stream_url:
            print("Could not find song.")
            return

        print(f"Playing: {title}")
        
        # Create temp file
        # We need a path, but yt-dlp adds extension.
        # So we create a directory or use a fixed name template.
        # Let's use a unique name.
        fd, temp_path = tempfile.mkstemp(prefix='music_engine_', suffix='.mp3')
        os.close(fd)
        os.remove(temp_path) # yt-dlp will create it
        
        # yt-dlp command to download and convert to mp3
        # We use --output to specify exact path (but we must handle extension)
        # Actually simplest is to let yt-dlp handle extension and we find it.
        # But we want mp3.
        
        yt_cmd = [
            'yt-dlp',
            '-f', 'bestaudio/best',
            '-x',                 # Extract audio
            '--audio-format', 'mp3',
            '--audio-quality', '128K', # Fast
            '-o', temp_path,      # Output to this path (yt-dlp might append .mp3 if missing, but we gave it?)
                                  # If we say -o temp_path and temp_path ends in .mp3, yt-dlp usually respects it 
                                  # if we don't use %(ext)s. 
                                  # BUT with -x --audio-format mp3, it ensures mp3.
            '--quiet',
            '--no-warnings',
            '--force-overwrites',
            stream_url
        ]
        
        try:
            # Run yt-dlp synchronously (blocking)
            # This is the trade-off for robustness.
            # Usually takes 1-3 seconds.
            subprocess.run(yt_cmd, check=True)
            
            self.current_file = temp_path
            
            # Check if file exists (yt-dlp might have added suffix or something)
            # With -o path.mp3 and -x --audio-format mp3, it usually works.
            
            if not os.path.exists(self.current_file):
                # Fallback check
                if os.path.exists(self.current_file + ".mp3"):
                     self.current_file += ".mp3"
            
            pygame.mixer.music.load(self.current_file)
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play()
            self.is_playing = True
            
        except subprocess.CalledProcessError as e:
            print(f"Error downloading: {e}")
        except Exception as e:
            print(f"Error playing: {e}")
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
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload() 
        except:
            pass
            
        self.is_playing = False
        
        # Cleanup temp file
        if self.current_file and os.path.exists(self.current_file):
            try:
                os.remove(self.current_file)
            except:
                pass
            self.current_file = None

    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        self._volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._volume)
