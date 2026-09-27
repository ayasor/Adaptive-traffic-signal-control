# Simulation code (revised, 2026)

Code used for chapters 6–8 of the English edition of the thesis. It replaces
the scripts in `Catalan/Annexos (CAT)/Annex 2`, which are kept only for
reference (see "What was fixed" below).

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
| `atsc/runner.py` | Runs one simulation and computes the metrics from SUMO's tripinfo output |
| `scenarios/` | SUMO networks and route templates (unchanged from the original thesis) |
| `calibrate_saturation.py` | Measures the saturation flow μ |
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

## What was fixed with respect to the original scripts

1. **Formula.** The original code computed `(N/μ) / (1 + λ/μ)`, so pressure
   *decreased* with saturation. The thesis derives `(N/μ)(1 + λ/μ)`, a
   first-order approximation of the exact `(N/μ) / (1 − λ/μ)` used now.
2. **Signal control.** `traci.trafficlight.setPhase` let SUMO's static
   program keep advancing (5 s pedestrian phase in the simple network), and in
   the Shibuya network phase indices pointed at amber/green phases of the
   wrong direction. Signals are now set explicitly with
   `setRedYellowGreenState` and every transition (pedestrian clearance, amber,
   all-red) is generated from the phase definitions.
3. **Pedestrians in Shibuya** were added equally to every phase, so they never
   influenced a decision. Now each phase counts only the crossings it opens.
4. **λ** was estimated as the absolute change in the number of vehicles on the
   lane; it is now the number of vehicles *entering* the lane per second.
5. **μ** was 1.8 veh/s (6,480 veh/h per lane); it is now measured: ≈ 0.49 veh/s.
6. **Metrics** were computed differently in each script (the fixed-time
   pedestrian waiting time was always 0). All controllers are now measured
   with the same code from SUMO's `tripinfo` output.
7. **Baseline.** The original fixed-time plan had a 10 s amber and arbitrary
   greens. Baselines are now a Webster fixed-time plan and SUMO's actuated
   controller, with the same transitions as the adaptive controller.
8. **Statistics.** One run per case → 20 seeds per case, 95 % confidence
   intervals, paired comparisons, and a sweep over demand levels.

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
