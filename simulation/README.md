# Simulation code

Code used for chapters 6–8 of the English edition of the thesis.

## Quick start

```bash
python -m venv .venv
.venv/bin/pip install -r simulation/requirements.txt   # installs SUMO too
cd simulation
../.venv/bin/python -m unittest discover -s tests       # model unit tests
../.venv/bin/python calibrate_saturation.py             # measures mu  -> results/saturation_flow.json
../.venv/bin/python tune.py                             # parameter grid search (seeds 101-103)
../.venv/bin/python run_experiments.py                  # full evaluation (seeds 1-20) -> results/runs.jsonl
../.venv/bin/python analyze.py                          # tables + figures -> results/
```

Watch one run in the SUMO GUI:

```bash
../.venv/bin/python run_experiments.py --gui simple adaptive 1.0
```

`run_experiments.py` appends to `results/runs.jsonl` and skips simulations
that are already there, so it can be interrupted and resumed.

## Layout

| Path | Contents |
|---|---|
| `atsc/pressure.py` | Phase-pressure functional (pure functions, unit-tested) |
| `atsc/scenarios.py` | Phases, lanes and crossings of each intersection; safe transitions; demand scaling |
| `atsc/adaptive.py` | Adaptive controller (TraCI): sensors, pressure, control policy |
| `atsc/programs.py` | Baselines: Webster fixed-time plan and SUMO actuated program |
| `atsc/conflict_graph.py` | Conflict graph of a junction: independent sets and chromatic number |
| `atsc/runner.py` | Runs one simulation and computes the metrics from SUMO's tripinfo output |
| `scenarios/` | SUMO networks and route templates of both intersections |
| `calibrate_saturation.py` | Measures the saturation flow μ |
| `plot_conflict_graph.py` | Draws the Shibuya conflict graph → `docs/conflict-graph.png` |
| `record_gif.py` | Records the simulation GIF → `docs/shibuya-adaptive.gif` |
| `tune.py` | Grid search of T_max, T_crit and pedestrian weights on tuning seeds |
| `run_experiments.py` | Evaluation grid: scenarios × demand × controllers × 20 seeds |
| `analyze.py` | Means, 95 % confidence intervals, paired improvements, figures |
| `results/` | All raw results and generated tables/figures |

## The model

For each green phase *k*:

```
P_k = s_k [ Σ_{i∈C_k} w_i (N_i/μ_i) / (1 − ρ_i)  +  Σ_{j∈V_k} (β N_j + γ T_j + δ max(0, T_j − T_crit)) ]
ρ_i = min(λ_i / μ_i, 0.95)
```

The vehicle term is the time to clear the queue, `N / (μ − λ)`. The
controller activates `argmax_k P_k` subject to `T_min ≤ T_green ≤ T_max`.

## Implementation notes

1. **Formula.** The vehicle term uses the exact queue-clearing time
   `N / (μ − λ) = (N/μ) / (1 − λ/μ)`; `(1 + λ/μ)` is only its first-order
   approximation for light traffic. A unit test checks the implementation.
2. **Signal control.** Every signal is set explicitly with
   `setRedYellowGreenState`, so SUMO's static program never advances on its
   own. Every transition (pedestrian clearance, amber, all-red) is generated
   from the phase definitions, and a test checks that no transition gives
   green to two conflicting movements.
3. **Pedestrians.** Each phase counts only the pedestrians waiting at the
   crossings it opens.
4. **λ** is the number of vehicles *entering* the lane per second, averaged
   over a 60 s window.
5. **μ** is measured in SUMO with a queue-discharge experiment:
   ≈ 0.49 veh/s (≈ 1,780 veh/h per lane).
6. **Metrics.** All controllers are measured with the same code, from SUMO's
   `tripinfo` output.
7. **Baselines.** A Webster fixed-time plan and SUMO's actuated controller,
   with the same phases and transitions as the adaptive controller.
8. **Statistics.** 20 seeds per case, 95 % confidence intervals, paired
   comparisons, and a sweep over demand levels.

## Metrics

* **Vehicle delay** = `timeLoss + departDelay` from SUMO's tripinfo (time lost
  compared with driving at the desired speed, including the time spent
  waiting to enter a full road). Vehicles still in the network or not yet
  inserted when the simulation stops are included with their delay so far.
* **Vehicle waiting time** = time spent below 0.1 m/s.
* **Pedestrian waiting time** = SUMO `waitingTime`, averaged over the people
  who used a signalised crossing.
* **Throughput** = vehicles that completed their trip during the first hour.
* **CO₂ / NOx** = SUMO's HBEFA emission model, per vehicle.

Demand is generated for 3,600 s; the simulation then runs until the network
is empty or for at most 1,800 s more.
