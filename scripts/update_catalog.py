#!/usr/bin/env -S uv run

"""Update the catalog from the Greenhouse API documentation."""

import http
import importlib.resources
import json
import logging
import sys
from pathlib import Path

import urllib3

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

SLUG = "post_auth-token"  # Any slug endpoint seems to work
API_DOCS_URL = f"https://harvestdocs.greenhouse.io/greenhouse-harvest/api-next/v2/branches/3.0/reference/{SLUG}"
PARAMETERS = {
    "dereference": "true",
    "reduce": "false",
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def _preprocess_schema(stream_name: str, schema: dict) -> dict:  # noqa: C901, PLR0911
    """Preprocess the schema for the given stream."""
    if stream_name == "applications":
        schema["properties"]["answers"]["items"]["properties"]["answer"]["type"] = ["string", "null"]
        return schema

    if stream_name == "candidates":
        return schema["oneOf"][0]

    if stream_name == "demographic_answer_options":
        schema["properties"]["created_at"]["type"] = ["string", "null"]
        schema["properties"]["updated_at"]["type"] = ["string", "null"]
        return schema

    if stream_name == "demographic_questions":
        schema["properties"]["created_at"]["type"] = ["string", "null"]
        schema["properties"]["updated_at"]["type"] = ["string", "null"]
        return schema

    if stream_name == "eeoc":
        schema["properties"]["gender"]["type"] = ["object", "null"]
        schema["properties"]["race"]["type"] = ["object", "null"]
        schema["properties"]["veteran_status"]["type"] = ["object", "null"]
        schema["properties"]["disability_status"]["type"] = ["object", "null"]
        return schema

    if stream_name == "interviewers":
        del schema["properties"]["response_status"]["enum"]
        return schema

    if stream_name == "job_candidate_attributes":
        schema["properties"]["sort_order"]["type"] = ["integer", "null"]
        return schema

    if stream_name == "jobs":
        schema["properties"]["custom_fields"]["additionalProperties"]["additionalProperties"] = True
        return schema

    if stream_name == "notes":
        schema["properties"]["email_attachment_file_names"] = {
            "type": ["array", "null"],
            "items": {"type": ["string", "null"]},
        }
        return schema

    if stream_name == "offers":
        schema["properties"]["custom_fields"]["additionalProperties"]["additionalProperties"] = True
        return schema

    if stream_name == "scorecards":
        schema["properties"]["candidate_rating"]["type"] = ["string", "null"]
        return schema

    if stream_name == "users":
        schema["properties"]["emails"]["type"] = ["array", "null"]
        return schema

    return schema


def main() -> None:
    """Update the OpenAPI schema from the Polar API."""
    logger.info("Updating OpenAPI schema from %s", API_DOCS_URL)
    schemas_path = Path("tap_greenhouse/schemas")
    with importlib.resources.files("tap_greenhouse").joinpath("streams.toml").open() as f_paths:
        paths: dict[str, str] = tomllib.loads(f_paths.read())

    response = urllib3.request("GET", API_DOCS_URL, fields=PARAMETERS)
    if response.status != http.HTTPStatus.OK:
        logger.error("Failed to fetch OpenAPI spec: %s", response.reason)
        sys.exit(1)

    data = response.json()
    openapi = data["data"]["api"]["schema"]
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
