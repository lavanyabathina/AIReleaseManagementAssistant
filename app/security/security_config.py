from pathlib import Path

from app.utils.load_config import load_config

# Resolved relative to this file so the policy loads regardless of the
# working directory the app is started from.
CONFIG_FILE = (
    Path(__file__).resolve().parents[1] / "config" / "application_config.yaml"
)

security_config = load_config(CONFIG_FILE)["security"]

ALLOWED_PROJECTS = set(
    security_config["allowed_jira_projects"]
)

AUTHORIZED_ACTIONS = set(
    security_config["authorized_jira_actions"]
)

AUTHORIZED_ASSIGNEES = set(
    security_config["authorized_task_assignees"]
)

AUTHORIZED_PARENT_STORY_ASSIGNEES = set(
    security_config["authorized_parent_story_assignees"]
)

ALLOWED_CONFLUENCE_SPACES = set(
    security_config["allowed_confluence_spaces"]
)
