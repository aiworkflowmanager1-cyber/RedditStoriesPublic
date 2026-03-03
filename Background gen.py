# CELL 5: Video Creator with Updated Background Path

def create_videos_batch(max_videos=5):
    """
    Create videos for scripts that have audio
    Uses random background selection from multiple files
    Returns: (successful, failed)
    """
    import gc
    from pathlib import Path
    import subprocess
    import sys
    
    SCRIPTS_DIR = Path("/kaggle/working/scripts")
    AUDIO_DIR = Path("/kaggle/working/audio")
    VIDEOS_DIR = Path("/kaggle/working/videos")
    
    # UPDATED BACKGROUND PATH
    BACKGROUNDS_DIR = Path("/kaggle/input/vertical-background-videos/background-videos")
    
    # Validate background directory exists
    if not BACKGROUNDS_DIR.exists():
        print(f"❌ Background directory not found: {BACKGROUNDS_DIR}")
        print("   Expected: /kaggle/input/vertical-background-videos/background-videos")
        print("   Make sure you've added the dataset as an input to your notebook")
        return 0, 0
    
    # Find all background videos
    bg_files = []
    for ext in ['.mp4', '.mov', '.webm', '.avi']:
        bg_files.extend(list(BACKGROUNDS_DIR.glob(f"*{ext}")))
    
    if not bg_files:
        print(f"❌ No background videos found in {BACKGROUNDS_DIR}")
        print("   Supported formats: .mp4, .mov, .webm, .avi")
        return 0, 0
    
    print(f"📂 Found {len(bg_files)} background video(s):")
    for bg in bg_files[:5]:  # Show first 5
        print(f"   - {bg.name}")
    if len(bg_files) > 5:
        print(f"   ... and {len(bg_files) - 5} more")
    print("")
    
    # Get scripts that have audio
    scripts_with_audio = []
    
    if not AUDIO_DIR.exists():
        print("⚠️  No audio directory found")
        return 0, 0
    
    for audio_folder in AUDIO_DIR.iterdir():
        if not audio_folder.is_dir():
            continue
        
        mp3_files = list(audio_folder.glob("*.mp3"))
        mp3_count = len(mp3_files)
        
        if mp3_count == 0:
            continue
        
        script_path = SCRIPTS_DIR / f"{audio_folder.name}.txt"
        if not script_path.exists():
            print(f"⚠️  Audio folder {audio_folder.name} has no matching script")
            continue
        
        video_path = VIDEOS_DIR / f"{audio_folder.name}.mp4"
        if video_path.exists():
            print(f"⏭️  {audio_folder.name}: Video already exists")
            continue
        
        scripts_with_audio.append((script_path, mp3_count))
    
    if not scripts_with_audio:
        print("✅ No new videos to create (all scripts already processed)")
        return 0, 0
    
    # Limit to max_videos
    scripts_with_audio = scripts_with_audio[:max_videos]
    
    print(f"🎬 Processing {len(scripts_with_audio)} script(s):")
    for script_path, mp3_count in scripts_with_audio:
        print(f"   - {script_path.stem}: {mp3_count} audio files")
    print("")
    
    successful = 0
    failed = 0
    
    for script_path, mp3_count in scripts_with_audio:
        script_name = script_path.stem
        video_output = VIDEOS_DIR / f"{script_name}.mp4"
        
        print(f"🎬 {script_name}: Creating video ({mp3_count} lines)...")
        
        try:
            # Call kaggle_video.py as subprocess
            result = subprocess.run([
                sys.executable,
                "/kaggle/working/kaggle_video.py",
                str(script_path),
                str(AUDIO_DIR),
                str(BACKGROUNDS_DIR),
                str(video_output)
            ], capture_output=True, text=True, timeout=1200)  # 20 min timeout
            
            # Check result
            if result.returncode == 0 and video_output.exists():
                size_mb = video_output.stat().st_size / (1024 * 1024)
                
                # Try to get video duration
                try:
                    from moviepy.editor import VideoFileClip
                    with VideoFileClip(str(video_output)) as clip:
                        duration = clip.duration
                    print(f"  ✅ Created: {size_mb:.1f} MB, {duration:.1f}s ({mp3_count} lines)")
                except:
                    print(f"  ✅ Created: {size_mb:.1f} MB ({mp3_count} lines)")
                
                successful += 1
            else:
                print(f"  ❌ Failed")
                if result.stderr:
                    # Print first 200 chars of error
                    error_preview = result.stderr[:200]
                    print(f"     Error: {error_preview}")
                failed += 1
                
        except subprocess.TimeoutExpired:
            print(f"  ❌ Timeout (>20 minutes)")
            failed += 1
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
            failed += 1
        
        # Clear memory after each video
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
    
    return successful, failed

print("✅ Video creator ready (with random background selection)")
