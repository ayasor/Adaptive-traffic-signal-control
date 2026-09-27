"""Calibrate the free parameters of the adaptive and actuated controllers.

The original thesis fixed T_max, T_crit and the pedestrian weights by hand.
Here they are chosen with a grid search, using *tuning seeds* (101-103) that
are never used in the final evaluation (seeds 1-20), so the reported results
are not fitted to the evaluation data.

Objective: total person-delay per hour,
    J = 1.2 * sum(vehicle delay) + sum(pedestrian waiting at the crossings)
(1.2 = average car occupancy), normalised by the J of the Webster fixed-time
plan in the same case, and averaged over four representative cases (low and
high demand in both intersections).  One single parameter set is selected
for both intersections.

Usage:  python tune.py   -> results/tuning.jsonl and results/tuning_summary.json
"""

from __future__ import annotations

import itertools
import json
import os
import statistics
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

from atsc.runner import RunSpec
from run_experiments import RESULTS, _key, _work

TUNING_SEEDS = (101, 102, 103)
CASES = [("simple", 0.5), ("simple", 1.0), ("shibuya", 0.3), ("shibuya", 1.0)]
T_MAX = (30, 40, 60, 90, 120)
T_CRIT = (30.0, 45.0, 60.0, 90.0, 120.0)
PED_SCALE = (0.5, 1.0, 2.0)
OCCUPANCY = 1.2
OUT = RESULTS / "tuning.jsonl"


def person_delay(r: dict) -> float:
    n_veh = r["veh_loaded"]
    return OCCUPANCY * r["veh_delay_mean_s"] * n_veh + r["ped_wait_mean_s"] * r["ped_crossing_n"]


def specs() -> list[RunSpec]:
    out = []
    for (scn, scale), seed in itertools.product(CASES, TUNING_SEEDS):
        out.append(RunSpec(scn, "fixed", seed, scale))
        for t_max in T_MAX:
            out.append(RunSpec(scn, "actuated", seed, scale, t_max=t_max))
            for t_crit, ps in itertools.product(T_CRIT, PED_SCALE):
                out.append(RunSpec(scn, "adaptive", seed, scale, t_max=t_max,
                                   t_crit=t_crit, ped_scale=ps))
    return out


def run_all() -> list[dict]:
    done = {}
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            d = json.loads(line)
            done[_key(d)] = d
    todo = [s for s in specs() if _key(asdict(s)) not in done]
    print(f"{len(todo)} tuning simulations to run")
    with ProcessPoolExecutor(max(1, (os.cpu_count() or 2) - 2)) as pool, OUT.open("a") as f:
        futs = [pool.submit(_work, s) for s in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            done[_key(r)] = r
            f.write(json.dumps(r) + "\n")
            f.flush()
            if i % 50 == 0:
                print(f"  {i}/{len(todo)}", flush=True)
    return list(done.values())


def summarise(results: list[dict]) -> dict:
    base = defaultdict(list)
    for r in results:
        if r["controller"] == "fixed":
            base[(r["scenario"], r["veh_scale"])].append(person_delay(r))
    base_j = {k: statistics.fmean(v) for k, v in base.items()}

    scores = defaultdict(lambda: defaultdict(list))
    for r in results:
        if r["controller"] == "fixed":
            continue
        params = (r["controller"], r["t_max"], r["t_crit"], r["ped_scale"])
        if r["controller"] == "actuated":
            params = ("actuated", r["t_max"], None, None)
        case = (r["scenario"], r["veh_scale"])
        scores[params][case].append(person_delay(r) / base_j[case])

    table = []
    for params, per_case in scores.items():
        rel = {f"{c[0]}@{c[1]:g}": statistics.fmean(v) for c, v in per_case.items()}
        table.append({"controller": params[0], "t_max": params[1], "t_crit": params[2],
                      "ped_scale": params[3], "relative_J": rel,
                      "mean_relative_J": statistics.fmean(rel.values())})
    table.sort(key=lambda d: d["mean_relative_J"])
    best = {c: next(d for d in table if d["controller"] == c) for c in ("adaptive", "actuated")}
    return {"objective": "person-delay relative to Webster fixed-time (lower is better)",
            "best": best, "all": table}


def main() -> None:
    summary = summarise(run_all())
    (RESULTS / "tuning_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary["best"], indent=2))
    print("\nTop 10:")
    for d in summary["all"][:10]:
        print(f"  {d['controller']:9} t_max={d['t_max']} t_crit={d['t_crit']} "
              f"ped={d['ped_scale']}  J={d['mean_relative_J']:.3f}  {d['relative_J']}")


if __name__ == "__main__":
    main()
