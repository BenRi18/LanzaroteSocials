"""
TikTok Auto Poster (Daily Scheduler) - FULLY AUTOMATIC
-------------------------------------------------------
This script will automatically:
1. Generate a video script using AI (NO user input needed!)
2. Upload and post it to TikTok at your scheduled time
3. Repeat daily

IMPORTANT:
1. Replace YOUR_LATE_API_KEY with your real key (already set).
2. Replace ACCOUNT_ID with the TikTok account ID from Late (already set).
3. Set your GROQ_API_KEY for free AI script generation.
4. Customize video_content_settings() with your preferences.
5. Set POST_TIME to the time you want videos to post daily (24h format).

Run with:
    python main.py

This script runs forever like a service - completely hands-free!
"""

import os
import time
import json
import requests
import random
from datetime import datetime

# ========================= CONFIG =========================
LATE_API_KEY = "sk_90ac09dff1ad38e38f860dbe1c8f703a6c91e706a66edb4a0e3c314601c93dbe"
ACCOUNT_ID = "6926a13bf43160a0bc999214"
GROQ_API_KEY = "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"  # Get free key from https://console.groq.com/
VIDEO_FOLDER = "videos"
POST_TIME = "19:22"  # HH:MM (24hr) time to post every day

# Correct API endpoints for Late
API_MEDIA_URL = "https://getlate.dev/api/v1/media"
API_POST_URL = "https://getlate.dev/api/v1/posts"

# AI Generation Settings
ENABLE_AI_GENERATION = True  # Set to False to only upload existing videos

# Video Generation API Settings
# Choose one: "hailuo" (minimax - free tier), "wan" (alibaba), or "custom_flow"
VIDEO_API_PROVIDER = "hailuo"  
AIML_API_KEY = "7e98b8578cb14b60a31491ab0f73fede"
# ===========================================================


def video_content_settings():
    """
    Customize your video content preferences here.
    The AI will use these settings to generate videos automatically.
    NO USER INTERACTION NEEDED - just configure once!
    """
    return {
        "niche": "travel and lifestyle in Lanzarote", 
        "tone": "fun, engaging, informative", 
        "duration": 30, 
        "call_to_action": "Follow for more Lanzarote tips!",
        "themes": [  
            "hidden beaches",
            "local food spots",
            "activities and adventures",
            "travel tips",
            "cultural insights",
            "best photo spots"
        ]
    }


def generate_script_with_groq():
    
    settings = video_content_settings()
    
    today_theme = random.choice(settings["themes"])
    
    prompt = f"""You are a TikTok video script writer specializing in {settings['niche']}.

Create a compelling TikTok video script with these requirements:
- Theme/Topic: {today_theme}
- Tone: {settings['tone']}
- Duration: {settings['duration']} seconds
- Call-to-Action: {settings['call_to_action']}

The script should include:
1. A catchy HOOK (first 3 seconds to grab attention)
2. MAIN CONTENT broken into clear scenes with visuals and narration
3. The specified call-to-action at the end

Format as JSON with this structure:
{{
  "topic": "{today_theme}",
  "hook": "opening line",
  "scenes": [
    {{"narration": "what to say", "visual": "what to show", "duration": 5}},
    ...
  ],
  "cta": "{settings['call_to_action']}"
}}

Make it viral-worthy and perfect for TikTok! Be creative and engaging."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a professional TikTok video script writer. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 2000
    }
    
    try:
        print(f"🤖 Generating script about '{today_theme}' with Groq AI...")
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        ai_response = response.json()["choices"][0]["message"]["content"]
        print("📝 Script generated!\n")
        print("-" * 60)
        print(ai_response)
        print("-" * 60 + "\n")
        
        return ai_response, today_theme
        
    except Exception as e:
        print(f"❌ Error calling Groq API: {e}")
        return None, None


def generate_video_from_script(script_content, theme):
    """
    Generates actual .mp4 video file using AI video generation API.
    This function sends the script to a video generation API and waits for the result.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"auto_{theme.replace(' ', '_')}_{timestamp}.mp4"
    filepath = os.path.join(VIDEO_FOLDER, filename)
    
    os.makedirs(VIDEO_FOLDER, exist_ok=True)
    
    # Extract just the text content for the video prompt
    try:
        script_json = json.loads(script_content)
        # Combine hook, scenes, and CTA into one prompt
        prompt_parts = [script_json.get("hook", "")]
        for scene in script_json.get("scenes", []):
            prompt_parts.append(scene.get("narration", ""))
        prompt_parts.append(script_json.get("cta", ""))
        video_prompt = " ".join(filter(None, prompt_parts))
    except:
        # If JSON parsing fails, use the raw script
        video_prompt = script_content[:500]  # Limit to 500 chars
    
    print(f"🎬 Generating video with AI...")
    print(f"Prompt: {video_prompt[:200]}...")
    
    if VIDEO_API_PROVIDER == "hailuo":
        video_url = generate_with_hailuo(video_prompt)
    elif VIDEO_API_PROVIDER == "wan":
        video_url = generate_with_wan(video_prompt)
    elif VIDEO_API_PROVIDER == "custom_flow":
        print("⚠️  Custom Flow integration not yet implemented.")
        print("   Please implement your Flow API calls in generate_video_from_script()")
        return None
    else:
        print(f"❌ Unknown video API provider: {VIDEO_API_PROVIDER}")
        return None
    
    if not video_url:
        return None
    
    # Download the generated video
    print(f"📥 Downloading video from {video_url[:50]}...")
    try:
        response = requests.get(video_url, timeout=60)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Video saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        return None


