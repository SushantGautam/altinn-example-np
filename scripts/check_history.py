"""Check reachable Git blobs across all fetched refs for common credential formats.

This lightweight check deliberately reports paths, never possible secret values.
It supplements, but does not replace, a dedicated secret scanner and review.
Run against a full clone: git fetch --all --tags; python scripts/check_history.py
"""
import re
import subprocess
import sys
from pathlib import PurePosixPath

PATTERNS = {
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"(?:ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"),
    "AWS access key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "OpenAI-style secret": re.compile(rb"sk-(?:proj-)?[A-Za-z0-9_-]{30,}"),
    "Slack token": re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
}
BLOCKED_FILES = {".env", ".env.local", ".demo.local.env"}
BLOCKED_EXT = {".pem", ".key", ".p12", ".pfx"}

def git(*args):
    return subprocess.check_output(["git", *args])

def main():
    objects = git("rev-list", "--objects", "--all").decode().splitlines()
    refs = []
    paths = {}
    for line in objects:
        oid, _, path = line.partition(" ")
        if oid in paths:
            continue
        refs.append(oid)
        paths[oid] = path or "(path unavailable)"
    if not refs:
        sys.exit("No Git objects found. Use a non-shallow checkout with fetched refs.")

    proc = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    proc.stdin.write(("\n".join(refs) + "\n").encode())
    proc.stdin.close()
    problems = []
    scanned = 0
    for expected in refs:
        header = proc.stdout.readline().decode().strip().split()
        if len(header) != 3 or header[0] != expected:
            sys.exit("Unexpected git cat-file output")
        oid, kind, size_str = header
        size = int(size_str)
        data = proc.stdout.read(size)
        if len(data) != size or proc.stdout.read(1) != b"\n":
            sys.exit("Incomplete git cat-file response")
        if kind != "blob":
            continue
        scanned += 1
        path = paths[oid]
        filename = PurePosixPath(path).name
        suffix = PurePosixPath(path).suffix.lower()
        if filename in BLOCKED_FILES or suffix in BLOCKED_EXT:
            problems.append(f"{path}: sensitive/generated file was committed")
        for name, pattern in PATTERNS.items():
            if pattern.search(data):
                problems.append(f"{path}: possible {name}")
    if proc.wait() != 0:
        sys.exit("git cat-file failed")

    if problems:
        print("History check found possible credentials or sensitive files:")
        for problem in sorted(set(problems)):
            print(f"- {problem}")
        sys.exit(1)
    print(f"PASS: scanned {scanned} reachable Git blobs across all fetched refs")
    print("This does not detect every secret type; use a dedicated history scanner before publication.")

if __name__ == "__main__":
    main()
