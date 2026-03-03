# CELL 4: TTS Generator (SHORT Phrase Splitting - PRODUCTION)

def generate_tts_for_scripts(voice_name="am_adam", max_words_per_phrase=12):
    """
    Generate TTS audio using SHORT phrase splitting
    
    CRITICAL: Uses split_text_into_short_phrases() from Cell 3.5
    - Same function as video creation
    - Ensures perfect MP3/subtitle sync
    - Short, natural phrases (10-15 words)
    
    Args:
        voice_name: Kokoro voice (am_adam, af_sarah, etc.)
        max_words_per_phrase: Max words per subtitle (default: 12)
    
    Returns:
        (successful, failed) counts
    """
    import time
    import gc
    from pathlib import Path
    import subprocess
    
    try:
        import soundfile as sf
        import numpy as np
        from kokoro import KPipeline
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure kokoro, soundfile, numpy are installed")
        return 0, 0
    
    SCRIPTS_DIR = Path("/kaggle/working/scripts")
    AUDIO_DIR = Path("/kaggle/working/audio")
    
    if not SCRIPTS_DIR.exists():
        print(f"❌ Scripts directory not found: {SCRIPTS_DIR}")
        return 0, 0
    
    print("🎙️  Initializing Kokoro TTS...")
    try:
        pipeline = KPipeline(lang_code='a')
    except Exception as e:
        print(f"❌ Failed to initialize Kokoro: {e}")
        return 0, 0
    
    scripts = sorted([f for f in SCRIPTS_DIR.glob("*.txt") if f.name != "seen_stories.json"])
    
    if not scripts:
        print("⚠️  No scripts found to process")
        return 0, 0
    
    print(f"📝 Found {len(scripts)} scripts to process")
    
    successful = 0
    failed = 0
    
    for script_path in scripts:
        script_name = script_path.stem
        audio_dir = AUDIO_DIR / script_name
        
        # Skip if audio already exists
        if audio_dir.exists():
            existing_mp3s = list(audio_dir.glob("*.mp3"))
            if len(existing_mp3s) > 0:
                print(f"⏭️  {script_name}: Audio exists ({len(existing_mp3s)} files)")
                continue
        
        print(f"🎙️  {script_name}: Generating TTS...")
        
        # Read script content
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  ❌ Failed to read script: {e}")
            failed += 1
            continue
        
        if not content.strip():
            print(f"  ⚠️  Empty script, skipping")
            failed += 1
            continue
        
        # CRITICAL: Use shared splitting function (same as video!)
        try:
            cleaned_content, profanity_count = clean_profanity(content, censor_char='[bleep]')
            if profanity_count > 0:
                print(f"⚠️  Censored {profanity_count} word(s)")
            phrases = split_text_into_natural_phrases(cleaned_content, max_words=12)
        except Exception as e:
            print(f"  ❌ Text splitting failed: {e}")
            failed += 1
            continue
        
        if not phrases:
            print(f"  ⚠️  No phrases after splitting")
            failed += 1
            continue
        
        # Show splitting stats
        word_counts = [len(p.split()) for p in phrases]
        avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
        max_words_found = max(word_counts) if word_counts else 0
        
        print(f"  📝 Split into {len(phrases)} phrases")
        print(f"     Avg: {avg_words:.1f} words, Max: {max_words_found} words")
        
        # Create audio directory
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate audio for each phrase
        line_success = 0
        line_failed = 0
        
        for i, text in enumerate(phrases):
            mp3_path = audio_dir / f"line_{i:03d}.mp3"
            
            # Skip if exists and valid
            if mp3_path.exists() and mp3_path.stat().st_size > 1000:
                line_success += 1
                continue
            
            # Validate text
            if not text.strip():
                print(f"    ⚠️  Line {i}: Empty text, using placeholder")
                text = "..."
            
            # Generate with retry logic (3 attempts)
            for attempt in range(3):
                try:
                    # Generate audio
                    generator = pipeline(text, voice=voice_name)
                    
                    audio_chunks = []
                    for gs, ps, audio in generator:
                        audio_chunks.append(audio)
                    
                    if not audio_chunks:
                        raise Exception("No audio generated")
                    
                    # Concatenate chunks
                    full_audio = np.concatenate(audio_chunks) if len(audio_chunks) > 1 else audio_chunks[0]
                    
                    if len(full_audio) == 0:
                        raise Exception("Empty audio array")
                    
                    # Save to WAV temporarily
                    wav_tmp = audio_dir / f"line_{i:03d}.tmp.wav"
                    sf.write(str(wav_tmp), full_audio, 24000)
                    
                    # Validate WAV file
                    if not wav_tmp.exists() or wav_tmp.stat().st_size < 1000:
                        raise Exception("WAV file invalid or too small")
                    
                    # Convert to MP3 using ffmpeg
                    result = subprocess.run([
                        "ffmpeg", "-y", "-loglevel", "error",
                        "-i", str(wav_tmp),
                        "-b:a", "192k",
                        str(mp3_path)
                    ], capture_output=True, timeout=30)
                    
                    # Clean up WAV
                    wav_tmp.unlink(missing_ok=True)
                    
                    # Validate MP3
                    if result.returncode != 0:
                        raise Exception(f"ffmpeg failed: {result.stderr[:100]}")
                    
                    if not mp3_path.exists():
                        raise Exception("MP3 file not created")
                    
                    if mp3_path.stat().st_size < 1000:
                        raise Exception("MP3 file too small")
                    
                    # Success!
                    line_success += 1
                    break
                
                except subprocess.TimeoutExpired:
                    print(f"    ⚠️  Line {i}: Timeout on attempt {attempt + 1}")
                    if attempt < 2:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        line_failed += 1
                
                except Exception as e:
                    if attempt < 2:
                        # Retry with backoff
                        time.sleep(2 ** attempt)
                        continue
                    else:
                        # Final failure
                        print(f"    ❌ Line {i}: {str(e)[:60]}")
                        line_failed += 1
        
        # Report results for this script
        success_rate = (line_success / len(phrases) * 100) if phrases else 0
        print(f"  ✅ Generated {line_success}/{len(phrases)} audio files ({success_rate:.1f}%)")
        
        if line_failed > 0:
            print(f"  ⚠️  {line_failed} files failed")
        
        # Consider script successful if >50% of lines worked
        if success_rate >= 50:
            successful += 1
        else:
            print(f"  ❌ Too many failures ({success_rate:.1f}% success)")
            failed += 1
        
        # Clear memory
        gc.collect()
    
    print()
    return successful, failed


print("✅ TTS generator ready (SHORT phrase splitting)")
print("  🎯 Default: max 12 words per phrase (TikTok style)")
print("  📝 Uses split_text_into_short_phrases() from Cell 3.5")
print("  ✅ Natural pauses at sentences, commas, conjunctions")
print("  🔄 3x retry with exponential backoff")
print("  ✅ Validates all audio files")
