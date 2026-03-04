# DSA Practice Repository

A structured Data Structures and Algorithms (DSA) practice repository with automated progress reporting.

<!-- DSA_DASHBOARD:START -->
## DSA Dashboard

![Solved](https://img.shields.io/badge/Solved-1-0A66C2)
![Easy](https://img.shields.io/badge/Easy-1-2EA44F)
![Medium](https://img.shields.io/badge/Medium-0-FB8C00)
![Hard](https://img.shields.io/badge/Hard-0-D73A49)
![Progress](https://img.shields.io/badge/Progress-1%25-6F42C1)

- Total solved: 1
- Difficulty: Easy 1 | Medium 0 | Hard 0
- Progress: █------------------- 1% (target: 300)

### Topic Coverage

- Arrays: 1
- Strings: 0
- Linked List: 0
- Stack: 0
- Queue: 0
- Trees: 0
- Graphs: 0
- Dynamic Programming: 0
- Recursion: 0

### Analytics Files

- [Progress Dashboard](./progress.md)
- [Problem History Timeline](./history.md)
- [Contributor Leaderboard](./leaderboard.md)
- [Raw Statistics](./stats.json)
<!-- DSA_DASHBOARD:END -->

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
├── stats.json
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
