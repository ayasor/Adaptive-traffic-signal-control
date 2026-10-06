"""Record the adaptive controller at the Shibuya-type junction as an animated GIF.

Usage:  python record_gif.py [output.gif]   (default: docs/shibuya-adaptive.gif)

Runs the real SUMO simulation (headless) with the project's AdaptiveController,
and draws every frame from SUMO's vehicle/pedestrian positions and signal states.
"""
import math
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "simulation"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from PIL import Image
import sumolib
import traci

from atsc.adaptive import AdaptiveController, AdaptiveParams
from atsc.runner import load_mu
from atsc.scenarios import SHIBUYA, write_routes
from atsc.sumo_env import sumo_binary

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "docs" / "shibuya-adaptive.gif"
SCALE, WARMUP, RECORD, SEED = 0.5, 300, 150, 7
CX, CY, HALF_W, HALF_H = -100.0, 0.0, 38.0, 38.0

BG, ROAD, WALK, NODE = "#E9ECE4", "#3B4150", "#CBCFC6", "#454B5B"
MOVING, STOPPED, PED = "#8EC5FF", "#F2A93B", "#F7F4EC"
SIG = {"G": "#1BAF7A", "g": "#1BAF7A", "y": "#F2A93B", "r": "#D9534F", "s": "#D9534F", "o": "#888888"}
INK, SOFT = "#14213D", "#4A5568"

net = sumolib.net.readNet(str(SHIBUYA.net_file), withInternal=True, withPedestrianConnections=True)
mu = load_mu(REPO / "simulation/results/saturation_flow.json")


def lane_poly(shape, width):
    """Offset a lane centre-line into a polygon."""
    left, right = [], []
    for i, (x, y) in enumerate(shape):
        x0, y0 = shape[max(i - 1, 0)]
        x1, y1 = shape[min(i + 1, len(shape) - 1)]
        dx, dy = x1 - x0, y1 - y0
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n * width / 2, dx / n * width / 2
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    return left + right[::-1]


# static layers ---------------------------------------------------------------
static = []
for e in net.getEdges(withInternal=True):
    fn = e.getFunction()
    for ln in e.getLanes():
        shp = ln.getShape()
        if fn == "walkingarea":
            static.append(("walk", shp))
        elif fn == "crossing":
            static.append(("cross", lane_poly(shp, ln.getWidth()), ln.getID()))
        elif fn == "internal":
            continue
        else:
            kind = "walk" if ln.allows("pedestrian") and not ln.allows("passenger") else "road"
            static.append((kind, lane_poly(shp, ln.getWidth())))
node_shape = net.getNode(SHIBUYA.tl_id).getShape()

