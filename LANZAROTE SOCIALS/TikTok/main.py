"""
TikTok Auto Poster - Daily Dynamic Content (FIXED VERSION)
-----------------------------------------------------------
Generates daily videos with weather, news, and recommendations for Lanzarote.
Uses stock videos from Pexels for reliability.

Setup:
1. Get API keys from:
   - Groq: https://console.groq.com
   - Pexels: https://www.pexels.com/api/ (FREE)
2. Update API keys in CONFIG section below
3. Run: python main.py
"""

import os
import time
import json
import requests
import random
from datetime import datetime, timedelta

# ========================= CONFIG =========================
LATE_API_KEY = "sk_90ac09dff1ad38e38f860dbe1c8f703a6c91e706a66edb4a0e3c314601c93dbe"
ACCOUNT_ID = "6926a13bf43160a0bc999214"
GROQ_API_KEY = "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"  # ← UPDATE THIS
PEXELS_API_KEY = "0CNV1ZIKU8isghrWkt1cYadcekfKRpRW2JR101R8I7cyDVcIsD3b3QOd"  # ← ADD THIS (free from pexels.com/api)

VIDEO_FOLDER = "videos"
POST_TIME = "14:55"  # HH:MM (24hr)
API_MEDIA_URL = "https://getlate.dev/api/v1/media"
API_POST_URL = "https://getlate.dev/api/v1/posts"
# =================================================================


def get_current_weather():
    """Fetches real-time weather data for Lanzarote."""
    print("🌤️  Fetching weather...")
    try:
        response = requests.get("https://wttr.in/Lanzarote?format=j1", timeout=15)
        response.raise_for_status()
        current = response.json()['current_condition'][0]
        weather = {
            'temp_c': current['temp_C'],
            'condition': current['weatherDesc'][0]['value'],
            'wind_kph': current.get('windspeedKmph', 'N/A'),
            'humidity': current.get('humidity', 'N/A')
        }
        print(f"   ✅ {weather['temp_c']}°C, {weather['condition']}")
        return weather
    except Exception as e:
        print(f"   ⚠️  Error: {e}, using fallback")
        return {
            'temp_c': '22',
            'condition': 'Partly Cloudy',
            'wind_kph': '15',
            'humidity': '65'
        }


def get_local_news_and_events():
    """Fetches recent news/events about Lanzarote using Groq AI."""
    print("📰 Gathering news...")
    
    if GROQ_API_KEY == "YOUR_NEW_GROQ_KEY_HERE":
        print("   ⚠️  Groq API key not set, using fallback")
        return "Lanzarote is enjoying perfect beach weather with volcanic landscapes and coastal attractions open year-round."
    
    prompt = f"""Today is {datetime.now().strftime('%B %d, %Y')}. Provide 2-3 current events, festivals, or seasonal activities in Lanzarote. Keep each item to 1-2 sentences. Focus on what tourists can do right now."""
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "Provide concise info about current Lanzarote events."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 300
            },
            timeout=30
        )
        response.raise_for_status()
        news = response.json()["choices"][0]["message"]["content"].strip()
        print(f"   ✅ News gathered\n")
        return news
    except Exception as e:
        print(f"   ⚠️  Error: {e}, using fallback")
        return "Lanzarote is enjoying perfect beach weather with volcanic landscapes and coastal attractions open year-round."


def get_daily_recommendations():
    """Generates daily recommendations for Lanzarote."""
    print("🎯 Generating recommendations...")
    
    restaurants = [
        "La Cascada - Fresh seafood in Puerto del Carmen",
        "Amura - Upscale dining in Puerto Calero marina",
        "El Rincón de Juan Carlos - Michelin-recommended in Teguise",
        "Casa Torano - Traditional Canarian in Teguise",
        "El Diablo - Restaurant over volcanic heat in Timanfaya",
        "La Tabla - Tapas and local wines in Arrecife",
        "Lilium - Creative cuisine in Puerto del Carmen"
    ]
    
    places_to_visit = [
        "Timanfaya National Park - Volcanic landscapes",
        "Jameos del Agua - César Manrique's cave complex",
        "Cueva de los Verdes - Underground lava tubes",
        "Mirador del Río - Clifftop viewpoint",
        "La Graciosa Island - Pristine beaches",
        "Teguise Market - Sunday market (Sundays only)",
        "Jardín de Cactus - Cactus garden by César Manrique",
        "Papagayo Beaches - Protected coves",
        "Charco de los Clicos - Green lagoon",
        "Castillo de San José - Art museum with ocean views"
    ]
    
    activities = [
        "Surfing at Famara Beach",
        "Wine tasting in La Geria vineyards",
        "Scuba diving at Museo Atlántico",
        "Catamaran sunset cruise",
        "Camel trekking in Timanfaya",
        "Paddleboarding in calm bays",
        "Cycling the coastal paths",
        "Snorkeling at Playa Chica"
    ]
    
    recommendations = {
        'restaurant': random.choice(restaurants),
        'visit': random.choice(places_to_visit),
        'activity': random.choice(activities)
    }
    
    print(f"   ✅ Done\n")
    return recommendations


