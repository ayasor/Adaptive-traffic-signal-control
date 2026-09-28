"""Draw the conflict graph of the Shibuya-type junction.

Vertices are the 16 signalised movements, placed by the side of the junction
they belong to; solid edges are strong conflicts (must be separated by the
signal), dashed edges are weak ones (resolved by giving way).  Vertices are
coloured with the phase that serves them, which is a proper colouring of the
strong graph with chi = 2 colours.

Usage:  python plot_conflict_graph.py   -> docs/conflict-graph.png
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from atsc.conflict_graph import load  # noqa: E402
from atsc.scenarios import SHIBUYA  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "docs" / "conflict-graph.png"
PHASE_COLOUR = ["#2a78d6", "#eb6834"]            # north-south, east-west
SIDE_ANGLE = {"N": 90, "E": 0, "S": 270, "W": 180}
DIR_NAME = {"s": "straight", "l": "left", "r": "right"}


def positions(g):
    pos = {}
    for v, lab in g.labels.items():
        kind, side = ("ped", lab.split()[1]) if lab.startswith("ped") else ("veh", lab.split()[0])
        base = SIDE_ANGLE[side]
        if kind == "ped":
            r, off = 0.45, 0
        else:
            r, off = 1.0, {"r": -22, "s": 0, "l": 22}[lab.split()[1]]
        a = math.radians(base + off)
        pos[v] = (r * math.cos(a), r * math.sin(a))
    return pos


def label(lab: str) -> str:
    if lab.startswith("ped"):
        return f"crossing\n{lab.split()[1]} arm"
    side, d = lab.split()
    return f"from {side}\n{DIR_NAME[d]}"


def main() -> None:
    g = load(SHIBUYA.net_file, SHIBUYA.tl_id)
    phase_of = {}
    for k, ph in enumerate(SHIBUYA.phases):
        for i, c in enumerate(ph.state):
            if c in "Gg":
                phase_of[i] = k
    pos = positions(g)

    fig, ax = plt.subplots(figsize=(9, 9), dpi=150)
    ax.set_aspect("equal")
    ax.axis("off")
    for e in g.weak:
        a, b = tuple(e)
        ax.plot(*zip(pos[a], pos[b]), color="#b5b4ad", lw=1.3, ls=(0, (4, 3)), zorder=1)
    for e in g.strong:
        a, b = tuple(e)
        ax.plot(*zip(pos[a], pos[b]), color="#52514e", lw=1.4, zorder=2)
    for v, (x, y) in pos.items():
        ped = g.labels[v].startswith("ped")
        ax.scatter([x], [y], s=1500 if not ped else 1700, color=PHASE_COLOUR[phase_of[v]],
                   marker="s" if ped else "o", edgecolor="#fbfaf6", linewidth=2.5, zorder=3)
        ax.text(x, y, label(g.labels[v]), ha="center", va="center", fontsize=7.2,
                color="white", weight="bold", zorder=4)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.35, 1.3)
    handles = [
        plt.Line2D([], [], marker="o", ls="", ms=12, color=PHASE_COLOUR[0], label="Phase 1: north–south"),
        plt.Line2D([], [], marker="o", ls="", ms=12, color=PHASE_COLOUR[1], label="Phase 2: east–west"),
        plt.Line2D([], [], color="#52514e", lw=1.6, label=f"Strong conflict ({len(g.strong)})"),
        plt.Line2D([], [], color="#b5b4ad", lw=1.6, ls=(0, (4, 3)), label=f"Weak conflict, give way ({len(g.weak)})"),
    ]
    ax.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=9,
              bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout()
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, facecolor="white")
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
