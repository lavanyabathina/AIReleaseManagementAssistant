from app.security.security_config import (
    ALLOWED_PROJECTS,
    AUTHORIZED_ACTIONS,
    AUTHORIZED_ASSIGNEES,
    AUTHORIZED_PARENT_STORY_ASSIGNEES
)


def authorize_jira_project(project: str):
    if project.upper() not in ALLOWED_PROJECTS:
        raise PermissionError(f"Project {project} is not authorized.")


def authorize_jira_action(project: str, action: str):
    if project not in ALLOWED_PROJECTS:
        raise PermissionError(f"Project {project} is not an authorized project")
    if action not in AUTHORIZED_ACTIONS:
        raise PermissionError(f"Action {action} is not authorized")


def authorize_jira_task_assignee(assignee: str):
    if assignee not in AUTHORIZED_ASSIGNEES:
        raise PermissionError(f"{assignee} is not an authorized task assignee")


def authorize_jira_story_assignee(assignee: str):
    if assignee not in AUTHORIZED_PARENT_STORY_ASSIGNEES:
        raise PermissionError(
            f"{assignee} is not an authorized parent story assignee"
        )
