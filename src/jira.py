import requests
import re
from datetime import date, datetime
from dateutil import parser
import json

class JiraApi:
    def __init__(self, base_url: str, access_token: str) -> None:
        self.base_url = f"{base_url}/rest/api/2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_myself(self) -> dict:
        return requests.get(f'{self.base_url}/myself', headers=self.headers).json()

    def get_search(self, jql: str) -> dict:
        return requests.get(f'{self.base_url}/search', headers=self.headers, params={
            "jql": jql,
        }).json()

    def get_issue_worklogs(self, issue_key: str) -> dict:
        return requests.get(f'{self.base_url}/issue/{issue_key}/worklog', headers=self.headers).json()

    def create_issue_worklog(self, issue_key: str, started: str, time_spent: int, comment: str) -> requests.Response:
        return requests.post(
            url=f'{self.base_url}/issue/{issue_key}/worklog',
            data=json.dumps({
                "comment": comment,
                "timeSpentSeconds": time_spent,
                "started": started
            }),
            headers=self.headers
        )

    def delete_issue_worklog(self, issue_key: str, worklog_id: int) -> requests.Response:
        return requests.delete(
            url=f'{self.base_url}/issue/{issue_key}/worklog/{worklog_id}',
            headers=self.headers
        )

class Jira:
    def __init__(self, jira_api: JiraApi, project_slug: str) -> None:
        self.jira_api = jira_api
        self.project_slug = project_slug
        self.worklog_comment_pattern = re.compile(r"^.*\[toggl-track-sync\]([a-z0-9=-]+)\[\/toggl-track-sync\].*$", flags=re.DOTALL)

    def get_user(self) -> dict:
        return self.jira_api.get_myself()

    def get_issues_by_worklogs(self, author: dict, from_date: date, to_date: date) -> list:
        jql = f'project = {self.project_slug} AND worklogDate >= "{from_date}" AND worklogDate < "{to_date}" AND worklogAuthor = "{author["name"]}"'
        return self.jira_api.get_search(jql)['issues']

    def get_worklogs_from_issue(self, issue: dict, author: dict, from_date: date, to_date: date) -> list:
        worklogs = self.jira_api.get_issue_worklogs(issue['key'])['worklogs']
        # filter all worklogs by sync window and author
        worklogs = list(filter(lambda wl: (
            wl['author']['name'] == author['name']
            and parser.isoparse(wl['started']).timestamp() >= datetime.combine(from_date, datetime.min.time()).timestamp()
            and parser.isoparse(wl['started']).timestamp() < datetime.combine(to_date, datetime.min.time()).timestamp()
        ), worklogs))
        # add issue key to all worklogs to make sync possible
        return list(map(lambda w: dict(w, **{'issueKey': issue['key']}), worklogs))

    def worklog_filter(self, worklog: dict) -> bool:
        return (
            self.worklog_comment_pattern.match(worklog['comment'])
        )

    def create_worklog(self, worklog: dict) -> None:
        response = self.jira_api.create_issue_worklog(worklog['issueKey'], worklog['started'], worklog['timeSpentSeconds'], worklog['comment'])
        if response.status_code != 201:
            raise Exception(f"{response.status_code} {response.content.decode('utf-8')}")

    def delete_worklog(self, worklog: dict) -> None:
        response = self.jira_api.delete_issue_worklog(worklog['issueKey'], worklog['id'])
        if response.status_code != 204:
            raise Exception(f"{response.status_code} {response.content.decode('utf-8')}")
