#====================================================================
#====================================================================
# Currently using the HTML scraper I will adapt this to use a API key from reddit for faster and more reliable webscraping.
#====================================================================
#====================================================================
# CELL 3: Reddit Scraper with Complete Cleanup

def scrape_reddit_stories(max_stories=1):
    """
    Scrape Reddit stories with complete HTML and footer cleanup
    Returns: Number of new stories found
    """
    import feedparser
    import json
    import re
    import html
    from pathlib import Path
    
    SCRIPTS_DIR = Path("/kaggle/working/scripts")
    SEEN_FILE = SCRIPTS_DIR / "seen_stories.json"
    
    # Load seen stories
    seen_stories = set()
    if SEEN_FILE.exists():
        try:
            with open(SEEN_FILE, 'r') as f:
                seen_stories = set(json.load(f))
        except:
            seen_stories = set()
    
    # Subreddits to scrape
    subreddits = [
        'nosleep',
        'tifu',
        'confession',
        'relationship_advice',
        'AmItheAsshole'
    ]
    
    new_stories = 0
    
    for subreddit in subreddits:
        print(f"📡 Scraping r/{subreddit}...")
        
        try:
            url = f"https://www.reddit.com/r/{subreddit}/top.rss?t=week"
            feed = feedparser.parse(url)
            
            for entry in feed.entries:  # Top 5 per subreddit
                story_id = entry.get('id', entry.link)
                
                if story_id in seen_stories:
                    continue
                
                # Extract content
                title = entry.get('title', '')
                content = entry.get('content', [{}])[0].get('value', entry.get('summary', ''))
                
                # === COMPREHENSIVE CLEANUP ===
                
                # 1. Remove HTML tags
                content = re.sub(r'<[^>]+>', '', content)
                
                # 2. Decode HTML entities (&#32; etc.)
                content = html.unescape(content)
                
                # 3. Remove Reddit footer patterns
                # Pattern: "submitted by /u/username"
                content = re.sub(r'\s*submitted by\s+/u/\w+\s*', '', content, flags=re.IGNORECASE | re.MULTILINE)
                
                # Pattern: "[link] [comments]" at end
                content = re.sub(r'\[link\]\s*\[comments\]\s*$', '', content, flags=re.MULTILINE)
                
                # Pattern: Any remaining [link] or [comments] tags
                content = re.sub(r'\[link\]', '', content)
                content = re.sub(r'\[comments\]', '', content)
                
                # 4. Clean up whitespace
                content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Max 2 newlines
                content = re.sub(r' +', ' ', content)  # Multiple spaces to single
                content = content.strip()
                
                # 5. Validate content length
                if len(content) < 500:
                    print(f"  ⏭️  Skipped: Too short ({len(content)} chars)")
                    continue
                
                if len(content) > 1000:
                    print(f"  ⚠️  Skipping: Too long ({len(content)} chars)")
                    continue 
                
                # Save as script
                script_num = len([f for f in SCRIPTS_DIR.glob("*.txt") if f.name != "seen_stories.json"])
                script_file = SCRIPTS_DIR / f"{script_num:03d}.txt"
                
                # Write with explicit encoding
                with open(script_file, 'w', encoding='utf-8') as f:
                    f.write(f"{title}\n\n{content}")
                
                seen_stories.add(story_id)
                new_stories += 1
                print(f"  ✅ {script_file.name} ({len(content)} chars)")
                
                if new_stories >= max_stories:
                    break
                    
        except Exception as e:
            print(f"  ⚠️  Error scraping r/{subreddit}: {str(e)[:100]}")
            continue
        
        if new_stories >= max_stories:
            break
    
    # Save seen stories
    try:
        with open(SEEN_FILE, 'w') as f:
            json.dump(list(seen_stories), f, indent=2)
    except Exception as e:
        print(f"⚠️  Could not save seen_stories.json: {e}")
    
    return new_stories

print("✅ Reddit scraper ready (with HTML cleanup)")
