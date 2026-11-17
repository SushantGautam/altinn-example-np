"""Guard against doc drift and missing Markdown references.

Run: python3 scripts/check_docs.py
Checks only local relative links, known terminology, and documentation presence.
External URLs are manually reviewed, not downloaded.
"""
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
required = {
    "README.md", "docs/README.md", "docs/GOVERNMENT_BRIEF_EN.md",
    "docs/GOVERNMENT_BRIEF_NP.md", "docs/PRESENTATION_SCRIPT.md",
    "docs/ARCHITECTURE.md", "docs/IDENTITY_AND_CHANNELS.md",
    "docs/DEVELOPER_GUIDE.md", "docs/INTEGRATION_CONTRACTS.md",
    "docs/ALTINN_COMPONENT_STATUS.md", "docs/NATIVE_ALTINN_PATH.md",
    "docs/PILOT_PLAN.md", "native-altinn/nepal-licence/README.md",
    "native-altinn/nepal-licence/UPSTREAM.md",
}
for file in sorted(required):
    assert (ROOT / file).exists(), f"Missing required documentation: {file}"

for file in sorted(required):
    md = ROOT / file
    content = md.read_text(encoding="utf-8")
    assert content.strip().startswith("#"), f"Expected markdown title: {file}"
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", content):
        link = match.group(1).strip().split(" ", 1)[0].strip("<>")
        if not link or re.match(r"^(https?://|mailto:|#|tel:)", link, re.I):
            continue
        path = unquote(link.split("#", 1)[0].split("?", 1)[0])
        assert (md.parent / path).exists(), f"Broken local link in {file}: {path}"

main = (ROOT / "README.md").read_text(encoding="utf-8")
gov = (ROOT / "docs/GOVERNMENT_BRIEF_EN.md").read_text(encoding="utf-8")
native = (ROOT / "docs/ALTINN_COMPONENT_STATUS.md").read_text(encoding="utf-8")
architecture = (ROOT / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
ui = (ROOT / "api/static/app.js").read_text(encoding="utf-8")
for label, value in [("README", main), ("government", gov),
                     ("status", native), ("architecture", architecture),
                     ("visual UI", ui)]:
    lower = value.lower()
    assert "mobile" in lower, f"{label} must reflect Nagarik mobile channel"
    assert "web" in lower, f"{label} must mention possible web evolution"
    assert "altinn" in lower, f"{label} must identify Altinn"
assert "not a government channel" in ui.lower()
assert "LocalTest" in main and "Keycloak" in main
assert "not yet" in native.lower()
assert "ttd/nepal-licence" in main
assert "http://localhost:8085" in main and "local.altinn.cloud:8000" in main
assert "api/stubs/dotm/licence" in (ROOT/"api/main.py").read_text()
assert "native.altinn.task.completed" in (ROOT/"api/main.py").read_text()
print(f"PASS: {len(required)} Markdown docs, local links and mobile/web/Altinn consistency")
