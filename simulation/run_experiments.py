"""Run the full experiment grid in parallel.

    scenarios  x  demand levels  x  controllers  x  random seeds

Results are appended to results/runs.jsonl (one JSON line per simulation),
so an interrupted run can be resumed: finished combinations are skipped.

Usage:
    python run_experiments.py                 # full grid (20 seeds)
    python run_experiments.py --seeds 2 --quick
    python run_experiments.py --gui simple adaptive 1.0   # watch one run
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

from atsc.runner import RunSpec, load_mu, run

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MU_FILE = RESULTS / "saturation_flow.json"
CONTROLLERS = ("fixed", "actuated", "adaptive")
# Parameters selected by tune.py on the tuning seeds (see results/tuning_summary.json)
TUNED = {
    "fixed": {},
    "actuated": {"t_max": 40},
    "adaptive": {"t_max": 90, "t_crit": 90.0, "ped_scale": 1.0},
}
DEMAND = {   # vehicle demand as a fraction of the original thesis demand
    "simple": (0.25, 0.5, 0.75, 1.0),
    "shibuya": (0.2, 0.3, 0.4, 0.5, 0.75, 1.0),
}


def grid(n_seeds: int, quick: bool) -> list[RunSpec]:
    specs = []
    for scenario, scales in DEMAND.items():
        if quick:
            scales = (scales[-1],)
        for scale, ctrl, seed in itertools.product(scales, CONTROLLERS, range(1, n_seeds + 1)):
            specs.append(RunSpec(scenario, ctrl, seed, scale, **TUNED[ctrl]))
    for ctrl, seed in itertools.product(CONTROLLERS, range(1, n_seeds + 1)):
        specs.append(RunSpec("shibuya", ctrl, seed, 1.0, "unbalanced", **TUNED[ctrl]))
    return specs


def _key(d: dict) -> tuple:
    return (d["scenario"], d["variant"], float(d["veh_scale"]), d["controller"], int(d["seed"]),
            int(d["t_max"]), float(d["t_crit"]), float(d["ped_scale"]))


def _work(spec: RunSpec, attempts: int = 3) -> dict:
    """Run one simulation; retry if SUMO/TraCI fails to start (port race)."""
    mu = load_mu(MU_FILE)
    for i in range(attempts):
        try:
            with tempfile.TemporaryDirectory() as tmp:
                return run(spec, mu, Path(tmp))
        except Exception:
            if i == attempts - 1:
                raise


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--quick", action="store_true", help="only the highest demand level")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--out", default=str(RESULTS / "runs.jsonl"))
    ap.add_argument("--gui", nargs=3, metavar=("SCENARIO", "CONTROLLER", "SCALE"))
    args = ap.parse_args()

    if args.gui:
        scenario, ctrl, scale = args.gui
        with tempfile.TemporaryDirectory() as tmp:
            print(json.dumps(run(RunSpec(scenario, ctrl, 1, float(scale), **TUNED[ctrl]),
                                 load_mu(MU_FILE), Path(tmp), gui=True), indent=2))
        return

    out = Path(args.out)
    out.parent.mkdir(exist_ok=True)
    done = set()
    if out.exists():
        done = {_key(json.loads(line)) for line in out.read_text().splitlines() if line}
    todo = [s for s in grid(args.seeds, args.quick) if _key(asdict(s)) not in done]
    print(f"{len(todo)} simulations to run ({len(done)} already done), {args.jobs} workers")

    with ProcessPoolExecutor(args.jobs) as pool, out.open("a") as f:
        futures = {pool.submit(_work, s): s for s in todo}
        for i, fut in enumerate(as_completed(futures), 1):
            spec = futures[fut]
            try:
                res = fut.result()
            except Exception as exc:  # keep going, report at the end
                print(f"FAILED {spec}: {exc!r}")
                continue
            f.write(json.dumps(res) + "\n")
            f.flush()
            if i % 10 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)}  last: {spec.scenario} {spec.variant} "
                      f"x{spec.veh_scale} {spec.controller} seed {spec.seed}: "
                      f"delay {res['veh_delay_mean_s']:.1f}s", flush=True)


if __name__ == "__main__":
    main()
