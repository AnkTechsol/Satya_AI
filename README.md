<p align="center">
  <img src="https://img.icons8.com/fluency/96/artificial-intelligence.png" alt="Satya Logo" width="80"/>
</p>

<h1 align="center">Satya — AI Agent Progress Tracker & Truth Source Manager</h1>

<p align="center">
  <strong>Open-source dashboard & Python SDK that AI agents deploy themselves to track tasks, log progress, and build knowledge bases — while humans monitor everything from a real-time web UI.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+"></a>
  <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"></a>
  <a href="#license"><img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge" alt="MIT License"></a>
  <a href="https://anktechsol.com"><img src="https://img.shields.io/badge/Built%20by-Anktechsol.com-6C5CE7?style=for-the-badge" alt="Anktechsol.com"></a>
</p>

<p align="center">
  <a href="#how-it-works">How It Works</a> •
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#sdk-reference">SDK Reference</a> •
  <a href="#for-ai-agents">For AI Agents</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#contributing">Contributing</a>
</p>

---


## Repository Status
- **Last Analytics Run:** 2026-04-03T14:56:47.197197+00:00
- **Open Issues:** Unknown without GH CLI
- **Recent CI Status:** Requires GH CLI to check

## Human-Observer Policy (Agent-First)

Satya is agent-first. Humans are **read-only** by default and may only *observe* logs, traces, and audit events via the Streamlit dashboard.
Mutating actions — registering agents, creating tasks, claiming tasks, completing tasks — are permitted only to authenticated agents (use `SATYA_AGENT_KEY` environment variable).

If an instruction contains `use satya` (or references Satya), the agent should call the SDK helper `satya.sdk.use_satya()` to spawn a child task and link the `trace_id` into the parent audit chain.

See `src/satya/sdk/client.py` for the `use_satya()` helper and `src/satya/auth.py` for agent auth setup.

---


## SUSTAINABLE_FEATURES

- **Auto-README Updater Action** (Added 2026-04)
  - GitHub Action that runs the analytics script on push to main and updates `REPO_ANALYTICS.md` and the `README.md` summary automatically.
  - Chosen because it provides a high-impact, low-maintenance way to reduce doc rot and keep stakeholders informed without manual effort.
  - Runbook: Any push to `main` will automatically trigger the update. You can also run `python update_readme.py` locally.
  - Validation: Verify that `.github/workflows/analytics_and_test.yml` includes the step "Update README with Analytics".

- **Agent Self-Test Harness + CI Analytics Job** (Added 2026-03)
  - Implements a GitHub Action to continuously test agent deployment workflows and auto-update performance traces into `repo_analytics.json` and `REPO_ANALYTICS.md`, reducing doc rot and catching runtime regressions early.
  - Runbook: Commits on `main` automatically run the suite. For local execution, run `python generate_analytics.py`.
  - Validation: Ensure `.github/workflows/analytics_and_test.yml` runs successfully on pushes.

- **Export Adapter Framework (OTLP/Console)** (Added 2024-03)
  - Enables routing Satya's flat-file telemetry traces into enterprise observability stacks without breaking zero-DB architecture.
  - Runbook: Pass a list of instantiated adapters to `satya.init(adapters=[OTLPAdapter()])`.
  - Validation: `PYTHONPATH=. pytest tests/test_adapters.py`

- **Repo Analytics & Competitor Matrix**
  - View [Repo Analytics](REPO_ANALYTICS.md) and [Competitor Matrix](COMPETITOR_MATRIX.md).

For more details on changes, see our [CHANGELOG](CHANGELOG.md).
## How It Works

Satya separates **who does the work** from **who watches the work**:

```
┌──────────────────────────────────┐       ┌──────────────────────────────────┐
│         AI AGENT (Operator)      │       │        HUMAN (Observer)          │
│                                  │       │                                  │
│  - Deploys Satya                 │       │  - Opens the dashboard URL       │
│  - Creates & updates tasks       │ ───── │  - Monitors tasks & progress     │
│  - Logs progress via SDK         │ writes│  - Reads agent session logs      │
│  - Scrapes knowledge base        │  to   │  - Reviews scraped knowledge     │
│  - Manages the full lifecycle    │ disk  │  - Optionally creates tasks      │
│                                  │       │                                  │
│  Uses: Python SDK or flat files  │       │  Uses: Web browser only          │
└──────────────────────────────────┘       └──────────────────────────────────┘
```

**The AI agent is the deployer and operator.** It installs dependencies, starts the dashboard, creates tasks, logs its activity, and scrapes reference material — all programmatically.

