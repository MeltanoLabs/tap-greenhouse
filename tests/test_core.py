"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_greenhouse.tap import TapGreenhouse

SAMPLE_CONFIG = {
    "start_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
}


# Run standard built-in tap tests from the SDK:
TestTapGreenhouse = get_tap_test_class(
    tap_class=TapGreenhouse,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(ignore_no_records=True),
)
