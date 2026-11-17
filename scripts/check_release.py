"""Basic repository hygiene checks for public review.

Run with: python scripts/check_release.py

This checks tracked files in the current checkout. It does not scan the entire
Git history or replace dedicated tools such as Gitleaks.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_NAMES = {".demo.local.env", ".env", ".env.local"}
EXCLUDED_EXTENSIONS = {".pem", ".p12", ".pfx", ".key", ".sqlite", ".db"}
SUSPICIOUS = {
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"(?:ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"),
    "AWS access key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "OpenAI-style secret": re.compile(rb"sk-(?:proj-)?[A-Za-z0-9_-]{30,}"),
    "Slack token": re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
}
try:
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT
    ).decode().split("\0")
except (OSError, subprocess.CalledProcessError) as exc:
    sys.exit(f"Could not list tracked files: {exc}")

problems = []
for relative in filter(None, tracked):
    path = ROOT / relative
    if not path.is_file():
        continue
    if path.name in EXCLUDED_NAMES or path.suffix.lower() in EXCLUDED_EXTENSIONS:
        problems.append(f"{relative}: generated data, credentials or key material must not be tracked")
        continue
    data = path.read_bytes()
    for name, pattern in SUSPICIOUS.items():
        if pattern.search(data):
            problems.append(f"{relative}: possible {name}")

required = ["LICENSE", "THIRD_PARTY_NOTICES.md", "SECURITY.md", "CONTRIBUTING.md"]
for relative in required:
    if not (ROOT / relative).is_file():
        problems.append(f"{relative}: required for public release")

if problems:
    print("Release hygiene checks failed:")
    for problem in problems:
        print(f"- {problem}")
    sys.exit(1)
print(f"PASS: checked {sum(bool(p) for p in tracked)} tracked paths for selected secret patterns and release files")
print("Note: full Git-history scanning and manual legal/security review remain necessary.")
