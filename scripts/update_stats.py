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


def fmt_short(day):
    return day.strftime("%b %d, '%y") if day else "No active streak"


def streak_svg(total, current, longest):
    curr_range = f"{fmt_short(current[1])} — {fmt_short(current[2])}" if current[0] else "No active streak"
    long_range = f"{fmt_short(longest[1])} — {fmt_short(longest[2])}" if longest[0] else "No streak recorded"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="860" height="260" viewBox="0 0 860 260" role="img" aria-label="Contribution Streak">
  <defs>
    <linearGradient id="streak-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="54%" stop-color="#161b22"/>
      <stop offset="100%" stop-color="#0d1117"/>
    </linearGradient>
    <radialGradient id="streak-orb-0" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#58a6ff" stop-opacity="0.72"/>
      <stop offset="58%" stop-color="#58a6ff" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#58a6ff" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="streak-orb-1" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#39d353" stop-opacity="0.5"/>
      <stop offset="58%" stop-color="#39d353" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#39d353" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="streak-orb-2" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#a371f7" stop-opacity="0.72"/>
      <stop offset="58%" stop-color="#a371f7" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#a371f7" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="streak-orb-3" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.5"/>
      <stop offset="58%" stop-color="#22d3ee" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="streak-ring-grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#58a6ff"/>
      <stop offset="55%" stop-color="#a371f7"/>
      <stop offset="100%" stop-color="#2ad5ef"/>
    </linearGradient>
  </defs>
  <style>
    #gs-streak .orb-a {{ animation: s-float-a 9s ease-in-out infinite; }}
    #gs-streak .orb-b {{ animation: s-float-b 11s ease-in-out infinite 1.1s; }}
    #gs-streak .orb-c {{ animation: s-float-c 13s ease-in-out infinite 0.6s; }}
    #gs-streak .ring-p {{ animation: s-ring 8s ease-in-out infinite; }}
    #gs-streak .bar-a {{ animation: s-bar 1.15s ease-out both; transform-box: fill-box; transform-origin: left; }}
    @keyframes s-float-a {{ 0%,100% {{ transform: translate(0,0); opacity: .58; }} 50% {{ transform: translate(28px,-20px); opacity: .86; }} }}
    @keyframes s-float-b {{ 0%,100% {{ transform: translate(0,0); opacity: .42; }} 50% {{ transform: translate(-24px,18px); opacity: .72; }} }}
    @keyframes s-float-c {{ 0%,100% {{ transform: translate(0,0) scale(1); opacity: .34; }} 50% {{ transform: translate(18px,-12px) scale(1.18); opacity: .62; }} }}
    @keyframes s-ring {{ 0%,100% {{ opacity: .06; }} 50% {{ opacity: .22; }} }}
    @keyframes s-bar {{ from {{ opacity: 0.4; }} to {{ opacity: 0.95; }} }}
  </style>
  <g id="gs-streak" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
    <rect width="860" height="260" rx="20" fill="url(#streak-bg)"/>
    <ellipse class="orb-a" cx="138" cy="47" rx="206" ry="120" fill="url(#streak-orb-0)"/>
    <ellipse class="orb-b" cx="654" cy="57" rx="241" ry="109" fill="url(#streak-orb-1)"/>
    <ellipse class="orb-c" cx="499" cy="229" rx="310" ry="88" fill="url(#streak-orb-2)"/>
    <ellipse class="orb-b" cx="826" cy="203" rx="172" ry="109" fill="url(#streak-orb-3)"/>

    <circle class="ring-p" cx="760" cy="60" r="18" fill="none" stroke="#e6edf3" stroke-opacity="0.34"/>
    <circle class="ring-p" cx="760" cy="60" r="32" fill="none" stroke="#e6edf3" stroke-opacity="0.20"/>
    <circle cx="792" cy="60" r="3.5" fill="#58a6ff"/>

    <rect x="28" y="26" width="804" height="206" rx="20" fill="rgba(8,8,12,0.5)" stroke="#58a6ff" stroke-opacity="0.48"/>
    <text x="46" y="61" font-size="28" font-weight="850" letter-spacing="-0.5" fill="#e6edf3">Contribution Streak</text>
    <text x="48" y="84" font-size="13" font-weight="650" letter-spacing="1.0" fill="#8b949e">Public rolling calendar · verified consistency</text>

    <rect x="42" y="96" width="248" height="120" rx="18" fill="rgba(8,8,12,0.5)" stroke="#58a6ff" stroke-opacity="0.72"/>
    <text x="64" y="126" font-size="12" font-weight="800" letter-spacing="1.2" fill="#8b949e">Total Contributions</text>
    <text x="64" y="166" font-size="34" font-weight="900" letter-spacing="-0.8" fill="#58a6ff">{total:,}</text>
    <text x="64" y="186" font-size="11" font-weight="600" fill="#8b949e">Rolling 12 months</text>
    <rect x="64" y="198" width="204" height="6" rx="3" fill="rgba(255,255,255,0.1)"/>
    <rect class="bar-a" x="64" y="198" width="168" height="6" rx="3" fill="#58a6ff" opacity="0.9"/>

    <rect x="306" y="96" width="248" height="120" rx="18" fill="rgba(8,8,12,0.5)" stroke="#a371f7" stroke-opacity="0.78"/>
    <circle cx="430" cy="138" r="26" fill="none" stroke="url(#streak-ring-grad)" stroke-width="4.5"/>
    <circle cx="430" cy="111" r="7" fill="#0d1117"/>
    <path d="M430 103 c2.4 3.4 4.8 5.8 4.8 8.5 a4.8 4.8 0 0 1 -9.6 0 c0-2.7 2.4-5.1 4.8-8.5z" fill="#a371f7"/>
    <text x="430" y="147" text-anchor="middle" font-size="25" font-weight="900" fill="#e6edf3">{current[0]}</text>
    <text x="430" y="183" text-anchor="middle" font-size="12" font-weight="800" letter-spacing="1.0" fill="#a371f7">Current Streak</text>
    <text x="430" y="201" text-anchor="middle" font-size="11" font-weight="600" fill="#8b949e">{html.escape(curr_range)}</text>

    <rect x="570" y="96" width="248" height="120" rx="18" fill="rgba(8,8,12,0.5)" stroke="#58a6ff" stroke-opacity="0.72"/>
    <text x="592" y="126" font-size="12" font-weight="800" letter-spacing="1.2" fill="#8b949e">Longest Streak</text>
    <text x="592" y="166" font-size="34" font-weight="900" letter-spacing="-0.8" fill="#2ad5ef">{longest[0]}</text>
    <text x="592" y="186" font-size="11" font-weight="600" fill="#8b949e">{html.escape(long_range)}</text>
    <rect x="592" y="198" width="204" height="6" rx="3" fill="rgba(255,255,255,0.1)"/>
    <rect class="bar-a" x="592" y="198" width="142" height="6" rx="3" fill="#2ad5ef" opacity="0.9"/>

    <rect x="0.5" y="0.5" width="859" height="259" rx="19.5" fill="none" stroke="#58a6ff" stroke-opacity="0.62"/>
  </g>
</svg>"""


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
