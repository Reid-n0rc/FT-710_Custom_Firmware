#!/usr/bin/env python3
"""docs-check: the mechanical part of the documentation standard (docs/documentation-standard.md).

Usage: python3 -I tools/check_docs.py [--base REF]

Checks, and exits 1 with a message per problem:
1. With --base REF (in CI: the pull request's base commit): if any file outside docs/ changed between REF and HEAD, something in
   docs/ changed too. Changes only to the upstream/ pin are exempt (upstream-sync pull requests).
2. Every docs/projects/*.md page has the required "## " sections, in order.
3. Every relative Markdown link in *.md files (outside upstream/) points to an existing file.
It only reads files and runs `git diff --name-only`; it never changes anything.
"""
import os
import re
import subprocess
import sys

REQUIRED = ["Summary", "Status", "Background", "Design", "Delivery and the way back", "Risks", "Plan", "Test log", "Decisions",
            "Open questions"]


def changed_files(base):
    out = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if f]


def check_docs_travel(base, problems):
    files = changed_files(base)
    outside = [f for f in files if not f.startswith("docs/") and f != "upstream"]
    if outside and not any(f.startswith("docs/") for f in files):
        problems.append("files outside docs/ changed but nothing in docs/ did: " + ", ".join(outside[:10]))


def check_project_pages(problems):
    d = "docs/projects"
    for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not name.endswith(".md") or name == "README.md":
            continue
        heads = [m.group(1).strip() for m in re.finditer(r"^## (.+)$", open(os.path.join(d, name), encoding="utf-8").read(), re.M)]
        it = iter(heads)
        missing = [r for r in REQUIRED if r not in it]
        if missing:
            problems.append(f"{d}/{name}: missing or out-of-order sections: " + ", ".join(missing))


def check_links(problems):
    for root, dirs, files in os.walk("."):
        dirs[:] = [x for x in dirs if x not in (".git", "upstream", "node_modules")]
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            text = re.sub(r"```.*?```", "", open(path, encoding="utf-8").read(), flags=re.S)
            for target in re.findall(r"\]\(([^)\s]+)\)", text):
                if re.match(r"[a-z]+:|#", target):
                    continue
                file = target.split("#")[0]
                if file and not os.path.exists(os.path.normpath(os.path.join(root, file))):
                    problems.append(f"{path[2:]}: broken link {target}")


def main():
    problems = []
    if "--base" in sys.argv:
        check_docs_travel(sys.argv[sys.argv.index("--base") + 1], problems)
    check_project_pages(problems)
    check_links(problems)
    for p in problems:
        print(f"::error::{p}")
    print("docs-check: OK" if not problems else f"docs-check: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
