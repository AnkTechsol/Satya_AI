# Basic Workflow Example

This example is a small end-to-end Satya session that:

- initializes the SDK
- creates a realistic backlog
- logs progress
- scrapes one public reference URL
- picks and finishes work through the SDK
- flushes logs at the end

It writes task artifacts to `satya_data/example_outputs/basic_workflow/` by default so a normal demo run does not modify tracked source files.

## Run It

Run these commands from the repository root.

### 1. Install the project dependencies

```bash
pip install streamlit beautifulsoup4 markdownify requests pandas gitpython
```

### 2. Export the minimum auth settings

```bash
export SATYA_AGENT_KEYS=DEMO_KEY
export SATYA_AGENT_KEY=DEMO_KEY
export AUDIT_SECRET=basic-workflow-secret
```

### 3. Start the dashboard

```bash
streamlit run app.py --server.port 5000
```

Open `http://localhost:5000` in a browser.

### 4. Run the example workflow

```bash
python examples/basic_workflow/run_example.py
```

The script will:

- create two tasks in `satya_data/tasks/`
- scrape `https://example.com` into `satya_data/truth/`
- write example artifacts under `satya_data/example_outputs/basic_workflow/`
- append agent logs under `satya_data/agents/`

## Isolated Demo Run

If you want to test the workflow without touching the repository's default `satya_data/` directory, point the example at a temporary location:

```bash
python examples/basic_workflow/run_example.py \
  --repo-path /tmp/satya-basic-workflow \
  --output-dir /tmp/satya-basic-workflow/satya_data/example_outputs/basic_workflow
```

## Notes

- The example uses `https://example.com` because it is a stable public page that works well for a scraper demo.
- Scraping requires outbound network access. If the request fails, the workflow still shows task creation, logging, picking, and task completion behavior.
- The example sets development defaults for `SATYA_AGENT_KEYS`, `SATYA_AGENT_KEY`, and `AUDIT_SECRET` if they are not already exported, but the commands above make the runtime requirements explicit.
