"""Tests for AutoInsta class."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.autoinsta import AutoInsta


class TestAutoInstaInit:
    """Test AutoInsta initialization."""

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'test_token',
        'INSTAGRAM_USER_ID': 'test_user_id'
    })
    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    def test_init_with_env_credentials(self, mock_media_creator, mock_poster):
        """Test initialization with environment variables."""
        autoinsta = AutoInsta(
            user_prompt="Test prompt",
            image_model="test:model",
            video_model="test:video"
        )

        assert autoinsta.user_prompt == "Test prompt"
        assert autoinsta.access_token == 'test_token'
        assert autoinsta.ig_user_id == 'test_user_id'
        assert autoinsta.creator is None

    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    def test_init_with_explicit_credentials(self, mock_media_creator, mock_poster):
        """Test initialization with explicit credentials."""
        autoinsta = AutoInsta(
            user_prompt="Test prompt",
            access_token="explicit_token",
            ig_user_id="explicit_user_id"
        )

        assert autoinsta.access_token == "explicit_token"
        assert autoinsta.ig_user_id == "explicit_user_id"

    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    def test_init_missing_credentials(self, mock_media_creator, mock_poster):
        """Test initialization fails without credentials."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('src.autoinsta.load_dotenv'):
                with pytest.raises(ValueError, match="Missing Instagram credentials"):
                    AutoInsta(user_prompt="Test prompt")

    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    def test_init_kwargs_passed_to_creator(self, mock_media_creator, mock_poster):
        """Test kwargs are properly passed to creation."""
        with patch.dict('os.environ', {
            'INSTAGRAM_ACCESS_TOKEN': 'token',
            'INSTAGRAM_USER_ID': 'user'
        }):
            autoinsta = AutoInsta(
                user_prompt="Test",
                width=1088,
                height=1920,
                narration_speed=1.5,
                background_relative_volume=2.0
            )

            assert autoinsta.creation_kwargs['width'] == 1088
            assert autoinsta.creation_kwargs['height'] == 1920
            assert autoinsta.creation_kwargs['narration_speed'] == 1.5
            assert autoinsta.creation_kwargs['background_relative_volume'] == 2.0

    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    def test_init_none_values_excluded(self, mock_media_creator, mock_poster):
        """Test None values are excluded from creation_kwargs."""
        with patch.dict('os.environ', {
            'INSTAGRAM_ACCESS_TOKEN': 'token',
            'INSTAGRAM_USER_ID': 'user'
        }):
            autoinsta = AutoInsta(
                user_prompt="Test",
                width=1088,
                height=1920,
                cover_url=None,
                some_param=None
            )

            assert 'cover_url' not in autoinsta.creation_kwargs
            assert 'some_param' not in autoinsta.creation_kwargs


class TestAutoInstaCreate:
    """Test AutoInsta.create() method."""

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    @pytest.mark.asyncio
    async def test_create_success(self, mock_media_creator_class, mock_poster_class):
        """Test successful media creation."""
        # Setup mocks
        mock_creator_instance = AsyncMock()
        mock_creator_instance.output = "media/path/video.mp4"
        mock_media_creator_class.return_value = mock_creator_instance

        autoinsta = AutoInsta(
            user_prompt="Test prompt",
            image_model="test:model",
            video_model="test:video"
        )

        result = await autoinsta.create()

        assert result == "media/path/video.mp4"
        assert autoinsta.creator == mock_creator_instance
        mock_creator_instance.create.assert_called_once()

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    @pytest.mark.asyncio
    async def test_create_with_kwargs(self, mock_media_creator_class, mock_poster_class):
        """Test create passes kwargs to MediaCreator."""
        mock_creator_instance = AsyncMock()
        mock_creator_instance.output = "video.mp4"
        mock_media_creator_class.return_value = mock_creator_instance

        autoinsta = AutoInsta(
            user_prompt="Test",
            narration_speed=2.0,
            background_relative_volume=1.5
        )

        await autoinsta.create()

        call_kwargs = mock_creator_instance.create.call_args[1]
        assert call_kwargs['narration_speed'] == 2.0
        assert call_kwargs['background_relative_volume'] == 1.5


class TestAutoInstaCreateCaptions:
    """Test AutoInsta.create_captions() method."""

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    @pytest.mark.asyncio
    async def test_create_captions_success(self, mock_media_creator_class, mock_poster_class):
        """Test successful caption creation."""
        mock_creator_instance = AsyncMock()
        mock_creator_instance.create_captions.return_value = "Generated captions"
        mock_media_creator_class.return_value = mock_creator_instance

        autoinsta = AutoInsta(user_prompt="Test")
        autoinsta.creator = mock_creator_instance

        result = await autoinsta.create_captions()

        assert result == "Generated captions"
        mock_creator_instance.create_captions.assert_called_once()

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    @pytest.mark.asyncio
    async def test_create_captions_without_creator(self, mock_media_creator_class, mock_poster_class):
        """Test captions creation fails without creator."""
        autoinsta = AutoInsta(user_prompt="Test")

        with pytest.raises(ValueError, match="Call create\\(\\) first"):
            await autoinsta.create_captions()


