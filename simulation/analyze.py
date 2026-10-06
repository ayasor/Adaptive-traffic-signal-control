"""Aggregate results/runs.jsonl into tables and figures.

For every (scenario, variant, demand, controller) the mean over the seeds and
a 95 % confidence interval (Student t) are reported.  Improvements of the
adaptive controller are computed *paired by seed* (same random demand for all
controllers) as  m = (W_baseline - W_adaptive) / W_baseline,  the same
improvement ratio the thesis defines in section 8.1.

Outputs: results/summary.csv, results/comparison.json, results/figures/*.png
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"
FIG = RESULTS / "figures"
CONTROLLERS = ("fixed", "actuated", "adaptive")
LABEL = {"fixed": "Fixed-time (Webster)", "actuated": "Actuated (SUMO)",
         "adaptive": "Adaptive (phase pressure)"}
COLOR = {"fixed": "#2a78d6", "actuated": "#eb6834", "adaptive": "#1baf7a"}
MARKER = {"fixed": "s", "actuated": "^", "adaptive": "o"}
METRICS = {
    "veh_delay_mean_s": "Mean vehicle delay [s]",
    "veh_wait_mean_s": "Mean vehicle waiting time [s]",
    "veh_wait_p95_s": "95th pct. vehicle waiting time [s]",
    "throughput_vph": "Throughput in the first hour [veh/h]",
    "ped_wait_mean_s": "Mean pedestrian waiting time [s]",
    "ped_wait_p95_s": "95th pct. pedestrian waiting time [s]",
    "ped_wait_max_s": "Max. pedestrian waiting time [s]",
    "co2_g_per_veh": "CO2 per vehicle [g]",
    "nox_g_per_veh": "NOx per vehicle [g]",
    "mean_cycle_s": "Mean cycle length [s]",
    "teleports": "Teleports",
}
# 97.5 % Student-t quantiles for small samples (df = n - 1)
T975 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26,
        10: 2.23, 11: 2.20, 12: 2.18, 13: 2.16, 14: 2.14, 15: 2.13, 16: 2.12, 17: 2.11,
        18: 2.10, 19: 2.09, 20: 2.09, 25: 2.06, 30: 2.04}


def t975(df: int) -> float:
    if df in T975:
        return T975[df]
    return 1.96 if df > 30 else T975[min(k for k in T975 if k >= df)]


def mean_ci(v: list[float]) -> tuple[float, float]:
    v = [x for x in v if x is not None and not math.isnan(x)]
    if not v:
        return float("nan"), float("nan")
    m = statistics.fmean(v)
    if len(v) < 2:
        return m, float("nan")
    return m, t975(len(v) - 1) * statistics.stdev(v) / math.sqrt(len(v))


def load(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line]
    # keep only the default-parameter runs written by run_experiments.py
    return rows


def main() -> None:
    rows = load(RESULTS / "runs.jsonl")
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        groups[(r["scenario"], r["variant"], r["veh_scale"], r["controller"])].append(r)

    FIG.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "summary.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "variant", "veh_scale", "controller", "n_seeds"]
                   + [x for m in METRICS for x in (m, m + "_ci95")])
        for key in sorted(groups):
            g = groups[key]
            vals = []
            for m in METRICS:
                mean, ci = mean_ci([r[m] for r in g])
                vals += [round(mean, 3), round(ci, 3)]
            w.writerow([*key, len(g)] + vals)

    # paired improvements of adaptive vs each baseline
    comparison = []
    for (scn, var, scale, ctrl), g in sorted(groups.items()):
        if ctrl != "adaptive":
            continue
        by_seed = {r["seed"]: r for r in g}
        entry = {"scenario": scn, "variant": var, "veh_scale": scale}
        for base in ("fixed", "actuated"):
            b = {r["seed"]: r for r in groups.get((scn, var, scale, base), [])}
            seeds = sorted(set(by_seed) & set(b))
            for m in ("veh_delay_mean_s", "veh_wait_mean_s", "ped_wait_mean_s", "co2_g_per_veh"):
                ratios = [(b[s][m] - by_seed[s][m]) / b[s][m] for s in seeds if b[s][m]]
                mean, ci = mean_ci(ratios)
                wins = sum(1 for s in seeds if by_seed[s][m] < b[s][m])
                entry[f"m_{m}_vs_{base}"] = {"mean": round(mean, 4), "ci95": round(ci, 4),
                                             "adaptive_better_in": f"{wins}/{len(seeds)}"}
        comparison.append(entry)
    (RESULTS / "comparison.json").write_text(json.dumps(comparison, indent=2))

    plot_sweeps(groups)
    plot_unbalanced(groups)
    print(f"wrote {RESULTS/'summary.csv'}, {RESULTS/'comparison.json'} and figures in {FIG}")


def _style(ax, title: str, ylabel: str, xlabel: str | None = None) -> None:
    ax.set_title(title, fontsize=10, loc="left", color="#0b0b0b")
    ax.set_ylabel(ylabel, fontsize=9, color="#52514e")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=9, color="#52514e")
    ax.grid(True, color="#e6e5e0", linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#b5b4ad")
    ax.tick_params(colors="#52514e", labelsize=8)


def plot_sweeps(groups) -> None:
    panels = ["veh_delay_mean_s", "ped_wait_mean_s", "throughput_vph", "co2_g_per_veh"]
    for scn, title in (("simple", "Simple intersection"), ("shibuya", "Shibuya-type intersection")):
        fig, axes = plt.subplots(2, 2, figsize=(9, 6.5))
        for ax, metric in zip(axes.flat, panels):
            ys = []
            for ctrl in CONTROLLERS:
                pts = sorted((k[2], mean_ci([r[metric] for r in g]))
                             for k, g in groups.items()
                             if k[0] == scn and k[1] == "balanced" and k[3] == ctrl)
                if not pts:
                    continue
                x = [p[0] * 100 for p in pts]
                y = [p[1][0] for p in pts]
                e = [0 if math.isnan(p[1][1]) else p[1][1] for p in pts]
                ax.plot(x, y, color=COLOR[ctrl], marker=MARKER[ctrl], markersize=6,
                        linewidth=2, label=LABEL[ctrl])
                ax.fill_between(x, [a - b for a, b in zip(y, e)], [a + b for a, b in zip(y, e)],
                                color=COLOR[ctrl], alpha=0.15, linewidth=0)
                ys += y
            if ys and min(ys) > 0 and max(ys) / min(ys) > 20:   # delays spanning decades
                ax.set_yscale("log")
                ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
                    lambda v, _: f"{v:,.0f}"))
                ax.set_title(METRICS[metric] + " (log scale)", fontsize=10, loc="left")
            _style(ax, ax.get_title(loc="left") or METRICS[metric], "",
                   "Vehicle demand [% of original]")
        handles, labels = axes.flat[0].get_legend_handles_labels()
        fig.suptitle(f"{title}: mean of 20 seeds, shaded band = 95 % confidence interval",
                     fontsize=11, y=0.99, x=0.01, ha="left")
        fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.955),
                   ncol=3, frameon=False, fontsize=9)
        fig.tight_layout(rect=(0, 0, 1, 0.925))
        fig.savefig(FIG / f"{scn}_demand_sweep.png", dpi=200)
        plt.close(fig)


def plot_unbalanced(groups) -> None:
    metrics = ["veh_delay_mean_s", "veh_wait_mean_s", "ped_wait_mean_s", "throughput_vph"]
    fig, axes = plt.subplots(2, 2, figsize=(9, 6))
    for ax, metric in zip(axes.flat, metrics):
        top = 0.0
        for i, ctrl in enumerate(CONTROLLERS):
            g = groups.get(("shibuya", "unbalanced", 1.0, ctrl), [])
            m, ci = mean_ci([r[metric] for r in g])
            ci = 0.0 if math.isnan(ci) else ci
            ax.bar(i, m, width=0.6, color=COLOR[ctrl], label=LABEL[ctrl], yerr=ci, capsize=3,
                   error_kw={"ecolor": "#52514e", "linewidth": 1})
            ax.annotate(f"{m:,.0f}", (i, m + ci), xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8, color="#0b0b0b")
            top = max(top, m + ci)
        ax.set_ylim(0, top * 1.15)
        ax.set_xticks([])
        _style(ax, METRICS[metric], "")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.suptitle("Shibuya-type intersection, unbalanced demand: mean of 20 seeds, "
                 "error bar = 95 % CI", fontsize=11, y=0.99, x=0.01, ha="left")
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.95),
               ncol=3, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(FIG / "shibuya_unbalanced.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
