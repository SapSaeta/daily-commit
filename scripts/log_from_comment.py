from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "logs"
AREAS = ["physical", "study", "work", "nutrition"]


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True, sort_keys=True)


def extract_date(title: str, body: str) -> str:
    text = f"{title}\n{body}"
    match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if not match:
        raise ValueError("No date found in issue title or body")
    return match.group(1)


def extract_scores(comment: str) -> list[int]:
    numbers = [int(value) for value in re.findall(r"\b[0-4]\b", comment)]
    if len(numbers) < 4:
        raise ValueError("Comment must contain at least four scores from 0 to 4")
    return numbers[:4]


def main() -> None:
    issue_title = os.environ["ISSUE_TITLE"]
    issue_body = os.environ.get("ISSUE_BODY", "")
    comment_body = os.environ["COMMENT_BODY"]

    date = extract_date(issue_title, issue_body)
    scores = extract_scores(comment_body)
    year = date[:4]
    log_path = LOGS_DIR / f"{year}.yml"
    logs = load_yaml(log_path)
    logs[date] = dict(zip(AREAS, scores, strict=True))
    write_yaml(log_path, logs)


if __name__ == "__main__":
    main()
