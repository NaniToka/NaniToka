#!/usr/bin/env python3
"""Generate profile cards from GitHub's public API and contribution calendar."""

import html
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

USER = "NaniToka"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
TODAY = datetime.now(timezone.utc).date()
TOKENS = list(dict.fromkeys(t for t in (os.environ.get("STATS_TOKEN"), os.environ.get("GITHUB_TOKEN")) if t))
PALETTE = ["#A78BFA", "#A3E635", "#FBBF24", "#F472B6", "#2DD4BF", "#FB7185"]
BG = "#0B1120"
CARD = "#111A2C"
BORDER = "#2B3548"
TEXT = "#E2E8F0"
MUTED = "#94A3B8"
DAY_PATTERN = re.compile(
    r'<td\b[^>]*data-date="(?P<day>\d{4}-\d{2}-\d{2})"[^>]*data-level="(?P<level>\d)"[^>]*>\s*</td>'
    r'\s*<tool-tip\b[^>]*>(?P<label>[^<]+)</tool-tip>',
    re.S,
)


def fetch(url, api=False):
    attempts = TOKENS + [None] if api else [None]
    errors = []
    for token in attempts:
        command = [
            "curl", "-L", "-sS", "--fail", "--max-time", "45",
            "-H", "User-Agent: NaniToka-profile-stats", url,
        ]
        if api:
            command[1:1] = ["-H", "Accept: application/vnd.github+json"]
        if token:
            command[1:1] = ["-H", f"Authorization: Bearer {token}"]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        errors.append(result.stderr.strip())
    raise RuntimeError(f"Unable to fetch {url}: {'; '.join(errors)}")


def fetch_json(url):
    return json.loads(fetch(url, api=True))


def contribution_data():
    source = fetch(f"https://github.com/users/{USER}/contributions")
    plain = html.unescape(re.sub(r"<[^>]+>", " ", source))
    plain = re.sub(r"\s+", " ", plain)
    total_match = re.search(r"([\d,]+) contributions in the last year", plain)
    if not total_match:
        raise RuntimeError("GitHub contribution total was not found")
    total = int(total_match.group(1).replace(",", ""))

    days = {}
    for match in DAY_PATTERN.finditer(source):
        day = datetime.strptime(match.group("day"), "%Y-%m-%d").date()
        if day > TODAY:
            continue
        label = match.group("label")
        if label.startswith("No contributions"):
            count = 0
        else:
            count_match = re.match(r"([\d,]+) contributions? on", label)
            if not count_match:
                raise RuntimeError(f"Unexpected contribution label: {label}")
            count = int(count_match.group(1).replace(",", ""))
        days[day] = count

    if not days or sum(days.values()) != total:
        raise RuntimeError(
            f"Contribution calendar mismatch: header={total}, days={sum(days.values())}"
        )
    return total, days


def streaks(days):
    longest = (0, None, None)
    run = 0
    start = None
    for day in sorted(days):
        if days[day] > 0:
            if run == 0:
                start = day
            run += 1
            if run > longest[0]:
                longest = (run, start, day)
        else:
            run = 0

    cursor = TODAY if days.get(TODAY, 0) > 0 else TODAY - timedelta(days=1)
    end = cursor
    current = 0
    while days.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    current_start = end - timedelta(days=current - 1) if current else None
    return (current, current_start, end if current else None), longest


def fmt(day):
    return day.strftime("%b %d, %Y") if day else "No active streak"


def svg_shell(width, height, title, subtitle, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}. {html.escape(subtitle)}">
<rect width="{width}" height="{height}" rx="18" fill="{BG}" stroke="{BORDER}"/>
<rect x="1" y="1" width="{width - 2}" height="3" rx="1.5" fill="url(#accent)"/>
<defs><linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#A78BFA"/><stop offset="0.34" stop-color="#F472B6"/><stop offset="0.67" stop-color="#FBBF24"/><stop offset="1" stop-color="#A3E635"/><animateTransform attributeName="gradientTransform" type="translate" values="-0.6 0; 0.6 0; -0.6 0" dur="8s" repeatCount="indefinite"/></linearGradient>
<linearGradient id="tileStroke" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#A78BFA" stop-opacity="0.5"/><stop offset="1" stop-color="#A3E635" stop-opacity="0.5"/></linearGradient>
<filter id="tileShadow" x="-30%" y="-30%" width="160%" height="180%"><feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#000000" flood-opacity="0.5"/></filter>
</defs>
<g font-family="Inter, Segoe UI, Helvetica, Arial, sans-serif">
<text x="28" y="35" fill="{TEXT}" font-size="14" font-weight="700" letter-spacing="1.7">{html.escape(title)}</text>
<text x="932" y="35" text-anchor="end" fill="{MUTED}" font-size="11" letter-spacing="0.8">{html.escape(subtitle)}</text>
{body}
</g>
</svg>"""


def tile(x, y, width, height, value, label, detail, color):
    begin = f"{(x - 28) / 300 * 1.2:.2f}s"
    return f"""<g filter="url(#tileShadow)">
