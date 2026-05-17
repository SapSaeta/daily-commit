from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]

HABIT_MAP = {
    "physical": {
        "Caminar / paseo": "walk",
        "Entrenamiento": "workout",
        "Core": "core",
        "Movilidad": "mobility",
    },
    "study": {
        "ABAP / SAP": "abap",
        "Curso / tutorial": "course",
        "Lectura técnica": "reading",
        "Práctica real": "practice",
    },
    "work": {
        "Trabajo profundo": "deep_work",
        "Tickets avanzados": "tickets",
        "Documentación": "documentation",
        "Sin distracciones": "no_distractions",
    },
    "nutrition": {
        "Agua suficiente": "water",
        "Proteína suficiente": "protein",
        "Sin ultraprocesados": "no_ultraprocessed",
        "Cena controlada": "controlled_dinner",
    },
}

SECTION_LABELS = {
    "physical": "Actividad física",
    "study": "Estudio",
    "work": "Trabajo",
    "nutrition": "Alimentación",
}


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True, sort_keys=True)


def extract_date(body: str, title: str) -> str:
    candidates = [body, title]
    for candidate in candidates:
        match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", candidate)
        if match:
            return match.group(1)
    raise ValueError("No date found. Use YYYY-MM-DD in the issue date field or title.")


def extract_section(body: str, label: str) -> str:
    pattern = rf"### {re.escape(label)}\s*(.*?)(?=\n### |\Z)"
    match = re.search(pattern, body, flags=re.DOTALL)
    return match.group(1) if match else ""


def is_checked(section: str, habit_label: str) -> bool:
    escaped = re.escape(habit_label)
    return bool(re.search(rf"- \[[xX]\]\s+{escaped}\s*(?:\n|$)", section))


def parse_issue(body: str, title: str) -> tuple[str, dict[str, dict[str, bool]]]:
    date = extract_date(body, title)
    result: dict[str, dict[str, bool]] = {}

    for category_id, label in SECTION_LABELS.items():
        section = extract_section(body, label)
        result[category_id] = {}
        for habit_label, habit_id in HABIT_MAP[category_id].items():
            result[category_id][habit_id] = is_checked(section, habit_label)

    return date, result


def main() -> None:
    issue_body = os.environ.get("ISSUE_BODY", "")
    issue_title = os.environ.get("ISSUE_TITLE", "")
    date, day_log = parse_issue(issue_body, issue_title)
    year = date[:4]
    log_path = ROOT / "logs" / f"{year}.yml"
    logs = load_yaml(log_path)
    logs[date] = day_log
    write_yaml(log_path, logs)


if __name__ == "__main__":
    main()
