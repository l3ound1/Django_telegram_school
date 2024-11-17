import logging
from pathlib import Path
from typing import Optional

import requests
from elasticsearch_dsl import Search
from elasticsearch_dsl.response import Response

from .config import Config
from .domain.es_request import EsRequest
from .domain.user_auth import UserAuth
from .exceptions import RefreshTokenExpiredError
from .model.access_token import AccessToken
from .model.device_token import DeviceToken


class Mine:
    _host: str
    es_request: EsRequest
    _user_auth: UserAuth
    _access_token: Optional[AccessToken]
    _device_token: Optional[DeviceToken]

    def __init__(self, es_request: EsRequest):
        """
        Initialize the MINE object. All interactions with the MINE system are done via the MINE object.

        Parameters
        ----------
        es_request : :py:class:`~minetext.domain.es_request.EsRequest`
            the object containing request information to Elasticsearch
        """
        self._host = Config.host
        self.es_request = es_request
        self._user_auth = UserAuth(host=Config.host)
        self._access_token = None
        self._device_token = None

    def search(self) -> Response:
        """
        Call the search endpoint with parameters provided via the
        :py:class:`~minetext.domain.es_request.EsRequest` property.

        Returns
        -------
        result : :ref:`Response <es-dsl:search_dsl>`
            the search result wrapped in the :ref:`Response <es-dsl:search_dsl>` object.

        Raises
        ------
        HTTPError
            if the request failed.
        """
        url = f'{self._host}/document/search'

        payload = {
            'q': self.es_request.search_term,
            'r[]': self.es_request.resources,
            'f[]': self.es_request.filters,
            'a': self.es_request.aggregation,
            'p': self.es_request.page,
            's': self.es_request.size,
            'wa': self.es_request.analytics
        }

        if self._access_token:

            # Refresh the access token if necessary
            if UserAuth.is_token_expired(creation_time=self._access_token.creation_time.timestamp(),
                                         expires_in=self._access_token.expires_in):
                self._access_token = self._user_auth.refresh_token(self._access_token)

            # Use the access token
            headers = {
                'Authorization': f'Bearer {self._access_token.access_token}'
            }

            try:
                result = requests.get(url, params=payload, headers=headers)
            except requests.HTTPError as e:
                # This is when the user is unauthorized. If they have an _access_token but 
                # are unauthorized the _access_token probably expired. 401 is unauthorized.
                if e.response.status_code == 401:
                    self._access_token = self._user_auth.refresh_token(self._access_token)
                    headers['Authorization'] = f'Bearer {self._access_token.access_token}'
                    result = requests.get(url, params=payload, headers=headers)
                else:
                    raise e
        else:
            result = requests.get(url, params=payload)

        # Parse the result using Elasticsearch Response
        response = Response(Search(), result.json())

        return response

    def login(self, save_credentials: bool = True, credentials_location: Path = None) -> None:
        """
        Calls the functions to authorize user.

        It first checks if the credentials is already available at ``credentials_location``. If yes, it will try to
        authenticate using the refresh token found in that credentials. In case the credentials is not found in the
        system, or the refresh token is already expired, the full login process is triggered.

        In the full login process, users need to follow the URL printed in the console to log in, grant access
        to the app, and response to the console input.

        Parameters
        ----------
        save_credentials : bool, default=True
            Indicate if the credentials should be saved in the machine after login.
        credentials_location: :py:class:`~pathlib.Path`, default=$HOME/.minetext/user.pickle
            Where the file should be stored. The path must also include the file name.
        """
        logger = logging.getLogger(__name__)

        if not credentials_location:
            credentials_location = self._user_auth.default_file_location

        need_login_again = False

        try:
            # Load credentials
            logger.info(f'Loading credentials at {credentials_location}')
            self._access_token = self._user_auth.load_credentials(credentials_location)

            # Obtain new token
            logger.info('Obtaining new access token...')
            self._access_token = self._user_auth.refresh_token(self._access_token)
        except FileNotFoundError:
            need_login_again = True
            logger.info(f'Token is not found at {credentials_location}')
        except RefreshTokenExpiredError as e:
            logger.info(e.message)
            need_login_again = True

        if need_login_again:
            self._device_token = self._user_auth.create_device_token()
            print(f'Please sign in at this website and grant access: {self._device_token.verification_uri_complete}')
            input_str = input('Did you grant the access? [y/N] ')
            if input_str != 'y':
                return
            self._access_token = self._user_auth.create_access_token(device_code=self._device_token.device_code)
            print('Login successful! You are now authorized.')

        if save_credentials:
            logger.info(f'Save credentials at {credentials_location}')
            self._user_auth.save_credentials(self._access_token, credentials_location)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value: str):
        self._host = value.rstrip('/')
