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


def normalize_score(value: str) -> int:
    match = re.search(r"[0-4]", value or "0")
    return int(match.group(0)) if match else 0


def validate_date(value: str) -> str:
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", value or ""):
        raise ValueError("Date must use YYYY-MM-DD format")
    return value


def main() -> None:
    date = validate_date(os.environ["LOG_DATE"])
    year = date[:4]
    log_path = LOGS_DIR / f"{year}.yml"
    logs = load_yaml(log_path)

    logs[date] = {
        area: normalize_score(os.environ.get(area.upper(), "0"))
        for area in AREAS
    }

    write_yaml(log_path, logs)


if __name__ == "__main__":
    main()
