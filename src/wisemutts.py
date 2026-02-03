import os
import random
import time
from typing import Optional
from datetime import datetime
from .autoinsta import AutoInsta


class WiseMutts:
    """Automated content creation and posting to Instagram with WiseMutts configuration."""

    PROMPTS = [
        # Original: Presence & Simplicity (Locked)
        """
## Video Prompt

### Visual
A peaceful pixel art loop of a dog in a tranquil natural setting. Compose
the image with the upper portion featuring a clear, open area for text
overlay, and the lower portion containing the dog with subtle, gentle
movements. The loop should feel meditative and seamless. Avoid cluttering
the upper portion to leave space for subtitles.

**Style:** Pixel art, 8-bit/16-bit aesthetic
**Composition:** Upper portion - clear/open background, Lower portion -
dog with movement
**Subject:** Dog in a peaceful environment
**Movement:** Minimal, loopable micro-animations
**Mood:** Peaceful, contemplative, meditative

### Narration
Short, whispered philosophical reflections on life's meaning. Each phrase
focuses on presence, simple joys, or finding peace in stillness. Keep
sentences brief and impactful.

**Voice:** Soft, contemplative
**Phrases:** 3-5 short sentences
**Theme:** The meaning of life, presence, simplicity
""",
        # Alien Scenario
        """
## Video Prompt

### Visual
A pixel art dog-like spirit exploring a beautiful alien planet.
The landscape is vibrant with otherworldly beauty. The upper portion is
clear for text overlay.

**Style:** Pixel art, 8-bit/16-bit aesthetic, alien/sci-fi environment
**Composition:** Upper portion - clear for text; Lower portion - dog with movement
**Subject:** Dog in an alien landscape
**Movement:** Minimal, loopable micro-animations
**Mood:** Inspiring, wondrous, peaceful

### Narration
Short, whispered reflections on growth, embracing the unknown, and finding
beauty in unfamiliar places.

**Voice:** Soft, contemplative, hopeful
**Phrases:** 3-5 short sentences
**Theme:** Growth, uniqueness, embracing the unknown
""",
        # Social Scenario
        """
## Video Prompt

### Visual
A pixel art dog wandering through a city or town. Buildings, streets, and
urban environment. The upper portion is clear for text overlay. The dog
walks calmly through the urban landscape, finding peace in the town.

**Style:** Pixel art, 8-bit/16-bit aesthetic, urban setting
**Composition:** Upper portion - clear/open for text, Lower portion - dog with movement
**Subject:** Dog in a city or town
**Movement:** Minimal, loopable micro-animations
**Mood:** Calm, peaceful, grounded

### Narration
Short, whispered reflections on authenticity, individuality, and being true
to yourself in a world that often pressures conformity.

**Voice:** Soft, contemplative
**Phrases:** 3-5 short sentences
**Theme:** Authenticity, individuality
""",
        # Nighttime Nature Scenario
        """
## Video Prompt

### Visual
A peaceful pixel art loop of a dog in a tranquil natural setting at night.
A moonlit landscape with a very starry sky filling the upper portion, creating
a sense of calm wonder and serenity. The composition features the night sky with
the moon and numerous stars for text overlay, and the lower portion containing
the dog with subtle, gentle movements. The loop should feel meditative and seamless.

**Style:** Pixel art, 8-bit/16-bit aesthetic
**Composition:** Upper portion - moonlit night sky with abundant stars and clear area
for text; Lower portion - dog with movement
**Subject:** Dog in a peaceful natural environment at night
**Movement:** Minimal, loopable micro-animations
**Mood:** Peaceful, contemplative, meditative, serene, mystical

### Narration
Short, whispered philosophical reflections on life's meaning under the stars.
Each phrase focuses on presence, simple joys, quiet moments, and finding peace
in stillness and the night sky. Keep sentences brief and impactful.

**Voice:** Soft, contemplative, gentle
**Phrases:** 3-5 short sentences
**Theme:** The meaning of life, presence, simplicity, the night, serenity
""",
        # Lofi Home with Owner
        """
## Video Prompt

### Visual
A cozy lofi pixel art home scene with a dog and its owner sitting together.
The owner is seated and absorbed in their smartphone, seemingly oblivious.
The dog sits nearby, looking at the owner with a sad or longing expression,
yearning for attention and connection. The room has warm, comfortable lighting
but feels emotionally distant. The upper portion is clear for text overlay.

**Style:** Pixel art, 8-bit/16-bit aesthetic, lofi/cozy vibes
**Composition:** Upper portion - clear/open for text; Lower portion - scene
with owner and dog
**Subject:** Dog and owner in a home setting, with emotional disconnect
**Movement:** Minimal, loopable micro-animations
**Mood:** Bittersweet, melancholic, neglected, yearning

### Narration
Short, whispered reflections on digital distraction, loneliness despite
physical proximity, the importance of presence, or being forgotten by those
we love. Observations about connection lost to screens.

**Voice:** Soft, melancholic, contemplative
**Phrases:** 3-5 short sentences
**Theme:** Digital distraction, neglect, loneliness, the need for presence
"""
    ]

    @staticmethod
    def get_daily_prompt():
        """Select a prompt based on the current day for even distribution."""
        day_of_year = datetime.now().timetuple().tm_yday
        prompt_index = (day_of_year - 1) % len(WiseMutts.PROMPTS)
        return WiseMutts.PROMPTS[prompt_index]

    @staticmethod
    def get_random_prompt():
        """Select a random prompt."""
        return random.choice(WiseMutts.PROMPTS)

    @staticmethod
    def get_background_audio_paths():
        """Get background audio paths with support for both local dev and Lambda environments."""
        # Get the base directory - Lambda uses /var/task, local uses project root
        if os.getenv("LAMBDA_TASK_ROOT"):
            base_dir = os.getenv("LAMBDA_TASK_ROOT")
        else:
            # For local development, go up from src/ to project root
            base_dir = os.path.dirname(os.path.dirname(__file__))

        track_files = [
            "4YnecPKoxaI.mp3",
            "KnbZN_FNwk0.mp3",
            "Udf4_YCp_Mg.mp3",
            "SNWM2DxcDfI.mp3",
            "nhDp_MQhX9Y.mp3",
            "z17Ild98vzY.mp3",
            "eeOYPbDmlOo.mp3",
            "hHREvYAZP-A.mp3",
            "7bYf1AQBaj8.mp3",
            "aVM6Fbh4hc4.mp3",
            "h11FkwrbM3I.mp3",
            "m-6-PMiaZgM.mp3",
            "MKGXYNTnp1g.mp3",
            "5BIqnLWSC_s.mp3"
        ]

        return [os.path.join(base_dir, "tracks", track)
                for track in track_files]

    def __init__(
        self,
        access_token: Optional[str] = None,
        ig_user_id: Optional[str] = None,
        prompt_index: Optional[int] = None,
        prompt_mode: str = "daily"
    ):
        """Initialize WiseMutts with predefined configuration.

        Args:
            access_token: Instagram API token
            ig_user_id: Instagram user ID
            prompt_index: Which prompt to use (0-4). If None, uses prompt_mode.
            prompt_mode: How to select prompts - "daily" (default), "random",
                         or explicit index.
        """
        if prompt_index is not None:
            daily_prompt = self.PROMPTS[prompt_index]
        elif prompt_mode == "random":
            daily_prompt = self.get_random_prompt()
        else:  # "daily" or default
            daily_prompt = self.get_daily_prompt()
        self.auto_insta = AutoInsta(
            user_prompt=daily_prompt,
            access_token=access_token,
            ig_user_id=ig_user_id,
            image_model="rundiffusion:110@101",
            video_model="bytedance:1@1",
            width=1088,
            height=1920,
            narration_silence_tail=5,
            narration_speed=1.0,
            background_relative_volume=2.0,
            background_audio_paths=self.get_background_audio_paths(),
            subtitle_fontname="Times New Roman",
            subtitle_fontsize=18,
            subtitle_color="#FFFFFF",
            subtitle_outline_color="#000000",
            subtitle_positions=["top_center"]
        )

    async def create(self):
        """Create media using MediaCreator."""
        await self.auto_insta.create()
        return self.auto_insta.creator.output

    def get_captions(self):
        """Get captions generated during media creation."""
        return self.auto_insta.get_captions()

    def post(
        self,
        caption: str = "🧘 Wisdom from WiseMutts",
        share_to_feed: bool = True,
        max_retries: int = 10,
        retry_timeout: int = 600
    ) -> bool:
        """Post the created media to Instagram as a reel with retry logic.

        Args:
            caption: Caption text for the reel
            share_to_feed: Whether to share to feed
            max_retries: Maximum number of retry attempts
            retry_timeout: Total timeout in seconds (default 600 = 10 minutes)

        Returns:
            True if post was successful, False otherwise
        """
        start_time = time.time()
        attempt = 0

        while attempt < max_retries:
            elapsed_time = time.time() - start_time

            # Check if we've exceeded the timeout
            if elapsed_time > retry_timeout:
                print(f"⏱️ Retry timeout exceeded ({retry_timeout}s). Giving up.")
                return False

            attempt += 1
            time_left = retry_timeout - elapsed_time

            try:
                print(f"📤 Upload attempt {attempt}/{max_retries} "
                      f"(Time left: {int(time_left)}s)")
                result = self.auto_insta.post(
                    caption=caption,
                    share_to_feed=share_to_feed
                )
                if result:
                    print("✅ Post successful!")
                    return True
                else:
                    print("⚠️ Post returned False, retrying...")
            except Exception as e:
                print(f"❌ Upload error: {e}")
                if attempt < max_retries:
                    # Calculate exponential backoff: 5, 10, 20, 40, 60, 60, 60...
                    backoff = min(2 ** (attempt - 1) * 5, 60)
                    time_left = retry_timeout - (time.time() - start_time)

                    if time_left > 0:
                        wait_time = min(backoff, time_left)
                        print(f"⏳ Waiting {wait_time:.0f}s before retry...")
                        time.sleep(wait_time)
                    else:
                        print("⏱️ Timeout reached, no time for retry.")
                        return False
                else:
                    return False

        print(f"❌ Failed after {max_retries} attempts")
        return False
