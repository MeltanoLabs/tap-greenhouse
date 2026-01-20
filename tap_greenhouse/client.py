"""REST client handling, including GreenhouseStream base class."""

from __future__ import annotations

import importlib.resources
import sys
from base64 import b64encode
from typing import TYPE_CHECKING, Any, ClassVar
from urllib.parse import parse_qs

from singer_sdk import SchemaDirectory, StreamSchema
from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from singer_sdk.pagination import HeaderLinkPaginator
from singer_sdk.streams import RESTStream

from tap_greenhouse import schemas

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Sequence
    from urllib.parse import ParseResult

    from singer_sdk import Tap
    from singer_sdk.helpers.types import Context

SCHEMAS_DIR = SchemaDirectory(schemas)


class GreenhouseOAuthAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """OAuth2 authenticator for Greenhouse Harvest API V3."""

    @property
    @override
    def oauth_request_body(self) -> dict[str, Any]:
        """The OAuth request body."""
        return {
            "grant_type": "client_credentials",
        }


class GreenhouseStream(RESTStream):
    """Greenhouse stream class."""

    url_base: ClassVar[str] = "https://harvest.greenhouse.io"
    records_jsonpath: ClassVar[str] = "$[*]"
    schema = StreamSchema(SCHEMAS_DIR)

    @override
    def __init__(
        self,
        *args: Any,
        replication_key: str | None,
        primary_keys: Sequence[str],
        **kwargs: Any,
    ) -> None:
        """Initialize the GreenhouseStream instance.

        Args:
            args: The arguments to pass to the superclass.
            replication_key: The replication key for the stream.
            primary_keys: The primary keys for the stream.
            kwargs: The keyword arguments to pass to the superclass.
        """
        super().__init__(*args, **kwargs)
        self.replication_key = replication_key
        self.primary_keys = primary_keys

    @classmethod
    def from_streams_toml(cls, *, tap: Tap) -> list[GreenhouseStream]:
        """Create a list of GreenhouseStream instances from the streams.toml file."""
        with importlib.resources.files("tap_greenhouse").joinpath("streams.toml").open() as f_streams:
            streams: dict[str, Any] = tomllib.loads(f_streams.read())

        defaults = streams.get("defaults", {})
        return [
            cls(
                tap=tap,
                name=stream_attrs["name"],
                path=stream_attrs["path"],
                replication_key=stream_attrs.get("replication_key", defaults.get("replication_key")),
                primary_keys=stream_attrs.get("primary_keys", defaults.get("primary_keys")),
            )
            for stream_attrs in streams["streams"]
        ]

    @property
    @override
    def authenticator(self) -> GreenhouseOAuthAuthenticator:
        """Return an OAuth2 authenticator for the Greenhouse V3 API."""
        client_id = self.config["client_id"]
        client_secret = self.config["client_secret"]
        auth_header = b64encode(f"{client_id}:{client_secret}".encode()).decode()
        return GreenhouseOAuthAuthenticator(
            auth_endpoint="https://auth.greenhouse.io/token",
            oauth_headers={"Authorization": f"Basic {auth_header}"},
        )

    @override
    def get_new_paginator(self) -> HeaderLinkPaginator:
        """Create a new pagination helper instance."""
        return HeaderLinkPaginator()

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: ParseResult | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        # Cursor overrides any other query parameters
        if next_page_token:
            return parse_qs(next_page_token.query)

        params: dict[str, Any] = {"per_page": 500}
        if self.replication_key and (start_date := self.get_starting_timestamp(context)):
            params[self.replication_key] = f"gte|{start_date.isoformat()}"
        return params
