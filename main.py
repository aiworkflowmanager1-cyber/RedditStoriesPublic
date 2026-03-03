# CELL 7: Main Execution with Clear Deletion Logging

from datetime import datetime, timedelta
from pathlib import Path
import shutil

# ========================================
# CLEANUP FUNCTION WITH CLEAR LOGGING
# ========================================
def cleanup_old_files():
    """
    Delete old files according to retention policy
    
    DELETION RULES:
    - Scripts: Deleted if last modified >365 days ago
    - Audio folders: Deleted if newest MP3 >14 days old
    - Videos: Deleted if last modified >7 days ago
    - seen_stories.json: NEVER deleted
    
    WHEN: Runs at the start of Cell 7, every time
    """
    
    SCRIPTS_DIR = Path("/kaggle/working/scripts")
    AUDIO_DIR = Path("/kaggle/working/audio")
    VIDEOS_DIR = Path("/kaggle/working/videos")
    
    print("=" * 70)
    print("🗑️  FILE CLEANUP - RETENTION POLICY")
    print("=" * 70)
    print("")
    print("📋 DELETION RULES:")
    print("  ├─ Scripts:      Delete if >365 days old (1 year)")
    print("  ├─ Audio:        Delete if >14 days old (2 weeks)")
    print("  ├─ Videos:       Delete if >7 days old (1 week)")
    print("  └─ seen_stories: NEVER deleted (tracks duplicates)")
    print("")
    print("⏰ RUNS: Every time Cell 7 executes (automatic)")
    print("")
    
    deleted_scripts = 0
    deleted_audio = 0
    deleted_videos = 0
    
    # ===================================
    # DELETE OLD SCRIPTS (>365 days)
    # ===================================
    cutoff_scripts = datetime.now() - timedelta(days=365)
    
    if SCRIPTS_DIR.exists():
        print("🔍 Checking scripts...")
        for script_file in SCRIPTS_DIR.glob("*.txt"):
            if script_file.name == "seen_stories.json":
                continue  # NEVER delete this
            
            try:
                mtime = datetime.fromtimestamp(script_file.stat().st_mtime)
                age_days = (datetime.now() - mtime).days
                
                if mtime < cutoff_scripts:
                    script_file.unlink()
                    deleted_scripts += 1
                    print(f"  🗑️  DELETED: {script_file.name} (age: {age_days} days)")
                    
            except Exception as e:
                print(f"  ⚠️  Error checking {script_file.name}: {e}")
    
    # ===================================
    # DELETE OLD AUDIO FOLDERS (>7 days)
    # ===================================
    cutoff_audio = datetime.now() - timedelta(days=7)
    
    if AUDIO_DIR.exists():
        print("🔍 Checking audio folders...")
        for audio_folder in AUDIO_DIR.iterdir():
            if not audio_folder.is_dir():
                continue
            
            try:
                mp3_files = list(audio_folder.glob("*.mp3"))
                if not mp3_files:
                    continue
                
                # Use newest MP3 file as reference
                newest_mtime = max(datetime.fromtimestamp(f.stat().st_mtime) for f in mp3_files)
                age_days = (datetime.now() - newest_mtime).days
                
                if newest_mtime < cutoff_audio:
                    shutil.rmtree(audio_folder)
                    deleted_audio += 1
                    mp3_count = len(mp3_files)
                    print(f"  🗑️  DELETED: {audio_folder.name}/ ({mp3_count} MP3s, age: {age_days} days)")
                    
            except Exception as e:
                print(f"  ⚠️  Error checking {audio_folder.name}: {e}")
    
    # ===================================
    # DELETE OLD VIDEOS (>1 days)
    # ===================================
    cutoff_videos = datetime.now() - timedelta(days=1)
    
    if VIDEOS_DIR.exists():
        print("🔍 Checking videos...")
        for video_file in VIDEOS_DIR.glob("*.mp4"):
            try:
                mtime = datetime.fromtimestamp(video_file.stat().st_mtime)
                age_days = (datetime.now() - mtime).days
                
                if mtime < cutoff_videos:
                    size_mb = video_file.stat().st_size / (1024 * 1024)
                    video_file.unlink()
                    deleted_videos += 1
                    print(f"  🗑️  DELETED: {video_file.name} ({size_mb:.1f} MB, age: {age_days} days)")
                    
            except Exception as e:
                print(f"  ⚠️  Error checking {video_file.name}: {e}")
    
    # ===================================
    # SUMMARY
    # ===================================
    print("")
    if deleted_scripts == 0 and deleted_audio == 0 and deleted_videos == 0:
        print("✅ No files met deletion criteria")
    else:
        print("📊 DELETION SUMMARY:")
        if deleted_scripts > 0:
            print(f"  ├─ Scripts deleted: {deleted_scripts}")
        if deleted_audio > 0:
            print(f"  ├─ Audio folders deleted: {deleted_audio}")
        if deleted_videos > 0:
            print(f"  └─ Videos deleted: {deleted_videos}")
    
    print("")
    print("=" * 70)
    print("")


