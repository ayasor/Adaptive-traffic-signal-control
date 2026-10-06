"""Run one simulation and compute the evaluation metrics.

All three controllers are evaluated with *identical* measurement code: the
metrics come from SUMO's own tripinfo / statistics output, never from the
controller.  The TraCI loop is used for every controller only to (a) drive
the adaptive controller and (b) note which pedestrians used a signalised
crossing, so that pedestrian waiting times are averaged over the people who
actually had to wait for the signal.
"""

from __future__ import annotations

import json
import math
import statistics
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import traci

from .adaptive import AdaptiveController, AdaptiveParams
from .pressure import PedestrianWeights
from .programs import webster, write_actuated, write_fixed_time
from .scenarios import SCENARIOS, vehicle_demand, write_routes
from .sumo_env import sumo_binary

DEMAND_END = 3600     # vehicles and pedestrians are generated during 1 h
CLEARANCE = 1800      # then up to 30 min more to let the queues empty


@dataclass
class RunSpec:
    scenario: str
    controller: str            # "fixed" | "actuated" | "adaptive"
    seed: int
    veh_scale: float = 1.0
    variant: str = "balanced"  # "balanced" | "unbalanced"
    t_max: int = 90            # maximum green (adaptive and actuated)
    t_crit: float = 90.0       # critical pedestrian waiting time (adaptive)
    ped_scale: float = 1.0     # multiplies beta and gamma (adaptive)


UNBALANCED = {  # thesis, Shibuya simulation 2: one busy approach (from the west)
    "shibuya": {f"f_{i}": 0.007 for i in range(3, 12)},
}


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    i = (len(s) - 1) * q
    lo, hi = math.floor(i), math.ceil(i)
    return s[lo] + (s[hi] - s[lo]) * (i - lo)


def run(spec: RunSpec, mu: dict[str, float], workdir: Path, gui: bool = False) -> dict:
    scn = SCENARIOS[spec.scenario]
    workdir.mkdir(parents=True, exist_ok=True)
    tag = (f"{spec.scenario}_{spec.variant}_{spec.veh_scale:g}_{spec.controller}_{spec.seed}"
           f"_{spec.t_max}_{spec.t_crit:g}_{spec.ped_scale:g}")
    overrides = UNBALANCED.get(spec.scenario) if spec.variant == "unbalanced" else None
    routes = write_routes(scn, workdir / f"{tag}.rou.xml", spec.veh_scale, overrides)
    tripinfo, stats = workdir / f"{tag}.tripinfo.xml", workdir / f"{tag}.stats.xml"

    cmd = [sumo_binary(gui), "-n", str(scn.net_file), "-r", str(routes),
           "--seed", str(spec.seed), "--end", str(DEMAND_END + CLEARANCE),
           "--tripinfo-output", str(tripinfo), "--tripinfo-output.write-unfinished",
           "--statistic-output", str(stats), "--device.emissions.probability", "1",
           "--no-step-log", "--no-warnings", "--duration-log.disable"]
    plan = None
    if spec.controller == "fixed":
        plan = webster(scn, vehicle_demand(scn, spec.veh_scale, overrides), mu)
        cmd += ["-a", str(write_fixed_time(scn, plan, workdir / f"{tag}.tls.xml"))]
    elif spec.controller == "actuated":
        cmd += ["-a", str(write_actuated(scn, workdir / f"{tag}.tls.xml", spec.t_max))]
    if gui:
        cmd += ["--start", "--delay", "50"]

    traci.start(cmd, label=tag)
    conn = traci.getConnection(tag)
    traci.switch(tag)
    crossed: set[str] = set()
    crossing_prefix = f":{scn.tl_id}_c"
    green_states = {p.state for p in scn.phases}
    last_state, greens_started = None, 0
    try:
        ctrl = None
        if spec.controller == "adaptive":
            base = PedestrianWeights()
            ped = replace(base, beta=base.beta * spec.ped_scale,
                          gamma=base.gamma * spec.ped_scale, t_crit=spec.t_crit)
            ctrl = AdaptiveController(scn, mu, AdaptiveParams(t_max=spec.t_max, ped=ped))
        while True:
            t = conn.simulation.getTime()
            if t >= DEMAND_END + CLEARANCE:
                break
            if t >= DEMAND_END and conn.simulation.getMinExpectedNumber() == 0:
                break
            conn.simulationStep()
            if ctrl:
                ctrl.step()
            for p in conn.person.getIDList():
                if conn.person.getRoadID(p).startswith(crossing_prefix):
                    crossed.add(p)
            state = conn.trafficlight.getRedYellowGreenState(scn.tl_id)
            if state != last_state and state in green_states:
                greens_started += 1
            last_state = state
        sim_end = conn.simulation.getTime()
    finally:
        traci.close()

    metrics = evaluate(tripinfo, stats, crossed, sim_end)
    metrics.update(asdict(spec))
    metrics["green_phases_started"] = greens_started
    metrics["mean_cycle_s"] = sim_end / (greens_started / len(scn.phases)) if greens_started else None
    if plan:
        metrics["webster_cycle_s"] = round(plan.cycle, 1)
        metrics["webster_greens_s"] = [round(g, 1) for g in plan.greens]
    for f in (routes, tripinfo, stats):
        f.unlink(missing_ok=True)
    return metrics


