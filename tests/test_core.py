"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_greenhouse.tap import TapGreenhouse

SAMPLE_CONFIG = {
    "start_date": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
}


# Run standard built-in tap tests from the SDK:
TestTapGreenhouse = get_tap_test_class(
    tap_class=TapGreenhouse,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        ignore_no_records_for_streams=[
            "candidate_tags",
            "close_reasons",
            "custom_field_departments",
            "custom_field_offices",
            "default_interviewers",
            "demographic_answers",
            "demographic_question_sets",
            "departments",
            "focus_candidate_attributes",
            "interviewer_tags",
            "job_notes",
            "offices",
            "rejection_reasons",
            "scorecard_question_answer_options",
            "scorecard_question_candidate_attributes",
            "scorecard_question_options",
            "sources",
        ],
    ),
)
