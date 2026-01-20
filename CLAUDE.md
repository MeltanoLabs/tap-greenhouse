# CLAUDE.md - AI Agent Development Guide for tap-greenhouse

This document provides guidance for AI coding agents and developers working on this Singer tap.

## Project Overview

- **Project Type**: Singer Tap
- **Source**: Greenhouse Harvest API V3
- **Stream Type**: REST
- **Authentication**: OAuth2 (client credentials)
- **Framework**: Meltano Singer SDK

## Architecture

This tap follows the Singer specification and uses the Meltano Singer SDK to extract data from Greenhouse.

### Key Components

1. **Tap Class** (`tap_greenhouse/tap.py`): Main entry point, defines configuration schema
2. **Client** (`tap_greenhouse/client.py`): API client, authentication, and `GreenhouseStream` base class
3. **Stream Definitions** (`tap_greenhouse/streams.toml`): TOML file defining stream names, paths, and replication keys
4. **Schemas** (`tap_greenhouse/schemas/*.json`): JSON Schema files for each stream

### Project Structure

```
tap-greenhouse/
├── tap_greenhouse/
│   ├── __init__.py
│   ├── tap.py              # Main tap class with config schema
│   ├── client.py           # GreenhouseStream base class and OAuth authenticator
│   ├── streams.toml        # Stream definitions (name, path, replication_key)
│   └── schemas/            # Auto-generated JSON Schema files for each stream
│       ├── __init__.py
│       ├── applications.json
│       ├── candidates.json
│       └── ... (63 schema files)
├── scripts/
│   └── update_catalog.py   # Script to regenerate schemas from API docs
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── meltano.yml             # Meltano configuration
├── pyproject.toml          # Dependencies and metadata
└── README.md               # User documentation
```

## Development Guidelines for AI Agents

### Understanding Singer Concepts

Before making changes, ensure you understand these Singer concepts:

- **Streams**: Individual data endpoints (e.g., users, candidates, applications)
- **State**: Tracks incremental sync progress using bookmarks
- **Catalog**: Metadata about available streams and their schemas
- **Records**: Individual data items emitted by the tap
- **Schemas**: JSON Schema definitions for stream data

### Common Tasks

#### Adding a New Stream

1. Add stream definition to `tap_greenhouse/streams.toml`:
   ```toml
   [[streams]]
   name = "my_new_stream"
   path = "/v3/my_resource"
   replication_key = "updated_at"  # or "" for no replication key
   ```

2. Run the schema update script to auto-generate the JSON schema:
   ```bash
   uv run scripts/update_catalog.py
   ```

