#!/usr/bin/env python3
"""Validate the Anti-Haram Guardian source registry."""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from urllib.parse import urlparse


REQUIRED = {"id", "topic", "reference", "url", "evidence_type", "scope_note"}
ALLOWED_TYPES = {"direct-text", "interpretation", "application", "precautionary-default"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED - fields
        if missing:
            return [f"missing columns: {', '.join(sorted(missing))}"]

        for line, row in enumerate(reader, start=2):
            source_id = row["id"].strip()
            url = row["url"].strip()
            evidence_type = row["evidence_type"].strip()

            if not source_id:
                errors.append(f"line {line}: empty id")
            elif source_id in seen_ids:
                errors.append(f"line {line}: duplicate id {source_id!r}")
            seen_ids.add(source_id)

            parsed = urlparse(url)
            if parsed.scheme != "https" or not parsed.netloc:
                errors.append(f"line {line}: invalid HTTPS URL {url!r}")
            elif url in seen_urls:
                errors.append(f"line {line}: duplicate URL {url!r}")
            seen_urls.add(url)

            if evidence_type not in ALLOWED_TYPES:
                errors.append(
                    f"line {line}: evidence_type must be one of {sorted(ALLOWED_TYPES)}, got {evidence_type!r}"
                )

            for field in REQUIRED - {"id", "url", "evidence_type"}:
                if not row[field].strip():
                    errors.append(f"line {line}: empty {field}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_sources.py PATH_TO_SOURCES.csv", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"not a file: {path}", file=sys.stderr)
        return 2

    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
