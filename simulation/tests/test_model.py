"""Unit tests for the parts of the model that do not need SUMO.

Run with:  python -m unittest discover -s tests
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from atsc.pressure import (PedestrianWeights, pedestrian_pressure, phase_pressure,  # noqa: E402
                           saturation_factor, vehicle_pressure)
from atsc.programs import webster  # noqa: E402
from atsc.scenarios import AMBER, ALL_RED, SHIBUYA, SIMPLE, vehicle_demand  # noqa: E402


class VehiclePressure(unittest.TestCase):
    def test_equals_queue_clearance_time(self):
        # 10 vehicles, mu = 0.5 veh/s, lambda = 0.25 veh/s -> 10 / (0.5 - 0.25) = 40 s
        self.assertAlmostEqual(vehicle_pressure(10, 0.25, 0.5), 40.0)

    def test_grows_with_saturation(self):
        low = vehicle_pressure(5, 0.1, 0.5)
        high = vehicle_pressure(5, 0.4, 0.5)
        self.assertGreater(high, low)

    def test_taylor_is_first_order_of_exact(self):
        # for rho << 1 the exact factor matches the original (1 + rho)
        rho = 0.01
        self.assertAlmostEqual(saturation_factor(rho, 1.0), 1 + rho, places=3)

    def test_capped_when_oversaturated(self):
        self.assertTrue(math.isfinite(vehicle_pressure(5, 2.0, 0.5)))
        self.assertAlmostEqual(saturation_factor(2.0, 0.5), 1 / (1 - 0.95))

    def test_empty_lane_has_no_pressure(self):
        self.assertEqual(vehicle_pressure(0, 0.4, 0.5), 0.0)


class PedestrianPressure(unittest.TestCase):
    w = PedestrianWeights(beta=2.0, gamma=0.2, delta=5.0, t_crit=30.0)  # explicit, not defaults

    def test_below_critical_time(self):
        self.assertAlmostEqual(pedestrian_pressure(3, 20.0, self.w), 2 * 3 + 0.2 * 20)

    def test_starvation_term(self):
        self.assertAlmostEqual(pedestrian_pressure(1, 40.0, self.w), 2 + 0.2 * 40 + 5 * 10)

    def test_no_pedestrians(self):
        self.assertEqual(pedestrian_pressure(0, 0.0, self.w), 0.0)


class PhasePressure(unittest.TestCase):
    def test_incompatible_phase_is_zero(self):
        self.assertEqual(phase_pressure([(5, 0.2, 0.5, 1.0)], [(2, 10.0)], s_k=0.0), 0.0)

    def test_sum_of_terms(self):
        w = PedestrianWeights()
        p = phase_pressure([(4, 0.0, 0.5, 1.0), (2, 0.0, 0.5, 2.0)], [(1, 0.0)], w)
        self.assertAlmostEqual(p, 8 + 8 + w.beta)


class Transitions(unittest.TestCase):
    def test_vehicle_to_pedestrian(self):
        steps = SIMPLE.transition(0, 1)
        self.assertEqual(steps, [("yyrr", AMBER), ("rrrr", ALL_RED)])

    def test_pedestrian_to_vehicle_has_clearance(self):
        steps = SIMPLE.transition(1, 0)
        self.assertEqual(steps, [("rrrr", SIMPLE.ped_clearance)])

    def test_no_conflicting_greens_during_transition(self):
        for a, b in ((0, 1), (1, 0)):
            for state, _ in SHIBUYA.transition(a, b):
                ns = any(state[i] in "Gg" for i in (0, 1, 2, 6, 7, 8))
                ew = any(state[i] in "Gg" for i in (3, 4, 5, 9, 10, 11))
                self.assertFalse(ns and ew, state)

    def test_shibuya_crossings_clear_before_amber(self):
        steps = SHIBUYA.transition(0, 1)
        self.assertEqual(steps[0][0], "gGgrrrgGgrrrrrrr")
        self.assertEqual(steps[1][0], "yyyrrryyyrrrrrrr")


class Webster(unittest.TestCase):
    def test_cycle_formula(self):
        mu = {ln: 0.5 for p in SIMPLE.phases for ln in p.lanes}
        plan = webster(SIMPLE, vehicle_demand(SIMPLE, 0.5), mu)
        Y = 0.15 / 0.5
        self.assertAlmostEqual(plan.cycle, (1.5 * plan.lost_time + 5) / (1 - Y))
        self.assertAlmostEqual(sum(plan.greens) + plan.lost_time - 10, plan.cycle)


if __name__ == "__main__":
    unittest.main()
