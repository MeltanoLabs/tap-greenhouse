"""Greenhouse tap class."""

from __future__ import annotations

import sys

from singer_sdk import Tap
from singer_sdk import typing as th

from tap_greenhouse.client import GreenhouseStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

try:
    import requests_cache

    requests_cache.install_cache()
except ImportError:
    pass


class TapGreenhouse(Tap):
    """Singer tap for Greenhouse Harvest API."""

    name = "tap-greenhouse"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            secret=True,
            title="Client ID",
            description="OAuth2 client key for Greenhouse Harvest API V3",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            secret=True,
            title="Client Secret",
            description="OAuth2 client secret for Greenhouse Harvest API V3",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[GreenhouseStream]:
        """Return a list of discovered streams."""
        return GreenhouseStream.from_streams_toml(tap=self)


if __name__ == "__main__":
    TapGreenhouse.cli()
