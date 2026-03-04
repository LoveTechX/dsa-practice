import os

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

output = "# DSA Progress Tracker\n\n"

for topic in topics:
    output += f"## {topic.capitalize()}\n"

    if os.path.exists(topic):
        files = os.listdir(topic)

        for file in files:
            if file.endswith(".cpp") or file.endswith(".py"):
                name = file.replace("_", " ").replace(".cpp","").replace(".py","").title()
                path = f"{topic}/{file}"
                output += f"- [x] [{name}]({path})\n"

    output += "\n"

with open("progress.md", "w") as f:
    f.write(output)

print("Progress updated!")
