import os
from typing import Optional
from dotenv import load_dotenv
import boto3

from mediaichemy.creator import MediaCreator
from mediaichemy.media import StorylineVideo
from instapost import InstagramPoster
from src.retry import retry_with_backoff


class S3Uploader:
    """Upload and delete files from AWS S3."""

    def __init__(self, s3_uri: Optional[str] = None):
        """Initialize S3Uploader.

        Args:
            s3_uri: S3 URI in format s3://bucket-name.
                    If not provided, reads from S3_URI env var.

        Raises:
            ValueError: If s3_uri is not provided or is invalid format.
        """
        s3_uri = s3_uri or os.getenv("S3_URI")
        if not s3_uri:
            raise ValueError("S3 URI required - pass s3_uri parameter or set S3_URI env var")

        # Parse S3 URI (s3://bucket-name)
        if not s3_uri.startswith("s3://"):
            raise ValueError(f"Invalid S3 URI format: {s3_uri}. Expected: s3://bucket-name")

        self.bucket_name = s3_uri[5:]  # Remove s3:// prefix
        self.s3_client = boto3.client("s3")

    def upload(self, file_path: str, object_name: Optional[str] = None) -> str:
        """Upload a file to S3 and return its URL.

        Args:
            file_path: Local path to the file
            object_name: Name to use in S3 (defaults to filename)

        Returns:
            S3 URL for the uploaded file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if object_name is None:
            object_name = os.path.basename(file_path)

        self.s3_client.upload_file(file_path, self.bucket_name, object_name)
        url = f"https://{self.bucket_name}.s3.amazonaws.com/{object_name}"
        return url

    def delete(self, object_name: str) -> bool:
        """Delete a file from S3.

        Args:
            object_name: Name of the object in S3

        Returns:
            True if successful
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except Exception as e:
            print(f"Failed to delete {object_name}: {e}")
            return False


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

        # Extract S3 URI and create S3 uploader
        s3_uri = kwargs.pop("s3_uri", None)
        self.s3_uploader = S3Uploader(s3_uri=s3_uri) if s3_uri else None

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

            # StorylineVideo returns a list of VideoFile objects; use the first one
            output = self.creator.output
            if isinstance(output, list):
                video_path = output[0].path if output else None
            else:
                video_path = output.path if hasattr(output, 'path') else output

            if not video_path:
                raise ValueError(f"Could not extract video path from output: {output}")

            # Upload to S3 if uploader is provided
            if self.s3_uploader:
                print("☁️  Uploading video to S3...")
                video_path = self.s3_uploader.upload(video_path)
                print(f"✅ Video uploaded to S3: {video_path}")

            result = self._post_reel_with_retry(
                video=video_path,
                caption=caption,
                share_to_feed=share_to_feed
            )
            print(f"✅ Reel posted! (ID: {result.get('id')})")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False

    @retry_with_backoff()
    def _post_reel_with_retry(self, video: str, caption: str, share_to_feed: bool):
        """
        Internal method to post reel with retry logic.

        Args:
            video: Path to video file
            caption: Caption text
            share_to_feed: Whether to share to feed

        Returns:
            Result dict with post details
        """
        return self.poster.post_reel(
            video=video,
            caption=caption,
            share_to_feed=share_to_feed
        )
