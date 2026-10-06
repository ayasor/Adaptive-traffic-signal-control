"""Load the simulation outputs used by the document (numbers are never typed by hand)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "simulation" / "results"
CTRL_NAME = {"fixed": "Fixed-time (Webster)", "actuated": "Actuated", "adaptive": "Adaptive"}


def summary() -> dict:
    out = {}
    with (RES / "summary.csv").open() as f:
        for row in csv.DictReader(f):
            key = (row["scenario"], row["variant"], float(row["veh_scale"]), row["controller"])
            out[key] = {k: (float(v) if v not in ("", "nan") else float("nan"))
                        for k, v in row.items()
                        if k not in ("scenario", "variant", "controller")}
    return out


def comparison() -> list[dict]:
    return json.loads((RES / "comparison.json").read_text())


def runs() -> list[dict]:
    return [json.loads(line) for line in (RES / "runs.jsonl").read_text().splitlines() if line]


def saturation() -> dict:
    return json.loads((RES / "saturation_flow.json").read_text())


def tuning() -> dict:
    return json.loads((RES / "tuning_summary.json").read_text())


def fmt(mean: float, ci: float | None = None, nd: int = 1) -> str:
    if mean != mean:  # nan
        return "–"
    s = f"{mean:,.{nd}f}"
    if ci is not None and ci == ci:
        s += f" ± {ci:,.{nd}f}"
    return s


def pct(x: float) -> str:
    return f"{x * 100:+.0f} %"


OCCUPANCY = 1.2


def person_delay_per_person(r: dict) -> float:
    """Mean delay per person: car occupants (1.2 per car) and pedestrians who crossed."""
    n_veh, n_ped = r["veh_loaded"], r["ped_crossing_n"]
    total = OCCUPANCY * r["veh_delay_mean_s"] * n_veh + r["ped_wait_mean_s"] * n_ped
    return total / (OCCUPANCY * n_veh + n_ped)


def paired(rows: list[dict], scenario: str, variant: str, scale: float, metric,
           base: str) -> tuple[float, float, int, int]:
    """Paired improvement m = (base - adaptive) / base over seeds.

    metric is a key or a function of the run dict.  Returns (mean, ci95, wins, n)."""
    import math
    import statistics
    get = metric if callable(metric) else (lambda r: r[metric])
    by = {}
    for r in rows:
        if r["scenario"] == scenario and r["variant"] == variant and r["veh_scale"] == scale:
            by.setdefault(r["controller"], {})[r["seed"]] = r
    a, b = by.get("adaptive", {}), by.get(base, {})
    seeds = sorted(set(a) & set(b))
    ratios = [(get(b[s]) - get(a[s])) / get(b[s]) for s in seeds if get(b[s])]
    if not ratios:
        return float("nan"), float("nan"), 0, 0
    m = statistics.fmean(ratios)
    ci = 2.093 * statistics.stdev(ratios) / math.sqrt(len(ratios)) if len(ratios) > 1 else float("nan")
    wins = sum(1 for s in seeds if get(a[s]) < get(b[s]))
    return m, ci, wins, len(seeds)


def group_mean(rows: list[dict], scenario: str, variant: str, scale: float, ctrl: str, metric):
    import math
    import statistics
    get = metric if callable(metric) else (lambda r: r[metric])
    v = [get(r) for r in rows if r["scenario"] == scenario and r["variant"] == variant
         and r["veh_scale"] == scale and r["controller"] == ctrl]
    v = [x for x in v if x == x]
    if not v:
        return float("nan"), float("nan")
    m = statistics.fmean(v)
    ci = 2.093 * statistics.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else float("nan")
    return m, ci
