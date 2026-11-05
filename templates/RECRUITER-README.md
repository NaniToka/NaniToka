# Recruiter-first README template for pinned repos

> Copy everything below the line into a project's `README.md`. Fill every `{{...}}`.
> Delete sections you can't back with code in the repo — an unverifiable claim is worse than no claim.
> Reference implementation: github.com/NaniToka/TokenFlow-AI

---

# {{Project Name}}

> **One line a recruiter repeats to the hiring manager:** {{what it does + the number that matters}}.

[![CI](https://github.com/{{owner}}/{{repo}}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{owner}}/{{repo}}/actions)
[![Coverage](https://img.shields.io/badge/Coverage-{{n}}%25-brightgreen.svg)](#)
![{{Lang}}](https://img.shields.io/badge/{{Lang}}-{{color}}?logo={{lang}}) `…one badge per core tech`

## 🎬 Demo

<!-- Drop a 30–60s screen recording into the GitHub issue/composer, paste the hosted URL here. -->
![Demo]({{video-or-gif-url}})

> No video? Give a **one-command reproduction** instead, like TokenFlow's `python benchmarks/run.py`.

## ⚡ The Problem

{{2–3 sentences: who suffers, what it costs them, why existing tools don't solve it. Quantify if possible.}}

## 📊 Measured Result

| Metric | Result |
| :--- | :--- |
| {{primary metric}} | {{number}} |
| {{quality/safety guard}} | {{number}} |

> **Conditions**: sample size, baseline, method, how to reproduce. Honesty about a small sample *builds* credibility.

## 📐 Architecture

```mermaid
graph TD
    {{one diagram: data in → core engines → output}}
```

## 🛠️ Key Design Decisions

1. **{{decision}}** — *Why:* {{reason}} · *Trade-off:* {{what you gave up}}

{{2–4 decisions. This section is what senior interviewers actually read.}}

## 🚀 Quickstart

```bash
{{clone + one command to run (docker compose up -d is ideal)}}
{{curl line proving it works}}
```

## 🧪 Verify It Yourself

```bash
{{test command}}
{{benchmark/repro command}}
```

## 📖 Docs & Links

[Live product]({{url or omit}}) · [API docs]({{url}}) · [Engineering notes]({{path}}) · [Contributing](CONTRIBUTING.md)

## ⚠️ Known Limitations

{{2–3 honest limitations. This section separates builders from tutorial-followers.}}

## 🗺️ Roadmap

{{3 unchecked items — shows the project is alive.}}
