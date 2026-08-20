from app.models.certification_request import CertificationRequest
from pydantic import ValidationError

def get_certification_request() -> CertificationRequest:

    certification = input("Enter certification: ")
    release = input("Enter release: ")
    jira_project = input("Enter Jira project: ")
    confluence_space= input("Enter Confluence space: ")
    parent_story_assignee = input("Enter parent story assignee: ")
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")

    try:
         return CertificationRequest(
             certification=certification,
             release=release,
             jira_project=jira_project,
             confluence_space=confluence_space,
             parent_story_assignee=parent_story_assignee,
             start_date=start_date,
             end_date=end_date
    )
    except ValidationError as e:
            print("Invalid certification request:")
            print(e)
            raise