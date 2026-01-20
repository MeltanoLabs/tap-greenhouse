"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.testing import get_tap_test_class

from tap_greenhouse.tap import TapGreenhouse

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "api_key": os.environ.get("TAP_GREENHOUSE_API_KEY", "test-api-key"),
}


# Run standard built-in tap tests from the SDK:
TestTapGreenhouse = get_tap_test_class(
    tap_class=TapGreenhouse,
    config=SAMPLE_CONFIG,
)