3. If the schema needs fixes (API docs don't match actual responses), add preprocessing logic to `scripts/update_catalog.py` in `_preprocess_schema()`.

4. Run tests to verify: `uv run pytest`

#### Updating Schemas

Schemas are auto-generated from the Greenhouse API documentation. **Do not edit JSON schema files directly.** Instead:

1. Run the schema update script:
   ```bash
   uv run scripts/update_catalog.py
   ```

2. If a schema needs special handling (e.g., API docs don't match reality), add preprocessing logic to `scripts/update_catalog.py` in the `_preprocess_schema()` function.

The script:
- Fetches the OpenAPI spec from Greenhouse's API documentation
- Generates JSON schema files for each stream defined in `streams.toml`
- Applies stream-specific fixes via `_preprocess_schema()` for known API inconsistencies

#### Authentication

This tap uses the Greenhouse Harvest API V3 with OAuth2 client credentials authentication.

**Configuration:**
- Client credentials stored in `client_id` and `client_secret` config properties (both required)
- Implements OAuth2 client credentials flow via `GreenhouseOAuthAuthenticator` class
- Token endpoint: `https://auth.greenhouse.io/token`
- Requires scopes to be configured in Greenhouse Dev Center

**Required Scopes:**
Each stream requires a corresponding scope in the format `harvest:{resource}:list`. For example:
- `harvest:candidates:list` for the candidates stream
- `harvest:applications:list` for the applications stream

#### Handling Pagination

This tap uses the SDK's `HeaderLinkPaginator` which parses RFC 5988 Link headers from responses. No custom pagination logic is needed.

#### State and Incremental Sync

- Set `replication_key` in `streams.toml` to enable incremental sync (e.g., `"updated_at"`)
- Set `replication_key = ""` for full-table replication (no incremental sync)
- State is automatically managed by the SDK
- The tap passes replication key as a query parameter: `?updated_at=gte|{timestamp}`

### Testing

Run tests to verify your changes:

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_core.py -k test_name

# Run tap manually
LOGLEVEL=warning uv run tap-greenhouse --config ENV > singer.jsonl
```

### Configuration

Configuration properties are defined in `tap_greenhouse/tap.py`:

```python
config_jsonschema = th.PropertiesList(
    th.Property("client_id", th.StringType, required=True, secret=True),
    th.Property("client_secret", th.StringType, required=True, secret=True),
    th.Property("start_date", th.DateTimeType),
).to_dict()
```

### streams.toml Format

The `streams.toml` file defines all streams:

```toml
[defaults]
primary_keys = ["id"]           # Default primary key for all streams
replication_key = "updated_at"  # Default replication key

[[streams]]
name = "applications"
path = "/v3/applications"
replication_key = "last_activity_at"  # Override default

[[streams]]
name = "demographic_questions"
path = "/v3/demographic_questions"
replication_key = ""  # No replication key (full table sync)
```

### Keeping meltano.yml and Tap Settings in Sync

When this tap is used with Meltano, the settings defined in `meltano.yml` must stay in sync with the `config_jsonschema` in the tap class.

**Setting kind mappings:**

| Python Type | Meltano Kind |
|-------------|--------------|
| `StringType` | `string` |
| `IntegerType` | `integer` |
| `BooleanType` | `boolean` |
| `NumberType` | `number` |
| `DateTimeType` | `date_iso8601` |
| `ArrayType` | `array` |
| `ObjectType` | `object` |

Any properties with `secret=True` should be marked with `sensitive: true` in `meltano.yml`.

### Common Pitfalls

1. **Schema Mismatches**: If you see warnings like "Properties X were present in stream but not found in catalog schema", run `uv run scripts/update_catalog.py` to regenerate schemas. If the issue persists, add a fix to `_preprocess_schema()` in the script.
2. **Missing Replication Key**: If a stream doesn't have `updated_at` in the API response, set `replication_key = ""` in streams.toml
3. **Rate Limiting**: The SDK handles retries automatically
4. **Timezone Handling**: Use UTC, the API returns ISO 8601 datetime strings
5. **Don't Edit Schemas Directly**: Always use `scripts/update_catalog.py` to update schemas

### SDK Resources

- [Singer SDK Documentation](https://sdk.meltano.com)
- [Singer Spec](https://hub.meltano.com/singer/spec)
- [SDK Reference](https://sdk.meltano.com/en/latest/reference.html)
- [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html)

### Best Practices

1. **Logging**: Use `self.logger` for structured logging
2. **Validation**: Validate API responses before emitting records
3. **Documentation**: Update README with new streams and config options
4. **Type Hints**: Add type hints to improve code clarity
5. **Testing**: Write tests for new streams and edge cases
6. **Error Messages**: Provide clear, actionable error messages

## Additional Resources

- Project README: See `README.md` for setup and usage
- Singer SDK: https://sdk.meltano.com
- Meltano: https://meltano.com
- Singer Specification: https://hub.meltano.com/singer/spec
- Greenhouse Harvest API V3: https://developers.greenhouse.io/harvest.html

## Making Changes

When implementing changes:

1. Understand the existing code structure
2. Follow Singer and SDK patterns
3. Test thoroughly with real API credentials
4. Update documentation and docstrings
5. Ensure backward compatibility when possible
6. Run linting and type checking: `uv run ruff check`

## Questions?

If you're uncertain about an implementation:

- Check SDK documentation for similar examples
- Review other Singer taps for patterns
- Test incrementally with small changes
- Validate against the Singer specification
