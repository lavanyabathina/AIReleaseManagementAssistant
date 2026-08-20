import os
import requests
from typing import Optional
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain_core.tools import tool

load_dotenv()

JIRA_API_BASE_URL= os.getenv("JIRA_API_BASE_URL")
JIRA_EMAIL= os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN= os.getenv("JIRA_API_TOKEN")


@tool
def get_jira_fields() -> dict :
    """
    Retrieve all Jira system and custom fields.

    Returns:
        A list of Jira fields containing field ID, name, and schema information.
    """

    url = f"{JIRA_API_BASE_URL}/rest/api/3/field"

    try:
        response = requests.get(
            url,
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={
                "Accept": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        fields = []

        for field in data:
            fields.append({
                "id": field.get("id"),
                "name": field.get("name"),
                "custom": field.get("custom"),
                "schema": field.get("schema")
            })

        return {
            "count": len(fields),
            "fields": fields
        }

    except requests.exceptions.RequestException as e:
        return {
            "error": f"Jira API request failed: {str(e)}"
        }



    
@tool
def get_jira_issue(issue_id_or_key : str) -> dict :
    """
    Retrieve all Jira system and custom fields.

    Returns:
        A list of Jira fields containing field ID, name, and schema information.
    """

    url = f"{JIRA_API_BASE_URL}/rest/api/3/issue/{issue_id_or_key}"
    try:
        response = requests.get(
            url,
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={
                "Accept": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()
        #return data
        fields = data.get("fields", {})
        linked_issues = []

        for link in fields.get("issuelinks", []):

            if "outwardIssue" in link:
                issue = link["outwardIssue"]
            elif "inwardIssue" in link:
                issue = link["inwardIssue"]
            else:
                continue

            linked_issues.append({
                "key": issue.get("key"),
                "summary": issue.get("fields", {}).get("summary"),
                "issue_type": issue.get("fields", {})
                            .get("issuetype", {})
                            .get("name"),
                "status": issue.get("fields", {})
                        .get("status", {})
                        .get("name")
            })

    
        result = {
            "issue_id": data.get("id"),
            "issue_key": data.get("key"),
            "summary": fields.get("summary"),
            "issue_type": fields.get("issuetype", {}).get("name"),
            "project": {
                "key": fields.get("project", {}).get("key"),
                "name": fields.get("project", {}).get("name")
            },
            "status": fields.get("status", {}).get("name"),
            "assignee": {
                "display_name": fields.get("assignee", {}).get("displayName"),
                "email": fields.get("assignee", {}).get("emailAddress"),
                "account_id": fields.get("assignee", {}).get("accountId")
            },
            "start_date": fields.get("customfield_10015"),
            "due_date": fields.get("duedate"),
            "description": fields.get("description"),
            "linked_issues": linked_issues
        }
        return result
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Jira API request failed: {str(e)}"
        }

@tool
def get_jira_user(email: str) -> dict:
    """
    Find a Jira user using their email address.

    Args:
        email: Email address of the Jira user.

    Returns:
        Jira user details including account ID and display name.
    """

    url = f"{JIRA_API_BASE_URL}/rest/api/3/user/search"

    params = {
        "query": email
    }

    try:
        response = requests.get(
            url,
            params=params,
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={
                "Accept": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            return {
                "success": False,
                "error": f"No Jira user found for email: {email}"
            }
        user = data[0]

        result = {
        "account_id": user.get("accountId"),
        "display_name": user.get("displayName"),
        "email": user.get("emailAddress"),
        "active": user.get("active")
        }       

        return result
   

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Jira API request failed: {str(e)}"
        }


@tool
def create_jira_issue(
    project_key: str,
    issue_type: str,
    summary: str,
    description: str,
    start_date: str,
    end_date: str,
    assignee_account_id: Optional[str] = None
) -> dict:
    """
    Create a Jira Story or Task.

    Args:
        project_key: Jira project key, for example REL.
        issue_type: Jira issue type, either Story or Task.
        summary: Summary of the Jira issue.
        description: Description of the Jira issue.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        assignee_account_id: Atlassian account ID of the assignee.
    """

    if issue_type not in ["Story", "Task"]:
        return {
            "error": "issue_type must be either 'Story' or 'Task'."
        }

    url = f"{JIRA_API_BASE_URL}/rest/api/3/issue"

    fields = {
        "project": {
            "key": project_key
        },
        "issuetype": {
            "name": issue_type
        },
        "summary": summary,
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": description
                        }
                    ]
                }
            ]
        },
        "customfield_10015": start_date,
        "duedate": end_date
    }

    if assignee_account_id:
        fields["assignee"] = {
            "accountId": assignee_account_id
        }

    payload = {
        "fields": fields
    }

    try:

        response = requests.post(
            url,
            json=payload,
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()
        result = {
            "issue_id": data.get("id"),
            "issue_key": data.get("key"),
            "issue_url": f"{JIRA_API_BASE_URL}/browse/{data.get('key')}"
        }
        return result

    except requests.exceptions.RequestException as e:

        return {
            "error": f"Jira API request failed: {str(e)}"
        }


@tool
def link_jira_issue(
    inward_issue_key: str,
    outward_issue_key: str,
    link_type: str = "Relates"
) -> dict:
    """
    Link two Jira issues.

    Args:
        inward_issue_key: Jira issue key, for example REL-12.
        outward_issue_key: Jira issue key, for example REL-13.
        link_type: Jira link type, for example Relates, Blocks, Cloners.

    Returns:
        Details of the created Jira issue link.
    """

    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        return {
            "error": "Jira credentials are not configured."
        }

    url = f"{JIRA_API_BASE_URL}/rest/api/3/issueLink"

    payload = {
        "type": {
            "name": link_type
        },
        "inwardIssue": {
            "key": inward_issue_key
        },
        "outwardIssue": {
            "key": outward_issue_key
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()

        result = {
            "inward_issue": inward_issue_key,
            "outward_issue": outward_issue_key,
            "link_type": link_type,
            "message": (
                f"{inward_issue_key} linked to "
                f"{outward_issue_key} using '{link_type}'"
            )
        }
        return result

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Jira API request failed: {str(e)}"
        }

@tool
def update_jira_issue(
    issue_key: str,
    summary: str = None,
    description: str = None,
    assignee_account_id: str = None,
    start_date: str = None,
    due_date: str = None,
    priority_id: str = None
) -> dict:
    """
    Update an existing Jira issue.

    Args:
        issue_key: Jira issue key, for example REL-28.
        summary: New issue summary.
        description: New issue description.
        assignee_account_id: Atlassian account ID of the assignee.
        start_date: New start date in YYYY-MM-DD format.
        due_date: New due date in YYYY-MM-DD format.
        priority_id: Jira priority ID.

    Returns:
        Updated Jira issue information.
    """

    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        return {
            "error": "Jira credentials are not configured."
        }

    url = f"{JIRA_API_BASE_URL}/rest/api/3/issue/{issue_key}"

    fields = {}

    if summary:
        fields["summary"] = summary

    if description:
        fields["description"] = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": description
                        }
                    ]
                }
            ]
        }

    if assignee_account_id:
        fields["assignee"] = {
            "accountId": assignee_account_id
        }

    if start_date:
        fields["customfield_10015"] = start_date

    if due_date:
        fields["duedate"] = due_date

    if priority_id:
        fields["priority"] = {
            "id": priority_id
        }

    if not fields:
        return {
            "error": "No fields provided for update."
        }

    payload = {
        "fields": fields
    }

    try:
        response = requests.put(
            url,
            json=payload,
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()

        result = {
            "issue_key": issue_key,
            "message": "Jira issue updated successfully",
            "updated_fields": list(fields.keys()),
            "issue_url": f"{JIRA_BASE_URL}/browse/{issue_key}"
        }
        return result

    except requests.exceptions.RequestException as e:
        return {
            "error": f"Jira API request failed: {str(e)}"
        }

@tool
def add_jira_comment(
    issue_key: str,
    comment: str
) -> dict:
    """
    Add a comment to a Jira issue.

    Args:
        issue_key: Jira issue key, for example REL-28.
        comment: Comment text to add to the issue.

    Returns:
        Jira comment information.
    """

    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        return {
            "error": "Jira credentials are not configured."
        }

    url = f"{JIRA_API_BASE_URL}/rest/api/3/issue/{issue_key}/comment"

    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": comment
                        }
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        result = {
            "issue_key": issue_key,
            "comment_id": data.get("id"),
            "message": "Comment added successfully"
        }
        return result

    except requests.exceptions.RequestException as e:
        return {
            "error": f"Jira API request failed: {str(e)}"
        }