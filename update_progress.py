import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

TOPICS = [
    ("arrays", "Arrays"),
    ("strings", "Strings"),
    ("linked-list", "Linked List"),
    ("stack", "Stack"),
    ("queue", "Queue"),
    ("trees", "Trees"),
    ("graphs", "Graphs"),
    ("dynamic-programming", "Dynamic Programming"),
    ("recursion", "Recursion"),
]
DIFFICULTIES = ["easy", "medium", "hard"]
SUPPORTED_EXTENSIONS = {".cpp", ".py"}
TARGET_PROBLEMS = 300
PROGRESS_BAR_LENGTH = 20
LATEST_PROBLEMS_COUNT = 10

TOPIC_DISPLAY = dict(TOPICS)
VALID_TOPIC_SLUGS = set(TOPIC_DISPLAY.keys())
VALID_DIFFICULTIES = set(DIFFICULTIES)

README_START = "<!-- DSA_DASHBOARD:START -->"
README_END = "<!-- DSA_DASHBOARD:END -->"

METADATA_PATTERN = re.compile(
    r"^\s*(Problem|Link|Difficulty|Topic)\s*:\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class Solution:
    problem: str
    link: str
    topic_slug: str
    topic_display: str
    difficulty: str
    path: str


@dataclass
class GitInfo:
    date: str
    author: str


def run_git_command(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def parse_metadata(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for key, value in METADATA_PATTERN.findall(text):
        metadata[key.lower()] = value.strip()
    return metadata


def normalize_difficulty(value: str, fallback: str) -> str:
    candidate = value.strip().lower() if value else fallback.lower()
    return candidate if candidate in VALID_DIFFICULTIES else fallback.lower()


def normalize_topic(value: str, fallback: str) -> str:
    candidate = value.strip().lower().replace(" ", "-") if value else fallback
    if candidate in VALID_TOPIC_SLUGS:
        return candidate
    return fallback if fallback in VALID_TOPIC_SLUGS else "arrays"


def collect_solutions() -> list[Solution]:
    """Collect solved problems from topic/difficulty folders and parse metadata."""
    solutions: list[Solution] = []

    for topic_slug, _ in TOPICS:
        for difficulty in DIFFICULTIES:
            folder = Path(topic_slug) / difficulty
            if not folder.exists():
                continue

            for file in sorted(folder.iterdir()):
                if not file.is_file() or file.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue

                text = file.read_text(encoding="utf-8", errors="replace")
                metadata = parse_metadata(text)
                path_parts = file.parts

                topic_from_path = path_parts[0] if len(path_parts) >= 1 else topic_slug
                difficulty_from_path = path_parts[1] if len(path_parts) >= 2 else difficulty

                normalized_topic = normalize_topic(metadata.get("topic", ""), topic_from_path)
                normalized_difficulty = normalize_difficulty(metadata.get("difficulty", ""), difficulty_from_path)

                solutions.append(
                    Solution(
                        problem=metadata.get("problem") or file.stem.replace("_", " ").title(),
                        link=metadata.get("link", ""),
                        topic_slug=normalized_topic,
                        topic_display=TOPIC_DISPLAY.get(normalized_topic, normalized_topic.title()),
                        difficulty=normalized_difficulty,
                        path=file.as_posix(),
                    )
                )

    return solutions


def get_solution_git_info(path: str) -> GitInfo:
    # Use the first-add commit to represent when a problem was solved.
    created = run_git_command(
        ["log", "--follow", "--diff-filter=A", "--reverse", "--format=%ad|%an", "--date=short", "--", path]
    )
    line = created.splitlines()[0] if created else ""
    if not line:
        latest = run_git_command(["log", "-1", "--format=%ad|%an", "--date=short", "--", path])
        line = latest.splitlines()[0] if latest else ""

    if "|" in line:
        date, author = line.split("|", 1)
        return GitInfo(date=date.strip(), author=author.strip())
    return GitInfo(date="Unknown Date", author="Unknown Author")


def build_progress_bar(total_solved: int, target: int, length: int = PROGRESS_BAR_LENGTH) -> tuple[str, int]:
    percent = 0 if target <= 0 else int((total_solved / target) * 100)
    if total_solved > 0 and percent == 0:
        percent = 1
    percent = max(0, min(100, percent))
    filled = round((percent / 100) * length)
    if total_solved > 0 and filled == 0:
        filled = 1
    bar = ("█" * filled) + ("-" * (length - filled))
    return bar, percent


def compute_statistics(solutions: list[Solution]) -> dict:
    """Compute analytics payload for markdown/json outputs."""
    total_solved = len(solutions)
    difficulty_counter = Counter(solution.difficulty for solution in solutions)
    topic_counter = Counter(solution.topic_slug for solution in solutions)
    progress_bar, progress_percent = build_progress_bar(total_solved, TARGET_PROBLEMS)

    return {
        "target": TARGET_PROBLEMS,
        "total_solved": total_solved,
        "progress_percentage": progress_percent,
        "progress_bar": progress_bar,
        "difficulty": {
            "easy": difficulty_counter["easy"],
            "medium": difficulty_counter["medium"],
            "hard": difficulty_counter["hard"],
        },
        "topics": {topic_slug: topic_counter[topic_slug] for topic_slug, _ in TOPICS},
    }


def badge(label: str, value: str, color: str) -> str:
    return f"https://img.shields.io/badge/{quote(label)}-{quote(value)}-{quote(color)}"


def render_progress_md(solutions: list[Solution], git_info: dict[str, GitInfo], stats: dict) -> str:
    lines: list[str] = [
        "# DSA Progress Dashboard",
        "",
        "This file is automatically generated by `update_progress.py`.",
        "",
        "## Overall",
        "",
        f"Total solved: {stats['total_solved']}",
        f"Progress: {stats['progress_bar']} {stats['progress_percentage']}%",
        "",
        "## Difficulty Statistics",
        "",
        f"Easy: {stats['difficulty']['easy']}",
        f"Medium: {stats['difficulty']['medium']}",
        f"Hard: {stats['difficulty']['hard']}",
        "",
        "## Topic Coverage",
        "",
    ]

    for topic_slug, topic_name in TOPICS:
        lines.append(f"{topic_name}: {stats['topics'][topic_slug]}")

    lines.extend(["", "## Latest Solved Problems", ""])

    latest = sorted(
        solutions,
        key=lambda s: (git_info.get(s.path, GitInfo("Unknown Date", "Unknown Author")).date, s.problem.lower()),
        reverse=True,
    )[:LATEST_PROBLEMS_COUNT]

    if not latest:
        lines.append("No solved problems found.")
    else:
        for solution in latest:
            info = git_info.get(solution.path, GitInfo("Unknown Date", "Unknown Author"))
            line = (
                f"- {info.date}: [{solution.problem}]({solution.path}) "
                f"({solution.topic_display} - {solution.difficulty.title()})"
            )
            if solution.link:
                line += f" | [Problem Link]({solution.link})"
            lines.append(line)

    lines.extend(["", "## All Solved Problems", ""])

    if not solutions:
        lines.append("No solved problems found.")
    else:
        ordered = sorted(
            solutions,
            key=lambda s: (TOPIC_DISPLAY.get(s.topic_slug, s.topic_slug), s.difficulty, s.problem.lower()),
        )
        for solution in ordered:
            line = f"- [{solution.problem}]({solution.path}) ({solution.topic_display} - {solution.difficulty.title()})"
            if solution.link:
                line += f" | [Problem Link]({solution.link})"
            lines.append(line)

    return "\n".join(lines) + "\n"


def render_history_md(solutions: list[Solution], git_info: dict[str, GitInfo]) -> str:
    timeline: defaultdict[str, list[Solution]] = defaultdict(list)
    for solution in solutions:
        timeline[git_info.get(solution.path, GitInfo("Unknown Date", "Unknown Author")).date].append(solution)

    lines = [
        "# Problem History Timeline",
        "",
        "Chronological timeline generated from git commit history.",
        "",
    ]

    for date in sorted(timeline.keys()):
        lines.append(f"## {date}")
        lines.append("")
        entries = sorted(timeline[date], key=lambda s: s.problem.lower())
        for solution in entries:
            lines.append(f"- {solution.problem} ({solution.topic_display} - {solution.difficulty.title()})")
        lines.append("")

    if len(timeline) == 0:
        lines.append("No solved problems found.")
        lines.append("")

    return "\n".join(lines)


def render_leaderboard_md(git_info: dict[str, GitInfo]) -> str:
    contributors = Counter(info.author for info in git_info.values())
    lines = [
        "# Leaderboard",
        "",
        "Contributor ranking based on number of solution files introduced.",
        "",
    ]

    if not contributors:
        lines.append("No contributor data found.")
        lines.append("")
        return "\n".join(lines)

    for rank, (author, solved) in enumerate(contributors.most_common(), start=1):
        lines.append(f"{rank}. {author} - {solved} problems")

    lines.append("")
    return "\n".join(lines)


def render_readme_dashboard(stats: dict) -> str:
    solved = stats["total_solved"]
    easy = stats["difficulty"]["easy"]
    medium = stats["difficulty"]["medium"]
    hard = stats["difficulty"]["hard"]
    progress = f"{stats['progress_percentage']}%"

    lines = [
        "## DSA Dashboard",
        "",
        f"![Solved]({badge('Solved', str(solved), '0A66C2')})",
        f"![Easy]({badge('Easy', str(easy), '2EA44F')})",
        f"![Medium]({badge('Medium', str(medium), 'FB8C00')})",
        f"![Hard]({badge('Hard', str(hard), 'D73A49')})",
        f"![Progress]({badge('Progress', progress, '6F42C1')})",
        "",
        f"- Total solved: {solved}",
        (
            f"- Difficulty: Easy {easy} | Medium {medium} | Hard {hard}"
        ),
        (
            f"- Progress: {stats['progress_bar']} {stats['progress_percentage']}% "
            f"(target: {stats['target']})"
        ),
        "",
        "### Topic Coverage",
        "",
    ]

    for topic_slug, topic_name in TOPICS:
        lines.append(f"- {topic_name}: {stats['topics'][topic_slug]}")

    lines.extend(
        [
            "",
            "### Analytics Files",
            "",
            "- [Progress Dashboard](./progress.md)",
            "- [Problem History Timeline](./history.md)",
            "- [Contributor Leaderboard](./leaderboard.md)",
            "- [Raw Statistics](./stats.json)",
        ]
    )

    return "\n".join(lines)


def update_readme_dashboard(stats: dict) -> None:
    readme_path = Path("README.md")
    if not readme_path.exists():
        return

    text = readme_path.read_text(encoding="utf-8")
    section = f"{README_START}\n{render_readme_dashboard(stats)}\n{README_END}"

    if README_START in text and README_END in text:
        pattern = re.compile(f"{re.escape(README_START)}.*?{re.escape(README_END)}", re.DOTALL)
        text = pattern.sub(section, text, count=1)
    else:
        text = text.rstrip() + "\n\n" + section + "\n"

    readme_path.write_text(text, encoding="utf-8")


def generate_dashboard(solutions: list[Solution], stats: dict, git_info: dict[str, GitInfo]) -> dict[str, str]:
    """Generate all markdown/json artifacts for the analytics portfolio."""
    return {
        "progress.md": render_progress_md(solutions, git_info, stats),
        "history.md": render_history_md(solutions, git_info),
        "leaderboard.md": render_leaderboard_md(git_info),
        "stats.json": json.dumps(stats, indent=2) + "\n",
    }


def write_outputs(outputs: dict[str, str]) -> None:
    for path, content in outputs.items():
        Path(path).write_text(content, encoding="utf-8")


def main() -> None:
    solutions = collect_solutions()
    stats = compute_statistics(solutions)
    git_info = {solution.path: get_solution_git_info(solution.path) for solution in solutions}

    outputs = generate_dashboard(solutions, stats, git_info)
    write_outputs(outputs)
    update_readme_dashboard(stats)

    print("Generated progress.md, history.md, leaderboard.md, stats.json, and README dashboard")


if __name__ == "__main__":
    main()
