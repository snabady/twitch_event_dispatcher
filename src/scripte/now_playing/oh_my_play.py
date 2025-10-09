import subprocess
import time

last_song = ""

while True:
    try:
        song = subprocess.check_output(["audtool", "current-song"], text=True).strip()
        if song != last_song:
            print(f"now playing: {song}")
            last_song = song
    except subprocess.CalledProcessError:
        pass
    time.sleep(15)  

