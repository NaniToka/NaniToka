#!/usr/bin/env python3
"""Fetch GitHub data via GraphQL and render stats + streak SVG cards."""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

USER = "NaniToka"
TOKEN = os.environ.get("STATS_TOKEN") or os.environ["GITHUB_TOKEN"]
OUT = Path("assets")

PROFILE_Q = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      nodes { stargazerCount }
    }
    contributionsCollection {
      contributionYears
      totalCommitContributions
      totalPullRequestReviewContributions
    }
  }
}
"""

YEAR_Q = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def gql(query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def all_days(years):
    days = {}
    for y in years:
        u = gql(YEAR_Q, {"login": USER, "from": f"{y}-01-01T00:00:00Z", "to": f"{y}-12-31T23:59:59Z"})
        for w in u["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[datetime.strptime(d["date"], "%Y-%m-%d").date()] = d["contributionCount"]
    return days


def streaks(days):
    ordered = sorted(days)
    longest = (0, None, None)
    run, start = 0, None
    for d in ordered:
        if days[d] > 0:
            if run == 0:
                start = d
            run += 1
            if run > longest[0]:
                longest = (run, start, d)
        else:
            run = 0
    today = datetime.now(timezone.utc).date()  # GitHub counts days in UTC
    cursor = today if days.get(today, 0) > 0 else today - timedelta(days=1)
    end, cur = cursor, 0
    while days.get(cursor, 0) > 0:
        cur += 1
        cursor -= timedelta(days=1)
    cur_start = end - timedelta(days=cur - 1) if cur else None
    return (cur, cur_start, end if cur else None), longest


def rank(commits, prs, issues, reviews, stars, followers):
    """Same idea as github-readme-stats: weighted percentile -> letter."""
    exp = lambda x: 1 - 2 ** -x
    logn = lambda x: x / (1 + x)
    total_w = 12
    score = (
        2 * exp(commits / 250) + 3 * exp(prs / 50) + 1 * exp(issues / 25)
        + 1 * exp(reviews / 2) + 4 * logn(stars / 50) + 1 * logn(followers / 10)
    )
    pct = (1 - score / total_w) * 100
    for letter, limit in [("S", 1), ("A+", 12.5), ("A", 25), ("B+", 37.5), ("B", 62.5)]:
        if pct <= limit:
            return letter, pct
    return "C", pct


def fmt(d):
    return d.strftime("%b %d, %Y") if d else "-"


def stats_svg(name, rows, letter, pct):
    circ = 2 * 3.14159 * 40
    dash = circ * (1 - pct / 100)
    lines = "".join(
        f'<text x="30" y="{80 + i * 25}" fill="#a9b1d6" font-size="14">{label}</text>'
        f'<text x="230" y="{80 + i * 25}" fill="#7aa2f7" font-size="14" font-weight="700">{val}</text>'
        for i, (label, val) in enumerate(rows)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="215" viewBox="0 0 495 215" font-family="Segoe UI, Ubuntu, sans-serif">
<rect width="495" height="215" rx="6" fill="#1a1b27" stroke="#6c5ce7" stroke-width="1.5"/>
<text x="30" y="40" fill="#6c5ce7" font-size="19" font-weight="700">{name}'s GitHub Stats</text>
{lines}
<g transform="translate(400,115)">
<circle r="40" fill="none" stroke="#2a2b3d" stroke-width="7"/>
<circle r="40" fill="none" stroke="#6c5ce7" stroke-width="7" stroke-linecap="round" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{dash:.1f}" transform="rotate(-90)"/>
<text y="9" text-anchor="middle" fill="#a9b1d6" font-size="26" font-weight="700">{letter}</text>
</g>
</svg>"""


def streak_svg(total, cur, longest, first_day):
    def col(x, big, label, sub, color):
        return (
            f'<text x="{x}" y="85" text-anchor="middle" fill="{color}" font-size="32" font-weight="700">{big}</text>'
            f'<text x="{x}" y="115" text-anchor="middle" fill="{color}" font-size="14">{label}</text>'
            f'<text x="{x}" y="138" text-anchor="middle" fill="#787c99" font-size="11">{sub}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="170" viewBox="0 0 495 170" font-family="Segoe UI, Ubuntu, sans-serif">
<rect width="495" height="170" rx="6" fill="#1a1b27" stroke="#6c5ce7" stroke-width="1.5"/>
{col(82, total, "Total Contributions", f"{fmt(first_day)} - Present", "#7aa2f7")}
<line x1="165" y1="45" x2="165" y2="130" stroke="#2a2b3d"/>
{col(247, cur[0], "Current Streak", f"{fmt(cur[1])} - {fmt(cur[2])}" if cur[0] else "Contribute today!", "#6c5ce7")}
<line x1="330" y1="45" x2="330" y2="130" stroke="#2a2b3d"/>
{col(412, longest[0], "Longest Streak", f"{fmt(longest[1])} - {fmt(longest[2])}", "#7aa2f7")}
</svg>"""


def main():
    u = gql(PROFILE_Q, {"login": USER})
    cc = u["contributionsCollection"]
    days = all_days(cc["contributionYears"])
    cur, longest = streaks(days)
    first_day = min((d for d, c in days.items() if c > 0), default=None)
    total = sum(days.values())

    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    commits = cc["totalCommitContributions"]
    prs, issues = u["pullRequests"]["totalCount"], u["issues"]["totalCount"]
    reviews = cc["totalPullRequestReviewContributions"]
    followers = u["followers"]["totalCount"]
    letter, pct = rank(commits, prs, issues, reviews, stars, followers)

    rows = [
        ("Total Stars Earned:", stars),
        ("Total Commits (last year):", commits),
        ("Total PRs:", prs),
        ("Total Issues:", issues),
        ("Followers:", followers),
    ]
    OUT.mkdir(exist_ok=True)
    (OUT / "stats.svg").write_text(stats_svg("Toka Nani", rows, letter, pct), encoding="utf-8")
    (OUT / "streak.svg").write_text(streak_svg(total, cur, longest, first_day), encoding="utf-8")
    print(f"stars={stars} commits={commits} rank={letter} current={cur[0]} longest={longest[0]} total={total}")


if __name__ == "__main__":
    main()
