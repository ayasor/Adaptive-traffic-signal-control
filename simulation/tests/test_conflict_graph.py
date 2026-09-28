"""Tests for the conflict graph (graph theory behind the safety factor s_k).

Run with:  python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from atsc.conflict_graph import ConflictGraph, load  # noqa: E402
from atsc.scenarios import SHIBUYA, SIMPLE  # noqa: E402


def green(phase):
    return [i for i, c in enumerate(phase.state) if c in "Gg"]


class Colouring(unittest.TestCase):
    def test_triangle_needs_three_colours(self):
        g = ConflictGraph({0: "a", 1: "b", 2: "c"},
                          strong={frozenset((0, 1)), frozenset((1, 2)), frozenset((0, 2))})
        self.assertEqual(g.chromatic_number()[0], 3)

    def test_colouring_is_proper(self):
        g = load(SHIBUYA.net_file, SHIBUYA.tl_id)
        k, colour = g.chromatic_number(include_weak=True)
        for e in g.edges(include_weak=True):
            a, b = tuple(e)
            self.assertNotEqual(colour[a], colour[b])


class Junctions(unittest.TestCase):
    def test_every_phase_is_an_independent_set(self):
        for scn in (SIMPLE, SHIBUYA):
            g = load(scn.net_file, scn.tl_id)
            for ph in scn.phases:
                self.assertTrue(g.is_independent(green(ph)), (scn.name, ph.name))

    def test_two_phases_are_the_minimum(self):
        for scn in (SIMPLE, SHIBUYA):
            g = load(scn.net_file, scn.tl_id)
            self.assertEqual(g.chromatic_number()[0], len(scn.phases))

    def test_fully_protected_shibuya_needs_four_phases(self):
        g = load(SHIBUYA.net_file, SHIBUYA.tl_id)
        self.assertEqual(g.chromatic_number(include_weak=True)[0], 4)

    def test_weak_conflicts_inside_a_phase_give_way(self):
        # a weak conflict allowed inside a phase must involve a movement that
        # yields (lower-case 'g') or a pedestrian crossing, which has priority
        g = load(SHIBUYA.net_file, SHIBUYA.tl_id)
        for ph in SHIBUYA.phases:
            on = set(green(ph))
            for e in g.weak:
                if e <= on:
                    self.assertTrue(any(ph.state[i] == "g" for i in e), (ph.name, e))


if __name__ == "__main__":
    unittest.main()
