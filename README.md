# tap-greenhouse

`tap-greenhouse` is a Singer tap for Greenhouse.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

<!--

Developer TODO: Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPI repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

## Installation

Install from PyPI:

```bash
uv tool install tap-greenhouse
```

Install from GitHub:

```bash
uv tool install git+https://github.com/ORG_NAME/tap-greenhouse.git@main
```

-->

## Configuration

### Accepted Config Options

| Setting | Required | Description |
|---------|----------|-------------|
| `client_id` | Yes | OAuth2 client ID for Greenhouse Harvest API V3 |
| `client_secret` | Yes | OAuth2 client secret for Greenhouse Harvest API V3 |
| `start_date` | No | The earliest record date to sync (ISO 8601 format) |

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-greenhouse --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

```bash
export TAP_GREENHOUSE_CLIENT_ID=your-client-id
export TAP_GREENHOUSE_CLIENT_SECRET=your-client-secret
```

### Authentication

This tap uses the **Greenhouse Harvest API V3** with OAuth2 client credentials authentication.

#### Setting up OAuth2 credentials

1. Go to **Configure** → **Dev Center** → **API Credential Management** in Greenhouse
2. Create a new **API credential** with type **Harvest API - OAuth 2.0**
3. Copy the **Client Key** and **Client Secret**
4. Configure the required scopes for the streams you want to sync (see below)

#### Required Scopes

Enable the following scopes in Greenhouse Dev Center based on which streams you need:

| Stream | Required Scope |
|--------|----------------|
| applications | `harvest:applications:list` |
| candidates | `harvest:candidates:list` |
| jobs | `harvest:jobs:list` |
| users | `harvest:users:list` |
| departments | `harvest:departments:list` |
| offices | `harvest:offices:list` |
| offers | `harvest:offers:list` |
| scheduled_interviews | `harvest:scheduled_interviews:list` |
| job_stages | `harvest:job_stages:list` |
| scorecards | `harvest:scorecards:list` |
| sources | `harvest:sources:list` |
| rejection_reasons | `harvest:rejection_reasons:list` |
| job_posts | `harvest:job_posts:list` |
| custom_fields | `harvest:custom_fields:list` |
| activity_feed | `harvest:candidates:activity_feed:list` |

## Usage

You can easily run `tap-greenhouse` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-greenhouse --version
tap-greenhouse --help
tap-greenhouse --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

Prerequisites:

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

### Create and Run Tests

Create tests within the `tests` subfolder and
then run:

```bash
uv run pytest
```

You can also test the `tap-greenhouse` CLI interface directly using `uv run`:

```bash
uv run tap-greenhouse --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

<!--
Developer TODO:
Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.
-->

Use Meltano to run an EL pipeline:

```bash
# Install meltano
uv tool install meltano

# Test invocation
meltano invoke tap-greenhouse --version

# Run a test EL pipeline
meltano run tap-greenhouse target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
