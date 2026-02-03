#!/usr/bin/env python3
"""Test script to upload a video to Instagram using instapost."""
import os
from dotenv import load_dotenv
from instapost import InstagramPoster

# Load environment variables
load_dotenv()

# Get credentials
access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
ig_user_id = os.getenv("INSTAGRAM_USER_ID")

if not access_token or not ig_user_id:
    raise ValueError("Missing INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_USER_ID in .env")

# Video path and caption
video_path = "media/storylinevideo/storylinevideo(2)/video_8.mp4"
caption = "Venture into the unknown and discover your magic ✨🪐 What makes you different makes you beautiful 💫 #inspiration #motivational #growth #selflove #positivevibes"

print(f"📹 Uploading video: {video_path}")
print(f"📝 Caption: {caption[:50]}...\n")

# Create poster instance
poster = InstagramPoster(access_token=access_token, ig_user_id=ig_user_id)

# Upload video
try:
    print("🚀 Uploading to Instagram...")
    result = poster.post_reel(
        video=video_path,
        caption=caption
    )
    print(f"\n✅ Upload successful!")
    print(f"Result: {result}")
except Exception as e:
    print(f"\n❌ Upload failed: {e}")
    import traceback
    traceback.print_exc()
