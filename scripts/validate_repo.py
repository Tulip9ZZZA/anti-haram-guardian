#!/usr/bin/env python3
"""Run zero-dependency structural checks for the public skill repository."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "anti-haram-guardian"
REQUIRED = [
    ROOT / "README.md",
    ROOT / "LICENSE",
    SKILL / "SKILL.md",
    SKILL / "agents" / "openai.yaml",
    SKILL / "assets" / "icon.svg",
    SKILL / "references" / "sources.csv",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


for path in REQUIRED:
    if not path.is_file():
        fail(f"missing required file: {path.relative_to(ROOT)}")

text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
if not match:
    fail("SKILL.md has no valid YAML frontmatter block")

keys = {
    line.split(":", 1)[0].strip()
    for line in match.group(1).splitlines()
    if line and not line.startswith((" ", "\t")) and ":" in line
}
if keys != {"name", "description"}:
    fail(f"SKILL.md frontmatter keys must be name and description, got {sorted(keys)}")

if "name: anti-haram-guardian" not in match.group(0):
    fail("SKILL.md name must be anti-haram-guardian")

with (SKILL / "references" / "sources.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
if not rows:
    fail("source registry is empty")

print("OK: repository structure and skill frontmatter")
