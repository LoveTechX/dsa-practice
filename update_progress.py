import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

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
LATEST_PROBLEMS_COUNT = 10

TOPIC_DISPLAY = dict(TOPICS)
VALID_TOPIC_SLUGS = set(TOPIC_DISPLAY.keys())
VALID_DIFFICULTIES = set(DIFFICULTIES)

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
    """Run a git command and return stdout. Fail soft for local non-git contexts."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def discover_solution_files() -> list[Path]:
    files: list[Path] = []
    for topic_slug, _ in TOPICS:
        for difficulty in DIFFICULTIES:
            folder = Path(topic_slug) / difficulty
            if not folder.exists():
                continue
            for file in folder.iterdir():
                if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
                    files.append(file)
    return sorted(files)


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


def file_to_solution(path: Path) -> Solution:
    text = path.read_text(encoding="utf-8", errors="replace")
    metadata = parse_metadata(text)

    topic_from_path = path.parts[0] if len(path.parts) >= 1 else "arrays"
    difficulty_from_path = path.parts[1] if len(path.parts) >= 2 else "easy"

    topic_slug = normalize_topic(metadata.get("topic", ""), topic_from_path)
    difficulty = normalize_difficulty(metadata.get("difficulty", ""), difficulty_from_path)
    problem_name = metadata.get("problem") or path.stem.replace("_", " ").title()
    link = metadata.get("link", "")

    return Solution(
        problem=problem_name,
        link=link,
        topic_slug=topic_slug,
        topic_display=TOPIC_DISPLAY.get(topic_slug, topic_slug.title()),
        difficulty=difficulty,
        path=path.as_posix(),
    )


def get_solution_git_info(path: str) -> GitInfo:
    """Get first commit date/author for a file. Fallback to latest commit if needed."""
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


def build_progress_bar(total_solved: int, target: int, length: int = 20) -> tuple[str, int]:
    # Keep percentage readable for small progress values toward large targets.
    percent = 0 if target <= 0 else int((total_solved / target) * 100)
    if total_solved > 0 and percent == 0:
        percent = 1
    percent = max(0, min(100, percent))
    filled = round((percent / 100) * length)
    if total_solved > 0 and filled == 0:
        filled = 1
    bar = ("█" * filled) + ("-" * (length - filled))
    return bar, percent


def render_progress_md(solutions: list[Solution], git_info: dict[str, GitInfo]) -> str:
    total_solved = len(solutions)
    difficulty_counts = Counter(solution.difficulty for solution in solutions)
    topic_counts = Counter(solution.topic_slug for solution in solutions)
    bar, percent = build_progress_bar(total_solved, TARGET_PROBLEMS)

    lines: list[str] = [
        "# DSA Progress Dashboard",
        "",
        "This file is automatically generated by `update_progress.py`.",
        "",
        "## Overall",
        "",
        f"Total solved: {total_solved}",
        f"Progress: {bar} {percent}%",
        "",
        "## Difficulty Statistics",
        "",
        f"Easy: {difficulty_counts['easy']}",
        f"Medium: {difficulty_counts['medium']}",
        f"Hard: {difficulty_counts['hard']}",
        "",
        "## Topic Coverage",
        "",
    ]

    for topic_slug, topic_display in TOPICS:
        lines.append(f"{topic_display}: {topic_counts[topic_slug]}")

    lines.extend(["", "## Latest Solved Problems", ""])

    latest = sorted(
        solutions,
        key=lambda s: (git_info[s.path].date if s.path in git_info else "", s.problem.lower()),
        reverse=True,
    )[:LATEST_PROBLEMS_COUNT]

    if not latest:
        lines.append("No solved problems found.")
    else:
        for solution in latest:
            info = git_info.get(solution.path, GitInfo("Unknown Date", "Unknown Author"))
            item = (
                f"- {info.date}: [{solution.problem}]({solution.path}) "
                f"({solution.topic_display} - {solution.difficulty.title()})"
            )
            if solution.link:
                item += f" | [Problem Link]({solution.link})"
            lines.append(item)

    lines.extend(["", "## All Solved Problems", ""])

    if not solutions:
        lines.append("No solved problems found.")
    else:
        ordered = sorted(
            solutions,
            key=lambda s: (TOPIC_DISPLAY.get(s.topic_slug, s.topic_slug), s.difficulty, s.problem.lower()),
        )
        for solution in ordered:
            item = f"- [{solution.problem}]({solution.path}) ({solution.topic_display} - {solution.difficulty.title()})"
            if solution.link:
                item += f" | [Problem Link]({solution.link})"
            lines.append(item)

    return "\n".join(lines) + "\n"


def render_history_md(solutions: list[Solution], git_info: dict[str, GitInfo]) -> str:
    timeline: defaultdict[str, list[Solution]] = defaultdict(list)
    for solution in solutions:
        date = git_info.get(solution.path, GitInfo("Unknown Date", "Unknown Author")).date
        timeline[date].append(solution)

    lines: list[str] = [
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

    if len(lines) <= 4:
        lines.append("No solved problems found.")
        lines.append("")

    return "\n".join(lines)


def render_leaderboard_md(git_info: dict[str, GitInfo]) -> str:
    counter = Counter(info.author for info in git_info.values())
    lines: list[str] = [
        "# Leaderboard",
        "",
        "Contributor ranking based on number of solution files introduced.",
        "",
    ]

    if not counter:
        lines.append("No contributor data found.")
        lines.append("")
        return "\n".join(lines)

    for rank, (author, solved_count) in enumerate(counter.most_common(), start=1):
        lines.append(f"{rank}. {author} - {solved_count} problems")

    lines.append("")
    return "\n".join(lines)


def write_file(path: str, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")


def main() -> None:
    solution_files = discover_solution_files()
    solutions = [file_to_solution(path) for path in solution_files]
    git_info = {solution.path: get_solution_git_info(solution.path) for solution in solutions}

    write_file("progress.md", render_progress_md(solutions, git_info))
    write_file("history.md", render_history_md(solutions, git_info))
    write_file("leaderboard.md", render_leaderboard_md(git_info))

    print("Generated progress.md, history.md, and leaderboard.md")


if __name__ == "__main__":
    main()
