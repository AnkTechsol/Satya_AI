# HN Post Draft — Satya AI

## Title (pick one — A/B test)

**Option A (recommended):**
> Show HN: Satya – Open-source governance layer for AI agents (MIT, Python)

**Option B:**
> Show HN: I built a governance layer for AI agents after one deleted files and charged me $40

---

## Body Text

I watched an AI agent delete files it wasn't supposed to touch, mark itself "done," and charge me $40 in API costs.

The problem wasn't that it was dumb. It had no boundaries.

Every monitoring tool I tried — LangSmith, Langfuse, AgentOps — answers the same question: *"What did your agent do?"* Nobody was asking the more important one: *"What is your agent **allowed** to do?"*

So I built Satya (Sanskrit for "truth").

**What it does:**

- Per-task `allowed_actions` / `forbidden_actions` — default-deny validator
- Completion checker: agents can't self-certify. Verify via file existence, test pass, subtask completion, or manual human approval
- Real-time dashboard: the agent populates it, the human watches it in a browser — no terminal needed
- Watchdog: auto-detects stale tasks
- 3 lines to integrate:

```python
import satya.sdk as satya
client = satya.init("my_agent")
task = client.create_task("Analyze pricing", "Compare competitors")
satya.log("Starting...")
```

Zero infra — flat JSON + Markdown files in your repo. No database, no cloud service.

We used Claude Code to build v0.2.0 (the Reliability Core), operating inside Satya's own task system the whole time. It asked the right questions before writing a line of code: *"Where are the edges?"*

GitHub: https://github.com/AnkTechsol/Satya_AI
Landing page: https://anktechsol.github.io/Satya_AI/

Happy to answer questions about the design decisions — especially the default-deny action validator and the completion checker architecture.

---

## Submission Notes

- **Post time**: Tuesday or Wednesday, 8–10am ET (HN peak traffic window)
- **URL to submit**: https://github.com/AnkTechsol/Satya_AI
  (HN prefers GitHub URLs for Show HN — more credibility, direct code access)
- **Backup URL**: https://anktechsol.github.io/Satya_AI/
- **Tag**: Show HN
- **Engage fast**: respond to every comment within the first 2 hours — HN ranking rewards comment velocity
- **Don't ask for upvotes** in the body — HN will penalize the post

---

## Follow-up comment (post immediately after submission)

> Hi HN — Anuj here, one of the builders. Happy to discuss any design decision:
> - Why default-deny over allowlist-only?
> - How the completion checker works (and why agents shouldn't self-certify)
> - What "Satya" means and why the name fits
>
> If you're using Claude Code, Jules, or Codex for serious work, you're probably already running into the accountability gap this solves. Curious what you've built to work around it.
