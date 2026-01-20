"""REST client handling, including GreenhouseStream base class."""

from __future__ import annotations

import decimal
import sys
from typing import TYPE_CHECKING, Any, ClassVar
from urllib.parse import parse_qs, urlparse

from requests.auth import HTTPBasicAuth
from singer_sdk.authenticators import OAuthAuthenticator
from singer_sdk.pagination import BaseAPIPaginator
from singer_sdk.streams import RESTStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Iterable

    import requests
    from singer_sdk.helpers.types import Context


class GreenhouseLinkHeaderPaginator(BaseAPIPaginator[str | None]):
    """Paginator for Greenhouse API using Link headers (RFC 5988)."""

    def __init__(self) -> None:
        """Initialize the paginator."""
        super().__init__(start_value=None)

    @override
    def get_next(self, response: requests.Response) -> str | None:
        """Get the next page URL from Link header.

        Args:
            response: The HTTP response object.

        Returns:
            The next page URL or None if no more pages.
        """
        link_header = response.headers.get("Link", "")
        if not link_header:
            return None

        for link in link_header.split(","):
            parts = link.strip().split(";")
            if len(parts) < 2:
                continue

            url_part = parts[0].strip()
            rel_part = parts[1].strip()

            if 'rel="next"' in rel_part or "rel='next'" in rel_part:
                return url_part.strip("<>")

        return None


class GreenhouseBasicAuthenticator(HTTPBasicAuth):
    """Basic Auth authenticator for Greenhouse Harvest API V1."""

    def __init__(self, api_key: str) -> None:
        """Initialize with API key as username, blank password.

        Args:
            api_key: The Greenhouse API key.
        """
        super().__init__(username=api_key, password="")


class GreenhouseOAuthAuthenticator(OAuthAuthenticator):
    """OAuth2 authenticator for Greenhouse Harvest API V3."""

    @property
    @override
    def oauth_request_body(self) -> dict:
        """Build the OAuth request body.

        Returns:
            The request body for token exchange.
        """
        return {
            "grant_type": "client_credentials",
        }

    @property
    @override
    def client_id(self) -> str:
        """Return the client ID.

        Returns:
            The client ID.
        """
        return self.config["client_key"]

    @property
    @override
    def client_secret(self) -> str:
        """Return the client secret.

        Returns:
            The client secret.
        """
        return self.config["client_secret"]


class GreenhouseStream(RESTStream):
    """Greenhouse stream class."""

    records_jsonpath = "$[*]"
    _authenticator: GreenhouseBasicAuthenticator | GreenhouseOAuthAuthenticator | None = None

    # Subclasses can set this to filter by updated_at
    replication_key: ClassVar[str | None] = None

    @property
    @override
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings.

        Returns:
            The base URL for API requests.
        """
        return self.config.get("api_url", "https://harvest.greenhouse.io/v1")

    @property
    @override
    def authenticator(self) -> GreenhouseBasicAuthenticator | GreenhouseOAuthAuthenticator:
        """Return an authenticator object based on config.

        Uses Basic Auth if api_key is provided, otherwise OAuth2.

        Returns:
            An authenticator instance.
        """
        if self._authenticator is None:
            if self.config.get("api_key"):
                self._authenticator = GreenhouseBasicAuthenticator(
                    api_key=self.config["api_key"],
                )
            else:
                self._authenticator = GreenhouseOAuthAuthenticator(
                    stream=self,
                    auth_endpoint="https://auth.greenhouse.io/token",
                    oauth_scopes="",
                )
        return self._authenticator

    @property
    @override
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {
            "Accept": "application/json",
        }

    @override
    def get_new_paginator(self) -> GreenhouseLinkHeaderPaginator:
        """Create a new pagination helper instance.

        Returns:
            A pagination helper instance.
        """
        return GreenhouseLinkHeaderPaginator()

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page URL (contains params).

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict[str, Any] = {
            "per_page": 500,
        }

        if next_page_token:
            parsed = urlparse(next_page_token)
            query_params = parse_qs(parsed.query)
            for key, value in query_params.items():
                params[key] = value[0] if len(value) == 1 else value

        return params

    @override
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        data = response.json(parse_float=decimal.Decimal)
        if isinstance(data, list):
            yield from data
        elif isinstance(data, dict):
            yield data
