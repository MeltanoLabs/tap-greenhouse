#!/usr/bin/env -S uv run

"""Update the catalog from the Greenhouse API documentation."""

import http
import importlib.resources
import json
import logging
import re
import sys
from pathlib import Path

import urllib3
from toolz import assoc_in, get_in

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

# The Greenhouse API docs embed the full OpenAPI spec in the HTML of any reference page.
# The spec lives in a <script> tag as JSON, under document.api.schema.
API_DOCS_URL = "https://harvestdocs.greenhouse.io/reference/get_v3-applications"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def _make_nullable(schema: dict, path: list[str], expected_type: str) -> dict:
    """Make the given path nullable."""
    if get_in(path, schema) == expected_type:
        return assoc_in(schema, path, [expected_type, "null"])
    return schema


def _preprocess_schema(stream_name: str, schema: dict) -> dict:  # noqa: C901, PLR0911, PLR0912
    """Preprocess the schema for the given stream."""
    if stream_name == "applications":
        return _make_nullable(schema, ["properties", "answers", "items", "properties", "answer", "type"], "string")

    if stream_name == "candidates":
        return get_in(["oneOf", 0], schema)

    if stream_name == "demographic_answer_options":
        schema = _make_nullable(schema, ["properties", "created_at", "type"], "string")
        schema = _make_nullable(schema, ["properties", "updated_at", "type"], "string")
        return schema  # noqa: RET504

    if stream_name == "demographic_questions":
        schema = _make_nullable(schema, ["properties", "created_at", "type"], "string")
        schema = _make_nullable(schema, ["properties", "updated_at", "type"], "string")
        return schema  # noqa: RET504

    if stream_name == "eeoc":
        schema = _make_nullable(schema, ["properties", "gender", "type"], "object")
        schema = _make_nullable(schema, ["properties", "race", "type"], "object")
        schema = _make_nullable(schema, ["properties", "veteran_status", "type"], "object")
        schema = _make_nullable(schema, ["properties", "disability_status", "type"], "object")
        return schema  # noqa: RET504

    if stream_name == "interviewers":
        del schema["properties"]["response_status"]["enum"]
        if get_in(["properties", "response_status", "enum"], schema):
            del schema["properties"]["response_status"]["enum"]
            return schema

    if stream_name == "job_candidate_attributes":
        return _make_nullable(schema, ["properties", "sort_order", "type"], "integer")

    if stream_name == "jobs":
        path = ["properties", "custom_fields", "additionalProperties", "additionalProperties"]
        default_props = get_in(path, schema, default=False)
        if not default_props:
            schema = assoc_in(schema, path, value=True)
        return schema

    if stream_name == "notes":
        if get_in(["properties", "email_attachment_file_names", "type"], schema) == ["string", "null"]:
            schema = assoc_in(
                schema,
                ["properties", "email_attachment_file_names"],
                {
                    "type": ["array", "null"],
                    "items": {"type": ["string", "null"]},
                },
            )
        return schema

    if stream_name == "offers":
        path = ["properties", "custom_fields", "additionalProperties", "additionalProperties"]
        default_props = get_in(path, schema, default=False)
        if not default_props:
            schema = assoc_in(schema, path, value=True)
        return schema

    if stream_name == "scorecards":
        return _make_nullable(schema, ["properties", "candidate_rating", "type"], "string")

    if stream_name == "prospect_details":
        schema = _make_nullable(schema, ["properties", "department_id", "type"], "integer")
        return _make_nullable(schema, ["properties", "office_id", "type"], "integer")

    if stream_name == "users":
        return _make_nullable(schema, ["properties", "emails", "type"], "array")

    return schema


def main() -> None:
    """Update the OpenAPI schema from the Greenhouse API."""
    logger.info("Updating OpenAPI schema from %s", API_DOCS_URL)
    schemas_path = Path("tap_greenhouse/schemas")
    with importlib.resources.files("tap_greenhouse").joinpath("streams.toml").open() as f_paths:
        paths: dict[str, str] = tomllib.loads(f_paths.read())

    response = urllib3.request("GET", API_DOCS_URL)
    if response.status != http.HTTPStatus.OK:
        logger.error("Failed to fetch OpenAPI spec: %s", response.reason)
        sys.exit(1)

    html = response.data.decode("utf-8")
    scripts = re.findall(r"<script[^>]*>({.*?})</script>", html, re.DOTALL)
    data = next(
        (json.loads(s) for s in scripts if '"document"' in s and '"paths"' in s),
        None,
    )
    if data is None:
        logger.error("Could not find embedded OpenAPI spec in page HTML")
        sys.exit(1)

    openapi = data["document"]["api"]["schema"]

    stream_paths_to_names = {stream_attrs["path"]: stream_attrs["name"] for stream_attrs in paths["streams"]}

    for path, operation in openapi["paths"].items():
        if stream_name := stream_paths_to_names.get(path):
            logger.info("Updating schema for %s", stream_name)
            stream_schema = operation["get"]["responses"]["200"]["content"]["application/json"]["schema"]["items"]
            stream_schema = _preprocess_schema(stream_name, stream_schema)
            stream_schema["description"] = f"Schema for the '{stream_name}' stream, linked to the '{path}' endpoint."
            contents = json.dumps(stream_schema, indent=2) + "\n"
            with schemas_path.joinpath(f"{stream_name}.json").open("w") as f_schema:
                f_schema.write(contents)
            continue


if __name__ == "__main__":
    main()
