from app.inputs.certification_input import get_certification_request
from app.prompts.release_planning_prompt import release_planning_prompt
from app.utils.load_config import load_config
from app.llm.llm_factory import *
from dotenv import load_dotenv
from app.tools.confluence_tools import *
from app.tools.jira_tools import *
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
import sys
import os


def test_tools():
    """
    Test method to invoke individual tools and verify they work correctly.
    """
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL TOOLS")
    print("="*60 + "\n")

    # Test 1: Get Jira Issue
    print("\n[TEST 1] Get Jira Issue")
    print("-" * 60)
    get_jira_issue_response = get_jira_issue.invoke("REL-15")
    print("Get Jira issue result is:****")
    print(get_jira_issue_response)

    # Test 2: Get Jira User
    print("\n[TEST 2] Get Jira User")
    print("-" * 60)
    assignee = get_jira_user.invoke("lavanya.bathina@gmail.com")
    account_id = assignee["account_id"]
    print("Account id of lavanya.bathina@gmail.com:", account_id)

    # Test 3: Create Jira Story
    print("\n[TEST 3] Create Jira Story")
    print("-" * 60)
    create_story_issue_result = create_jira_issue.invoke({
        "project_key": "REL",
        "issue_type": "Story",
        "summary": "Oracle Linux6",
        "description": "Certification Activity for Oracle Linux6",
        "start_date": "2026-08-13",
        "end_date": "2026-09-13",
        "assignee_account_id": account_id
    })
    print("Create issue(story) result is:*****")
    print(create_story_issue_result)
    story_issue_key = create_story_issue_result.get("issue_key")

    # Test 4: Create Jira Task
    print("\n[TEST 4] Create Jira Task")
    print("-" * 60)
    create_task_issue_result = create_jira_issue.invoke({
        "project_key": "REL",
        "issue_type": "Task",
        "summary": "Certify WLS with Oracle Linux6",
        "description": "Certification Activity for WLS with Oracle Linux6",
        "start_date": "2026-08-13",
        "end_date": "2026-09-13",
        "assignee_account_id": account_id
    })
    print("Create issue(task) result is:*****")
    print(create_task_issue_result)
    task_issue_key = create_task_issue_result.get("issue_key")

    # Test 5: Link Jira Issues
    print("\n[TEST 5] Link Jira Issues")
    print("-" * 60)
    link_issues_result = link_jira_issue.invoke({
        "inward_issue_key": story_issue_key,
        "outward_issue_key": task_issue_key,
        "link_type": "Relates"
    })
    print("Link issues result:")
    print(link_issues_result)

    # Test 6: Get Confluence Space Details
    print("\n[TEST 6] Get Confluence Space Details")
    print("-" * 60)
    space_details = get_confluence_space_details.invoke("lavanya bathina")
    space_id = space_details.get("space_id")
    print("Space id is:", space_id)

    # Test 7: Create Confluence Page
    print("\n[TEST 7] Create Confluence Page")
    print("-" * 60)
    create_page_result = create_confluence_page.invoke({
        "title": "Test Certification Page3",
        "space_id": space_id,
        "content": "<p>Hello from API V2</p>"
    })
    print("Create page result:")
    print(create_page_result)

    print("\n" + "="*60)
    print("TOOL TESTING COMPLETE")
    print("="*60 + "\n")


def run_certification_agent():
    print ("Loading .env file")
    load_dotenv()
    print("Loading config files.")
    application_config = load_config('app/config/application_config.yaml');
    request = get_certification_request()

    # Convert Pydantic model to a json compatible dictionary
    request_data = request.model_dump(mode="json")
    print("\nCertification Request:")
    print(request_data)

    model = get_llm(application_config)
    
    # Define tools for the agent
    tools = [
        search_confluence_page,
        get_confluence_page_content,
        get_confluence_space_details,
        create_confluence_page,
        update_confluence_page,
        get_jira_fields,
        get_jira_issue,
        get_jira_user,
        create_jira_issue,
        link_jira_issue,
        update_jira_issue,
        add_jira_comment
    ]
    
    messages = release_planning_prompt.format_messages(
    certification_request=request_data
)

    agent = create_agent(
     model=model,
     tools=tools
    )

    result = agent.invoke({
        "messages": messages
    })

   

    print("\n==============================")
    print("AGENT ACTIONS")
    print("==============================")

    for message in result["messages"]:

        # Agent deciding to call a tool
        if hasattr(message, "tool_calls") and message.tool_calls:
            for call in message.tool_calls:
                print(f"\nAction: {call['name']}")
                print(f"Arguments: {call['args']}")

        # Output returned by the tool
        elif message.__class__.__name__ == "ToolMessage":
            print(f"Tool Output: {message.content}")

    print("\n==============================")
    print("FINAL AGENT OUTPUT")
    print("==============================")

    # Print only the final AI response
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage) and message.content:
            print(message.content)
            break

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "certification":
            run_certification_agent()
        elif sys.argv[1] == "releasereadiness":
            run_releasereadiness_agent()
    else:
        run_certification_agent()  # default