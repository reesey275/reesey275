#!/usr/bin/env python3
"""Generate a repository-hosted WakaTime dashboard and README details."""

from __future__ import annotations

import argparse
import collections
import dataclasses
import datetime as dt
import html
import json
import math
import pathlib
import tempfile
from typing import Any


WIDTH = 900
HEIGHT = 825
START_MARKER = "<!--START_SECTION:waka-->"
END_MARKER = "<!--END_SECTION:waka-->"

THEME = {
    "background": "#0d1117",
    "surface": "#161b22",
    "surface_alt": "#21262d",
    "border": "#30363d",
    "title": "#f0f6fc",
    "text": "#c9d1d9",
    "muted": "#8b949e",
    "blue": "#58a6ff",
    "purple": "#a371f7",
    "green": "#3fb950",
    "amber": "#d29922",
    "pink": "#f778ba",
}


@dataclasses.dataclass(frozen=True)
class Metric:
    """One ranked WakaTime metric."""

    name: str
    total_seconds: float
    percent: float
    text: str


@dataclasses.dataclass(frozen=True)
class Day:
    """One day of WakaTime activity."""

    date: dt.date
    total_seconds: float
    text: str


@dataclasses.dataclass(frozen=True)
class DashboardData:
    """Normalized data shared by the SVG and Markdown renderers."""

    timezone: str
    start: dt.date
    end: dt.date
    total_seconds: float
    total_text: str
    daily_average_seconds: float
    daily_average_text: str
    best_day: Day
    daily: tuple[Day, ...]
    languages: tuple[Metric, ...]
    editors: tuple[Metric, ...]
    operating_systems: tuple[Metric, ...]
    projects: tuple[Metric, ...]
    categories: tuple[Metric, ...]


class DashboardDataError(ValueError):
    """Raised when the WakaTime response cannot produce a safe dashboard."""


