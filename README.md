# LaunchMind - SkillSync MAS

## Startup Idea
SkillSync is an AI-powered browser extension for job seekers. It observes job listings across LinkedIn, Indeed, and Glassdoor, extracts in-demand skills, compares them against a user's resume, and shows a personalized gap report with recommendations.

## Agent Architecture

### Agents Overview
- *CEO Agent*: decomposes the startup idea, reviews outputs, triggers revisions, and posts final summary to Slack
- *Product Agent*: creates product specification JSON with features, personas, and success metrics
- *Engineer Agent*: generates landing page HTML, creates GitHub issue, commits code, opens PR
- *Marketing Agent*: generates tagline, launch copy, sends real email, posts Slack launch message
- *QA Agent*: reviews code and copy, posts PR comments, returns pass/fail verdict

### Communication Flow

Startup Idea → CEO Agent → Product Agent → CEO Review → Engineer Agent → Marketing Agent → CEO Review → QA Agent → CEO Final Summary → Slack


### Which Agent Talks to Which
| Sender | Receiver | Purpose |
|--------|----------|---------|
| CEO | Product | Send product specification task |
| Product | CEO | Return product specification |
| CEO | Engineer | Send landing page development task |
| Engineer | CEO | Return GitHub PR link |
| CEO | Marketing | Send marketing campaign task |
| Marketing | CEO | Return email & Slack confirmation |
| CEO | QA | Send quality assurance review task |
| QA | CEO | Return pass/fail report |

### Message Format
All agents communicate through structured JSON messages via message_bus.py:
json
{
  "message_id": "uuid-string",
  "from_agent": "ceo",
  "to_agent": "product",
  "message_type": "task",
  "payload": {},
  "timestamp": "2026-04-12T10:00:00+00:00",
  "parent_message_id": "optional-parent-id"
}


## Setup Instructions

### Step 1: Clone Repository
bash
git clone https://github.com/agentic35-del/launchmind-group-alpha.git
cd launchmind-group-alpha


### Step 2: Create Virtual Environment

*Windows:*
bash
python -m venv .venv
.venv\Scripts\activate


### Step 3: Install Dependencies
bash
pip install -r requirements.txt


### Step 4: Configure Environment
bash
cp .env.example .env

Then edit .env file and add your API keys:
env
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-5.4-mini
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO_OWNER=agentic35-del
GITHUB_REPO_NAME=launchmind-group-alpha
GITHUB_BASE_BRANCH=main
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_CHANNEL_ID=your_channel_id_here
RESEND_API_KEY=your_resend_api_key_here
RESEND_FROM_EMAIL=your_verified_sender@example.com
RESEND_TO_EMAIL=your_test_email@example.com
REDIS_URL=redis://localhost:6379/0
MESSAGE_HISTORY_FILE=message_history.jsonl


### Step 5: Start Redis
bash
redis-server

Verify Redis is running:
bash
redis-cli ping
# Should return: PONG


### Step 6: Run the System
bash
python main.py


## Platforms Used

| Platform | Purpose | Actions Performed |
|----------|---------|-------------------|
| *OpenAI API* | AI reasoning for all agents | Task decomposition, product spec generation, landing page code generation, marketing copy creation, QA review generation |
| *GitHub* | Code hosting and collaboration | Create issue, create branch, commit code, open pull request, add inline review comments |
| *Slack* | Team communication | Post launch message, post final summary |
| *Resend* | Email delivery | Send outreach email to test inbox |
| *Redis* | Message queuing | Handle agent-to-agent communication, store message history |

## Links

### GitHub Repository
https://github.com/agentic35-del/launchmind-group-alpha

### GitHub Pull Request (Created by Engineer Agent)
https://github.com/agentic35-del/launchmind-group-alpha/pull/48

### GitHub Issue (Created by Engineer Agent)
https://github.com/agentic35-del/launchmind-group-alpha/issues/47

### Slack Workspace Invite Link
https://join.slack.com/t/launchmind-mas/shared_invite/zt-3ulozcjyf-4UuuiEmC57ysaHj~FShaCQ


## How the System Runs

When you execute python main.py:

1. CEO agent receives the SkillSync startup idea
2. CEO sends structured task to Product agent
3. Product agent returns product specification
4. CEO reviews and approves
5. Engineer agent creates GitHub issue and pull request with landing page
6. Marketing agent sends real email and posts Slack launch message
7. CEO reviews and approves
8. QA agent reviews Engineer and Marketing outputs, adds inline PR comments
9. CEO posts final summary to Slack
10. System saves complete message history to message_history.jsonl

## Message History

All inter-agent communication is logged to message_history.jsonl:
jsonl
{"message_id": "abc123", "from_agent": "ceo", "to_agent": "product", "message_type": "task", "payload": {...}, "timestamp": "2026-04-12T10:00:00Z"}
{"message_id": "def456", "from_agent": "product", "to_agent": "ceo", "message_type": "result", "payload": {...}, "timestamp": "2026-04-12T10:01:00Z"}



## Requirements
- Python 3.8 or higher
- Redis server
- Internet connection
- GitHub account (with personal access token)
- Slack workspace (with bot token)
- Resend account (for email)
- OpenAI API key

## Project Structure

launchmind-group-alpha/
├── main.py                 # Run this file
├── message_bus.py         # Redis message bus
├── requirements.txt       # Python dependencies
├── .env                   # Your API keys (create this)
├── .env.example           # Example environment file
├── message_history.jsonl  # All messages logged here
├── agents/
│   ├── ceo_agent.py
│   ├── product_agent.py
│   ├── engineer_agent.py
│   ├── marketing_agent.py
│   └── qa_agent.py
├
└── README.md             # This file


## Quick Copy-Paste Commands

bash
# Complete setup in one go
git clone https://github.com/agentic35-del/launchmind-group-alpha.git
cd launchmind-group-alpha
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Now edit .env with your keys
redis-server
python main.py


---

*Group:* Atlas Malik(24i-8020), Aieza Noor(24i-8021) and Muqaddas Rizwan(24i-8051) 
*Date:* April 12, 2026  
*Assignment:* LaunchMind - SkillSync MAS
```