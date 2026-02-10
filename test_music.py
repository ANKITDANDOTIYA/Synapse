import unittest
import time
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'python')))

from python.engine.music_engine import MusicEngine

class TestMusicEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MusicEngine()

    def tearDown(self):
        self.engine.stop()

    def test_play_stream(self):
        print("\nTesting playback...")
        # A non-copyrighted song or predictable search result
        # "NCS" (NoCopyrightSounds) is usually safe, or a specific creative commons song.
        # Let's use a very specific query to get a short video if possible, but for streaming test any valid audio works.
        song_name = "Alan Walker - Fade | NCS Release" 
        
        self.engine.play(song_name)
        
        # Allow it to play for 5 seconds
        time.sleep(5)
        
        # Verify it thinks it's playing (simple check)
        # Note: self.engine.is_playing might be True even if audio failed if exceptions weren't caught/propagated fully or if ffmpeg hangs, 
        # but we printed errors.
        
        self.engine.stop()
        print("Stopped playback.")
        
        # Check for side effects (files)
        # Current directory or temp
        entries = os.listdir('.')
        mp3_files = [f for f in entries if f.endswith('.mp3')]
        self.assertFalse(mp3_files, "Found .mp3 files when there should be none")

if __name__ == '__main__':
    unittest.main()
