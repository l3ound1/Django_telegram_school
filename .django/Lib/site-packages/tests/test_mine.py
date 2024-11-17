from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from requests import Response

from minetext import EsRequest, Mine
from minetext.config import Config
from minetext.exceptions import RefreshTokenExpiredError
from minetext.model.access_token import AccessToken


class TestMine:

    def test_search(self, mocked_requests_get):
        """
        Test a simple search query.
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)
        mine.search()

        # Make sure that it calls to the MINE API
        mocked_requests_get.assert_called_once()

        # Make sure that the parameters are correct
        url = f'{Config.host}/document/search'
        payload = {
            'q': es_request.search_term,
            'r[]': es_request.resources,
            'f[]': es_request.filters,
            'a': es_request.aggregation,
            'p': es_request.page,
            's': es_request.size,
            'wa': es_request.analytics
        }
        mocked_requests_get.assert_called_with(url, params=payload)

    def test_search_with_valid_token(self, mocked_requests_get: MagicMock, access_token: AccessToken,
                                     mocked_user_auth: MagicMock):
        """
        Test search with a valid token
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)

        mine._user_auth = mocked_user_auth
        mine._access_token = access_token
        mine.search()

        # Make sure that the token is not refreshed, since it's still valid
        mocked_user_auth.refresh_token.assert_not_called()

        # Make sure that the parameters are correct
        url = f'{Config.host}/document/search'
        payload = {
            'q': es_request.search_term,
            'r[]': es_request.resources,
            'f[]': es_request.filters,
            'a': es_request.aggregation,
            'p': es_request.page,
            's': es_request.size,
            'wa': es_request.analytics
        }
        headers = {
            'Authorization': f'Bearer {access_token.access_token}'
        }
        mocked_requests_get.assert_called_with(url, params=payload, headers=headers)

    def test_search_with_expired_token(self, mocked_requests_get: MagicMock, access_token: AccessToken,
                                       mocked_user_auth: MagicMock):
        """
        Test search with an expired token
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)

        # Make the token invalid
        access_token.expires_in = 0

        mine._user_auth = mocked_user_auth
        mine._access_token = access_token
        mine.search()

        # Make sure that the token is refreshed
        mocked_user_auth.refresh_token.assert_called_once()
        mocked_user_auth.refresh_token.assert_called_with(access_token)
        assert mine._access_token.access_token == 'new token'

        # Make sure that the parameters are correct
        url = f'{Config.host}/document/search'
        payload = {
            'q': es_request.search_term,
            'r[]': es_request.resources,
            'f[]': es_request.filters,
            'a': es_request.aggregation,
            'p': es_request.page,
            's': es_request.size,
            'wa': es_request.analytics
        }
        headers = {
            'Authorization': f'Bearer {mine._access_token.access_token}'
        }
        mocked_requests_get.assert_called_with(url, params=payload, headers=headers)

    def test_search_with_forbidden_request(self, mocked_requests_get: MagicMock, access_token: AccessToken,
                                           mocked_user_auth: MagicMock):
        """
        When the first authenticated search request returns 401, the client should refresh the token and try again once.
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)

        mine._user_auth = mocked_user_auth
        mine._access_token = access_token

        # GET request returns 401
        fake_response = Response()
        fake_response.status_code = 401
        mocked_requests_get.side_effect = requests.HTTPError(response=fake_response)

        with pytest.raises(requests.HTTPError):
            mine.search()

        # Make sure that the parameters are correct
        url = f'{Config.host}/document/search'
        payload = {
            'q': es_request.search_term,
            'r[]': es_request.resources,
            'f[]': es_request.filters,
            'a': es_request.aggregation,
            'p': es_request.page,
            's': es_request.size,
            'wa': es_request.analytics
        }
        headers = {
            'Authorization': f'Bearer {mine._access_token.access_token}'
        }
        mocked_requests_get.assert_called_with(url, params=payload, headers=headers)

        # The token is refresh once
        mocked_user_auth.refresh_token.assert_called_once()
        assert mine._access_token.access_token == 'new token'

    def test_search_with_error_request(self, mocked_requests_get: MagicMock, access_token: AccessToken,
                                       mocked_user_auth: MagicMock):
        """
        Make sure that an exception is thrown when the error happened during the request
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)

        mine._user_auth = mocked_user_auth
        mine._access_token = access_token

        # GET request returns anything except 401
        fake_response = Response()
        fake_response.status_code = 500
        mocked_requests_get.side_effect = requests.HTTPError(response=fake_response)

        with pytest.raises(requests.HTTPError):
            mine.search()

    def test_login_y(self, access_token: AccessToken, mocked_user_auth: MagicMock, monkeypatch: MonkeyPatch):
        """
        Test the login method with the ``y`` input from the user.
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)

        # No token were saved in the system
        mocked_user_auth.load_credentials.side_effect = FileNotFoundError()

        mine._user_auth = mocked_user_auth

        # Mock user's input as y
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        # Perform the full login
        mine.login(save_credentials=False)

        # Make sure that the system tried to load the credentials
        mocked_user_auth.load_credentials.assert_called_once()

        # Make sure that the device token is created
        mocked_user_auth.create_device_token.assert_called_once()

        # Make sure that the access token is created with proper parameters
        mocked_user_auth.create_access_token.assert_called_once()
        mocked_user_auth.create_access_token.assert_called_with(device_code=mine._device_token.device_code)

        # Make sure that the access token is updated
        assert mine._access_token.access_token == access_token.access_token

    def test_login_n(self, mocked_user_auth: MagicMock, monkeypatch: MonkeyPatch):
        """
        Test the login method with the ``N`` input from the user.
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)

        # No token were saved in the system
        mocked_user_auth.load_credentials.side_effect = FileNotFoundError()

        mine._user_auth = mocked_user_auth

        # Mock user's input as N
        monkeypatch.setattr('builtins.input', lambda _: 'N')

        # Perform the login
        mine.login(save_credentials=False)

        # Make sure that the system tried to load the credentials
        mocked_user_auth.load_credentials.assert_called_once()

        # Make sure that the device token is created
        mocked_user_auth.create_device_token.assert_called_once()

        # Make sure that the access token is not created
        mocked_user_auth.create_access_token.assert_not_called()

        # Make sure that the access token is still None
        assert mine._access_token is None

    def test_login_with_saved_token(self, access_token: AccessToken, mocked_user_auth: MagicMock):
        """
        Test the login method when there is already a token saved in the system.
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)

        # Found a token in the system
        mocked_user_auth.load_credentials.return_value = access_token

        mine._user_auth = mocked_user_auth

        # Perform the login
        mine.login(save_credentials=False)

        # Make sure that the system tried to load the credentials
        mocked_user_auth.load_credentials.assert_called_once()

        # Make sure that the token was refreshed
        mocked_user_auth.refresh_token.assert_called_once()
        assert mine._access_token.access_token == 'new token'

        # Make sure that no new token was issued
        mocked_user_auth.create_device_token.assert_not_called()
        mocked_user_auth.create_access_token.assert_not_called()

    def test_login_with_expired_saved_token(self, access_token: AccessToken, mocked_user_auth: MagicMock,
                                            monkeypatch: MonkeyPatch):
        """
        Test the login method when there is an expired token saved in the system
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)

        # Found an expired token in the system
        mocked_user_auth.load_credentials.return_value = access_token
        mocked_user_auth.refresh_token.side_effect = RefreshTokenExpiredError(creation_time=access_token.creation_time,
                                                                              current_time=datetime.now())
        mine._user_auth = mocked_user_auth

        # Mock user's input as y
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        # Perform the login
        mine.login(save_credentials=False)

        # Make sure that the system tried to load the credentials
        mocked_user_auth.load_credentials.assert_called_once()

        # Make sure that the system tried to refresh the token
        mocked_user_auth.refresh_token.assert_called_once()

        # Make sure that the device token is created
        mocked_user_auth.create_device_token.assert_called_once()

        # Make sure that the access token is created with proper parameters
        mocked_user_auth.create_access_token.assert_called_once()
        mocked_user_auth.create_access_token.assert_called_with(device_code=mine._device_token.device_code)

        # Make sure that new access token was issued
        assert mine._access_token.access_token == access_token.access_token

    def test_login_save_credentials(self, access_token: AccessToken, mocked_user_auth: MagicMock, tmp_path: Path):
        """
        Test the login method to see if it saves the token correctly in the system.
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)

        # Found a token in the system
        mocked_user_auth.load_credentials.return_value = access_token

        mine._user_auth = mocked_user_auth
        location = tmp_path / 'custom.pickle'

        # Perform the login
        mine.login(save_credentials=True, credentials_location=location)

        # Make sure that the token is saved
        mocked_user_auth.save_credentials.assert_called_once()

        mocked_user_auth.save_credentials.assert_called_with(mine._access_token, location)

    def test_host_getter_setter(self):
        """
        Test the getter/setter of the ``host`` property.
        """
        es_request = EsRequest(search_term='*')
        mine = Mine(es_request)

        input_host = 'https://example.com/'
        expected_host = 'https://example.com'
        mine.host = input_host

        # The host must not have the trailing slash
        assert mine.host == expected_host
