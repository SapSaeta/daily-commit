from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "habits.yml"
LOGS_DIR = ROOT / "logs"
ASSETS_DIR = ROOT / "assets"

CELL = 11
GAP = 3
LEFT = 34
TOP = 24
WIDTH = LEFT + 53 * (CELL + GAP) + 16
HEIGHT = TOP + 7 * (CELL + GAP) + 42

COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
TEXT = "#7d8590"
BORDER = "#30363d"
BG = "#0d1117"

DAYS = ["Mon", "Wed", "Fri"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def all_dates_for_year(year: int) -> list[dt.date]:
    first = dt.date(year, 1, 1)
    start = first - dt.timedelta(days=first.weekday())
    return [start + dt.timedelta(days=index) for index in range(53 * 7)]


def score_day(day_data: dict[str, Any], category: str | None, categories: dict[str, Any]) -> float | None:
    values: list[bool] = []

    selected = categories.keys() if category is None else [category]
    for category_id in selected:
        category_config = categories.get(category_id, {})
        habit_ids = [habit["id"] for habit in category_config.get("habits", [])]
        category_log = day_data.get(category_id, {}) if isinstance(day_data, dict) else {}
        for habit_id in habit_ids:
            if habit_id in category_log:
                values.append(bool(category_log[habit_id]))

    if not values:
        return None
    return sum(values) / len(values)


def color_for_score(score: float | None) -> str:
    if score is None or score <= 0:
        return COLORS[0]
    if score <= 0.25:
        return COLORS[1]
    if score <= 0.50:
        return COLORS[2]
    if score <= 0.75:
        return COLORS[3]
    return COLORS[4]


def render_graph(title: str, category: str | None, year: int, categories: dict[str, Any], logs: dict[str, Any]) -> str:
    dates = all_dates_for_year(year)
    cells = []

    for index, current_date in enumerate(dates):
        week = index // 7
        weekday = current_date.weekday()
        x = LEFT + week * (CELL + GAP)
        y = TOP + weekday * (CELL + GAP)
        key = current_date.isoformat()
        score = score_day(logs.get(key, {}), category, categories) if current_date.year == year else None
        color = color_for_score(score)
        opacity = "1" if current_date.year == year else "0.35"
        label_score = "No data" if score is None else f"{round(score * 100)}%"
        cells.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" fill="{color}" opacity="{opacity}">' 
            f'<title>{key}: {label_score}</title></rect>'
        )

    month_labels = []
    seen_months = set()
    for index, current_date in enumerate(dates):
        if current_date.year != year or current_date.month in seen_months:
            continue
        seen_months.add(current_date.month)
        week = index // 7
        x = LEFT + week * (CELL + GAP)
        month_labels.append(f'<text x="{x}" y="14" fill="{TEXT}" font-size="10">{MONTHS[current_date.month - 1]}</text>')

    day_labels = [
        f'<text x="0" y="{TOP + 1 * (CELL + GAP) + 9}" fill="{TEXT}" font-size="10">Mon</text>',
        f'<text x="0" y="{TOP + 3 * (CELL + GAP) + 9}" fill="{TEXT}" font-size="10">Wed</text>',
        f'<text x="0" y="{TOP + 5 * (CELL + GAP) + 9}" fill="{TEXT}" font-size="10">Fri</text>',
    ]

    legend_x = WIDTH - 180
    legend_y = HEIGHT - 20
    legend = [f'<text x="{legend_x}" y="{legend_y + 9}" fill="{TEXT}" font-size="10">Less</text>']
    for level, color in enumerate(COLORS):
        x = legend_x + 32 + level * (CELL + 4)
        legend.append(f'<rect x="{x}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}" stroke="{BORDER}"/>')
    legend.append(f'<text x="{legend_x + 32 + 5 * (CELL + 4) + 4}" y="{legend_y + 9}" fill="{TEXT}" font-size="10">More</text>')

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{title}">',
        f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
        *month_labels,
        *day_labels,
        *cells,
        *legend,
        '</svg>',
    ])


def main() -> None:
    config = load_yaml(CONFIG_PATH)
    categories = config.get("categories", {})
    logs: dict[str, Any] = {}
    years = set()

    for path in LOGS_DIR.glob("*.yml"):
        yearly_logs = load_yaml(path)
        logs.update(yearly_logs)
        try:
            years.add(int(path.stem))
        except ValueError:
            pass

    year = max(years or {dt.date.today().year})
    ASSETS_DIR.mkdir(exist_ok=True)

    graphs = {"general": ("General", None)}
    for category_id, category_config in categories.items():
        graphs[category_id] = (category_config.get("name", category_id), category_id)

    for filename, (title, category_id) in graphs.items():
        svg = render_graph(title, category_id, year, categories, logs)
        (ASSETS_DIR / f"{filename}.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