def generate_with_hailuo(prompt):
    """Uses Hailuo/Minimax AI to generate video (free tier available)."""
    headers = {
        "Authorization": f"Bearer {AIML_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "minimax/hailuo-02",
        "prompt": prompt[:500]  # API limit
    }
    
    try:
        # Create generation task
        print("   Submitting to Hailuo AI...")
        response = requests.post(
            "https://api.aimlapi.com/v2/generate/video/minimax/generation",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        generation_id = result.get("id")
        
        if not generation_id:
            print(f"❌ No generation ID returned: {result}")
            return None
        
        print(f"   Generation ID: {generation_id}")
        print("   Waiting for video generation (this takes 4-8 minutes)...")
        
        # Poll for completion
        for attempt in range(60):  # Try for up to 10 minutes
            time.sleep(10)
            
            check_response = requests.get(
                f"https://api.aimlapi.com/v2/generate/video/minimax/generation?generation_id={generation_id}",
                headers=headers,
                timeout=30
            )
            check_response.raise_for_status()
            
            status_result = check_response.json()
            status = status_result.get("status")
            
            print(f"   Status: {status} (attempt {attempt + 1}/60)")
            
            if status == "completed":
                video_url = status_result.get("video", {}).get("url")
                if video_url:
                    print(f"   ✅ Video ready!")
                    return video_url
                else:
                    print(f"   ❌ No video URL in response: {status_result}")
                    return None
            elif status in ["failed", "error"]:
                print(f"   ❌ Generation failed: {status_result.get('error')}")
                return None
        
        print("   ❌ Timeout waiting for video generation")
        return None
        
    except Exception as e:
        print(f"   ❌ Error generating with Hailuo: {e}")
        return None


def generate_with_wan(prompt):
    """Uses Alibaba Wan 2.2 AI to generate video."""
    headers = {
        "Authorization": f"Bearer {AIML_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "alibaba/wan2.2-t2v-plus",
        "prompt": prompt[:500],
        "resolution": "1080P",
        "aspect_ratio": "9:16",  # TikTok format
        "watermark": False
    }
    
    try:
        # Create generation task
        print("   Submitting to Wan 2.2 AI...")
        response = requests.post(
            "https://api.aimlapi.com/v2/generate/video/alibaba/generation",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        generation_id = result.get("id")
        
        if not generation_id:
            print(f"❌ No generation ID returned: {result}")
            return None
        
        print(f"   Generation ID: {generation_id}")
        print("   Waiting for video generation (this takes several minutes)...")
        
        # Poll for completion
        for attempt in range(60):
            time.sleep(10)
            
            check_response = requests.get(
                f"https://api.aimlapi.com/v2/generate/video/alibaba/generation?generation_id={generation_id}",
                headers=headers,
                timeout=30
            )
            check_response.raise_for_status()
            
            status_result = check_response.json()
            status = status_result.get("status")
            
            print(f"   Status: {status} (attempt {attempt + 1}/60)")
            
            if status == "completed":
                video_url = status_result.get("video", {}).get("url")
                if video_url:
                    print(f"   ✅ Video ready!")
                    return video_url
                else:
                    print(f"   ❌ No video URL in response: {status_result}")
                    return None
            elif status in ["failed", "error"]:
                print(f"   ❌ Generation failed: {status_result.get('error')}")
                return None
        
        print("   ❌ Timeout waiting for video generation")
        return None
        
    except Exception as e:
        print(f"   ❌ Error generating with Wan: {e}")
        return None


def save_script(script_content, theme):
    """Saves the AI-generated script to a text file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    script_file = os.path.join(VIDEO_FOLDER, f"script_{theme.replace(' ', '_')}_{timestamp}.txt")
    
    os.makedirs(VIDEO_FOLDER, exist_ok=True)
    
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(f"TIKTOK VIDEO SCRIPT\n{'='*60}\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Theme: {theme}\n\n")
        f.write(f"{'='*60}\n\nAI GENERATED SCRIPT:\n{'-'*60}\n")
        f.write(script_content)
    
    print(f"📄 Script saved to: {script_file}\n")
    return script_file


def generate_daily_video():
    """
    Generates a new video using AI - FULLY AUTOMATIC, NO USER INPUT!
    Creates both the script AND the actual video file.
    """
    print("\n" + "="*60)
    print("🎬 STARTING AUTOMATIC AI VIDEO GENERATION")
    print("="*60 + "\n")
    
    # Generate script with AI (no user input needed!)
    script, theme = generate_script_with_groq()
    
    if not script:
        print("❌ Failed to generate script.")
        return False
    
    # Save script
    script_file = save_script(script, theme)
    
    # Generate actual video file from the script
    video_file = generate_video_from_script(script, theme)
    
    if video_file:
        print(f"\n✅ VIDEO GENERATION COMPLETE!")
        print(f"   Script: {script_file}")
        print(f"   Video: {video_file}\n")
        return True
    else:
        print(f"\n⚠️  Script generated but video creation failed.")
        print(f"   Script saved at: {script_file}")
        print(f"   You can manually create a video from the script.\n")
        return False


def next_video():
    """Returns the next video filepath in the folder."""
    files = [f for f in os.listdir(VIDEO_FOLDER) if f.lower().endswith((".mp4", ".mov"))]
    if not files:
        return None
    files.sort()
    return os.path.join(VIDEO_FOLDER, files[0])


def upload_video(filepath):
    """Uploads a video to Late API and returns the media URL."""
    print(f"Uploading {filepath} to Late media server...")
    
    with open(filepath, "rb") as f:
        files = {"files": f}
        headers = {"Authorization": f"Bearer {LATE_API_KEY}"}
        
        r = requests.post(
            API_MEDIA_URL,
            headers=headers,
            files=files
        )
    
    r.raise_for_status()
    response_data = r.json()
    
    # Late API returns uploaded media URL in files array
    if "files" in response_data and len(response_data["files"]) > 0:
        media_url = response_data["files"][0]["url"]
    else:
        raise ValueError(f"No media URL returned from API. Response: {response_data}")
    
    print(f"Upload successful. Media URL: {media_url}")
    return media_url


def create_post(media_url, caption="Auto‑posted video ✨"):
    """Creates a TikTok post using the uploaded media URL."""
    print("Creating TikTok post...")
    
    headers = {
        "Authorization": f"Bearer {LATE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "platforms": [{
            "platform": "tiktok",
            "accountId": ACCOUNT_ID
        }],
        "content": caption,
        "mediaItems": [{
            "type": "video",
            "url": media_url
        }]
    }
    
    r = requests.post(
        API_POST_URL,
        headers=headers,
        json=data
    )
    
    r.raise_for_status()
    return r.json()


def post_video():
    """Handles full posting sequence: pick video → upload → post → delete locally."""
    video = next_video()
    if video is None:
        print("⚠️  No videos found to post!")
        if ENABLE_AI_GENERATION:
            print("Tip: The AI generation created a script but no video file.")
            print("You need to integrate video generation (Flow API) or manually create the video.\n")
        return

    try:
        # Step 1: Upload video to get media URL
        media_url = upload_video(video)
        
        # Step 2: Create the TikTok post with that media URL
        res = create_post(media_url)
        print("✅ Posted successfully:", res)

        # Delete posted video to avoid repeats
        os.remove(video)
        print(f"🗑️  Deleted posted video: {video}\n")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error occurred: {e}")
        print(f"Response content: {e.response.text}")
        raise
    except Exception as e:
        print(f"❌ Error posting video: {e}")
        raise


def wait_until_post_time():
    """Sleeps until the daily post time."""
    while True:
        now = datetime.now().strftime("%H:%M")
        if now == POST_TIME:
            return
        time.sleep(30)  # check twice per minute


if __name__ == "__main__":
    print("="*60)
    print("🎥 TikTok Auto Poster Started (AI + Upload)")
    print("="*60)
    print(f"Configured to post daily at {POST_TIME}")
    print(f"Videos folder: {VIDEO_FOLDER}")
    print(f"TikTok Account ID: {ACCOUNT_ID}")
    print(f"AI Generation: {'ENABLED' if ENABLE_AI_GENERATION else 'DISABLED'}")
    print("-" * 60)
    
    # Check for API keys if AI generation is enabled
    if ENABLE_AI_GENERATION:
        if GROQ_API_KEY == "your_groq_api_key_here":
            print("\n⚠️  ERROR: GROQ_API_KEY not set!")
            print("Get FREE key from: https://console.groq.com/\n")
            exit(1)
        
        if VIDEO_API_PROVIDER != "custom_flow" and AIML_API_KEY == "your_aiml_api_key_here":
            print("\n⚠️  ERROR: AIML_API_KEY not set!")
            print("Get FREE key from: https://aimlapi.com/ (has free tier)")
            print("OR set VIDEO_API_PROVIDER = 'custom_flow' if using your own Flow setup\n")
            exit(1)
    
    print("\n")

    while True:
        # Wait until post time
        print(f"⏰ Waiting for post time ({POST_TIME})...")
        wait_until_post_time()
        
        # Generate video with AI if enabled
        if ENABLE_AI_GENERATION:
            generate_daily_video()
        
        # Upload and post video
        post_video()
        
        print("="*60)
        print("✅ Done for today! Waiting until tomorrow...")
        print("="*60 + "\n")
        
        time.sleep(60)  # avoid double-posting in the same minute