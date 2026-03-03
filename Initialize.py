# Cell 1: Install everything needed
!apt-get update -qq
!apt-get install -y -qq espeak-ng ffmpeg libsndfile1

!pip install -q kokoro>=0.9.2 soundfile pydub pillow moviepy numpy torch feedparser requests better-profanity 
print("✅ Dependencies installed")
# Cell 2: Create Clean Directory Structure

from pathlib import Path

# Simple, clean paths - NO GitHub artifacts
dirs = [
    "/kaggle/working/scripts",      # Stories from Reddit
    "/kaggle/working/audio",         # TTS audio files
    "/kaggle/working/videos"         # Final output videos
]

for d in dirs:
    Path(d).mkdir(parents=True, exist_ok=True)

print("✅ Directories created:")
for d in dirs:
    print(f"  {d}")