def get_stock_video(video_style, weather):
    """Downloads relevant stock video from Pexels API - optimized for size with audio preference."""
    print(f"🎬 Fetching stock video...")
    
    if PEXELS_API_KEY == "YOUR_PEXELS_KEY_HERE":
        print("   ❌ Pexels API key not set! Get one free at: https://www.pexels.com/api/")
        return None
    
    # Search terms based on style and weather
    search_terms = {
        "weather_focused": [
            "lanzarote beach waves",
            "canary islands beach ocean",
            "volcanic beach spain water",
            "spanish beach paradise sea"
        ],
        "recommendation_focused": [
            "lanzarote volcano nature",
            "volcanic landscape wind",
            "canary islands nature sounds",
            "lanzarote timanfaya"
        ],
        "mixed_highlights": [
            "lanzarote ocean",
            "canary islands travel beach",
            "spanish island waves",
            "volcanic island beach sea"
        ]
    }
    
    # Select search query
    queries = search_terms.get(video_style, search_terms["mixed_highlights"])
    search_query = random.choice(queries)
    
    print(f"   🔍 Searching: '{search_query}'")
    
    try:
        response = requests.get(
            f"https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={
                "query": search_query,
                "orientation": "portrait",  # Vertical for TikTok
                "per_page": 40,  # Increased to find more options with audio
                "size": "small"  # Request smaller videos
            },
            timeout=30
        )
        response.raise_for_status()
        
        videos = response.json().get('videos', [])
        
        if not videos:
            print(f"   ⚠️  No videos found, trying backup search...")
            # Fallback to generic search
            response = requests.get(
                f"https://api.pexels.com/videos/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={
                    "query": "beach waves ocean",
                    "orientation": "portrait",
                    "per_page": 40,
                    "size": "small"
                },
                timeout=30
            )
            response.raise_for_status()
            videos = response.json().get('videos', [])
        
        if not videos:
            print(f"   ❌ No videos available")
            return None
        
        # Shuffle videos to get variety
        random.shuffle(videos)
        
        # Try multiple videos to find one under 10MB, preferring those with natural audio
        max_attempts = 15
        for attempt in range(max_attempts):
            if attempt >= len(videos):
                break
                
            video = videos[attempt]
            
            # Check if video likely has natural audio (Pexels doesn't expose this directly)
            # Videos with nature/outdoor keywords are more likely to have ambient sound
            video_tags = video.get('video_tags', [])
            has_nature_tags = any(tag.get('name', '').lower() in ['ocean', 'waves', 'beach', 'water', 'nature', 'wind', 'sounds'] for tag in video_tags)
            
            # Find portrait video files, prefer smaller ones
            video_files = [vf for vf in video['video_files'] if vf.get('width', 0) < vf.get('height', 0)]
            
            if not video_files:
                video_files = video['video_files']
            
            # Sort by size (smallest to largest) and filter by quality
            # Prefer SD or lower quality to keep file size down
            sd_files = [vf for vf in video_files if vf.get('quality') in ['sd', 'hd']]
            if sd_files:
                video_files = sd_files
            
            video_files.sort(key=lambda x: x.get('width', 0) * x.get('height', 0))
            
            # Try the smallest available
            for video_file in video_files[:3]:  # Try up to 3 smallest
                video_url = video_file['link']
                quality = video_file.get('quality', 'unknown')
                width = video_file.get('width', 0)
                height = video_file.get('height', 0)
                
                audio_indicator = "🔊" if has_nature_tags else "🎵"
                print(f"   📥 Trying video {attempt+1}/{max_attempts} ({quality} {width}x{height}) {audio_indicator}...")
                
                # Download video
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(VIDEO_FOLDER, f"daily_video_{timestamp}.mp4")
                os.makedirs(VIDEO_FOLDER, exist_ok=True)
                
                video_response = requests.get(video_url, timeout=120)
                video_response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(video_response.content)
                
                file_size = os.path.getsize(filepath) / (1024 * 1024)
                
                # Check if file is under 10MB (safe limit for Late)
                if file_size <= 10:
                    print(f"   ✅ Video downloaded: {filepath} ({file_size:.2f} MB)")
                    
                    # Quick check if video has audio track using ffprobe (if available)
                    has_audio = check_video_has_audio(filepath)
                    if has_audio:
                        print(f"   🔊 Audio track detected!\n")
                    else:
                        print(f"   ⚠️  No audio track detected (silent video)\n")
                    
                    return filepath
                else:
                    print(f"   ⚠️  Video too large ({file_size:.2f} MB), trying another...")
                    os.remove(filepath)
                    break  # Try next video from search results
        
        print(f"   ❌ Could not find video under 10MB after {max_attempts} attempts")
        return None
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def check_video_has_audio(filepath):
    """Checks if video file has an audio track (requires ffprobe)."""
    try:
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 
             'stream=codec_type', '-of', 'default=noprint_wrappers=1:nokey=1', filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.stdout.decode().strip() == 'audio'
    except:
        # If ffprobe not available, assume video has audio
        return True


