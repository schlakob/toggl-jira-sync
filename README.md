# Toggl Track Jira Sync

## Install

1. Clone this repository
2. Install python requirements `python3 -m pip install -r requirements.txt`
3. Configure application (see below)

## Usage

Start each Toggl entry with a Jira issue reference followed by a slash to enable worklog sync for this time entry.

Example:

`MYPROJECT-1337/This text will also be synced to Jira`

Just run the sync script to sync all time entries within the configured sync window. This action is idempotent and can be executed multiple times without problems.

## Configuration

Configure by setting environment variables or creatng a `.env` file in the script directory. See `.env.example` for a template.

| Config              | Default                         | Description                                                                                                                           |
| ------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `JIRA_URL`          | **required**                    | Base URL to your Jira Server Instance (e.g. `https://jira.example`)                                                                   |
| `JIRA_ACCESS_TOKEN` | **required**                    | Jira personal access token. See [Jira Docs](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html) |
| `JIRA_PROJECT_SLUG` | **required**                    | Jira project slug that is considered for sync                                                                                         |
| `TOGGL_URL`         | `"https://api.track.toggl.com"` | Toggl API base URL                                                                                                                    |
| `TOGGL_API_KEY`     | **required**                    | Toggl API key. See [Toggl Docs](https://support.toggl.com/en/articles/3116844-where-is-my-api-key-located)                            |
| `SYNC_WINDOW_SIZE`  | `1`                             | Amount of days, the sync will look in the past                                                                                        |