def safe_number(value: object, label: str) -> float:
    """Return a finite, non-negative number."""

    if isinstance(value, bool):
        raise DashboardDataError(f"{label} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise DashboardDataError(f"{label} must be numeric") from error
    if not math.isfinite(number) or number < 0:
        raise DashboardDataError(f"{label} must be finite and non-negative")
    return number


def parse_date(value: object, label: str) -> dt.date:
    """Parse an ISO calendar date."""

    try:
        return dt.date.fromisoformat(str(value))
    except ValueError as error:
        raise DashboardDataError(f"{label} must be an ISO date") from error


def format_duration(total_seconds: float) -> str:
    """Format seconds using the compact wording used in the README."""

    seconds = int(total_seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    parts: list[str] = []
    if hours:
        parts.append(f"{hours} hr" if hours == 1 else f"{hours} hrs")
    if minutes or not parts:
        parts.append(f"{minutes} min" if minutes == 1 else f"{minutes} mins")
    return " ".join(parts)


def compact_duration(total_seconds: float) -> str:
    """Format seconds for a small SVG metric card."""

    seconds = int(total_seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    if hours and minutes:
        return f"{hours}h {minutes}m"
    if hours:
        return f"{hours}h"
    return f"{minutes}m"


def aggregate_metrics(
    days: list[dict[str, Any]],
    key: str,
    total_seconds: float,
    limit: int,
) -> tuple[Metric, ...]:
    """Aggregate and rank one WakaTime metric collection."""

    totals: collections.Counter[str] = collections.Counter()
    for index, day in enumerate(days):
        entries = day.get(key, [])
        if not isinstance(entries, list):
            raise DashboardDataError(f"data[{index}].{key} must be a list")
        for entry in entries:
            if not isinstance(entry, dict):
                raise DashboardDataError(f"data[{index}].{key} entry must be an object")
            name = str(entry.get("name") or "Unknown")
            totals[name] += safe_number(
                entry.get("total_seconds", 0),
                f"{key}.{name}.total_seconds",
            )

    metrics: list[Metric] = []
    for name, seconds in totals.most_common(limit):
        percent = seconds / total_seconds * 100 if total_seconds else 0
        metrics.append(Metric(name, seconds, percent, format_duration(seconds)))
    return tuple(metrics)


def dashboard_from_summaries(payload: dict[str, Any]) -> DashboardData:
    """Normalize a WakaTime summaries API response."""

    raw_days = payload.get("data")
    if not isinstance(raw_days, list) or not raw_days:
        raise DashboardDataError("WakaTime response must contain at least one summary day")
    if not all(isinstance(day, dict) for day in raw_days):
        raise DashboardDataError("Every WakaTime summary day must be an object")

    days = list(raw_days)
    daily: list[Day] = []
    timezone = "UTC"
    for index, day in enumerate(days):
        day_range = day.get("range")
        grand_total = day.get("grand_total")
        if not isinstance(day_range, dict) or not isinstance(grand_total, dict):
            raise DashboardDataError(f"data[{index}] is missing range or grand_total")
        date = parse_date(day_range.get("date"), f"data[{index}].range.date")
        seconds = safe_number(
            grand_total.get("total_seconds", 0),
            f"data[{index}].grand_total.total_seconds",
        )
        timezone = str(day_range.get("timezone") or timezone)
        daily.append(Day(date, seconds, format_duration(seconds)))

    daily.sort(key=lambda item: item.date)
    total_seconds = sum(day.total_seconds for day in daily)
    daily_average_seconds = total_seconds / len(daily)
    best_day = max(daily, key=lambda item: item.total_seconds)

    return DashboardData(
        timezone=timezone,
        start=daily[0].date,
        end=daily[-1].date,
        total_seconds=total_seconds,
        total_text=format_duration(total_seconds),
        daily_average_seconds=daily_average_seconds,
        daily_average_text=format_duration(daily_average_seconds),
        best_day=best_day,
        daily=tuple(daily),
        languages=aggregate_metrics(days, "languages", total_seconds, 5),
        editors=aggregate_metrics(days, "editors", total_seconds, 3),
        operating_systems=aggregate_metrics(
            days,
            "operating_systems",
            total_seconds,
            5,
        ),
        projects=aggregate_metrics(days, "projects", total_seconds, 5),
        categories=aggregate_metrics(days, "categories", total_seconds, 5),
    )


def snapshot_metrics(
    snapshot: dict[str, Any],
    key: str,
    total_seconds: float,
) -> tuple[Metric, ...]:
    """Read metrics from a trusted repository snapshot."""

    raw_metrics = snapshot.get(key, [])
    if not isinstance(raw_metrics, list):
        raise DashboardDataError(f"snapshot.{key} must be a list")
    metrics: list[Metric] = []
    for raw_metric in raw_metrics:
        if not isinstance(raw_metric, dict):
            raise DashboardDataError(f"snapshot.{key} entry must be an object")
        name = str(raw_metric.get("name") or "Unknown")
        seconds = safe_number(
            raw_metric.get("total_seconds", 0),
            f"snapshot.{key}.{name}.total_seconds",
        )
        percent = seconds / total_seconds * 100 if total_seconds else 0
        metrics.append(Metric(name, seconds, percent, format_duration(seconds)))
    return tuple(metrics)


def dashboard_from_snapshot(payload: dict[str, Any]) -> DashboardData:
    """Load a normalized snapshot used for the first committed dashboard."""

    snapshot = payload.get("snapshot")
    if not isinstance(snapshot, dict):
        raise DashboardDataError("snapshot must be an object")

    total_seconds = safe_number(snapshot.get("total_seconds"), "snapshot.total_seconds")
    average_seconds = safe_number(
        snapshot.get("daily_average_seconds"),
        "snapshot.daily_average_seconds",
    )
    best = snapshot.get("best_day")
    if not isinstance(best, dict):
        raise DashboardDataError("snapshot.best_day must be an object")
    best_day = Day(
        parse_date(best.get("date"), "snapshot.best_day.date"),
        safe_number(
            best.get("total_seconds"),
            "snapshot.best_day.total_seconds",
        ),
        format_duration(safe_number(best.get("total_seconds"), "best day")),
    )

    raw_daily = snapshot.get("daily", [])
    if not isinstance(raw_daily, list):
        raise DashboardDataError("snapshot.daily must be a list")
    daily = tuple(
        Day(
            parse_date(item.get("date"), "snapshot.daily.date"),
            safe_number(item.get("total_seconds"), "snapshot.daily.total_seconds"),
            format_duration(
                safe_number(item.get("total_seconds"), "snapshot daily")
            ),
        )
        for item in raw_daily
        if isinstance(item, dict)
    )

    return DashboardData(
        timezone=str(snapshot.get("timezone") or "UTC"),
        start=parse_date(snapshot.get("start"), "snapshot.start"),
        end=parse_date(snapshot.get("end"), "snapshot.end"),
        total_seconds=total_seconds,
        total_text=format_duration(total_seconds),
        daily_average_seconds=average_seconds,
        daily_average_text=format_duration(average_seconds),
        best_day=best_day,
        daily=daily,
        languages=snapshot_metrics(snapshot, "languages", total_seconds),
        editors=snapshot_metrics(snapshot, "editors", total_seconds),
        operating_systems=snapshot_metrics(
            snapshot,
            "operating_systems",
            total_seconds,
        ),
        projects=snapshot_metrics(snapshot, "projects", total_seconds),
        categories=snapshot_metrics(snapshot, "categories", total_seconds),
    )


def load_dashboard(path: pathlib.Path) -> DashboardData:
    """Load either a WakaTime API response or normalized snapshot."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DashboardDataError(f"Could not read dashboard input: {path}") from error
    if not isinstance(payload, dict):
        raise DashboardDataError("Dashboard input must be a JSON object")
    if "snapshot" in payload:
        return dashboard_from_snapshot(payload)
    return dashboard_from_summaries(payload)


def svg_text(value: object) -> str:
    """Escape text for use inside SVG markup."""

    return html.escape(str(value), quote=True)


def markdown_text(value: object) -> str:
    """Escape user-controlled names for a Markdown list item."""

    escaped = html.escape(str(value), quote=False)
    for character in ("\\", "`", "*", "_", "[", "]"):
        escaped = escaped.replace(character, f"\\{character}")
    return escaped


def short_label(value: str, limit: int = 24) -> str:
    """Truncate a long SVG label without changing the detailed text."""

    if len(value) <= limit:
        return value
    return f"{value[: limit - 1]}…"


def format_card_date(value: dt.date) -> str:
    """Format a concise, portable date without platform-specific flags."""

    return f"{value.strftime('%b')} {value.day}"


def metric_card(x: int, label: str, value: str, detail: str) -> str:
    """Render one summary metric card."""

    return f'''  <rect x="{x}" y="76" width="198" height="88" rx="8"
    fill="{THEME["surface"]}" stroke="{THEME["border"]}"/>
  <text x="{x + 16}" y="101" class="eyebrow">{svg_text(label)}</text>
  <text x="{x + 16}" y="132" class="metric">{svg_text(value)}</text>
  <text x="{x + 16}" y="151" class="muted">{svg_text(detail)}</text>'''


def daily_chart(data: DashboardData) -> str:
    """Render the daily activity card, with an honest first-run fallback."""

    parts = [
        f'''  <rect x="28" y="180" width="844" height="210" rx="8"
    fill="{THEME["surface"]}" stroke="{THEME["border"]}"/>
  <text x="48" y="210" class="section-title">Daily activity</text>'''
    ]
    if not data.daily:
        parts.extend(
            [
                '  <text x="852" y="210" text-anchor="end" class="muted">First automated refresh pending</text>',
                f'  <rect x="48" y="252" width="804" height="26" rx="6" fill="{THEME["surface_alt"]}"/>',
                f'  <rect x="48" y="252" width="804" height="26" rx="6" fill="{THEME["blue"]}" opacity="0.8"/>',
                f'  <text x="450" y="271" text-anchor="middle" class="bar-value">{svg_text(data.total_text)} total</text>',
                '  <text x="450" y="321" text-anchor="middle" class="label">Daily bars will appear after the next scheduled WakaTime refresh.</text>',
                f'  <text x="450" y="349" text-anchor="middle" class="muted">Current period: {data.start.isoformat()} – {data.end.isoformat()}</text>',
            ]
        )
        return "\n".join(parts)

    max_seconds = max(day.total_seconds for day in data.daily) or 1
    left = 58
    chart_width = 784
    baseline = 342
    max_height = 96
    slot = chart_width / len(data.daily)
    bar_width = min(68.0, slot * 0.62)
    parts.append(
        f'  <text x="852" y="210" text-anchor="end" class="muted">{len(data.daily)} calendar days</text>'
    )
    for index, day in enumerate(data.daily):
        center = left + slot * index + slot / 2
        height = max(4.0, day.total_seconds / max_seconds * max_height)
        x = center - bar_width / 2
        y = baseline - height
        opacity = "1" if day == data.best_day else "0.72"
        parts.extend(
            [
                f'  <rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{height:.1f}" rx="5" fill="{THEME["blue"]}" opacity="{opacity}"/>',
                f'  <text x="{center:.1f}" y="{y - 8:.1f}" text-anchor="middle" class="bar-label">{svg_text(compact_duration(day.total_seconds))}</text>',
                f'  <text x="{center:.1f}" y="365" text-anchor="middle" class="axis">{svg_text(day.date.strftime("%a"))}</text>',
                f'  <text x="{center:.1f}" y="381" text-anchor="middle" class="muted">{svg_text(format_card_date(day.date))}</text>',
            ]
        )
    return "\n".join(parts)


def breakdown_card(
    x: int,
    y: int,
    title: str,
    metrics: tuple[Metric, ...],
    accent: str,
) -> str:
    """Render one ranked horizontal-bar card."""

    parts = [
        f'''  <rect x="{x}" y="{y}" width="415" height="182" rx="8"
    fill="{THEME["surface"]}" stroke="{THEME["border"]}"/>
  <text x="{x + 18}" y="{y + 28}" class="section-title">{svg_text(title)}</text>'''
    ]
    if not metrics:
        parts.append(
            f'  <text x="{x + 18}" y="{y + 70}" class="muted">No activity recorded</text>'
        )
        return "\n".join(parts)

    for index, metric in enumerate(metrics[:5]):
        row_y = y + 52 + index * 25
        track_y = row_y + 8
        bar_width = max(2.0, 379 * min(metric.percent, 100) / 100)
        value = f"{metric.percent:.1f}% · {metric.text}"
        parts.extend(
            [
                f'  <text x="{x + 18}" y="{row_y}" class="label">{svg_text(short_label(metric.name))}</text>',
                f'  <text x="{x + 397}" y="{row_y}" text-anchor="end" class="breakdown-value">{svg_text(value)}</text>',
                f'  <rect x="{x + 18}" y="{track_y}" width="379" height="5" rx="2.5" fill="{THEME["surface_alt"]}"/>',
                f'  <rect x="{x + 18}" y="{track_y}" width="{bar_width:.1f}" height="5" rx="2.5" fill="{accent}"/>',
            ]
        )
    return "\n".join(parts)


def render_svg(data: DashboardData, updated: str) -> str:
    """Render the complete WakaTime dashboard as a self-contained SVG."""

    primary_editor = data.editors[0] if data.editors else None
    editor_value = primary_editor.name if primary_editor else "No data"
    editor_detail = (
        f"{primary_editor.percent:.1f}% of activity" if primary_editor else "Editor unavailable"
    )
    description = (
        f"{data.total_text} of activity from {data.start.isoformat()} through "
        f"{data.end.isoformat()}, averaging {data.daily_average_text} per day."
    )
    cards = "\n".join(
        [
            metric_card(28, "TOTAL ACTIVITY", compact_duration(data.total_seconds), "Rolling weekly total"),
            metric_card(
                240,
                "DAILY AVERAGE",
                compact_duration(data.daily_average_seconds),
                "Across calendar days",
            ),
            metric_card(
                452,
                "BEST DAY",
                compact_duration(data.best_day.total_seconds),
                format_card_date(data.best_day.date),
            ),
            metric_card(664, "PRIMARY EDITOR", editor_value, editor_detail),
        ]
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
  viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="dashboard-title dashboard-description">
  <title id="dashboard-title">Weekly WakaTime Development Dashboard</title>
  <desc id="dashboard-description">{svg_text(description)}</desc>
  <style>
    .title {{ fill: {THEME["title"]}; font: 700 24px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .section-title {{ fill: {THEME["title"]}; font: 600 16px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .metric {{ fill: {THEME["title"]}; font: 700 22px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .eyebrow {{ fill: {THEME["blue"]}; font: 600 10px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; letter-spacing: 0.8px; }}
    .label {{ fill: {THEME["text"]}; font: 500 12px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .breakdown-value {{ fill: {THEME["muted"]}; font: 400 10px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .bar-label {{ fill: {THEME["text"]}; font: 600 11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .bar-value {{ fill: {THEME["background"]}; font: 700 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .axis {{ fill: {THEME["text"]}; font: 600 11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .muted {{ fill: {THEME["muted"]}; font: 400 11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
  </style>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="{THEME["background"]}"/>
  <text x="28" y="36" class="title">Weekly Development Dashboard</text>
  <text x="28" y="58" class="muted">{data.start.isoformat()} – {data.end.isoformat()} · {svg_text(data.timezone)}</text>
  <text x="872" y="58" text-anchor="end" class="muted">Updated {svg_text(updated)}</text>
{cards}
{daily_chart(data)}
{breakdown_card(28, 406, "Languages", data.languages, THEME["purple"])}
{breakdown_card(457, 406, "Operating systems", data.operating_systems, THEME["green"])}
{breakdown_card(28, 604, "Projects", data.projects, THEME["amber"])}
{breakdown_card(457, 604, "Categories", data.categories, THEME["pink"])}
  <text x="28" y="811" class="muted">WakaTime reflects rolling workflow activity, not permanent skill depth.</text>
</svg>
'''


def metric_markdown(title: str, metrics: tuple[Metric, ...]) -> str:
    """Render one accessible Markdown metric subsection."""

    lines = [f"### {title}", ""]
    if not metrics:
        lines.append("- No activity recorded")
    else:
        lines.extend(
            f"- {markdown_text(metric.name)}: {metric.text} ({metric.percent:.2f}%)"
            for metric in metrics
        )
    return "\n".join(lines)


def render_markdown(data: DashboardData, updated: str) -> str:
    """Render a compact image plus collapsed accessible details."""

    sections = [
        "![Weekly WakaTime development dashboard](./profile/wakatime-dashboard.svg)",
        "",
        "<details>",
        "<summary>View detailed weekly data</summary>",
        "",
        f"- **Time Zone:** {markdown_text(data.timezone)}",
        f"- **Date Range:** {data.start.isoformat()} - {data.end.isoformat()}",
        f"- **Total:** {data.total_text}",
        f"- **Daily Average:** {data.daily_average_text}",
        f"- **Best Day:** {data.best_day.date.isoformat()} ({data.best_day.text})",
        "",
        metric_markdown("Languages", data.languages),
        "",
        metric_markdown("Editors", data.editors),
        "",
        metric_markdown("Operating Systems", data.operating_systems),
        "",
        metric_markdown("Projects", data.projects),
        "",
        metric_markdown("Categories", data.categories),
        "",
        "</details>",
        "",
        f"_Last updated: {markdown_text(updated)}_",
    ]
    return "\n".join(sections)


def write_atomic(path: pathlib.Path, content: str) -> None:
    """Replace a file only after its complete content is available."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
        newline="\n",
    ) as handle:
        handle.write(content)
        temporary_path = pathlib.Path(handle.name)
    temporary_path.replace(path)


def update_readme(path: pathlib.Path, markdown: str) -> None:
    """Replace the generated README section while preserving its markers."""

    content = path.read_text(encoding="utf-8")
    if content.count(START_MARKER) != 1 or content.count(END_MARKER) != 1:
        raise DashboardDataError("README must contain exactly one WakaTime marker pair")
    start_index = content.index(START_MARKER)
    end_index = content.index(END_MARKER, start_index)
    if end_index <= start_index:
        raise DashboardDataError("README WakaTime markers are out of order")
    replacement = f"{START_MARKER}\n\n{markdown.rstrip()}\n{END_MARKER}"
    updated = content[:start_index] + replacement + content[end_index + len(END_MARKER) :]
    write_atomic(path, updated)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=pathlib.Path)
    parser.add_argument(
        "--svg-output",
        type=pathlib.Path,
        default=pathlib.Path("profile/wakatime-dashboard.svg"),
    )
    parser.add_argument("--readme", type=pathlib.Path)
    parser.add_argument(
        "--updated",
        default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_dashboard(args.input)
    write_atomic(args.svg_output, render_svg(data, args.updated))
    if args.readme:
        update_readme(args.readme, render_markdown(data, args.updated))
    print(
        json.dumps(
            {
                "date_range": [data.start.isoformat(), data.end.isoformat()],
                "days": len(data.daily),
                "output": str(args.svg_output),
                "total": data.total_text,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