<animateTransform attributeName="transform" type="translate" values="0 0; 0 -4; 0 0" dur="5s" begin="{begin}" repeatCount="indefinite"/>
<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="13" fill="{CARD}" stroke="url(#tileStroke)"/>
<rect x="{x}" y="{y}" width="4" height="{height}" rx="2" fill="{color}">
<animate attributeName="opacity" values="1;0.45;1" dur="3s" begin="{begin}" repeatCount="indefinite"/>
</rect>
<text x="{x + 22}" y="{y + 52}" fill="{color}" font-size="38" font-weight="800" letter-spacing="-1">{value}</text>
<text x="{x + 22}" y="{y + 80}" fill="{TEXT}" font-size="11" font-weight="700" letter-spacing="0.8">{html.escape(label)}</text>
<text x="{x + 22}" y="{y + 100}" fill="{MUTED}" font-size="11">{html.escape(detail)}</text>
</g>"""


def github_rank(stars, pull_requests, contributions):
    score = stars * 10 + pull_requests * 50 + contributions * 0.5
    for threshold, grade in (
        (6000, "A++"), (4000, "A+"), (2500, "A"), (1500, "A-"),
        (800, "B+"), (400, "B"),
    ):
        if score >= threshold:
            return grade, score
    return "B-", score


def stats_svg(public_repos, stars, pull_requests, contributions):
    grade, score = github_rank(stars, pull_requests, contributions)
    body = "".join([
        tile(28, 58, 222, 120, public_repos, "PUBLIC REPOSITORIES", "Across this GitHub account", PALETTE[0]),
        tile(262, 58, 222, 120, stars, "STARS RECEIVED", "Owned public, non-fork repositories", PALETTE[2]),
        tile(496, 58, 222, 120, pull_requests, "PUBLIC PULL REQUESTS", "Authored across GitHub", PALETTE[3]),
        tile(730, 58, 222, 120, grade, f"GITHUB RANK · SCORE {score:,.0f}", "STARSx10 + PRSx50 + CONTRIBx0.5", PALETTE[1]),
    ])
    return svg_shell(960, 200, "PUBLIC GITHUB", f"VERIFIED {TODAY.strftime('%b %d, %Y').upper()}", body)


def streak_svg(total, current, longest):
    body = "".join([
        tile(28, 58, 290, 120, total, "CONTRIBUTIONS · 12 MONTHS", "GitHub rolling-year total", PALETTE[1]),
        tile(335, 58, 290, 120, current[0], "CURRENT STREAK", f"{fmt(current[1])} — {fmt(current[2])}", PALETTE[4]),
        tile(642, 58, 290, 120, longest[0], "LONGEST STREAK · 12 MONTHS", f"{fmt(longest[1])} — {fmt(longest[2])}", PALETTE[5]),
    ])
    return svg_shell(960, 200, "CONTRIBUTION ACTIVITY", "PUBLIC ROLLING CALENDAR", body)


def languages_svg(languages, repo_count):
    total = sum(languages.values())
    if total <= 0:
        raise RuntimeError("No language bytes were returned")
    ranked = sorted(languages.items(), key=lambda item: item[1], reverse=True)
    visible = ranked[:5]
    if len(ranked) > 5:
        visible.append(("Other", sum(size for _, size in ranked[5:])))

    segments = []
    legends = []
    cursor = 28.0
    bar_width = 904.0
    for index, (name, size) in enumerate(visible):
        color = PALETTE[index % len(PALETTE)]
        width = bar_width * size / total
        if index == len(visible) - 1:
            width = 932.0 - cursor
        segments.append(
            f'<rect x="{cursor:.2f}" y="62" width="{width:.2f}" height="22" fill="{color}"/>'
        )
        column = index % 3
        row = index // 3
        x = 28 + column * 307
        y = 119 + row * 40
        percent = size * 100 / total
        legends.append(f"""<circle cx="{x + 6}" cy="{y - 5}" r="5" fill="{color}"/>
<text x="{x + 20}" y="{y}" fill="{TEXT}" font-size="13" font-weight="600">{html.escape(name)}</text>
<text x="{x + 270}" y="{y}" text-anchor="end" fill="{color}" font-size="13" font-weight="700">{percent:.1f}%</text>""")
        cursor += width

    body = f"""<g>{''.join(segments)}</g>
{''.join(legends)}
<text x="28" y="194" fill="{MUTED}" font-size="11">Code bytes across {repo_count} owned public, non-fork repositories</text>"""
    return svg_shell(960, 214, "TOP LANGUAGES", "BY CODE BYTES · NOT REPOSITORY COUNT", body)


def main():
    profile = fetch_json(f"https://api.github.com/users/{USER}")
    repos = fetch_json(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&sort=updated")
    owned = [repo for repo in repos if not repo["fork"]]
    pull_requests = fetch_json(
        f"https://api.github.com/search/issues?q=author%3A{USER}%20type%3Apr"
    )["total_count"]
    stars = sum(repo["stargazers_count"] for repo in owned)

    languages = {}
    for repo in owned:
        for name, size in fetch_json(repo["languages_url"]).items():
            languages[name] = languages.get(name, 0) + size

    total, days = contribution_data()
    current, longest = streaks(days)

    OUT.mkdir(exist_ok=True)
    (OUT / "stats.svg").write_text(
        stats_svg(profile["public_repos"], stars, pull_requests, total), encoding="utf-8"
    )
    (OUT / "streak.svg").write_text(
        streak_svg(total, current, longest), encoding="utf-8"
    )
    (OUT / "languages.svg").write_text(
        languages_svg(languages, len(owned)), encoding="utf-8"
    )
    print(
        f"OK repos={profile['public_repos']} stars={stars} prs={pull_requests} "
        f"contributions={total} current={current[0]} longest={longest[0]} "
        f"languages={len(languages)}"
    )


if __name__ == "__main__":
    main()
