"""Intersection definitions shared by every controller.

Each scenario lists its green phases as SUMO signal-state strings together
with the incoming lanes and pedestrian crossings each phase serves.  The
transition between two green phases (pedestrian clearance, amber, all-red) is
derived automatically from the two state strings, so the fixed-time, actuated
and adaptive controllers all use exactly the same safety intervals.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

SCENARIO_DIR = Path(__file__).resolve().parent.parent / "scenarios"

AMBER = 3            # vehicle amber [s]
ALL_RED = 2          # vehicle all-red clearance [s]
PED_SPEED = 1.2      # design walking speed for pedestrian clearance [m/s]


@dataclass(frozen=True)
class GreenPhase:
    name: str
    state: str                    # SUMO state string during green
    lanes: tuple[str, ...]        # incoming vehicle lanes served (C_k)
    crossings: tuple[str, ...]    # crossing edges served (V_k)


@dataclass(frozen=True)
class Scenario:
    name: str
    tl_id: str
    phases: tuple[GreenPhase, ...]
    crossing_links: frozenset[int]          # link indices that are crossings
    crossing_length: float                  # [m]
    route_template: str = "routes.template.xml"
    extra_sumo_args: tuple[str, ...] = field(default_factory=tuple)

    @property
    def net_file(self) -> Path:
        return SCENARIO_DIR / self.name / "net.net.xml"

    @property
    def ped_clearance(self) -> int:
        return math.ceil(self.crossing_length / PED_SPEED)

    def transition(self, src: int, dst: int) -> list[tuple[str, int]]:
        """Intermediate (state, duration) steps from green phase src to dst."""
        a, b = self.phases[src].state, self.phases[dst].state
        steps: list[tuple[str, int]] = []
        cur = list(a)

        def keeps_green(i: int) -> bool:
            return a[i] in "Gg" and b[i] in "Gg"

        # 1) pedestrian clearance: crossings losing green turn red first,
        #    vehicles keep their current signal.
        ped_losing = [i for i in range(len(a))
                      if i in self.crossing_links and a[i] in "Gg" and not keeps_green(i)]
        if ped_losing:
            for i in ped_losing:
                cur[i] = "r"
            steps.append(("".join(cur), self.ped_clearance))
        # 2) amber for vehicle links losing green
        veh_losing = [i for i in range(len(a))
                      if i not in self.crossing_links and a[i] in "Gg" and not keeps_green(i)]
        if veh_losing:
            for i in veh_losing:
                cur[i] = "y"
            steps.append(("".join(cur), AMBER))
            for i in veh_losing:
                cur[i] = "r"
            steps.append(("".join(cur), ALL_RED))
        return steps

    def lost_time(self, src: int, dst: int) -> int:
        """Time during which no *new* movement of dst can start."""
        return sum(d for _, d in self.transition(src, dst))


SIMPLE = Scenario(
    name="simple",
    tl_id="clusterJ2_J3",
    phases=(
        GreenPhase("vehicles", "GGrr", ("-E0_1", "E0_1"), ()),
        GreenPhase("pedestrians", "rrGG", (), (":clusterJ2_J3_c0", ":clusterJ2_J3_c1")),
    ),
    crossing_links=frozenset({2, 3}),
    crossing_length=6.4,
)

SHIBUYA = Scenario(
    name="shibuya",
    tl_id="clusterJ13_J14",
    phases=(
        # North-South vehicles (E3 from the north, -E3.200 from the south)
        # plus the two crossings parallel to them (over the E/W arms).
        GreenPhase("north-south", "gGgrrrgGgrrrrGrG", ("E3_1", "-E3.200_1"),
                   (":clusterJ13_J14_c1", ":clusterJ13_J14_c3")),
        # East-West vehicles (-E2.200 from the east, E2 from the west)
        # plus the crossings over the N/S arms.
        GreenPhase("east-west", "rrrgGgrrrgGgGrGr", ("-E2.200_1", "E2_1"),
                   (":clusterJ13_J14_c0", ":clusterJ13_J14_c2")),
    ),
    crossing_links=frozenset({12, 13, 14, 15}),
    crossing_length=6.5,
)

SCENARIOS = {s.name: s for s in (SIMPLE, SHIBUYA)}


# --------------------------------------------------------------------------
# Demand
# --------------------------------------------------------------------------

def write_routes(scenario: Scenario, out: Path, veh_scale: float = 1.0,
                 veh_overrides: dict[str, float] | None = None) -> Path:
    """Copy the scenario's route template scaling every vehicle flow.

    veh_scale multiplies the per-second insertion probability of every
    vehicle <flow>.  veh_overrides maps a flow id to an absolute probability
    (used for the unbalanced Shibuya experiment).  Pedestrian flows are left
    unchanged.
    """
    text = (SCENARIO_DIR / scenario.name / scenario.route_template).read_text()
    overrides = veh_overrides or {}

    def repl(m: re.Match) -> str:
        tag = m.group(0)
        fid = re.search(r'id="([^"]+)"', tag).group(1)
        p = float(re.search(r'probability="([^"]+)"', tag).group(1))
        new_p = overrides.get(fid, p * veh_scale)
        new_p = min(max(new_p, 0.0), 1.0)
        return re.sub(r'probability="[^"]+"', f'probability="{new_p:.5f}"', tag)

    text = re.sub(r"<flow [^>]*>", repl, text)
    out.write_text(text)
    return out


def vehicle_demand(scenario: Scenario, veh_scale: float = 1.0,
                   veh_overrides: dict[str, float] | None = None) -> dict[str, float]:
    """Expected vehicle arrivals per second on each incoming lane."""
    text = (SCENARIO_DIR / scenario.name / scenario.route_template).read_text()
    overrides = veh_overrides or {}
    demand: dict[str, float] = {}
    for m in re.finditer(r"<flow [^>]*>", text):
        tag = m.group(0)
        fid = re.search(r'id="([^"]+)"', tag).group(1)
        src = re.search(r'from="([^"]+)"', tag).group(1)
        p = float(re.search(r'probability="([^"]+)"', tag).group(1))
        lane = f"{src}_1"   # every approach has a single vehicle lane (index 1)
        demand[lane] = demand.get(lane, 0.0) + overrides.get(fid, p * veh_scale)
    return demand