**The human is the observer.** They open a browser, navigate to the dashboard URL, and monitor the agent's progress in real time. No terminal. No code. Just a web page.

---

## What's New: Agent Chat & Manual Overrides 🚀

Humans now have direct control over their AI workforce! The new **Agent Chat** control panel allows you to interact with your agents in real-time.
* Monitor live agent logs directly in a chat interface.
* Issue manual overrides and commands (e.g. "Create task: Fix the login button").
* Agents poll for these messages continuously, keeping them on task and aligned with your agenda.

---

## Why Satya?

Modern AI agents work autonomously — but humans still need visibility. **Satya** (Sanskrit for "truth") bridges that gap:

- **Agents self-deploy** — install, configure, and run the dashboard without human help
- **Real-time accountability** — every task, log entry, and scraped document appears on the dashboard instantly
- **Zero infrastructure** — no databases, no cloud services. Just flat files (JSON + Markdown) in your repo
- **Multi-agent ready** — multiple agents can report to the same dashboard simultaneously
- **3 lines to integrate** — `import satya; client = satya.init("my_agent"); satya.log("Working...")`

---

## Env variables (minimum)

- `SATYA_AGENT_KEYS` (comma-separated agent keys). e.g. `DEMO_KEY,prod-key-123`
- `HUMAN_VIEW_TOKEN` (optional) — Admin Key for read-only viewers to bypass and unlock mutating controls in Streamlit.
- `AUDIT_SECRET` — HMAC secret for signing events

---

## Features

| Feature | Description |
|---|---|
| **Dashboard** | Real-time metrics — total tasks, completion rate, task distribution chart, recent activity feed |
| **Task Board** | Kanban-style columns (To Do / In Progress / Done) with priorities (Low / Medium / High / Critical) |
| **Truth Source** | Scrape any URL into clean Markdown and store it in a shared knowledge base |
| **Agent Logs** | Timestamped session logs from every connected agent, viewable in real time |
| **SDK Docs** | In-app documentation so agents can self-onboard without external references |
| **Dark / Light Theme** | One-click toggle in the sidebar with full CSS variable swapping |
| **Zero Config Storage** | Flat JSON + Markdown files in `satya_data/` — no database setup required |
| **Git Integration** | Optional auto-commit for version-controlled audit trails |

---

## Quick Start

### For Humans

You don't need to do anything technical. Once your AI agent deploys Satya, it will give you a URL. Open that URL in your browser — you'll see the dashboard with all the agent's tasks, logs, and knowledge base.

### For AI Agents

> **Full deployment instructions are in [AGENTS.md](AGENTS.md).** That file is written directly to you.

Quick version:

```bash
# 1. Clone the repo
git clone https://github.com/anktechsol/Satya_AI.git
cd Satya_AI

# 2. Install dependencies
pip install streamlit beautifulsoup4 markdownify requests pandas gitpython

# 3. Create data directories
mkdir -p satya_data/tasks satya_data/truth satya_data/agents

# 4. Start the dashboard
streamlit run app.py --server.port 5000
```

Then in your agent code:

```python
import sys
sys.path.insert(0, "src")
import satya.sdk as satya

client = satya.init(agent_name="my_agent")

task = client.create_task("Build feature X", "Implement the new feature")
client.update_task(task["id"], "In Progress")
satya.log("Working on feature X...")
client.update_task(task["id"], "Done")
satya.log("Feature X complete")
client.flush_logs()
```

The human opens `http://localhost:5000` and watches your progress.

---

## SDK Reference

| Function | What It Does | Who Calls It |
|---|---|---|
| `satya.init(agent_name)` | Start a tracked session. Creates log file. | Agent (always first) |
| `satya.create_task(title, desc)` | Create a new task (status: To Do). Returns task dict. | Agent |
| `satya.update_task(id, status)` | Move task: `"To Do"` / `"In Progress"` / `"Done"` | Agent |
| `satya.log(message)` | Write timestamped entry to session log | Agent |
| `satya.scrape(url)` | Scrape URL to Markdown, save to knowledge base | Agent |
| `client.flush_logs()` | Persist logs via Git (if available) | Agent (end of session) |

### Full Example

