#!/usr/bin/env python3
"""
sync_skills.py — Claude Skills Library discovery script

Searches GitHub for public repos containing Claude Skills (SKILL.md files),
collects metadata from the GitHub API only, and stores repo links.
No file content is fetched or copied — just pointers to the original repos.
"""

import os
import json
import time
import logging
from datetime import datetime, timezone

from github import Github, GithubException, RateLimitExceededException

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SKILLS_JSON_PATH = "skills.json"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
SLEEP = 1.2  # seconds between requests

CATEGORY_KEYWORDS = {
    "Files":   ["file", "document", "pdf", "excel", "docx", "pptx", "xlsx", "word", "spreadsheet"],
    "Design":  ["design", "ui", "frontend", "css", "html", "layout", "style", "visual", "figma"],
    "Data":    ["data", "chart", "analytics", "sql", "database", "csv", "analysis", "scrape"],
    "Writing": ["email", "write", "draft", "content", "blog", "copy", "letter", "message"],
    "Meta":    ["skill", "meta", "prompt", "claude", "anthropic", "llm", "ai", "agent"],
}


def infer_category(text: str) -> str:
    t = (text or "").lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(k in t for k in kws):
            return cat
    return "Community"


def skill_from_repo(repo) -> dict:
    """Build a skill entry using ONLY GitHub API metadata. No file content fetched."""
    name = (
        repo.name.lower()
        .replace("claude-skill-", "").replace("claude-skills-", "")
        .replace("-skill", "").replace("_skill", "").strip("-_")
    ) or repo.name.lower()

    description = (repo.description or "A Claude skill.").strip()[:160]

    try:
        topics = repo.get_topics()
    except Exception:
        topics = []

    category = infer_category(" ".join(topics) + " " + description + " " + name)
    last_updated = (
        repo.pushed_at.strftime("%Y-%m-%dT%H:%M:%SZ") if repo.pushed_at
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    return {
        "name": name,
        "description": description,
        "emoji": "🔧",
        "category": category,
        "repo_url": repo.html_url,   # link to original repo — nothing copied
        "author": repo.owner.login,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "last_updated": last_updated,
        "topics": topics[:6],
        "source": "community",
    }


def search_code(gh: Github) -> list:
    results, seen = [], set()
    for query in [
        "filename:SKILL.md",
        'filename:SKILL.md "Claude Skill"',
        "filename:SKILL.md anthropic",
    ]:
        log.info(f"Code search: {query!r}")
        try:
            for item in gh.search_code(query):
                repo = item.repository
                if repo.id in seen or repo.private:
                    continue
                seen.add(repo.id)
                results.append(skill_from_repo(repo))
                time.sleep(SLEEP)
        except RateLimitExceededException:
            log.warning("Rate limit — sleeping 60s"); time.sleep(60)
        except GithubException as e:
            log.warning(f"Code search error: {e}")
        time.sleep(SLEEP * 2)
    return results


def search_repos(gh: Github) -> list:
    results, seen = [], set()
    for query in [
        "topic:claude-skills",
        "topic:claude-skill",
        "topic:claude-skill-library",
        "claude-skill in:name",
        "claude-skills in:name",
        '"claude skills" in:description',
    ]:
        log.info(f"Repo search: {query!r}")
        try:
            for repo in gh.search_repositories(query):
                if repo.id in seen or repo.private:
                    continue
                seen.add(repo.id)
                results.append(skill_from_repo(repo))
                time.sleep(SLEEP)
        except RateLimitExceededException:
            log.warning("Rate limit — sleeping 60s"); time.sleep(60)
        except GithubException as e:
            log.warning(f"Repo search error: {e}")
        time.sleep(SLEEP * 2)
    return results


def deduplicate(skills: list) -> list:
    """Deduplicate by repo_url. Curated entries are never removed."""
    by_url, by_name = {}, {}

    # Curated first
    for s in skills:
        if s.get("source") == "curated":
            by_url[s.get("repo_url", s["name"])] = s
            by_name[s["name"]] = s

    # Community
    for s in skills:
        if s.get("source") == "curated":
            continue
        url_key = s.get("repo_url", "")
        name_key = s["name"]

        if url_key and url_key in by_url:
            if s["stars"] > by_url[url_key].get("stars", 0):
                by_url[url_key]["stars"] = s["stars"]
            continue

        if name_key in by_name and by_name[name_key].get("source") != "curated":
            if s["stars"] <= by_name[name_key].get("stars", 0):
                continue
            old_url = by_name[name_key].get("repo_url", "")
            if old_url in by_url:
                del by_url[old_url]

        by_url[url_key] = s
        by_name[name_key] = s

    return sorted(by_url.values(), key=lambda x: x.get("stars", 0), reverse=True)


def main():
    if not GITHUB_TOKEN:
        log.warning("No GITHUB_TOKEN — unauthenticated requests limited to 10/min")

    gh = Github(GITHUB_TOKEN) if GITHUB_TOKEN else Github()

    try:
        with open(SKILLS_JSON_PATH) as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {"meta": {}, "skills": []}

    existing = existing_data.get("skills", [])
    original_count = len(existing)
    log.info(f"Loaded {original_count} existing skills")

    # Discover repos — GitHub API metadata only, no file content fetched
    discovered = search_code(gh) + search_repos(gh)
    log.info(f"Discovered {len(discovered)} repos from GitHub")

    merged = deduplicate(existing + discovered)
    new_count = len(merged) - original_count

    output = {
        "meta": {
            "last_synced": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_skills": len(merged),
            "sources": ["github_search", "curated"],
        },
        "skills": merged,
    }

    with open(SKILLS_JSON_PATH, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"Found {new_count} new skills, {len(merged)} total")
    log.info("✅ skills.json updated — repo links only, no content copied")


if __name__ == "__main__":
    main()
