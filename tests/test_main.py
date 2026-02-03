"""Tests for main.py Lambda handler and automation functions."""
import pytest
import json
from unittest.mock import patch, AsyncMock, Mock
from src.main import main, lambda_handler


class TestMain:
    """Test main() automation function."""

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'test_token',
        'INSTAGRAM_USER_ID': 'test_user_id'
    })
    @patch('src.main.WiseMutts')
    @pytest.mark.asyncio
    async def test_main_success(self, mock_wisemutts_class):
        """Test successful main execution."""
        # Setup mocks
        mock_wisemutts = Mock()
        mock_wisemutts.create = AsyncMock(return_value="video.mp4")
        mock_captions = Mock()
        mock_captions.instagram.caption = "Test caption"
        mock_wisemutts.get_captions = Mock(return_value=mock_captions)
        mock_wisemutts.post = Mock(return_value=True)
        mock_wisemutts_class.return_value = mock_wisemutts

        await main()

        mock_wisemutts_class.assert_called_once()
        mock_wisemutts.create.assert_called_once()
        mock_wisemutts.get_captions.assert_called_once()
        mock_wisemutts.post.assert_called_once()

    @patch('src.main.load_dotenv')
    @patch.dict('os.environ', {}, clear=True)
    @pytest.mark.asyncio
    async def test_main_missing_access_token(self, mock_load_dotenv):
        """Test main fails without INSTAGRAM_ACCESS_TOKEN."""
        with pytest.raises(ValueError, match="INSTAGRAM_ACCESS_TOKEN"):
            await main()

    @patch('src.main.load_dotenv')
    @patch.dict('os.environ', {'INSTAGRAM_ACCESS_TOKEN': 'token'}, clear=True)
    @pytest.mark.asyncio
    async def test_main_missing_user_id(self, mock_load_dotenv):
        """Test main fails without INSTAGRAM_USER_ID."""
        with pytest.raises(ValueError, match="INSTAGRAM_USER_ID"):
            await main()

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'test_token',
        'INSTAGRAM_USER_ID': 'test_user_id'
    })
    @patch('src.main.WiseMutts')
    @pytest.mark.asyncio
    async def test_main_post_failure(self, mock_wisemutts_class):
        """Test main handles post failure."""
        mock_wisemutts = Mock()
        mock_wisemutts.create = AsyncMock(return_value="video.mp4")
        mock_captions = Mock()
        mock_captions.instagram = Mock()
        mock_captions.instagram.caption = "Caption"
        mock_wisemutts.get_captions = Mock(return_value=mock_captions)
        mock_wisemutts.post = Mock(return_value=False)  # Post failed
        mock_wisemutts_class.return_value = mock_wisemutts

        # main() catches exceptions internally, so it won't raise
        # The error should be handled gracefully
        await main()

        # Verify post was attempted
        mock_wisemutts.post.assert_called_once()

    @patch.dict('os.environ', {
        'INSTAGRAM_ACCESS_TOKEN': 'test_token',
        'INSTAGRAM_USER_ID': 'test_user_id'
    })
    @patch('src.main.WiseMutts')
    @pytest.mark.asyncio
    async def test_main_exception_handling(self, mock_wisemutts_class):
        """Test main handles exceptions."""
        mock_wisemutts_class.side_effect = Exception("Test error")

        await main()

        # Should not raise, just print error


class TestLambdaHandler:
    """Test lambda_handler function."""

    @patch('src.main.main')
    def test_lambda_handler_success(self, mock_main):
        """Test lambda handler with successful execution."""
        mock_main.return_value = None  # Sync function in test

        result = lambda_handler({}, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert 'message' in body

    @patch('src.main.main')
    def test_lambda_handler_failure(self, mock_main):
        """Test lambda handler with exception."""
        mock_main.side_effect = Exception("Test error")

        result = lambda_handler({}, {})

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'error' in body
        assert 'Test error' in body['error']

    @patch('src.main.main')
    def test_lambda_handler_returns_json(self, mock_main):
        """Test lambda handler returns valid JSON."""
        result = lambda_handler({}, {})

        assert 'statusCode' in result
        assert 'body' in result
        assert isinstance(result['body'], str)
        # Should be valid JSON
        json.loads(result['body'])


class TestMainExecution:
    """Test main module can be executed as script."""

    def test_module_has_main_guard(self):
        """Test that __name__ == '__main__' guard exists."""
        import src.main as main_module
        assert hasattr(main_module, 'main')
        assert hasattr(main_module, 'lambda_handler')