def evaluate(tripinfo: Path, stats: Path, crossed: set[str], sim_end: float) -> dict:
    root = ET.parse(tripinfo).getroot()
    veh_delay, veh_wait, co2, nox, fuel = [], [], 0.0, 0.0, 0.0
    arrived_in_hour = 0
    for ti in root.iter("tripinfo"):
        arrival = float(ti.get("arrival"))
        if 0 <= arrival <= DEMAND_END:
            arrived_in_hour += 1
        veh_delay.append(float(ti.get("timeLoss")) + float(ti.get("departDelay")))
        veh_wait.append(float(ti.get("waitingTime")))
        em = ti.find("emissions")
        if em is not None:
            co2 += float(em.get("CO2_abs"))
            nox += float(em.get("NOx_abs"))
            fuel += float(em.get("fuel_abs"))
    finished = sum(1 for ti in root.iter("tripinfo") if float(ti.get("arrival")) >= 0)

    ped_wait = []
    for pi in root.iter("personinfo"):
        if pi.get("id") in crossed:
            ped_wait.append(float(pi.get("waitingTime")))

    st = ET.parse(stats).getroot()
    vehicles = st.find("vehicles")
    loaded = int(vehicles.get("loaded"))
    not_inserted = int(vehicles.get("waiting"))
    trip_stats = st.find("vehicleTripStatistics")
    backlog_delay = not_inserted * float(trip_stats.get("departDelayWaiting") or 0)
    teleports = int(st.find("teleports").get("total"))

    total_delay = sum(veh_delay) + max(backlog_delay, 0.0)
    n_veh = len(veh_delay) + not_inserted
    return {
        "veh_loaded": loaded,
        "veh_finished": finished,
        "veh_not_inserted": not_inserted,
        "throughput_vph": arrived_in_hour,             # vehicles/hour that completed the trip in the first hour
        "veh_delay_mean_s": total_delay / n_veh if n_veh else float("nan"),
        "veh_wait_mean_s": statistics.fmean(veh_wait) if veh_wait else float("nan"),
        "veh_wait_p95_s": percentile(veh_wait, 0.95),
        "ped_crossing_n": len(ped_wait),
        "ped_wait_mean_s": statistics.fmean(ped_wait) if ped_wait else float("nan"),
        "ped_wait_p95_s": percentile(ped_wait, 0.95),
        "ped_wait_max_s": max(ped_wait) if ped_wait else float("nan"),
        "co2_g_per_veh": co2 / 1000 / len(veh_delay) if veh_delay else float("nan"),
        "nox_g_per_veh": nox / 1000 / len(veh_delay) if veh_delay else float("nan"),
        "fuel_g_per_veh": fuel / 1000 / len(veh_delay) if veh_delay else float("nan"),
        "teleports": teleports,
        "sim_end_s": sim_end,
    }


def load_mu(path: Path) -> dict[str, float]:
    """Saturation flow of every incoming lane (calibrate_saturation.py).
    All approaches share the same geometry, so one value is used for all."""
    mu = json.loads(path.read_text())["mu"]
    return {ln: mu for scn in SCENARIOS.values() for ph in scn.phases for ln in ph.lanes}