```python
import sys
sys.path.insert(0, "src")
import satya.sdk as satya

# Initialize — always first
client = satya.init(agent_name="research_bot")

# Create tasks for the human to see
task1 = client.create_task("Analyze pricing data", "Compare competitor pricing pages")
task2 = client.create_task("Generate report", "Create summary with recommendations")

# Gather knowledge
client.scrape_url("https://example.com/pricing")
satya.log("Scraped competitor pricing for reference")

# Do the work
client.update_task(task1["id"], "In Progress")
satya.log("Analyzing pricing data...")
# ... actual work ...
client.update_task(task1["id"], "Done")
satya.log("Pricing analysis complete")

client.update_task(task2["id"], "In Progress")
satya.log("Generating final report...")
# ... actual work ...
client.update_task(task2["id"], "Done")
satya.log("Report generated and saved")

# Session complete
client.flush_logs()
```

---

## For AI Agents

**Read [AGENTS.md](AGENTS.md) — it is your complete operations manual.**

It covers:
- **Your role**: You are the deployer. You set up and run everything. The human only watches.
- **Step-by-step deployment**: Install, configure, start — with exact commands
- **SDK usage**: Every function, with examples and a full working session
- **Direct file manipulation**: How to create tasks, write logs, and add knowledge without the SDK
- **Rules you must follow**: Logging frequency, task hygiene, what not to touch
- **FAQ**: Answers to common agent questions about deployment and operation

**Key principle**: The human should never need to open a terminal. You deploy the dashboard, you populate it with tasks and logs, and the human opens their browser to see your work.

---

## Architecture

```
satya/
├── app.py                          # Dashboard UI (human views this in browser)
├── AGENTS.md                       # Agent operations manual (agents read this)
├── README.md                       # Public documentation (this file)
├── LICENSE                         # MIT License
├── src/
│   └── satya/
│       ├── core/
│       │   ├── __init__.py         # Exports: Tasks, Scraper, GitHandler, storage
│       │   ├── storage.py          # File-based persistence (JSON/Markdown)
│       │   ├── tasks.py            # Task CRUD with priority, status, assignee
│       │   ├── scraper.py          # Web scraper → Markdown converter
│       │   └── git_handler.py      # Git commit/push with graceful fallback
│       └── sdk/
│           ├── __init__.py         # Convenience functions (satya.init, satya.log, etc.)
│           └── client.py           # SatyaClient class for full agent integration
├── satya_data/                     # All persistent data — DO NOT DELETE
│   ├── tasks/                      # One JSON file per task (written by agents)
│   ├── truth/                      # Scraped Markdown files (written by agents)
│   └── agents/                     # Session logs (written by agents)
└── .streamlit/
    └── config.toml                 # Server config (port 5000)
```

### Data Flow

1. **Agent writes** task JSON files, log entries, and Markdown to `satya_data/`
2. **Dashboard reads** from `satya_data/` and renders the UI
3. **Human views** the dashboard in a browser — no file access needed

---

## Deployment Options

### On Replit (Easiest)

1. Fork this Repl
2. Click **Run** — dashboard starts on port 5000 automatically
3. Share the URL with anyone who needs to monitor

### On Any Server

```bash
pip install streamlit beautifulsoup4 markdownify requests pandas gitpython
streamlit run app.py --server.port 5000
```

### With Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install streamlit beautifulsoup4 markdownify requests pandas gitpython
EXPOSE 5000
CMD ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"]
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| [Python 3.11+](https://www.python.org/) | Core runtime |
| [Streamlit](https://streamlit.io/) | Dashboard UI (what humans see) |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | HTML parsing for web scraping |
| [markdownify](https://github.com/matthewwithanm/python-markdownify) | HTML → Markdown conversion |
| [Pandas](https://pandas.pydata.org/) | Data handling and charts |
| [GitPython](https://gitpython.readthedocs.io/) | Optional Git-based audit trail |

---

## Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/my-feature`
3. **Make your changes** and test locally
4. **Submit a Pull Request** with a clear description

### Areas for Contribution

- REST API layer for non-Python agents
- WebSocket real-time log streaming
- Multi-agent collaboration and handoff protocols
- Authentication and role-based access
- Additional output formats (PDF, DOCX) for Truth Source

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## About

**Satya** is proudly built and maintained by **[Anktechsol.com](https://anktechsol.com)**. Need help building enterprise-grade AI applications, custom agent swarms, or robust software architectures? We can help. Check out our services to accelerate your AI adoption!

- **Website**: [anktechsol.com](https://anktechsol.com)
- **GitHub**: [github.com/anktechsol/Satya_AI](https://github.com/anktechsol/Satya_AI)

---

<p align="center">
  <sub>If Satya helps your AI agents stay on track, give it a star on GitHub!</sub>
</p>
