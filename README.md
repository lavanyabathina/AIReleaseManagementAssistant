# AI Release Management Assistant

An LLM agent that automates the planning of software certification activities for
Fusion Middleware (FMW) products. Given a short certification request, the agent
reads product/POC information from Confluence, creates the corresponding Jira
Story and Tasks, links them, publishes a Confluence certification summary page,
verifies everything it created, and returns a structured execution report.

Built with [LangChain](https://python.langchain.com/) agents and the Jira /
Confluence Cloud REST APIs.

---

## What it does

The agent executes the full certification workflow end to end:

1. **Read the source of truth** — searches Confluence for the
   *Product Contact Information for FMW Products* page and extracts the
   `Product -> POC` mapping.
2. **Create the parent Story** — one Jira Story for the certification, assigned
   to the requested owner, with the release and start/end dates.
3. **Resolve POCs to Jira users** — looks up each POC email in Jira.
4. **Create product Tasks** — one Task per product with a resolved POC
   (`Certify <PRODUCT> for <CERTIFICATION>`), assigned to that POC.
5. **Link Tasks to the Story** — every product Task is associated with the
   parent certification Story.
6. **Verify Jira artifacts** — re-reads each issue and checks project, summary,
   assignee, release, dates, and parent relationship.
7. **Resolve the Confluence space** — turns the space key into a real space ID.
8. **Create the summary page** — `<Certification> - <Release> - Certification
   Summary`, containing a purpose section, certification details with a live
   Jira link, and a six-column tracking table.
9. **Verify the Confluence page** — checks title, sections, table shape, and
   data consistency against what Jira actually returned.
10. **Report** — prints every tool call the agent made, followed by a final
    execution report with status `Completed`, `Partially Completed`, or `Failed`.

Products with no POC, or whose POC cannot be resolved to a Jira user, are
skipped and reported as exceptions rather than guessed at.

---

## Project structure

```
AIReleaseManagementAssistant/
├── main.py                                  # Entry point + a manual tool smoke test
├── requirements.txt
├── .env                                     # Secrets (not committed)
└── app/
    ├── config/
    │   └── application_config.yaml          # LLM provider / model / temperature
    ├── inputs/
    │   └── certification_input.py           # Interactive prompts for the request
    ├── models/
    │   └── certification_request.py         # Pydantic model + date validation
    ├── llm/
    │   ├── llm_factory.py                   # Provider dispatch
    │   ├── claude_llm.py                    # Anthropic Claude
    │   ├── gemini_llm.py                    # Google Gemini
    │   └── openai_llm.py                    # Placeholder
    ├── prompts/
    │   ├── release_planning_prompt.py       # System prompt driving the workflow
    │   └── release_planning_prompt_with_mcp.py
    ├── tools/
    │   ├── jira_tools.py                    # Jira Cloud REST v3 tools
    │   └── confluence_tools.py              # Confluence Cloud REST v2 tools
    └── utils/
        └── load_config.py                   # YAML config loader
```

---

## Prerequisites

- Python 3.14 (the local virtualenv was created with 3.14.4; 3.11+ should also
  work)
- An Atlassian Cloud account with API access to a Jira project and a Confluence
  space
- An API key for the LLM provider you configure (Anthropic or Google)

---

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

> **Note:** the code also imports `requests` and `pyyaml` directly. They are
> normally pulled in as transitive dependencies, but if you hit an
> `ImportError`, install them explicitly: `pip install requests pyyaml`

### 3. Configure credentials

Create a `.env` file in the project root:

```dotenv
# LLM providers (only the one you configure is required)
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Confluence Cloud
CONFLUENCE_API_BASE_URL=https://<your-site>.atlassian.net/wiki/api/v2
CONFLUENCE_EMAIL=you@example.com
CONFLUENCE_API_TOKEN=<atlassian-api-token>

# Jira Cloud
JIRA_API_BASE_URL=https://<your-site>.atlassian.net/rest/api/3
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=<atlassian-api-token>
```

Atlassian API tokens are created at
https://id.atlassian.com/manage-profile/security/api-tokens

### 4. Choose the model

Edit [app/config/application_config.yaml](app/config/application_config.yaml):

```yaml
llm:
  provider: claude          # claude | gemini
  model: claude-sonnet-4-6
  temperature: 0
```

---

## Prepare Confluence

The agent treats a single Confluence page as the authoritative product/POC
source. Before the first run, create a page titled:

```
Product Contact Information for FMW Products
```

It must list each FMW product alongside its POC (an email address that also
exists as a Jira account). Products without a POC are skipped by design.

---

## Usage

```powershell
python main.py certification
```

or simply `python main.py` — the certification agent is the default.

You will be prompted for the request fields:

| Field | Example | Notes |
| --- | --- | --- |
| `certification` | `Oracle Linux 10` | Becomes the parent Story summary |
| `release` | `14.1.2` | |
| `jira_project` | `REL` | Jira project key |
| `confluence_space` | `REL` | Space key, resolved to a space ID at runtime |
| `parent_story_assignee` | `you@example.com` | Assignee of the parent Story |
| `start_date` | `2026-08-13` | `YYYY-MM-DD` |
| `end_date` | `2026-09-13` | Must be on or after `start_date` |

The run prints each agent action and tool output, then the final execution
report.

---

## Available tools

### Jira ([app/tools/jira_tools.py](app/tools/jira_tools.py))

| Tool | Purpose |
| --- | --- |
| `get_jira_fields` | List available Jira fields (avoids hard-coded field IDs) |
| `get_jira_issue` | Fetch an issue by key or ID |
| `get_jira_user` | Resolve an email to a Jira account ID |
| `create_jira_issue` | Create a Story or Task with dates and assignee |
| `link_jira_issue` | Link two issues (e.g. Task to parent Story) |
| `update_jira_issue` | Update fields on an existing issue |
| `add_jira_comment` | Add a comment to an issue |

### Confluence ([app/tools/confluence_tools.py](app/tools/confluence_tools.py))

| Tool | Purpose |
| --- | --- |
| `search_confluence_page` | Find a page by title |
| `get_confluence_page_content` | Read page body (parsed with BeautifulSoup) |
| `get_confluence_space_details` | Resolve a space name/key to a space ID |
| `create_confluence_page` | Create a page in a space |
| `update_confluence_page` | Update an existing page |

---

## Testing the integrations

[main.py](main.py) includes a `test_tools()` helper that exercises each Jira and
Confluence tool directly — useful for verifying credentials and permissions
without involving the LLM. It creates real issues and pages, so point it at a
scratch project/space first. Call it from `__main__` or an interactive shell:

```python
from main import test_tools
test_tools()
```

---

## Safety rules built into the agent

The system prompt in
[app/prompts/release_planning_prompt.py](app/prompts/release_planning_prompt.py)
constrains the agent to:

- never invent products, POCs, issue keys, page IDs, space IDs, or URLs
- always use the actual values returned by tools
- never create duplicate Jira Tasks or Confluence pages
- never delete Jira issues or Confluence pages
- never modify existing issues or pages unless explicitly asked
- stop the workflow if the parent Story cannot be created
- verify every write operation before reporting success

---

## Known limitations

- `python main.py releasereadiness` is accepted as an argument, but
  `run_releasereadiness_agent()` is not implemented, so that path raises a
  `NameError`.
- The OpenAI provider ([app/llm/openai_llm.py](app/llm/openai_llm.py)) is a stub
  and returns `None`.
- The `tests/` directory is currently empty.
