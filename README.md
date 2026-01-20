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

Enable the following scopes in Greenhouse Dev Center based on which streams you need. Scopes follow the format `harvest:{resource}:list`.

## Available Streams

This tap supports 63 streams from the Greenhouse Harvest API V3:

| Stream | Replication Key | Description |
|--------|-----------------|-------------|
| `application_stages` | `updated_at` | Application stage history |
| `applications` | `last_activity_at` | Job applications |
| `applied_candidate_tags` | `updated_at` | Tags applied to candidates |
| `approval_flows` | `updated_at` | Approval workflows |
| `approver_groups` | `updated_at` | Groups of approvers |
| `approvers` | `updated_at` | Individual approvers |
| `attachments` | `updated_at` | Candidate attachments |
| `candidate_attribute_types` | `updated_at` | Candidate attribute type definitions |
| `candidate_educations` | `updated_at` | Candidate education records |
| `candidate_employments` | `updated_at` | Candidate employment history |
| `candidate_tags` | `updated_at` | Available candidate tags |
| `candidates` | `last_activity_at` | Candidate profiles |
| `close_reasons` | `updated_at` | Job close reasons |
| `custom_field_departments` | `updated_at` | Custom field department assignments |
| `custom_field_offices` | `updated_at` | Custom field office assignments |
| `custom_fields` | `updated_at` | Custom field definitions |
| `default_interviewers` | `updated_at` | Default interviewers for job stages |
| `demographic_answer_options` | None | Demographic question answer options |
| `demographic_answers` | `updated_at` | Candidate demographic answers |
| `demographic_question_sets` | `updated_at` | Demographic question sets |
| `demographic_questions` | None | Demographic questions |
| `departments` | `updated_at` | Company departments |
| `eeoc` | `updated_at` | EEOC data for applications |
| `focus_candidate_attributes` | `updated_at` | Focus attributes for candidates |
| `future_job_permissions` | `updated_at` | Future job permission settings |
| `interview_kits` | `updated_at` | Interview kit content |
| `interviewer_tags` | `updated_at` | Tags for interviewers |
| `interviewers` | `updated_at` | Interview participants |
| `interviews` | `updated_at` | Scheduled interviews |
| `job_board_custom_locations` | `updated_at` | Custom job board locations |
| `job_candidate_attributes` | `updated_at` | Job-specific candidate attributes |
| `job_hiring_managers` | `updated_at` | Hiring managers for jobs |
| `job_interview_stages` | `updated_at` | Interview stages for jobs |
| `job_interviews` | `updated_at` | Interview definitions for job stages |
| `job_notes` | `updated_at` | Notes on jobs |
| `job_owners` | `updated_at` | Job owners and coordinators |
| `job_post_locations` | `updated_at` | Locations for job posts |
| `job_posts` | `updated_at` | Job postings |
| `jobs` | `updated_at` | Job requisitions |
| `notes` | `updated_at` | Candidate notes |
| `offers` | `updated_at` | Job offers |
| `offices` | `updated_at` | Company offices |
| `openings` | `updated_at` | Job openings |
| `pay_input_ranges` | `updated_at` | Pay ranges for jobs |
| `prospect_details` | `updated_at` | Prospect pool details |
| `prospect_pool_stages` | `updated_at` | Stages within prospect pools |
| `prospect_pools` | `updated_at` | Prospect pools |
| `referrers` | `updated_at` | Referral sources |
| `rejection_details` | `updated_at` | Application rejection details |
| `rejection_reasons` | `updated_at` | Available rejection reasons |
| `scorecard_candidate_attributes` | `updated_at` | Candidate attributes on scorecards |
| `scorecard_question_answer_options` | `updated_at` | Answer options for scorecard questions |
| `scorecard_question_answers` | `updated_at` | Answers to scorecard questions |
| `scorecard_question_candidate_attributes` | `updated_at` | Candidate attributes linked to questions |
| `scorecard_question_options` | `updated_at` | Options for scorecard questions |
| `scorecard_questions` | `updated_at` | Scorecard questions |
| `scorecards` | `updated_at` | Interview scorecards |
| `sources` | `updated_at` | Candidate sources |
| `tracking_links` | `updated_at` | Job tracking links |
| `user_emails` | `updated_at` | User email addresses |
| `user_job_permissions` | `updated_at` | User permissions on jobs |
| `user_roles` | `updated_at` | User role definitions |
| `users` | `updated_at` | Greenhouse users |

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
