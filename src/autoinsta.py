import os
from typing import Optional
from dotenv import load_dotenv

from mediaichemy.creator import MediaCreator
from mediaichemy.media import StorylineVideo
from instapost import InstagramPoster


class AutoInsta:
    """General purpose class for creating media and posting to Instagram."""

    DEFAULT_WIDTH = 1920
    DEFAULT_HEIGHT = 1088
    DEFAULT_CREATOR_MODEL = "anthropic/claude-sonnet-4.5"

    def __init__(self, user_prompt: str, access_token: Optional[str] = None,
                 ig_user_id: Optional[str] = None,
                 **kwargs):
        """Initialize AutoInsta with media creation parameters."""
        load_dotenv()
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.ig_user_id = ig_user_id or os.getenv("INSTAGRAM_USER_ID")

        if not self.access_token or not self.ig_user_id:
            raise ValueError("Missing Instagram credentials in .env")

        self.user_prompt = user_prompt
        self.creation_kwargs = {
            "width": kwargs.pop("width", self.DEFAULT_WIDTH),
            "height": kwargs.pop("height", self.DEFAULT_HEIGHT),
        }
        self.creation_kwargs.update({k: v for k, v in kwargs.items() if v is not None})

        self.creator = None
        self.poster = InstagramPoster(
            access_token=self.access_token,
            ig_user_id=self.ig_user_id
        )

    async def create(self):
        """Create media using MediaCreator."""
        print("🎬 Creating media...")
        self.creator = MediaCreator(
            creator_model=self.DEFAULT_CREATOR_MODEL,
            media_type=StorylineVideo
        )

        await self.creator.create(user_prompt=self.user_prompt, **self.creation_kwargs)
        print("✅ Media created! Access via: self.creator.output")
        return self.creator.output

    async def create_captions(self):
        """Generate captions for the created media."""
        if not self.creator:
            raise ValueError("Call create() first")

        print("📝 Generating captions...")
        captions = await self.creator.create_captions()
        print("✅ Captions generated!")
        return captions

    def post(
        self,
        caption: str = "",
        share_to_feed: bool = True
    ) -> bool:
        """Post the created media to Instagram as a reel."""

        # Validate creator output exists
        if not self.creator or not self.creator.output:
            raise ValueError("Call create() first to generate media")

        print(f"📸 Posting reel...\n{caption}")

        try:
            user_info = self.poster.verify()
            print(f"✅ Connected as: {user_info.get('username', 'Unknown')}")

            # Handle different output formats from mediaichemy versions
            output = self.creator.output
            if isinstance(output, dict):
                # mediaichemy 1.1.0+ returns a dict with 'video' key
                video_url = output.get('video') or output.get('path')
            elif isinstance(output, (list, tuple)):
                # If it's a list/tuple, take the first element (video file)
                video_url = output[0] if output else None
            else:
                # Assume it's already a string path
                video_url = output

            if not video_url:
                raise ValueError(f"Could not extract video URL from output: {output}")

            result = self.poster.post_reel(
                video_url=video_url,
                caption=caption,
                share_to_feed=share_to_feed
            )
            print(f"✅ Reel posted! (ID: {result.get('id')})")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