class TestAutoInstaPost:
    """Test AutoInsta.post() method."""

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    def test_post_success_with_list_output(self, mock_media_creator_class, mock_poster_class):
        """Test successful post with list of VideoFile objects."""
        # Mock VideoFile object
        mock_video_file = Mock()
        mock_video_file.path = "/path/to/video.mp4"

        mock_creator_instance = Mock()
        mock_creator_instance.output = [mock_video_file]  # List like StorylineVideo returns
        mock_media_creator_class.return_value = mock_creator_instance

        mock_poster_instance = Mock()
        mock_poster_instance.verify.return_value = {'username': 'testuser'}
        mock_poster_instance.post_reel.return_value = {'id': 'reel_123'}
        mock_poster_class.return_value = mock_poster_instance

        autoinsta = AutoInsta(user_prompt="Test")
        autoinsta.creator = mock_creator_instance
        autoinsta.poster = mock_poster_instance

        result = autoinsta.post(caption="Test caption")

        assert result is True
        mock_poster_instance.post_reel.assert_called_once_with(
            video="/path/to/video.mp4",
            caption="Test caption",
            share_to_feed=True
        )

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    def test_post_success_with_single_file(self, mock_media_creator_class, mock_poster_class):
        """Test successful post with single File object."""
        # Mock single File object
        mock_file = Mock()
        mock_file.path = "/path/to/narration.mp3"

        mock_creator_instance = Mock()
        mock_creator_instance.output = mock_file  # Single File object
        mock_media_creator_class.return_value = mock_creator_instance

        mock_poster_instance = Mock()
        mock_poster_instance.verify.return_value = {'username': 'testuser'}
        mock_poster_instance.post_reel.return_value = {'id': 'post_456'}
        mock_poster_class.return_value = mock_poster_instance

        autoinsta = AutoInsta(user_prompt="Test")
        autoinsta.creator = mock_creator_instance
        autoinsta.poster = mock_poster_instance

        result = autoinsta.post()

        assert result is True
        mock_poster_instance.post_reel.assert_called_once()

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    def test_post_without_creator(self, mock_media_creator_class, mock_poster_class):
        """Test post fails without creator."""
        autoinsta = AutoInsta(user_prompt="Test")

        with pytest.raises(ValueError, match="Call create\\(\\) first"):
            autoinsta.post()

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    def test_post_instagram_failure(self, mock_media_creator_class, mock_poster_class):
        """Test post handles Instagram API failures."""
        mock_video_file = Mock()
        mock_video_file.path = "/path/to/video.mp4"

        mock_creator_instance = Mock()
        mock_creator_instance.output = [mock_video_file]
        mock_media_creator_class.return_value = mock_creator_instance

        mock_poster_instance = Mock()
        mock_poster_instance.verify.return_value = {'username': 'testuser'}
        mock_poster_instance.post_reel.side_effect = Exception("API Error")
        mock_poster_class.return_value = mock_poster_instance

        autoinsta = AutoInsta(user_prompt="Test")
        autoinsta.creator = mock_creator_instance
        autoinsta.poster = mock_poster_instance

        result = autoinsta.post()

        assert result is False

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    def test_post_empty_list(self, mock_media_creator_class, mock_poster_class):
        """Test post handles empty list output."""
        mock_creator_instance = Mock()
        mock_creator_instance.output = []  # Empty list
        mock_media_creator_class.return_value = mock_creator_instance

        mock_poster_instance = Mock()
        mock_poster_instance.verify.return_value = {'username': 'testuser'}
        mock_poster_class.return_value = mock_poster_instance

        autoinsta = AutoInsta(user_prompt="Test")
        autoinsta.creator = mock_creator_instance
        autoinsta.poster = mock_poster_instance

        # Empty list should raise ValueError since it's falsy
        with pytest.raises(ValueError, match="Call create\\(\\) first"):
            autoinsta.post()

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'token',
        'INSTAGRAM_USER_ID': 'user'
    })
    @patch('src.autoinsta.InstagramPoster')
    @patch('src.autoinsta.MediaCreator')
    def test_post_with_object_without_path_attribute(self, mock_media_creator_class, mock_poster_class):
        """Test post with object that has no path attribute (fallback to object itself)."""
        mock_creator_instance = Mock()
        # Create an object without a .path attribute
        mock_creator_instance.output = "video.mp4"  # String directly
        mock_media_creator_class.return_value = mock_creator_instance

        mock_poster_instance = Mock()
        mock_poster_instance.verify.return_value = {'username': 'testuser'}
        mock_poster_instance.post_reel.return_value = {'id': 'reel_888'}
        mock_poster_class.return_value = mock_poster_instance

        autoinsta = AutoInsta(user_prompt="Test")
        autoinsta.creator = mock_creator_instance
        autoinsta.poster = mock_poster_instance

        result = autoinsta.post()

        assert result is True
        # Should pass the string directly as video
        mock_poster_instance.post_reel.assert_called_once_with(
            video="video.mp4",
            caption="",
            share_to_feed=True
        )
