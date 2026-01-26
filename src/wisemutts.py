import os
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
        # Digital Scenario
        """
## Video Prompt

### Visual
A pixel art dog amidst a futuristic technological landscape filled with
robots and towering sci-fi buildings. Neon colors, glowing architecture,
and advanced technological elements surrounding the dog. The upper portion
is clear for text overlay. The dog moves peacefully through this futuristic
cityscape, with robots and hovering structures creating a dynamic yet serene
backdrop.

**Style:** Pixel art, 8-bit/16-bit aesthetic, futuristic sci-fi theme
**Composition:** Upper portion - clear/open for text, Lower portion - pixel art dog with movement
**Subject:** Pixel art dog in a futuristic technological world with robots and sci-fi buildings
**Movement:** Minimal, loopable micro-animations
**Mood:** Contemplative, futuristic, serene

### Narration
Short, whispered critiques about the digital age: how smartphones trap our attention,
how technology promised connection but delivered isolation, how we worship progress
while losing ourselves. Observations about the futility of endless scrolling,
the performance of digital life, and the human cost of constant connectivity.

**Voice:** Soft, contemplative, slightly melancholic
**Phrases:** 3-5 short sentences
**Theme:** Digital society, technology critique, disconnection, human cost of progress
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
"""
    ]

    @staticmethod
    def get_daily_prompt():
        """Select a prompt based on the current day for even distribution."""
        day_of_year = datetime.now().timetuple().tm_yday
        prompt_index = (day_of_year - 1) % len(WiseMutts.PROMPTS)
        return WiseMutts.PROMPTS[prompt_index]

    @staticmethod
    def get_background_audio_paths():
        """Get background audio paths with support for both local dev and Lambda environments."""
        # Get the base directory - Lambda uses /var/task, local uses current directory
        base_dir = os.getenv("LAMBDA_TASK_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

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

        return [os.path.join(base_dir, "tracks", track) for track in track_files]

    def __init__(
        self,
        access_token: Optional[str] = None,
        ig_user_id: Optional[str] = None,
        prompt_index: Optional[int] = None
    ):
        """Initialize WiseMutts with predefined configuration.

        Args:
            access_token: Instagram API token
            ig_user_id: Instagram user ID
            prompt_index: Which prompt to use (0, 1, or 2). If None, uses daily rotation.
        """
        if prompt_index is not None:
            daily_prompt = self.PROMPTS[prompt_index]
        else:
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

    async def create_captions(self):
        """Generate captions for the created media."""
        return await self.auto_insta.create_captions()

    def post(
        self,
        caption: str = "🧘 Wisdom from WiseMutts",
        share_to_feed: bool = True
    ) -> bool:
        """Post the created media to Instagram as a reel."""
        return self.auto_insta.post(caption=caption, share_to_feed=share_to_feed)
