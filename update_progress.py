import os
import re

topics = [
    "arrays",
    "strings",
    "linked-list",
    "stack",
    "queue",
    "trees",
    "graphs",
    "dynamic-programming",
    "recursion"
]

difficulties = ["easy", "medium", "hard"]

total_solved = 0
content = "# 📚 DSA Progress Tracker\n\n"
content += "This file is **automatically generated** from solved problems.\n\n"

content += "## 📊 Overall Progress\n\n"

solutions = []

for topic in topics:
    for diff in difficulties:
        path = os.path.join(topic, diff)

        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith(".cpp") or file.endswith(".py"):

                    filepath = os.path.join(path, file)
                    total_solved += 1

                    name = file.replace("_", " ").replace(".cpp", "").replace(".py", "").title()

                    problem_link = ""

                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            text = f.read()

                            match = re.search(r"https?://[^\s]+", text)
                            if match:
                                problem_link = match.group(0)

                    except:
                        pass

                    solutions.append((topic, diff, name, filepath, problem_link))

# Progress bar
bar_length = 20
filled = min(total_solved, bar_length)
progress_bar = "█" * filled + "░" * (bar_length - filled)

content += f"**Problems Solved:** {total_solved}\n\n"
content += f"Progress: {progress_bar}\n\n"

content += "---\n\n"

content += "## 📂 Solved Problems\n\n"

for topic, diff, name, path, link in solutions:

    if link:
        content += f"- [x] [{name}]({path}) ({diff}) | [Problem Link]({link})\n"
    else:
        content += f"- [x] [{name}]({path}) ({diff})\n"

content += "\n"

with open("progress.md", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ progress.md updated successfully")