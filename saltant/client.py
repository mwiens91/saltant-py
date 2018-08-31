"""Contains the saltant API client."""

# TODO(mwiens91): add support for JWT auth tokens
# TODO(mwiens91): specify what happens when default timeout is exhausted

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import requests
from saltant.constants import (
    DEFAULT_TIMEOUT_SECONDS,
    HTTP_200_OK,
)
from saltant.exceptions import (
    AuthenticationError,
    BadEnvironmentError,
)


class Client:
    """API client for communicating with a saltant server.

    Example:

        >>> import saltant
        >>> client = saltant.Client(
        ...     base_api_url='https://shahlabjobs.ca/api/',
        ...     auth_token='p0gch4mp101fy451do9uod1s1x9i4a')

    Attributes:
        base_api_url (str): The URL of the saltant API.
    """
    def __init__(
            self,
            base_api_url,
            auth_token,
            default_timeout=DEFAULT_TIMEOUT_SECONDS):
        """Initialize the saltant API client.

        Args:
            base_api_url (str): The URL of the saltant API.
            auth_token (str): The registered user's authentication token.
            default_timeout (int, optional): The maximum number
                of seconds to wait for a request to complete. Defaults
                to 90 seconds.
        """
        # TODO(mwiens91): use the timeout
        # The base URL of the saltant API
        self.base_api_url = base_api_url

        # Start a requests session
        self.session = requests.Session()
        self.session.headers.update(
            {'Authorization': 'Token ' + auth_token})

        # Test that we're authorized
        self.test_authentication()

    @classmethod
    def from_env(cls, default_timeout=DEFAULT_TIMEOUT_SECONDS):
        """Return a client configured from environment variables.

        Essentially copying this:
        https://github.com/docker/docker-py/blob/master/docker/client.py#L43.

        The environment variables looked for are the following:

        .. envvar:: SALTANT_API_URL

            The URL of the saltant API. For example,
            https://shahlabjobs.ca/api/

        .. envvar:: SALTANT_AUTH_TOKEN

            The registered saltant user's authentication token.

        Example:

            >>> import saltant
            >>> client = saltant.from_env()

        Args:
            default_timeout (int, optional): The maximum number of
                seconds to wait for a request to complete. Defaults to
                90 seconds.

        Returns:
            :class:`Client`: A saltant API client object.

        Raises:
            :py:class:`saltant.exceptions.BadEnvironmentError`: The user
                has an incorrectly configured environment.
        """
        # Get variables from environment
        try:
            base_api_url = os.environ['SALTANT_API_URL']
        except KeyError:
            raise BadEnvironmentError("SALTANT_API_URL not defined!")

        try:
            # Try to get an auth token
            auth_token = os.environ['SALTANT_AUTH_TOKEN']
        except KeyError:
            raise BadEnvironmentError("SALTANT_AUTH_TOKEN not defined!")

        # Return the configured client
        return cls(
            base_api_url=base_api_url,
            auth_token=auth_token,
            default_timeout=default_timeout,)

    def test_authentication(self):
        """Test that the client is authorized.

        This currently assumes that read-only operations require
        authentication, which is the intended authentication protocol
        for saltant servers.

        Raises:
            :py:class:`saltant.exceptions.AuthenticationError`: The
                authentication provided was invalid.
        """
        response = self.session.get(self.base_api_url + 'users/')

        try:
            assert response.status_code == HTTP_200_OK
        except AssertionError:
            raise AuthenticationError('Authentication invalid!')


# Allow convenient import access to environment-configured client
from_env = Client.from_env
