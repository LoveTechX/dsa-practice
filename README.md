# DSA Practice Repository

A structured Data Structures and Algorithms (DSA) practice repository with automated progress reporting.

## DSA Dashboard

This repository includes an automated dashboard generated from solution files and git history.

- Total Problems Solved: tracked in `progress.md`
- Difficulty Statistics: Easy / Medium / Hard counts
- Topic Coverage: Arrays, Strings, Linked List, Stack, Queue, Trees, Graphs, Dynamic Programming, Recursion
- Progress Bar: target-based visual progress toward 300 solved problems

Generated dashboard files:

- [Progress Dashboard](./progress.md)
- [Problem History Timeline](./history.md)
- [Contributor Leaderboard](./leaderboard.md)

## Project Overview

This project is used to:

- Practice core DSA topics consistently.
- Organize solutions by topic and difficulty.
- Track progress automatically without manual updates.
- Build interview-ready problem-solving patterns over time.

Solutions are grouped into topic folders (`arrays`, `graphs`, `trees`, etc.) and then by difficulty (`easy`, `medium`, `hard`).

## Automation

The repository includes GitHub Actions automation to keep dashboard files updated:

- Workflow file: `.github/workflows/update_progress.yml`
- Script used: `update_progress.py`
- Trigger: push events on `main`

Workflow behavior:

1. Checks out the repository.
2. Sets up Python 3.
3. Runs `python update_progress.py`.
4. Commits and pushes generated dashboard files if they changed.

You can also run the same process locally:

```bash
python update_progress.py
```

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── update_progress.yml
├── arrays/
│   ├── easy/
│   ├── medium/
│   └── hard/
├── dynamic-programming/
├── graphs/
├── linked-list/
├── queue/
├── recursion/
├── stack/
├── strings/
├── trees/
├── history.md
├── leaderboard.md
├── progress.md
├── update_progress.py
└── README.md
```

Notes:

- Each topic folder follows the same `easy/medium/hard` layout.
- Solution files are currently detected with `.cpp` and `.py` extensions.

## Progress Tracker

`progress.md` is generated automatically and includes:

- Total solved problems.
- Easy / Medium / Hard counts.
- Topic coverage statistics.
- Latest solved problems.
- A progress bar targeting 300 problems.

How analytics are generated:

- The script scans topic/difficulty directories and detects `.cpp` and `.py` solutions.
- Metadata is parsed from solution files:
  - `Problem:`
  - `Link:`
  - `Difficulty:`
  - `Topic:`
- If metadata is missing, values are inferred from file name and folder structure.
- Git history is used to generate:
  - chronological timeline in `history.md`
  - contributor ranking in `leaderboard.md`