with tempfile.TemporaryDirectory() as tmp:
    routes = write_routes(SHIBUYA, Path(tmp) / "r.rou.xml", SCALE)
    traci.start([sumo_binary(), "-n", str(SHIBUYA.net_file), "-r", str(routes), "--seed", str(SEED),
                 "--no-warnings", "--no-step-log"])
    ctrl = AdaptiveController(SHIBUYA, mu, AdaptiveParams())
    links = traci.trafficlight.getControlledLinks(SHIBUYA.tl_id)
    # one signal head per incoming vehicle lane: its first link index
    heads = {}
    for idx, lk in enumerate(links):
        if not lk:
            continue
        inlane = lk[0][0]
        if inlane.startswith(":"):
            continue
        heads.setdefault(inlane, idx)
    cross_idx = {}
    for idx, lk in enumerate(links):
        if lk and lk[0][1].startswith(f":{SHIBUYA.tl_id}_c"):
            cross_idx[lk[0][1].rsplit("_", 1)[0] + "_0"] = idx

    for _ in range(WARMUP):
        traci.simulationStep()
        ctrl.step()

    frames = []
    for k in range(RECORD):
        traci.simulationStep()
        ctrl.step()
        t = traci.simulation.getTime()
        state = traci.trafficlight.getRedYellowGreenState(SHIBUYA.tl_id)
        vehs = [(traci.vehicle.getPosition(v), traci.vehicle.getAngle(v), traci.vehicle.getSpeed(v))
                for v in traci.vehicle.getIDList()]
        peds = [traci.person.getPosition(p) for p in traci.person.getIDList()]
        P = ctrl.pressures()
        mode = "transition" if (ctrl.queue_steps or ctrl.target is not None) else "green"

        fig = plt.figure(figsize=(10, 6), dpi=80, facecolor=BG)
        ax = fig.add_axes([0.0, 0.0, 0.6, 1.0])
        ax.set_xlim(CX - HALF_W, CX + HALF_W)
        ax.set_ylim(CY - HALF_H, CY + HALF_H)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor(BG)
        fig.patches.append(Rectangle((0, 0), 0.6, 1, transform=fig.transFigure, color=BG, zorder=-1))
        for item in static:
            if item[0] == "road":
                ax.add_patch(Polygon(item[1], closed=True, color=ROAD, lw=0))
            elif item[0] == "walk":
                ax.add_patch(Polygon(item[1], closed=True, color=WALK, lw=0))
        ax.add_patch(Polygon(node_shape, closed=True, color=NODE, lw=0))
        for item in static:
            if item[0] == "cross":
                i = cross_idx.get(item[2])
                col = SIG.get(state[i], "#FFFFFF") if i is not None else "#FFFFFF"
                ax.add_patch(Polygon(item[1], closed=True, facecolor="#F4F4F0", edgecolor=col, lw=2.5, hatch="||"))
        for lane, idx in heads.items():
            x, y = net.getLane(lane).getShape()[-1]
            ax.add_patch(plt.Circle((x, y), 1.5, color=SIG.get(state[idx], "#888"), zorder=5, ec="#10182C", lw=1.2))
        for (x, y), ang, sp in vehs:
            a = math.radians(90 - ang)
            L, Wd = 4.6, 1.9
            dx, dy = math.cos(a), math.sin(a)
            # SUMO position = front bumper
            cx_, cy_ = x - dx * L / 2, y - dy * L / 2
            px, py = -dy, dx
            pts = [(cx_ + dx * L / 2 + px * Wd / 2, cy_ + dy * L / 2 + py * Wd / 2),
                   (cx_ + dx * L / 2 - px * Wd / 2, cy_ + dy * L / 2 - py * Wd / 2),
                   (cx_ - dx * L / 2 - px * Wd / 2, cy_ - dy * L / 2 - py * Wd / 2),
                   (cx_ - dx * L / 2 + px * Wd / 2, cy_ - dy * L / 2 + py * Wd / 2)]
            ax.add_patch(Polygon(pts, closed=True, color=STOPPED if sp < 0.1 else MOVING, zorder=6))
        for (x, y) in peds:
            ax.add_patch(plt.Circle((x, y), 0.5, color=PED, ec=INK, lw=0.8, zorder=7))

        # side panel -----------------------------------------------------------
        pa = fig.add_axes([0.6, 0.0, 0.4, 1.0])
        pa.set_xlim(0, 1)
        pa.set_ylim(0, 1)
        pa.axis("off")
        pa.add_patch(Rectangle((0, 0), 1, 1, color="#14213D"))
        pa.text(0.08, 0.92, "Adaptive traffic light", color="#F7F4EC", fontsize=17, weight="bold")
        pa.text(0.08, 0.865, "phase-pressure controller in SUMO", color="#C9D2E3", fontsize=12)
        mx = max(30.0, *P)
        names = ["North–South", "East–West"]
        for j, (name, v) in enumerate(zip(names, P)):
            y0 = 0.68 - j * 0.19
            active = (ctrl.current == j and mode == "green")
            pa.text(0.08, y0 + 0.055, f"Pressure {name}", color="#C9D2E3", fontsize=13)
            pa.add_patch(Rectangle((0.08, y0 - 0.02), 0.84, 0.055, color="#1E2E52"))
            pa.add_patch(Rectangle((0.08, y0 - 0.02), 0.84 * min(v / mx, 1), 0.055,
                                   color="#1BAF7A" if active else "#2A78D6"))
            pa.text(0.9, y0 - 0.005, f"{v:.0f}", color="#F7F4EC", fontsize=13, ha="right", va="bottom")
        ph = names[ctrl.current if ctrl.target is None else ctrl.target]
        status = f"Green: {names[ctrl.current]}" if mode == "green" else f"Changing to {ph}"
        pa.text(0.08, 0.25, status, color="#F2A93B" if mode != "green" else "#1BAF7A", fontsize=14, weight="bold")
        pa.text(0.08, 0.19, f"t = {int(t)} s", color="#C9D2E3", fontsize=12)
        pa.add_patch(Rectangle((0.08, 0.075), 0.05, 0.035, color=STOPPED))
        pa.text(0.16, 0.08, "stopped", color="#C9D2E3", fontsize=11)
        pa.add_patch(Rectangle((0.36, 0.075), 0.05, 0.035, color=MOVING))
        pa.text(0.44, 0.08, "moving", color="#C9D2E3", fontsize=11)
        pa.add_patch(plt.Circle((0.66, 0.092), 0.014, color=PED))
        pa.text(0.69, 0.08, "pedestrian", color="#C9D2E3", fontsize=11)

        fig.canvas.draw()
        img = Image.frombuffer("RGBA", fig.canvas.get_width_height(), fig.canvas.buffer_rgba()).convert("RGB")
        frames.append(img)
        plt.close(fig)
    traci.close()

pal = frames[len(frames) // 2].convert("P", palette=Image.ADAPTIVE, colors=64)
q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
q[0].save(OUT, save_all=True, append_images=q[1:], duration=125, loop=0, optimize=True)
print("frames", len(frames), "size", OUT.stat().st_size)