def create_daily_video_prompt(weather, recommendations):
    """Creates video search strategy from daily data."""
    print("📝 Creating video search strategy...\n")
    
    formats = ["weather_focused", "recommendation_focused", "mixed_highlights"]
    format_style = random.choice(formats)
    
    print(f"   🎬 Style: {format_style}")
    print(f"   🌡️  Weather: {weather['temp_c']}°C, {weather['condition']}")
    print(f"   📍 Highlight: {recommendations['visit'].split('-')[0].strip()}\n")
    
    return format_style


def create_daily_caption(weather, recommendations, video_style):
    """Generates TikTok caption with daily info."""
    print("✏️  Generating caption...")
    
    if GROQ_API_KEY == "YOUR_NEW_GROQ_KEY_HERE":
        print("   ⚠️  Groq API key not set, using template")
        visit_place = recommendations['visit'].split('-')[0].strip()
        caption = f"{weather['temp_c']}°C and {weather['condition'].lower()} in Lanzarote! ☀️ Perfect day to explore {visit_place}! Who's ready for paradise? 🌊 #Lanzarote #CanaryIslands #Travel #Spain"
        print(f"   ✅ Caption: {caption}\n")
        return caption
    
    prompt = f"""Create a TikTok caption for Lanzarote:
Weather: {weather['temp_c']}°C, {weather['condition']}
Today's Recommendation: {recommendations['visit']}
Activity: {recommendations['activity']}
Style: {video_style}

Requirements:
- 120-180 characters total
- Include 4-6 relevant hashtags (#Lanzarote #CanaryIslands always included)
- Use 1-2 emojis naturally
- End with an engaging question
- Enthusiastic but authentic tone

Return ONLY the caption text, no quotes or explanations."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a Lanzarote travel influencer creating engaging TikTok captions."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.85,
                "max_tokens": 250
            },
            timeout=30
        )
        response.raise_for_status()
        caption = response.json()["choices"][0]["message"]["content"].strip().strip('"').strip("'")
        print(f"   ✅ Caption: {caption}\n")
        return caption
    except Exception as e:
        print(f"   ⚠️  Error: {e}, using template")
        visit_place = recommendations['visit'].split('-')[0].strip()
        caption = f"{weather['temp_c']}°C and {weather['condition'].lower()} in Lanzarote! ☀️ Perfect day to explore {visit_place}! Who's ready for paradise? 🌊 #Lanzarote #CanaryIslands #Travel #Spain"
        print(f"   ✅ Caption: {caption}\n")
        return caption


def upload_video_to_late(filepath, max_retries=3):
    """Uploads video to Late API with retry logic."""
    print(f"📤 Uploading video to Late...")
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"   🔄 Retry attempt {attempt + 1}/{max_retries}...")
            
            with open(filepath, "rb") as f:
                response = requests.post(
                    API_MEDIA_URL,
                    headers={"Authorization": f"Bearer {LATE_API_KEY}"},
                    files={"files": f},
                    timeout=180  # Increased to 3 minutes
                )
            response.raise_for_status()
            media_url = response.json()["files"][0]["url"]
            print(f"   ✅ Upload successful!\n")
            return media_url
            
        except requests.exceptions.Timeout as e:
            if attempt < max_retries - 1:
                wait_time = 30 * (attempt + 1)
                print(f"   ⏱️  Upload timeout. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"   ❌ Upload failed after {max_retries} attempts: {e}")
                raise
        except Exception as e:
            print(f"   ❌ Upload failed: {e}")
            raise


def post_to_tiktok(media_url, caption, max_retries=3):
    """Posts video to TikTok via Late API with retry logic."""
    print(f"🚀 Posting to TikTok...")
    print(f"   📝 Caption: {caption[:100]}...\n")
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"   🔄 Retry attempt {attempt + 1}/{max_retries}...")
            
            response = requests.post(
                API_POST_URL,
                headers={"Authorization": f"Bearer {LATE_API_KEY}", "Content-Type": "application/json"},
                json={
                    "platforms": [{"platform": "tiktok", "accountId": ACCOUNT_ID}],
                    "content": caption,
                    "mediaItems": [{"type": "video", "url": media_url}]
                },
                timeout=180  # Increased to 3 minutes for TikTok processing
            )
            response.raise_for_status()
            result = response.json()
            print(f"   ✅ Posted successfully!\n")
            return result
            
        except requests.exceptions.Timeout as e:
            if attempt < max_retries - 1:
                wait_time = 30 * (attempt + 1)
                print(f"   ⏱️  Timeout occurred. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"   ❌ Posting failed after {max_retries} attempts: {e}")
                raise
        except Exception as e:
            print(f"   ❌ Posting failed: {e}")
            raise


def generate_and_post_daily_video():
    """Main function - generates and posts daily video."""
    print("\n" + "="*70)
    print(f"🌅 GENERATING TODAY'S VIDEO - {datetime.now().strftime('%A, %B %d, %Y')}")
    print("="*70 + "\n")
    
    # Gather data
    weather = get_current_weather()
    news = get_local_news_and_events()
    recommendations = get_daily_recommendations()
    
    print("-"*70)
    print(f"📊 TODAY'S SUMMARY:")
    print(f"   Weather: {weather['temp_c']}°C, {weather['condition']}")
    print(f"   Visit: {recommendations['visit']}")
    print(f"   Activity: {recommendations['activity']}")
    print(f"   Dine at: {recommendations['restaurant']}")
    print("-"*70 + "\n")
    
    # Create content
    video_style = create_daily_video_prompt(weather, recommendations)
    video_file = get_stock_video(video_style, weather)
    
    if not video_file:
        print("❌ Video download failed. Retrying at next scheduled time.\n")
        return False
    
    caption = create_daily_caption(weather, recommendations, video_style)
    
    # Upload and post
    try:
        media_url = upload_video_to_late(video_file)
        post_to_tiktok(media_url, caption)
        
        # Clean up local file
        os.remove(video_file)
        print(f"🗑️  Cleaned up local file\n")
        
    except Exception as e:
        print(f"❌ Upload/posting failed: {e}\n")
        # Keep video file for manual retry
        print(f"💾 Video saved at: {video_file}")
        return False
    
    print("="*70)
    print("✅ DAILY VIDEO POSTED SUCCESSFULLY!")
    print("="*70 + "\n")
    return True


def wait_until_post_time():
    """Waits until daily post time."""
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        if current_time == POST_TIME:
            return
        
        post_hour, post_minute = map(int, POST_TIME.split(':'))
        target_time = now.replace(hour=post_hour, minute=post_minute, second=0)
        
        if target_time < now:
            target_time += timedelta(days=1)
        
        time_diff = target_time - now
        hours_left = int(time_diff.total_seconds() // 3600)
        minutes_left = int((time_diff.total_seconds() % 3600) // 60)
        
        print(f"⏰ Next post in {hours_left}h {minutes_left}m (at {POST_TIME})", end='\r')
        time.sleep(30)


def check_api_keys():
    """Validates API keys are configured."""
    print("\n🔑 Checking API keys...")
    
    issues = []
    
    if GROQ_API_KEY == "YOUR_NEW_GROQ_KEY_HERE":
        issues.append("⚠️  Groq API key not set (will use fallback text)")
    else:
        print("   ✅ Groq API key configured")
    
    if PEXELS_API_KEY == "YOUR_PEXELS_KEY_HERE":
        issues.append("❌ Pexels API key REQUIRED - Get free at: https://www.pexels.com/api/")
    else:
        print("   ✅ Pexels API key configured")
    
    if LATE_API_KEY.startswith("sk_"):
        print("   ✅ Late API key configured")
    else:
        issues.append("❌ Late API key appears invalid")
    
    if issues:
        print("\n" + "\n".join(issues) + "\n")
        if "REQUIRED" in "\n".join(issues):
            print("❌ Cannot continue without required API keys. Exiting...\n")
            return False
    
    print()
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎥 TIKTOK DAILY DYNAMIC CONTENT GENERATOR")
    print("="*70)
    print(f"📅 Daily posting time: {POST_TIME}")
    print(f"📍 Location: Lanzarote, Canary Islands")
    
    # Check API keys before starting
    if not check_api_keys():
        exit(1)
    
    print("="*70 + "\n")

    # Main loop
    while True:
        try:
            wait_until_post_time()
            success = generate_and_post_daily_video()
            
            if success:
                print("😴 Sleeping for 60 seconds before next cycle...\n")
            else:
                print("⚠️  Post failed, will retry at next scheduled time.\n")
            
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down gracefully...")
            print("✅ All scheduled posts completed. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n⚠️  Unexpected error: {e}")
            print("Waiting 5 minutes before retry...\n")
            time.sleep(300)