"""Greenhouse tap class."""

from __future__ import annotations

import sys

from singer_sdk import Tap
from singer_sdk import typing as th

from tap_greenhouse import streams

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class TapGreenhouse(Tap):
    """Singer tap for Greenhouse Harvest API."""

    name = "tap-greenhouse"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            secret=True,
            title="API Key",
            description="Harvest API key for Basic Auth (V1). Use this OR client_key/client_secret.",
        ),
        th.Property(
            "client_key",
            th.StringType,
            secret=True,
            title="Client Key",
            description="OAuth2 client key for Greenhouse Harvest API (V3)",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            secret=True,
            title="Client Secret",
            description="OAuth2 client secret for Greenhouse Harvest API (V3)",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "api_url",
            th.StringType,
            title="API URL",
            default="https://harvest.greenhouse.io/v1",
            description="The base URL for the Greenhouse Harvest API",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[streams.GreenhouseStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.CandidatesStream(self),
            streams.ApplicationsStream(self),
            streams.JobsStream(self),
            streams.UsersStream(self),
            streams.DepartmentsStream(self),
            streams.OfficesStream(self),
            streams.OffersStream(self),
            streams.ScheduledInterviewsStream(self),
            streams.JobStagesStream(self),
            streams.ScorecardsStream(self),
            streams.SourcesStream(self),
            streams.RejectionReasonsStream(self),
            streams.JobPostsStream(self),
            streams.CustomFieldsStream(self),
            streams.ActivityFeedStream(self),
        ]


if __name__ == "__main__":
    TapGreenhouse.cli()
