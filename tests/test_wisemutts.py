"""Tests for WiseMutts class."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.wisemutts import WiseMutts


class TestWiseMuttsInit:
    """Test WiseMutts initialization."""

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.wisemutts.AutoInsta')
    def test_init_success(self, mock_autoinsta):
        """Test successful initialization."""
        wisemutts = WiseMutts()

        assert isinstance(wisemutts, WiseMutts)
        mock_autoinsta.assert_called_once()

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user',
        'PROMPT_MODE': '2'
    })
    @patch('src.wisemutts.AutoInsta')
    def test_init_with_custom_prompt_index(self, mock_autoinsta):
        """Test initialization with custom prompt index via PROMPT_MODE."""
        WiseMutts()

        call_kwargs = mock_autoinsta.call_args[1]
        # Verify the third prompt (index 2) was passed
        assert "authenticity" in call_kwargs['user_prompt']

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.wisemutts.AutoInsta')
    def test_init_passes_background_audio_paths(self, mock_autoinsta):
        """Test initialization passes background audio paths."""
        WiseMutts()

        call_kwargs = mock_autoinsta.call_args[1]
        assert 'background_audio_paths' in call_kwargs
        assert isinstance(call_kwargs['background_audio_paths'], list)
        assert len(call_kwargs['background_audio_paths']) == 14

        call_kwargs = mock_autoinsta.call_args[1]
        assert 'background_audio_paths' in call_kwargs
        assert isinstance(call_kwargs['background_audio_paths'], list)
        assert len(call_kwargs['background_audio_paths']) == 14


class TestWiseMuttsGetDailyPrompt:
    """Test WiseMutts.get_daily_prompt() static method."""

    def test_get_daily_prompt_jan_1(self):
        """Test daily prompt for January 1st."""
        with patch('src.wisemutts.datetime') as mock_datetime:
            mock_datetime.now.return_value.timetuple.return_value.tm_yday = 1
            prompt = WiseMutts.get_daily_prompt()
            assert prompt == WiseMutts.PROMPTS[0]

    def test_get_daily_prompt_rotation(self):
        """Test daily prompt rotates through all prompts."""
        with patch('src.wisemutts.datetime') as mock_datetime:
            mock_datetime.now.return_value.timetuple.return_value.tm_yday = 1
            assert WiseMutts.get_daily_prompt() == WiseMutts.PROMPTS[0]

            mock_datetime.now.return_value.timetuple.return_value.tm_yday = 2
            assert WiseMutts.get_daily_prompt() == WiseMutts.PROMPTS[1]

            mock_datetime.now.return_value.timetuple.return_value.tm_yday = 3
            assert WiseMutts.get_daily_prompt() == WiseMutts.PROMPTS[2]


class TestWiseMuttsGetBackgroundAudioPaths:
    """Test WiseMutts.get_background_audio_paths() static method."""

    def test_get_background_audio_paths_in_lambda(self):
        """Test audio paths in Lambda environment."""
        with patch.dict('os.environ', {'LAMBDA_TASK_ROOT': '/var/task'}):
            paths = WiseMutts.get_background_audio_paths()

            for path in paths:
                assert path.startswith('/var/task/tracks/')
                assert path.endswith('.mp3')

    def test_get_background_audio_paths_count(self):
        """Test correct number of audio paths returned."""
        with patch.dict('os.environ', {'LAMBDA_TASK_ROOT': '/var/task'}):
            paths = WiseMutts.get_background_audio_paths()
            assert len(paths) == 14


class TestWiseMuttsProxyMethods:
    """Test WiseMutts proxy methods."""

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.wisemutts.AutoInsta')
    @pytest.mark.asyncio
    async def test_create_proxies_to_autoinsta(self, mock_autoinsta_class):
        """Test create() proxies to AutoInsta."""
        mock_autoinsta_instance = AsyncMock()
        mock_creator = AsyncMock()
        mock_creator.output = "video.mp4"
        mock_autoinsta_instance.creator = mock_creator
        mock_autoinsta_class.return_value = mock_autoinsta_instance

        wisemutts = WiseMutts()
        result = await wisemutts.create()

        mock_autoinsta_instance.create.assert_called_once()
        assert result == "video.mp4"

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.wisemutts.AutoInsta')
    def test_get_captions_proxies_to_autoinsta(self, mock_autoinsta_class):
        """Test get_captions() proxies to AutoInsta."""
        mock_autoinsta_instance = Mock()
        mock_autoinsta_instance.get_captions.return_value = "Captions"
        mock_autoinsta_class.return_value = mock_autoinsta_instance

        wisemutts = WiseMutts()
        result = wisemutts.get_captions()

        mock_autoinsta_instance.get_captions.assert_called_once()
        assert result == "Captions"

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.wisemutts.AutoInsta')
    def test_post_proxies_to_autoinsta(self, mock_autoinsta_class):
        """Test post() proxies to AutoInsta."""
        mock_autoinsta_instance = Mock()
        mock_autoinsta_instance.post.return_value = True
        mock_autoinsta_class.return_value = mock_autoinsta_instance

        wisemutts = WiseMutts()
        result = wisemutts.post(caption="Test", share_to_feed=False)

        mock_autoinsta_instance.post.assert_called_once_with(
            caption="Test",
            share_to_feed=False
        )
        assert result is True


class TestWiseMuttsPromptsStructure:
    """Test WiseMutts prompts are properly defined."""

    def test_prompts_exist(self):
        """Test that prompts list exists."""
        assert hasattr(WiseMutts, 'PROMPTS')
        assert isinstance(WiseMutts.PROMPTS, list)
        assert len(WiseMutts.PROMPTS) >= 1

    def test_prompts_count(self):
        """Test that there are exactly 5 prompts."""
        assert len(WiseMutts.PROMPTS) == 5
