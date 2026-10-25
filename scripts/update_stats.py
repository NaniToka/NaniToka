#!/usr/bin/env python3
"""Fetch GitHub stats via GraphQL and inject them into README.md."""
import json
import os
import re
import urllib.request
from datetime import datetime, timedelta, timezone

USER = "NaniToka"
TOKEN = os.environ.get("STATS_TOKEN") or os.environ["GITHUB_TOKEN"]
README = "README.md"
START, END = "<!--STATS:START-->", "<!--STATS:END-->"

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def streaks(days):
    """days: list of (date, count) sorted ascending. Returns (current, longest)."""
    longest = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)

    # Current streak: today (UTC, same as GitHub) may still be empty without breaking it.
    today = datetime.now(timezone.utc).date()
    by_date = {d: c for d, c in days}
    cursor = today if by_date.get(today, 0) > 0 else today - timedelta(days=1)
    current = 0
    while by_date.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    return current, longest


def main():
    u = fetch()
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = sorted(
        (datetime.strptime(d["date"], "%Y-%m-%d").date(), d["contributionCount"])
        for w in cal["weeks"]
        for d in w["contributionDays"]
    )
    current, longest = streaks(days)
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    repos = u["repositories"]["totalCount"]
    followers = u["followers"]["totalCount"]
    total = cal["totalContributions"]
    stamp = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")

    block = f"""{START}
<div align="center">

| ⭐ Stars earned | 📦 Public repos | 👥 Followers | 🔥 Contributions (1 yr) | ⚡ Current streak | 🏅 Longest streak (1 yr) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **{stars}** | **{repos}** | **{followers}** | **{total}** | **{current} days** | **{longest} days** |

<sub>Auto-updated from the GitHub API · last refresh {stamp}</sub>

</div>
{END}"""

    with open(README, encoding="utf-8") as f:
        text = f.read()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        raise SystemExit("Stats markers not found in README.md")
    with open(README, "w", encoding="utf-8") as f:
        f.write(pattern.sub(block, text))
    print("README updated")


if __name__ == "__main__":
    main()
