"""
Generic KPI tools.

Platform-specific tools are optional.
These tools provide a generic KPI data layer for any Agile Team goal.
"""
import json
from datetime import datetime
from pathlib import Path


TOOL_UPSERT_METRIC = {
    "name": "kpi_upsert_metric",
    "description": "Create or update a KPI metric for a goal team.",
    "input_schema": {
        "type": "object",
        "properties": {
            "team_id": {"type": "string", "description": "Agile Team ID"},
            "metric": {"type": "string", "description": "Metric name"},
            "target": {"type": "number", "description": "Target value"},
            "current": {"type": "number", "description": "Current value"},
            "source": {"type": "string", "description": "Measurement source"},
            "frequency": {"type": "string", "description": "daily/weekly/monthly"},
            "note": {"type": "string", "description": "Optional note"},
        },
        "required": ["team_id", "metric", "target"],
    },
}

TOOL_LOG_MEASUREMENT = {
    "name": "kpi_log_measurement",
    "description": "Append a KPI measurement value to metric history.",
    "input_schema": {
        "type": "object",
        "properties": {
            "team_id": {"type": "string", "description": "Agile Team ID"},
            "metric": {"type": "string", "description": "Metric name"},
            "value": {"type": "number", "description": "Measured value"},
            "note": {"type": "string", "description": "Optional measurement note"},
            "measured_at": {"type": "string", "description": "ISO datetime (optional)"},
        },
        "required": ["team_id", "metric", "value"],
    },
}

TOOL_LIST_METRICS = {
    "name": "kpi_list_metrics",
    "description": "List KPI metrics and current progress for a goal team.",
    "input_schema": {
        "type": "object",
        "properties": {
            "team_id": {"type": "string", "description": "Agile Team ID"},
        },
        "required": ["team_id"],
    },
}


def _db_path(memory_dir: str) -> Path:
    return Path(memory_dir) / "kpi_metrics.json"


def _load_db(memory_dir: str) -> dict:
    path = _db_path(memory_dir)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save_db(memory_dir: str, data: dict):
    path = _db_path(memory_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def upsert_metric(
    memory_dir: str,
    team_id: str,
    metric: str,
    target: float,
    current: float | None = None,
    source: str = "",
    frequency: str = "daily",
    note: str = "",
) -> str:
    db = _load_db(memory_dir)
    team = db.setdefault(team_id, {})
    item = team.setdefault(metric, {"history": []})

    item["metric"] = metric
    item["target"] = target
    if current is not None:
        item["current"] = current
    item["source"] = source
    item["frequency"] = frequency
    item["note"] = note
    item["updated_at"] = datetime.now().isoformat()

    _save_db(memory_dir, db)

    return json.dumps(
        {
            "team_id": team_id,
            "metric": metric,
            "target": target,
            "current": item.get("current"),
            "source": source,
            "frequency": frequency,
            "status": "upserted",
        },
        ensure_ascii=False,
    )


def log_measurement(
    memory_dir: str,
    team_id: str,
    metric: str,
    value: float,
    note: str = "",
    measured_at: str = "",
) -> str:
    db = _load_db(memory_dir)
    team = db.setdefault(team_id, {})
    item = team.setdefault(metric, {"metric": metric, "history": []})

    ts = measured_at.strip() or datetime.now().isoformat()
    entry = {
        "value": value,
        "measured_at": ts,
        "note": note,
    }
    item.setdefault("history", []).append(entry)
    item["current"] = value
    item["updated_at"] = datetime.now().isoformat()

    _save_db(memory_dir, db)

    return json.dumps(
        {
            "team_id": team_id,
            "metric": metric,
            "current": value,
            "history_count": len(item.get("history", [])),
            "status": "logged",
        },
        ensure_ascii=False,
    )


def list_metrics(memory_dir: str, team_id: str) -> str:
    db = _load_db(memory_dir)
    team = db.get(team_id, {})

    metrics = []
    for metric_name, item in team.items():
        current = item.get("current")
        target = item.get("target")
        gap = None
        if isinstance(current, (int, float)) and isinstance(target, (int, float)):
            gap = target - current

        metrics.append(
            {
                "metric": metric_name,
                "current": current,
                "target": target,
                "gap": gap,
                "source": item.get("source", ""),
                "frequency": item.get("frequency", ""),
                "updated_at": item.get("updated_at", ""),
            }
        )

    return json.dumps(
        {
            "team_id": team_id,
            "metric_count": len(metrics),
            "metrics": metrics,
        },
        ensure_ascii=False,
    )


def _memory_dir(context: dict) -> str:
    return str(context.get("memory_dir", "./memory"))


def _handle_upsert(tool_input: dict, context: dict) -> str:
    return upsert_metric(
        memory_dir=_memory_dir(context),
        team_id=tool_input["team_id"],
        metric=tool_input["metric"],
        target=tool_input["target"],
        current=tool_input.get("current"),
        source=tool_input.get("source", ""),
        frequency=tool_input.get("frequency", "daily"),
        note=tool_input.get("note", ""),
    )


def _handle_log(tool_input: dict, context: dict) -> str:
    return log_measurement(
        memory_dir=_memory_dir(context),
        team_id=tool_input["team_id"],
        metric=tool_input["metric"],
        value=tool_input["value"],
        note=tool_input.get("note", ""),
        measured_at=tool_input.get("measured_at", ""),
    )


def _handle_list(tool_input: dict, context: dict) -> str:
    return list_metrics(
        memory_dir=_memory_dir(context),
        team_id=tool_input["team_id"],
    )


def get_tool_specs() -> list[dict]:
    return [
        {
            "definition": TOOL_UPSERT_METRIC,
            "handler": _handle_upsert,
        },
        {
            "definition": TOOL_LOG_MEASUREMENT,
            "handler": _handle_log,
        },
        {
            "definition": TOOL_LIST_METRICS,
            "handler": _handle_list,
        },
    ]
