import subprocess
import time
import psutil

subprocess.Popen(["cvlc", "--no-audio", "--no-video-title-show", "--no-metadata-network-access", "--no-osd", "--fullscreen", "-Iqt", "--repeat", "content/0001-4069.mp4"])

time.sleep(5)

for proc in psutil.process_iter():
    if proc.name() == "vlc" or proc.name() == "vlc.exe":
        proc.kill()
