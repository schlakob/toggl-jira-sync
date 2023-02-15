# Install dependencies
# python3 -m pip install -r requirements

from requests.auth import HTTPBasicAuth
from datetime import date, timedelta, datetime
from dateutil.parser import parse
import requests, json, sys, math, os

#
# Enter your variables here
jira_access_token = ""
toggle_api_key = ""
jira_project_slug = ""
jira_endpoint = ""



jira_headers = {
  "Authorization": f"Bearer {jira_access_token}",
  "Accept": "application/json",
  "Content-Type": "application/json"
}

# only for todays entrys
from_date = date.today()
to_date = date.today() + timedelta(days=1)

response = requests.get(f'https://api.track.toggl.com/api/v9/me/time_entries?start_date={from_date}&end_date={to_date}', auth=(toggle_api_key, "api_token"))

for entry in response.json():
    if jira_project_slug in entry['description']:
        if math.floor(entry['duration'] / 60) > 0:
            issue = entry['description'].split('/')[0]
            start = entry['start'].split("+")[0] + ".000+0000"
            print(f"Add worklog for: {issue} started at: {start} with duration: {entry['duration']}")
            jira_url = f"{jira_endpoint}/rest/api/2/issue/{issue}/worklog"
            jira_response = requests.request(
                "GET",
                jira_url,
                headers=jira_headers
            )
            exists_already = bool(False)
            for worklog in jira_response.json()['worklogs']:
              if parse(worklog['started']) == parse(start) and math.floor(worklog['timeSpentSeconds'] / 60) == math.floor(entry['duration'] / 60):
                exists_already = bool(True)

            if exists_already:
              print(f" - SKIPPED: Worklog for start: {start} and duration: {entry['duration']} already exists!") 
            else:
              jira_url = f"{jira_endpoint}/rest/api/2/issue/{issue}/worklog"
              jira_payload = json.dumps( {
                  "comment": f"Working on issue {issue} (logged automatic)",
                  "timeSpentSeconds": entry['duration'],
                  "started": start
              } ) 
              jira_response = requests.request(
                  "POST",
                  jira_url,
                  data=jira_payload,
                  headers=jira_headers
              )
              print(f" - Worklog created with JIRA response: {jira_response}")

