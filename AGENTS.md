# AGENTS.md — Your Deployment & Operations Manual

> **YOU ARE THE DEPLOYER.** This file is written directly to you — the AI agent.
> Satya is a tool **you** set up, run, and operate. The human does not deploy this.
> The human only opens the dashboard URL in their browser to watch your progress.
>
> Read this file completely before doing anything.

---

## TL;DR — What You Need to Understand

1. **You deploy Satya yourself.** Install dependencies, start the dashboard, create the data directories — all of this is your job.
2. **You use the SDK to report your work.** Every task you create, every log you write, every URL you scrape — that's you doing it programmatically through the SDK.
3. **The human does nothing technical.** They open a browser, navigate to the dashboard URL, and monitor your progress. That's it. They see your tasks, your logs, and your knowledge base — all in real time.
4. **Satya is your accountability layer.** Think of it as your project management board that the human can see. You update it. They read it.

---

## How This Works — The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                        AI AGENT (You)                       │
│                                                             │
│  1. Deploy Satya (install deps, start dashboard)            │
│  2. Initialize SDK: satya.init(agent_name="your_name")      │
│  3. Create tasks (backlog): satya.create_task("title", "desc") │
│  4. PICK WORK: satya.pick_task() (Auto-assigns highest prio)   │
│  5. Log progress: satya.log("Working...") (Auto-comments on task) │
│  6. Scrape knowledge: satya.scrape("https://...")              │
│  7. Finish task: satya.finish_task()                           │
│                                                             │
│  All data is saved to satya_data/ as flat files             │
│                          │                                  │
└──────────────────────────│──────────────────────────────────┘
                           │
                    writes to disk
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                       │
│                    (http://localhost:5000)                   │
│                                                             │
│  Reads satya_data/ and displays:                            │
│  - Task board (To Do / In Progress / Done)                  │
│  - Completion metrics and charts                            │
│  - Scraped knowledge base                                   │
│  - Your agent session logs                                  │
│                          │                                  │
└──────────────────────────│──────────────────────────────────┘
                           │
                   human opens browser
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      HUMAN (Observer)                       │
│                                                             │
│  - Opens the dashboard URL in their browser                 │
│  - Sees your tasks, logs, and scraped knowledge             │
│  - Can manually create tasks or scrape URLs via the UI      │
│  - Does NOT deploy, configure, or run anything              │
│  - Monitors your progress and reviews your work             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**You are the engine. The dashboard is the window. The human is the observer.**

---

## Step-by-Step: What You Must Do

### Step 1: Deploy the Dashboard

This is YOUR responsibility. The human will not do this for you.

```bash
# Clone the repository
git clone https://github.com/anktechsol/Satya_AI.git
cd Satya_AI

# Install dependencies
pip install streamlit beautifulsoup4 markdownify requests pandas gitpython

# Or if using uv (Replit):
uv add streamlit beautifulsoup4 markdownify requests pandas gitpython

# Create data directories
mkdir -p satya_data/tasks satya_data/truth satya_data/agents

# Start the dashboard
streamlit run app.py --server.port 5000
```

Once running, the dashboard is live at `http://localhost:5000`. Give this URL to the human — they will open it in their browser to monitor you.

### Step 2: Initialize the SDK in Your Code

Before you do any work, initialize Satya so your activity is tracked:

```python
import sys
sys.path.insert(0, "src")
import satya.sdk as satya

client = satya.init(agent_name="your_agent_name")
```

This creates a session log file at `satya_data/agents/your_agent_name_YYYYMMDD_HHMMSS.log`. The human will see this log on the dashboard.

### Step 3: Populate the Backlog (Optional)

If there are no tasks, create some. But usually, you or the human will have created tasks already.

```python
satya.create_task("Build authentication system", "Implement JWT-based login and signup")
```

### Step 4: Pick the Highest Priority Task

**This is the most important step.** Instead of choosing what to do, let Satya tell you what is most critical. Satya acts as your Scrum Master.

```python
# Automatically finds the highest priority 'To Do' task, assigns it to you,
# moves it to 'In Progress', and sets it as your active context.
task = satya.pick_task()

if not task:
    satya.log("No tasks available!")
    # Handle idle state
else:
    satya.log(f"Starting work on: {task['title']}")
```

### Step 5: Do the Work & Log

As you work, log your progress. Satya automatically attaches these logs to your active task as comments.

```python
satya.log("Designing the schema...")
# ... work ...
satya.log("Schema verified.")
```

### Step 6: Finish the Task

When done, mark it as finished. This closes the context.

```python
satya.finish_task()
```

### Step 5: Build the Knowledge Base

When you need reference material, scrape it into the Truth Source. The human (and other agents) can access it from the dashboard.

```python
client.scrape_url("https://jwt.io/introduction")
satya.log("Scraped JWT documentation for reference")
```

### Step 6: Flush Logs When Done

At the end of your session, flush your logs so everything is persisted:

```python
client.flush_logs()
```

---

## Complete Working Example

Here's a full session showing exactly what an agent should do:

```python
import sys
sys.path.insert(0, "src")
import satya.sdk as satya

# === INITIALIZE (always do this first) ===
client = satya.init(agent_name="builder_agent")
satya.log("Session started. Beginning project setup.")

# === CREATE BACKLOG ===
client.create_task("Setup database schema", "Create tables for users, sessions, and posts")
client.create_task("Build REST API", "Implement CRUD endpoints for all resources")
satya.log("Backlog populated.")

# === GATHER KNOWLEDGE ===
client.scrape_url("https://www.postgresql.org/docs/current/tutorial.html")

# === EXECUTE WORK (LOOP) ===
while True:
    task = satya.pick_task()
    if not task:
        satya.log("No more tasks to do.")
        break

    satya.log(f"Starting task: {task['title']}")

    # ... do work ...
    satya.log("Making progress...")

    satya.finish_task()
    satya.log("Task complete.")

# === SESSION COMPLETE ===
satya.log("All tasks complete. Session ending.")
client.flush_logs()
```

While you run this, the human sees:
- **Dashboard**: 3 tasks, completion going from 0% to 100%
- **Task Board**: Tasks moving from "To Do" to "In Progress" to "Done"
- **Truth Source**: PostgreSQL tutorial scraped and available
- **Agent Logs**: Every log message with timestamps

---

## SDK Function Reference

| Function | What It Does | When to Use |
|---|---|---|
| `satya.init(agent_name)` | Start a tracked session. Creates log file. | **Always call first** before any other function |
| `satya.create_task(title, description)` | Create a task (status: "To Do"). Returns task dict with `id`. | Before starting any unit of work |
| `satya.update_task(task_id, status)` | Change task status: `"To Do"`, `"In Progress"`, `"Done"` | Only if manual update is needed (prefer `pick_task`) |
| `satya.pick_task()` | **Recommended** Auto-assign highest priority task | When ready to work. Sets active context. |
| `satya.finish_task()` | Mark active task as Done | When work is complete. |
| `satya.log(message)` | Write log entry & comment on task | Frequently — creates history for the task |
| `satya.scrape(url)` | Scrape URL to Markdown, save to knowledge base | When you need reference docs before starting complex work |
| `client.flush_logs()` | Commit logs to Git (if available) | At the end of your session |

---

## Task JSON Schema

Each task is one JSON file in `satya_data/tasks/{id}.json`:

```json
{
    "id": "a344b224",
    "title": "Build login page",
    "description": "Implement OAuth2 login flow",
    "status": "To Do",
    "priority": "High",
    "assignee": "builder_agent",
    "created_at": "2026-02-07T04:34:36.378218",
    "updated_at": "2026-02-07T04:34:36.378218"
}
```

**Valid statuses:** `"To Do"`, `"In Progress"`, `"Done"`
**Valid priorities:** `"Low"`, `"Medium"`, `"High"`, `"Critical"`

---

## Direct File Manipulation (If SDK Is Not Available)

If you cannot import the SDK (e.g., different runtime, non-Python agent), you can manipulate the flat files directly. The dashboard reads from `satya_data/` — it does not care how the files got there.

### Create a Task
```python
import json, uuid, os
from datetime import datetime

task = {
    "id": str(uuid.uuid4())[:8],
    "title": "My Task",
    "description": "What this task is about",
    "status": "To Do",
    "priority": "Medium",
    "assignee": "agent_name",
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat()
}

os.makedirs("satya_data/tasks", exist_ok=True)
with open(f"satya_data/tasks/{task['id']}.json", "w") as f:
    json.dump(task, f, indent=4)
```

### Update a Task Status
```python
import json
from datetime import datetime

task_id = "a344b224"
with open(f"satya_data/tasks/{task_id}.json", "r") as f:
    task = json.load(f)
task["status"] = "In Progress"
task["updated_at"] = datetime.now().isoformat()
with open(f"satya_data/tasks/{task_id}.json", "w") as f:
    json.dump(task, f, indent=4)
```

### Delete a Task
```python
import os
os.remove(f"satya_data/tasks/{task_id}.json")
```

### Add a Truth Source
```python
os.makedirs("satya_data/truth", exist_ok=True)
with open("satya_data/truth/my_reference.md", "w") as f:
    f.write("# My Reference\n\nContent scraped or written by the agent.")
```

### Write Agent Logs
```python
from datetime import datetime
os.makedirs("satya_data/agents", exist_ok=True)
with open("satya_data/agents/my_agent_session.log", "a") as f:
    f.write(f"[{datetime.now().isoformat()}] Your log message here\n")
```

---

## Project Structure

```
app.py                        # Streamlit dashboard (the human looks at this)
AGENTS.md                     # This file (you read this)
README.md                     # Public repo documentation
src/satya/
  core/
    __init__.py               # Exports: Tasks, Scraper, GitHandler, storage
    storage.py                # File-based persistence (JSON/Markdown)
    tasks.py                  # Task CRUD operations
    scraper.py                # Web scraper → Markdown
    git_handler.py            # Git commit/push (graceful fallback)
  sdk/
    __init__.py               # Convenience functions: satya.init, satya.log, etc.
    client.py                 # SatyaClient class for full integration
satya_data/                   # ALL data lives here (auto-created)
  tasks/                      # One JSON file per task
  truth/                      # Scraped Markdown knowledge files
  agents/                     # Agent session logs (.log)
.streamlit/config.toml        # Server config (port 5000, bound to 0.0.0.0)
```

---

## Rules You Must Follow

1. **Deploy first.** Install dependencies and start the dashboard before you begin any work. The human needs to see the dashboard from the start.
2. **Always call `satya.init()` before anything else.** This creates your session and log file.
3. **Create tasks before doing work.** The human expects to see tasks on the board before you start working on them.
4. **Log frequently and descriptively.** The human cannot see your internal reasoning — your logs are how they follow what you're doing. Write logs a human can understand.
5. **Prioritize Work.** Always work on the highest priority task first. Use `satya.pick_task()` to let the system decide.
6. **Update task status honestly.** `satya.pick_task()` sets "In Progress", `satya.finish_task()` sets "Done".
7. **Set meaningful priorities.** "Critical" = blockers, "High" = important, "Medium" = normal, "Low" = nice-to-have.
8. **Scrape before complex work.** If you need reference material, scrape it first. The knowledge base is shared — other agents and the human can access it.
9. **Flush logs at session end.** Call `client.flush_logs()` before your session terminates.
10. **Do not delete `satya_data/`.** This is the persistent store. Deleting it erases all tasks, logs, and knowledge.
11. **Do not modify `app.py`** unless the human explicitly asks you to change the dashboard UI.

---

## Enterprise Governance & Compliance

Satya includes built-in compliance rules to ensure high-quality tracking across multi-agent environments:

1. **Audit Trails:** Every status change, task update, and comment is permanently recorded in the task's `audit_trail` array, noting the `agent` name, action, and timestamp.
2. **Rule 1: Task Descriptions:** You cannot create a task with an empty or extremely short description. Descriptions must be at least 10 characters long.
3. **Rule 2: Proof of Work:** You cannot mark a task as `"Done"` unless you have contributed at least one log entry (comment) to that task demonstrating your work.

---

## FAQ for AI Agents

**Q: Who starts the dashboard?**
A: You do. The human does not run commands. You deploy it and give them the URL.

**Q: Who creates tasks?**
A: You do, using the SDK. The human can also create tasks from the dashboard UI if they want to assign work to you.

**Q: Can multiple agents use Satya at the same time?**
A: Yes. Each agent initializes with a unique `agent_name`. Tasks and logs are separate files, so there are no conflicts. All agents' work appears on the same dashboard.

**Q: What if Git is not available?**
A: Satya works fine without Git. The `GitHandler` has a graceful fallback — it simply skips commits. All data is still saved to `satya_data/`.

**Q: Does the human need to install anything?**
A: No. They just open a browser and navigate to the dashboard URL. That's it.

**Q: What if the SDK import fails?**
A: You can manipulate the flat files in `satya_data/` directly. See the "Direct File Manipulation" section above. The dashboard reads from those files — it doesn't care whether the SDK or direct writes created them.

---

## Tech Stack

- **Python 3.11+**
- **Streamlit** — Dashboard UI (what the human sees)
- **BeautifulSoup4 + markdownify** — Web scraping engine
- **Pandas** — Data handling for charts
- **GitPython** — Optional audit trail via Git commits

---

## Contact

Built and maintained by **[Anktechsol.com](https://anktechsol.com)**
