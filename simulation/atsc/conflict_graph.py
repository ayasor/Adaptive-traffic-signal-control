"""Conflict graph of a signalised junction (graph theory behind s_k).

Vertices are the movements controlled by the traffic light (one per SUMO
link: a vehicle movement or a pedestrian crossing).  Two vertices are joined
by an edge when the movements conflict: their paths cross or merge, so they
cannot both move freely at the same time.  SUMO stores this information in
the junction's <request> rows: bit j of `foes` says that link j conflicts
with this link, and bit j of `response` says that this link must give way to
link j when both have green.  (SUMO writes the bit for link 0 last.)

Two kinds of edges are distinguished, with the usual traffic-engineering
rule for permissive movements:

* weak (permissive): the conflict can be resolved by giving way, so both
  movements may have green together: vehicles from opposite approaches (a
  left turn yielding to oncoming traffic, or two movements merging into the
  same exit), and a turning vehicle crossing the pedestrian crossing that is
  parallel to its own approach (the vehicle yields to the pedestrians);
* strong: the signal itself must separate the movements: vehicles from
  perpendicular approaches, and a vehicle that enters from, or drives
  straight into, the arm a pedestrian crossing spans.

A safe phase is an independent set of the strong graph, and the minimum
number of phases is its chromatic number.
"""

from __future__ import annotations

import itertools
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConflictGraph:
    labels: dict[int, str]                                   # link index -> readable name
    strong: set[frozenset[int]] = field(default_factory=set)
    weak: set[frozenset[int]] = field(default_factory=set)

    @property
    def nodes(self) -> list[int]:
        return sorted(self.labels)

    def edges(self, include_weak: bool = False) -> set[frozenset[int]]:
        return self.strong | self.weak if include_weak else set(self.strong)

    def neighbours(self, v: int, include_weak: bool = False) -> set[int]:
        return {u for e in self.edges(include_weak) if v in e for u in e if u != v}

    def is_independent(self, vertices, include_weak: bool = False) -> bool:
        """True if no two of the vertices are joined by an edge."""
        es = self.edges(include_weak)
        return not any(frozenset(p) in es for p in itertools.combinations(vertices, 2))

    def chromatic_number(self, include_weak: bool = False) -> tuple[int, dict[int, int]]:
        """Exact chromatic number by backtracking (fine for a junction: < 30 vertices)."""
        order = sorted(self.nodes, key=lambda v: -len(self.neighbours(v, include_weak)))
        adj = {v: self.neighbours(v, include_weak) for v in self.nodes}
        for k in range(1, len(order) + 1):
            colour: dict[int, int] = {}

            def place(i: int) -> bool:
                if i == len(order):
                    return True
                v = order[i]
                used = {colour[u] for u in adj[v] if u in colour}
                for c in range(k):
                    if c not in used:
                        colour[v] = c
                        if place(i + 1):
                            return True
                        del colour[v]
                return False

            if place(0):
                return k, dict(colour)
        raise RuntimeError("unreachable")


def _bits(s: str) -> list[int]:
    """SUMO request bitstrings list link 0 last."""
    return [j for j, b in enumerate(reversed(s)) if b == "1"]


def load(net_file: Path, tl_id: str) -> ConflictGraph:
    root = ET.parse(net_file).getroot()
    junction = next(j for j in root.iter("junction") if j.get("id") == tl_id)
    foes = {}
    for r in junction.iter("request"):
        foes[int(r.get("index"))] = set(_bits(r.get("foes")))

    labels, move = {}, {}
    compass = _compass(root, tl_id)
    for c in root.iter("connection"):
        if c.get("tl") != tl_id:
            continue
        i = int(c.get("linkIndex"))
        frm, to = c.get("from"), c.get("to")
        if frm.startswith(":"):                      # pedestrian crossing
            arm = compass.get(_crossed_edge(root, to), "?")
            labels[i] = f"ped {arm}"
            move[i] = ("ped", arm, None, None)
        else:
            side, d = compass.get(frm, "?"), c.get("dir")
            labels[i] = f"{side} {d}"
            move[i] = ("veh", side, d, compass.get(to, "?"))

    g = ConflictGraph(labels)
    for i, js in foes.items():
        for j in js:
            if i != j:
                e = frozenset((i, j))
                (g.weak if _permissive(move[i], move[j]) else g.strong).add(e)
    return g


OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}


def _permissive(a, b) -> bool:
    """Can this conflict be resolved by giving way (see module docstring)?"""
    if a[0] == "ped" and b[0] == "ped":
        return True
    if a[0] == "veh" and b[0] == "veh":
        return OPPOSITE[a[1]] == b[1]
    veh, ped = (a, b) if a[0] == "veh" else (b, a)
    _, origin, direction, _exit = veh
    crossed = ped[1]
    turning = direction in ("l", "r", "L", "R")
    parallel = origin not in (crossed, OPPOSITE[crossed])
    return turning and parallel


def _compass(root, tl_id: str) -> dict[str, str]:
    """Name each incoming edge by the side of the junction it comes from."""
    node = next(j for j in root.iter("junction") if j.get("id") == tl_id)
    cx, cy = float(node.get("x")), float(node.get("y"))
    names = {}
    for e in root.iter("edge"):
        if e.get("function") or e.get("to") != tl_id and e.get("from") != tl_id:
            continue
        other = e.get("from") if e.get("to") == tl_id else e.get("to")
        oj = next(j for j in root.iter("junction") if j.get("id") == other)
        dx, dy = float(oj.get("x")) - cx, float(oj.get("y")) - cy
        side = ("E" if dx > 0 else "W") if abs(dx) >= abs(dy) else ("N" if dy > 0 else "S")
        names[e.get("id")] = side
    return names


def _crossed_edge(root, crossing_edge: str) -> str:
    e = next(e for e in root.iter("edge") if e.get("id") == crossing_edge)
    return e.get("crossingEdges").split()[0]
