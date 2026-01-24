import sys
import time
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from engine.music_engine import MusicEngine

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 python/play.py <song name>")
        return

    song_name = " ".join(sys.argv[1:])

    engine = MusicEngine()

    print(f"Searching and playing: {song_name}")
    print("\nControls:")
    print("  p = pause")
    print("  r = resume")
    print("  s = stop")
    print("  q = quit")
    print("  Ctrl+C = force exit\n")

    try:
        engine.play(song_name)

        while True:
            if not engine.is_playing:
                time.sleep(0.5)

            cmd = input(">> ").strip().lower()

            if cmd == "p":
                engine.pause()
                print("Paused")

            elif cmd == "r":
                engine.resume()
                print("Resumed")

            elif cmd == "s":
                engine.stop()
                print("Stopped")

            elif cmd == "q":
                engine.stop()
                print("Bye 👋")
                break

    except KeyboardInterrupt:
        print("\nForce stopping...")
        engine.stop()

    except Exception as e:
        print(f"Error: {e}")
        engine.stop()

if __name__ == "__main__":
    main()
