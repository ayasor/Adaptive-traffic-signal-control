"""Measure the saturation flow mu_i of every incoming lane in SUMO.

Method (standard queue-discharge measurement): the approach is held on red
until a long queue has formed, then it receives green, and we count the
vehicles leaving the lane between 5 s and 35 s after the start of green
(the first seconds are excluded because of start-up lost time).  The
vehicles counted divided by 30 s is the discharge rate at saturation.

The measurement is done on the straight lanes of the simple intersection.
Every approach of both scenarios has the same geometry (one 3.2 m lane,
50 km/h), so the same mu is used for all of them.  Permissive left turns in
the Shibuya intersection reduce the *effective* capacity below this value;
that effect is part of the simulation, not of mu.

Usage:  python calibrate_saturation.py  -> writes results/saturation_flow.json
"""

from __future__ import annotations

import json
import statistics
import tempfile
from pathlib import Path

import traci

from atsc.scenarios import SCENARIOS, write_routes
from atsc.sumo_env import sumo_binary

RED, GREEN, WINDOW = (90, 40, (5, 35))
CYCLES, SEEDS = 6, (1, 2, 3)
OUT = Path(__file__).resolve().parent / "results" / "saturation_flow.json"


def measure(scn, seed: int, tmp: Path) -> dict[str, list[float]]:
    routes = write_routes(scn, tmp / f"{scn.name}_{seed}.rou.xml", veh_scale=3.0)
    traci.start([sumo_binary(), "-n", str(scn.net_file), "-r", str(routes),
                 "--seed", str(seed), "--no-warnings", "--no-step-log",
                 "--time-to-teleport", "-1"])
    rates: dict[str, list[float]] = {}
    try:
        for _ in range(CYCLES):
            for k, phase in enumerate(scn.phases):
                other = scn.phases[(k + 1) % len(scn.phases)]
                traci.trafficlight.setRedYellowGreenState(scn.tl_id, other.state)
                for _ in range(RED):
                    traci.simulationStep()
                traci.trafficlight.setRedYellowGreenState(scn.tl_id, phase.state)
                before = {ln: set(traci.lane.getLastStepVehicleIDs(ln)) for ln in phase.lanes}
                left = {ln: 0 for ln in phase.lanes}
                for t in range(GREEN):
                    traci.simulationStep()
                    for ln in phase.lanes:
                        now = set(traci.lane.getLastStepVehicleIDs(ln))
                        if WINDOW[0] <= t < WINDOW[1]:
                            left[ln] += len(before[ln] - now)
                        before[ln] = now
                for ln in phase.lanes:
                    rates.setdefault(ln, []).append(left[ln] / (WINDOW[1] - WINDOW[0]))
    finally:
        traci.close()
    return rates


def main() -> None:
    result = {}
    with tempfile.TemporaryDirectory() as d:
        scn = SCENARIOS["simple"]
        samples: dict[str, list[float]] = {}
        for seed in SEEDS:
            for ln, r in measure(scn, seed, Path(d)).items():
                samples.setdefault(ln, []).extend(r)
        pooled = [x for v in samples.values() for x in v]
        result = {
            "mu": round(statistics.mean(pooled), 4),
            "sd": round(statistics.stdev(pooled), 4),
            "n": len(pooled),
            "veh_per_hour": round(statistics.mean(pooled) * 3600),
            "per_lane": {ln: round(statistics.mean(v), 4) for ln, v in samples.items()},
        }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
