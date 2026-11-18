"""Max-pressure controller (Varaiya 2013), used as a reference baseline.

Max-pressure is the standard benchmark for adaptive signal control in the
literature: it is decentralised and, under stable demand, provably maximises
the throughput of a network.  Its rule is

    every slot of Delta seconds:  activate argmax_k  sum_{i in C_k} (N_i - N_out(i))

where N_i is the queue on an incoming lane and N_out(i) the queue on the lanes
it feeds.  Compared with the phase-pressure controller it has no saturation
factor 1/(1 - rho), no arrival-rate estimate and no pedestrian waiting-time
terms: waiting pedestrians simply count as queued road users.

To compare like with like it reuses the adaptive controller's sensors and
transitions, and the same T_MIN / T_MAX rules:
  * decisions are taken only at the end of each slot (slot = T_MIN);
  * at T_MAX it switches to the best *other* phase if that phase has demand,
    which bounds how long pedestrians can wait.
"""

from __future__ import annotations

import traci

from .adaptive import AdaptiveController, AdaptiveParams, LaneSensor
from .pressure import max_pressure
from .scenarios import Scenario


class MaxPressureController(AdaptiveController):
    def __init__(self, scn: Scenario, mu: dict[str, float], params: AdaptiveParams):
        super().__init__(scn, mu, params)
        self.slot = params.t_min
        self.downstream: dict[str, list[str]] = {}
        out_lanes: set[str] = set()
        for ln in self.lanes:
            outs = sorted({link[0] for link in traci.lane.getLinks(ln)})
            self.downstream[ln] = outs
            out_lanes.update(outs)
        self.out_sensors = {ln: LaneSensor(ln) for ln in out_lanes}

    def pressures(self) -> list[float]:
        peds = self.crossings.read()
        out = []
        for ph in self.scn.phases:
            lanes = [(self.lanes[ln].queue(),
                      [self.out_sensors[o].queue() for o in self.downstream[ln]])
                     for ln in ph.lanes]
            crossings = [peds.get(c, (0, 0.0))[0] for c in ph.crossings]
            out.append(max_pressure(lanes, crossings))
        return out

    def step(self) -> None:
        """Call once after every traci.simulationStep()."""
        for s in (*self.lanes.values(), *self.out_sensors.values()):
            s.update()

        if self.queue_steps or self.target is not None:
            self._advance_transition()
            return

        self.t_green += 1
        k = self.current
        if self.t_green >= self.p.t_max:
            P = self.pressures()
            others = [j for j in range(len(P)) if j != k]
            best = max(others, key=lambda j: P[j])
            if P[best] > 0:
                self._start_transition(best)
            return
        if self.t_green < self.p.t_min or self.t_green % self.slot:
            return
        P = self.pressures()
        best = max(range(len(P)), key=lambda j: P[j])
        if best != k and P[best] > P[k]:
            self._start_transition(best)