# ========================================
# MAIN WORKFLOW
# ========================================
print("")
print("=" * 70)
print("🎬 DAILY VIDEO GENERATION WORKFLOW")
print("=" * 70)
print("")

# ===================================
# STEP 0: CLEANUP (runs first, always)
# ===================================
cleanup_old_files()

# ===================================
# STEP 1: SCRAPE REDDIT
# ===================================
print("=" * 70)
print("📰 STEP 1: SCRAPE REDDIT STORIES")
print("=" * 70)
print("")

try:
    new_stories = scrape_reddit_stories(max_stories=1)
    print("")
    print(f"✅ Scraped {new_stories} new stories")
except Exception as e:
    print(f"❌ Reddit scraping failed: {e}")
    new_stories = 0

print("")

# ===================================
# STEP 2: GENERATE TTS
# ===================================
print("=" * 70)
print("🎙️  STEP 2: GENERATE TTS AUDIO")
print("=" * 70)
print("")

try:
    tts_ok, tts_fail = generate_tts_for_scripts(voice_name="am_adam")
    print("")
    print(f"✅ TTS: {tts_ok} successful, {tts_fail} failed")
except Exception as e:
    print(f"❌ TTS generation failed: {e}")
    tts_ok, tts_fail = 0, 0

print("")

# ===================================
# STEP 3: CREATE VIDEOS
# ===================================
print("=" * 70)
print("🎬 STEP 3: CREATE VIDEOS")
print("=" * 70)
print("")

try:
    vid_ok, vid_fail = create_videos_batch(max_videos=5)
    print("")
    print(f"✅ Videos: {vid_ok} successful, {vid_fail} failed")
except Exception as e:
    print(f"❌ Video creation failed: {e}")
    vid_ok, vid_fail = 0, 0

print("")

# ===================================
# FINAL SUMMARY
# ===================================
print("=" * 70)
print("🏁 WORKFLOW COMPLETE")
print("=" * 70)
print("")
print("📊 SUMMARY:")
print(f"  📰 Stories scraped: {new_stories}")
print(f"  🎙️  TTS generated: {tts_ok} (failed: {tts_fail})")
print(f"  🎬 Videos created: {vid_ok} (failed: {vid_fail})")
print("")

# ===================================
# LIST OUTPUT VIDEOS
# ===================================
from pathlib import Path

videos = list(Path("/kaggle/working/videos").glob("*.mp4"))

if videos:
    print("📹 OUTPUT VIDEOS:")
    total_size = 0
    for video in sorted(videos):
        size_mb = video.stat().st_size / (1024 * 1024)
        total_size += size_mb
        
        # Try to get video duration
        try:
            from moviepy.editor import VideoFileClip
            with VideoFileClip(str(video)) as clip:
                duration = clip.duration
            print(f"  ├─ {video.name}: {size_mb:.1f} MB, {duration:.1f}s")
        except:
            print(f"  ├─ {video.name}: {size_mb:.1f} MB")
    
    print(f"  └─ Total: {len(videos)} videos, {total_size:.1f} MB")
else:
    print("⚠️  No videos in output directory")

print("")
print("🎉 " * 35)
print("=" * 70)
