# 🛠️ Claude Skills Library

A community-curated, auto-updating directory of **Claude Skills** — reusable SKILL.md prompt modules that make Claude smarter at specific tasks.

👉 **Live site:** https://abeezith.github.io/claude-skills/

---

## What is a Claude Skill?

A Claude Skill is a structured prompt module — a `SKILL.md` file — that tells Claude how to perform a specific task with precision and consistency. When Claude detects a matching intent in your message, it loads the skill and follows its instructions.

**Example:** When you say *"Create a Word document summarizing this report"*, Claude loads the `docx` skill and follows its detailed instructions for generating high-quality `.docx` files.

---

## How to Use a Skill

1. Browse the library at the live site above
2. Find a skill that matches your task
3. Click **"Copy Trigger"** to copy the example prompt
4. Paste it into Claude — and Claude will use the skill automatically if it's installed in your environment

> **Note:** Skills only activate when the SKILL.md file is accessible to your Claude instance (e.g. via a system prompt, operator config, or tool mount). Check with your Claude deployment for how skills are loaded.

---

## How to Submit Your Own Skill

1. Create a `SKILL.md` file using the format below
2. Push it to a public GitHub repo
3. [Open an Issue](../../issues/new?template=submit-skill.yml) with a link to your repo

Your skill will be picked up automatically during the next daily sync.

### SKILL.md Format

```markdown
---
name: my-skill
description: One line summary of what this skill does
category: Files | Design | Data | Writing | Meta | Community
trigger: Example prompt that activates this skill
emoji: 🔧
---

# My Skill

Detailed instructions for Claude go here. Explain the task, the expected output
format, edge cases to handle, and any step-by-step process Claude should follow.

## When to use this skill
...

## Output format
...
```

---

## How the Daily Sync Works

Every day at **2am UTC**, a GitHub Actions workflow runs automatically:

```
GitHub Actions (cron: 0 2 * * *)
       ↓
scripts/sync_skills.py runs
       ↓
Searches GitHub for:
  - filename:SKILL.md
  - filename:SKILL.md "Claude Skill"
  - topic:claude-skills
  - topic:claude-skill
  - "claude skills" in repo names/descriptions
       ↓
Parses SKILL.md front matter from each result
       ↓
Merges with existing curated skills (curated skills are never removed)
       ↓
Writes updated skills.json
       ↓
Commits skills.json back to this repo
       ↓
GitHub Pages serves the updated site
```

You can also trigger a sync manually from the **Actions** tab in GitHub.

---

## Run the Sync Locally

```bash
# Install dependencies
pip install requests PyGithub python-dateutil

# Run with your GitHub token (higher rate limits)
GITHUB_TOKEN=your_token_here python scripts/sync_skills.py
```

The script will update `skills.json` in place.

---

## Repo Structure

```
claude-skills/
├── index.html                        # The GitHub Pages site
├── skills.json                       # Auto-updated skill data
├── README.md                         # This file
├── .github/
│   └── workflows/
│       └── sync-skills.yml           # Daily sync workflow
└── scripts/
    └── sync_skills.py                # Discovery & merge script
```

---

## Category Tags

| Category  | Covers |
|-----------|--------|
| Files     | DOCX, PPTX, XLSX, PDF, file reading/writing |
| Design    | UI, frontend, CSS, image generation |
| Data      | Analytics, charts, SQL, scraping, CSV |
| Writing   | Emails, blogs, drafts, content |
| Meta      | Skill creation, prompting, Claude-specific |
| Community | Everything else |

---

## Contributing

- **Submit a skill** — open an Issue using the skill submission template
- **Fix a bug** — PRs welcome
- **Improve the site** — edit `index.html` and open a PR
- **Star a skill** — starring the source repo boosts its ranking on the site

---

*Skills that make Claude smarter.* ⚡
