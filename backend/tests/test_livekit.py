"""
Tests for LiveKit Token Generation Router
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

from api.main import app

client = TestClient(app)


@pytest.fixture
def mock_livekit_env():
    """Mock LiveKit environment variables"""
    with patch.dict(os.environ, {
        'LIVEKIT_API_KEY': 'test_api_key',
        'LIVEKIT_API_SECRET': 'test_api_secret',
        'LIVEKIT_URL': 'wss://test.livekit.cloud'
    }):
        yield


class TestLiveKitTokenEndpoint:
    """Test cases for LiveKit token generation endpoint"""

    def test_generate_token_success(self, mock_livekit_env):
        """Test successful token generation"""
        with patch('api.routers.livekit.api.AccessToken') as mock_token:
            mock_token_instance = MagicMock()
            mock_token_instance.with_identity.return_value = mock_token_instance
            mock_token_instance.with_name.return_value = mock_token_instance
            mock_token_instance.with_grants.return_value = mock_token_instance
            mock_token_instance.to_jwt.return_value = 'test_jwt_token'
            mock_token.return_value = mock_token_instance

            response = client.post(
                '/api/v1/livekit/token',
                json={
                    'room_name': 'test-room',
                    'participant_name': 'test-user'
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert 'token' in data
            assert 'url' in data
            assert data['token'] == 'test_jwt_token'
            assert data['url'] == 'wss://test.livekit.cloud'

    def test_generate_token_missing_credentials(self):
        """Test token generation with missing credentials"""
        with patch.dict(os.environ, {}, clear=True):
            response = client.post(
                '/api/v1/livekit/token',
                json={
                    'room_name': 'test-room',
                    'participant_name': 'test-user'
                }
            )

            assert response.status_code == 500
            assert 'LiveKit credentials not configured' in response.json()['detail']

    def test_generate_token_default_participant_name(self, mock_livekit_env):
        """Test token generation with default participant name"""
        with patch('api.routers.livekit.api.AccessToken') as mock_token:
            mock_token_instance = MagicMock()
            mock_token_instance.with_identity.return_value = mock_token_instance
            mock_token_instance.with_name.return_value = mock_token_instance
            mock_token_instance.with_grants.return_value = mock_token_instance
            mock_token_instance.to_jwt.return_value = 'test_jwt_token'
            mock_token.return_value = mock_token_instance

            response = client.post(
                '/api/v1/livekit/token',
                json={
                    'room_name': 'test-room'
                }
            )

            assert response.status_code == 200
            mock_token_instance.with_identity.assert_called_with('user')
            mock_token_instance.with_name.assert_called_with('user')

    def test_generate_token_custom_participant_name(self, mock_livekit_env):
        """Test token generation with custom participant name"""
        with patch('api.routers.livekit.api.AccessToken') as mock_token:
            mock_token_instance = MagicMock()
            mock_token_instance.with_identity.return_value = mock_token_instance
            mock_token_instance.with_name.return_value = mock_token_instance
            mock_token_instance.with_grants.return_value = mock_token_instance
            mock_token_instance.to_jwt.return_value = 'test_jwt_token'
            mock_token.return_value = mock_token_instance

            response = client.post(
                '/api/v1/livekit/token',
                json={
                    'room_name': 'test-room',
                    'participant_name': 'custom-user'
                }
            )

            assert response.status_code == 200
            mock_token_instance.with_identity.assert_called_with('custom-user')
            mock_token_instance.with_name.assert_called_with('custom-user')

    def test_generate_token_livekit_error(self, mock_livekit_env):
        """Test token generation when LiveKit API fails"""
        with patch('api.routers.livekit.api.AccessToken') as mock_token:
            mock_token.side_effect = Exception('LiveKit API error')

            response = client.post(
                '/api/v1/livekit/token',
                json={
                    'room_name': 'test-room',
                    'participant_name': 'test-user'
                }
            )

            assert response.status_code == 500
            assert 'Failed to generate LiveKit token' in response.json()['detail']
