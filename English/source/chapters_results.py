"""Chapter 8 (results), chapter 11 (conclusions) and the results sentence of the
abstract.  All numbers are computed from simulation/results."""

from __future__ import annotations

import results_data as R
from docbuilder import Doc

FIG = R.RES / "figures"
CTRL = ("fixed", "actuated", "adaptive")
SIMPLE_LEVELS = (0.25, 0.5, 0.75, 1.0)
SHIBUYA_LEVELS = (0.2, 0.3, 0.4, 0.5, 0.75, 1.0)

_rows = None
_sum = None


def _data():
    global _rows, _sum
    if _rows is None:
        _rows, _sum = R.runs(), R.summary()
    return _rows, _sum


def S(scn, scale, ctrl, metric, variant="balanced"):
    return _data()[1][(scn, variant, scale, ctrl)][metric]


def CI(scn, scale, ctrl, metric, variant="balanced"):
    return _data()[1][(scn, variant, scale, ctrl)][metric + "_ci95"]


def M(scn, scale, metric, base, variant="balanced"):
    """Paired improvement of adaptive over base: (mean, ci, wins, n)."""
    return R.paired(_data()[0], scn, variant, scale, metric, base)


def pct(x: float) -> str:
    return f"{abs(x) * 100:.0f} %"


def m_cell(scn, scale, metric, base, variant="balanced") -> str:
    m, ci, w, n = M(scn, scale, metric, base, variant)
    return f"{m * 100:+.0f} ± {ci * 100:.0f} % ({w}/{n})"


def val(scn, scale, ctrl, metric, variant="balanced", nd=1) -> str:
    return R.fmt(S(scn, scale, ctrl, metric, variant), CI(scn, scale, ctrl, metric, variant), nd)


def change(scn, scale, metric, a="adaptive", b="fixed", variant="balanced") -> float:
    """Relative change of the means, (a - b) / b."""
    return (S(scn, scale, a, metric, variant) - S(scn, scale, b, metric, variant)) / \
        S(scn, scale, b, metric, variant)


def person(scn, scale, ctrl, variant="balanced"):
    return R.group_mean(_data()[0], scn, variant, scale, ctrl, R.person_delay_per_person)


# --------------------------------------------------------------------------------------
def abstract_results() -> str:
    s_ped = [-change("simple", x, "ped_wait_mean_s") for x in SIMPLE_LEVELS]
    s_veh = [change("simple", x, "veh_delay_mean_s") for x in SIMPLE_LEVELS]
    sh = -change("shibuya", 1.0, "veh_delay_mean_s")
    th = change("shibuya", 1.0, "throughput_vph")
    return (
        "Each case was simulated with 20 random seeds. In the simple crossing, the adaptive "
        "controller "
        f"gives vehicles practically the same delay as the Webster plan ({min(s_veh)*100:+.0f} "
        f"to {max(s_veh)*100:+.0f} %) while cutting pedestrian waiting by "
        f"{min(s_ped)*100:.0f}–{max(s_ped)*100:.0f} %. In the collapsed Shibuya-type "
        f"intersection it reduces vehicle delay by {sh*100:.0f} % and increases throughput by "
        f"{th*100:.0f} %, but at intermediate demand the fixed-time plan remains better. The "
        "adaptive controller outperforms SUMO’s actuated controller in almost every case. "
        "The hypothesis is therefore only partially confirmed: adaptive control helps most "
        "when the intersection is saturated or the demand is unbalanced, and a well-designed "
        "fixed-time plan is a strong competitor otherwise.")


# --------------------------------------------------------------------------------------
def chapter_8(doc: Doc, f: dict) -> None:
    doc.h("8. Results and analysis", 1, page_break=True)
    doc.p("Once the simulations had been completed, the results were collected and analysed.")
    _methodology(doc, f)
    _simple(doc)
    _shibuya(doc)
    _unbalanced(doc)
    _emissions(doc)
    _conclusions_comparative(doc)


def _methodology(doc: Doc, f: dict) -> None:
    doc.h("8.1 Methodology and evaluation metrics", 2)
    doc.p("Vehicle and pedestrian flows are random: every second, each flow inserts a new "
          "vehicle or pedestrian with a certain probability. This stochastic component "
          "reproduces the variability of real traffic, but it also means that a single "
          "simulation can be lucky or unlucky. Therefore:")
    doc.bullets([
        f"Every case (intersection × demand level × controller) was simulated with "
        f"**{f['seeds']} different random seeds** (1–{f['seeds']}). The three controllers use "
        "the same seeds, so they face exactly the same sequence of arrivals, and they can be "
        "compared *seed by seed* (paired comparison).",
        "Results are given as the **mean ± the half-width of the 95 % confidence "
        "interval** (Student’s t distribution). If two intervals do not overlap, the "
        "difference is very unlikely to be due to chance.",
        "Vehicle demand was varied from low to very high as a percentage of the demand of "
        "the route files (100 %), while pedestrian demand was kept at its base "
        "value. This shows how each controller behaves from light traffic to collapse.",
        "Demand is generated for one hour; the simulation then continues (up to 30 more "
        "minutes) until the queues have emptied.",
    ])
    doc.p("All controllers are measured with the same SUMO output (tripinfo), never with "
          "values computed by the controllers themselves. The metrics are:")
    doc.bullets([
        "**Mean vehicle delay** (primary metric): time lost by each vehicle compared with "
        "driving at its desired speed (SUMO’s *timeLoss*), plus the time it had to wait "
        "before it could even enter a full road (*departDelay*). Vehicles still queuing when "
        "the simulation stops are included with their delay so far, so a controller cannot "
        "look good by leaving vehicles out.",
        "**Mean vehicle waiting time** (Wᵥ): time spent stopped (speed below 0.1 m/s).",
        "**Mean pedestrian waiting time** (Wₚ): time spent standing still by the "
        "pedestrians who used a signalised crossing. The longest wait is also reported, "
        "to check the no-starvation property of section 6.5.4.",
        "**Throughput**: vehicles that completed their trip during the first hour.",
        "**Delay per person**: vehicle delay counted 1.2 times (average car occupancy) plus "
        "pedestrian waiting, divided by the number of people. It weighs one second of a "
        "person waiting equally in a car or on foot.",
        "**CO₂ per vehicle**: from SUMO’s HBEFA emission model (section 8.5).",
    ])
    doc.p("To quantify the improvement, the following ratio is computed for each seed and "
          "then averaged:")
    doc.equation(r"m=\frac{W_{ref}-W_{adapt}}{W_{ref}}")
    doc.p("If m > 0 the adaptive controller is better than the reference (fixed-time or "
          "actuated); if m < 0 the reference is better. In the tables, the number in "
          "brackets is the number of seeds in which the adaptive controller was better, "
          "for example (18/20).")


def _level_table(doc, scn, levels, metric, caption, nd=1):
    rows = [[f"{x * 100:.0f} %"] + [val(scn, x, c, metric, nd=nd) for c in CTRL] for x in levels]
    doc.table(["Demand", "Fixed-time (Webster)", "Actuated", "Adaptive"], rows, caption=caption,
              widths_cm=[2.2, 4.3, 4.3, 4.3])


def _m_table(doc, scn, levels, caption, extra_throughput=False):
    header = ["Demand", "Vehicle delay vs fixed", "vs actuated", "Pedestrian wait vs fixed",
              "vs actuated", "Delay per person vs fixed"]
    rows = []
    for x in levels:
        rows.append([f"{x * 100:.0f} %",
                     m_cell(scn, x, "veh_delay_mean_s", "fixed"),
                     m_cell(scn, x, "veh_delay_mean_s", "actuated"),
                     m_cell(scn, x, "ped_wait_mean_s", "fixed"),
                     m_cell(scn, x, "ped_wait_mean_s", "actuated"),
                     m_cell(scn, x, R.person_delay_per_person, "fixed")])
    doc.table(header, rows, caption=caption, widths_cm=[1.7, 3.0, 2.8, 3.0, 2.8, 3.0],
              font_size=8)


def _simple(doc: Doc) -> None:
    doc.h("8.2 Simple intersection: two-way road with a pedestrian crossing", 2)
    doc.image(FIG / "simple_demand_sweep.png",
              "Simple intersection: results as a function of vehicle demand (100 % = the "
              "base demand of 0.3 vehicles/s per direction).", 16)
    _level_table(doc, "simple", SIMPLE_LEVELS, "veh_delay_mean_s",
                 "Simple intersection: mean vehicle delay [s] (mean ± 95 % CI, 20 seeds).")
    _level_table(doc, "simple", SIMPLE_LEVELS, "ped_wait_mean_s",
                 "Simple intersection: mean pedestrian waiting time [s].")
    _m_table(doc, "simple", SIMPLE_LEVELS,
             "Simple intersection: improvement m of the adaptive controller (paired by seed; "
             "positive = adaptive better).")

    veh = [change("simple", x, "veh_delay_mean_s") for x in SIMPLE_LEVELS]
    dsec = [S("simple", x, "adaptive", "veh_delay_mean_s") - S("simple", x, "fixed",
            "veh_delay_mean_s") for x in SIMPLE_LEVELS]
    ped = [-change("simple", x, "ped_wait_mean_s") for x in SIMPLE_LEVELS]
    pers = [M("simple", x, R.person_delay_per_person, "fixed")[0] for x in SIMPLE_LEVELS]
    act_v = [M("simple", x, "veh_delay_mean_s", "actuated")[0] for x in SIMPLE_LEVELS]
    act_p100 = M("simple", 1.0, "ped_wait_mean_s", "actuated")[0]
    thr = [abs(change("simple", x, "throughput_vph")) for x in SIMPLE_LEVELS]
    pmax = S("simple", 1.0, "adaptive", "ped_wait_max_s")
    cyc_f, cyc_a = S("simple", 1.0, "fixed", "mean_cycle_s"), S("simple", 1.0, "adaptive", "mean_cycle_s")

    doc.p("**Vehicles.** With the adaptive controller, vehicles lose practically the same "
          "time as with the Webster fixed-time plan: the difference is between "
          f"{min(dsec):+.1f} and {max(dsec):+.1f} s per vehicle ({min(veh)*100:+.0f} to "
          f"{max(veh)*100:+.0f} %), slightly in favour of the fixed-time plan. This is "
          "expected: Webster’s method is designed precisely to minimise vehicle delay when "
          "the demand is known and constant, which is exactly the situation simulated here. "
          "The throughput is the same for all controllers (differences below "
          f"{max(thr)*100:.1f} %), because at this intersection all of them can serve all the "
          "vehicles. Compared with the actuated controller, however, the adaptive one reduces "
          f"vehicle delay by {min(act_v)*100:.0f}–{max(act_v)*100:.0f} % at every demand level; "
          "at 100 % demand the actuated controller starts to struggle, because it serves the "
          "pedestrian phase every cycle even when nobody is waiting.")
    doc.p("**Pedestrians.** This is where the adaptive controller makes a clear difference. "
          f"Pedestrians wait {min(ped)*100:.0f}–{max(ped)*100:.0f} % less than with the "
          "fixed-time plan, in all 20 seeds of every demand level. The fixed-time plan gives "
          f"vehicles long greens (its cycle reaches {cyc_f:.0f} s at 100 % demand) and "
          "pedestrians must wait for the next cycle regardless of how many are waiting; the "
          "adaptive controller opens the crossing when the pedestrian pressure justifies it "
          f"(mean cycle {cyc_a:.0f} s). Only at 100 % demand does the actuated controller give "
          f"pedestrians shorter waits ({pct(act_p100)} less than adaptive), at the cost of "
          "doubling the vehicle delay.")
    doc.p("**Per person.** Counting everyone who waits, the adaptive controller reduces the "
          f"delay per person by {min(pers)*100:.0f}–{max(pers)*100:.0f} % compared with the "
          "fixed-time plan. The longest pedestrian wait observed with the adaptive controller "
          f"was {pmax:.0f} s (mean of the maximum over the 20 seeds at 100 % demand), just "
          f"above T_crit = 90 s: the δ term of section 6.2.1.3 does guarantee that nobody "
          "waits indefinitely, but with the calibrated T_crit the guarantee only acts after a "
          "long wait.")


def _shibuya(doc: Doc) -> None:
    doc.h("8.3 Shibuya-type intersection", 2)
    doc.image(FIG / "shibuya_demand_sweep.png",
              "Shibuya-type intersection: results as a function of vehicle demand (100 % = "
              "the base demand of 756 vehicles/h per approach). The delay axis is "
              "logarithmic.", 16)
    _level_table(doc, "shibuya", SHIBUYA_LEVELS, "veh_delay_mean_s",
                 "Shibuya-type intersection: mean vehicle delay [s].", nd=0)
    _level_table(doc, "shibuya", SHIBUYA_LEVELS, "throughput_vph",
                 "Shibuya-type intersection: throughput in the first hour [veh/h].", nd=0)
    _level_table(doc, "shibuya", SHIBUYA_LEVELS, "ped_wait_mean_s",
                 "Shibuya-type intersection: mean pedestrian waiting time [s].")
    _m_table(doc, "shibuya", SHIBUYA_LEVELS,
             "Shibuya-type intersection: improvement m of the adaptive controller (paired by "
             "seed; positive = adaptive better).")

    cap = max(S("shibuya", x, c, "throughput_vph") for x in SHIBUYA_LEVELS for c in CTRL)
    d = {x: S("shibuya", x, "adaptive", "veh_delay_mean_s") for x in SHIBUYA_LEVELS}
    df = {x: S("shibuya", x, "fixed", "veh_delay_mean_s") for x in SHIBUYA_LEVELS}
    m75, m100 = (M("shibuya", x, "veh_delay_mean_s", "fixed")[0] for x in (0.75, 1.0))
    th75, th100 = (change("shibuya", x, "throughput_vph") for x in (0.75, 1.0))
    p100 = -change("shibuya", 1.0, "ped_wait_mean_s")
    cyc_f100 = S("shibuya", 1.0, "fixed", "mean_cycle_s")
    cyc_a100 = S("shibuya", 1.0, "adaptive", "mean_cycle_s")
    act = [M("shibuya", x, "veh_delay_mean_s", "actuated")[0] for x in SHIBUYA_LEVELS]

    doc.p("**A collapsed intersection.** The first thing the figure shows is that this "
          "intersection cannot serve the base demand with *any* of the controllers. Its "
          f"real capacity is about {cap:,.0f} vehicles/hour, far below the 3,024 vehicles/hour "
          "of the route file: from about 40 % of the base demand onwards, "
          "queues grow during the whole hour and the delay reaches many minutes per vehicle "
          "(most of it waiting to enter the network). The reason is geometric: each approach "
          "has a single lane shared by all movements, so a vehicle waiting to turn left "
          "(which must give way to oncoming traffic and to pedestrians) blocks all the "
          "vehicles behind it.")
    doc.p(f"**Low demand (20 %).** With little traffic the three controllers are similar "
          f"(delays around {df[0.2]:.0f}–{d[0.2]:.0f} s); the adaptive and fixed-time "
          "controllers are statistically indistinguishable.")
    doc.p(f"**Intermediate demand (30–50 %).** Here the fixed-time plan is the best: at 30 % "
          f"demand the adaptive controller has a mean delay of {d[0.3]:.0f} s against "
          f"{df[0.3]:.0f} s for Webster, and it loses in most seeds up to 50 %, although the "
          "difference shrinks as demand grows (at 50 % it is no longer significant). The most "
          "likely explanation is a limitation of the model itself: the vehicle term assumes "
          "that a queue is discharged at the saturation flow μ, but in a shared lane blocked "
          "by a left-turning vehicle (one of the weak conflicts of section 6.2.2) almost nobody moves. The controller then sees a long "
          "queue with high pressure and keeps giving it green even though that green is "
          "being wasted, while the fixed plan simply moves on after a short, regular green.")
    doc.p(f"**Saturation (75–100 %).** When the intersection is completely saturated, the "
          f"adaptive controller becomes the best one: it reduces vehicle delay by "
          f"{m75*100:.0f} % and {m100*100:.0f} % compared with the fixed-time plan and "
          f"increases throughput by {th75*100:.0f} % and {th100*100:.0f} %, with lower "
          f"pedestrian waits ({pct(p100)} less at 100 %). Webster’s formula is not designed "
          f"for this situation: as the flow ratios approach 1 it prescribes ever longer "
          f"cycles (the maximum, {cyc_f100:.0f} s, at 100 % demand), and long greens are "
          f"wasted behind blocked left-turners. The adaptive controller keeps changing phase every "
          f"~{cyc_a100 / 2:.0f} s (cycle {cyc_a100:.0f} s), which regularly clears the blocked "
          "vehicles.")
    doc.p("**Against the actuated controller**, the adaptive one is better at every demand "
          f"level ({min(act)*100:.0f}–{max(act)*100:.0f} % less vehicle "
          "delay), and pedestrians also wait less. SUMO’s actuated controller keeps extending "
          "the green while vehicles cross its detectors, which here produces very long "
          "cycles (around 100 s) and long waits for everyone else.")


def _unbalanced(doc: Doc) -> None:
    doc.h("8.4 Shibuya-type intersection with unbalanced demand", 2)
    doc.p("A second Shibuya experiment was run in which one "
          "approach carries much more traffic than the others: the three flows from the "
          "west keep their probability of 0.07 vehicles/s each, while all the other flows "
          "are reduced to 0.007. An adaptive controller should be especially useful here, "
          "since the demand is very different from one direction to another.")
    doc.image(FIG / "shibuya_unbalanced.png",
              "Shibuya-type intersection with unbalanced demand (20 seeds).", 15)
    metrics = [("veh_delay_mean_s", "Mean vehicle delay [s]", 0),
               ("veh_wait_mean_s", "Mean vehicle waiting time [s]", 1),
               ("throughput_vph", "Throughput [veh/h]", 0),
               ("ped_wait_mean_s", "Mean pedestrian waiting time [s]", 1),
               ("ped_wait_max_s", "Longest pedestrian wait [s]", 0),
               ("co2_g_per_veh", "CO₂ per vehicle [g]", 0)]
    rows = [[label] + [val("shibuya", 1.0, c, m, "unbalanced", nd) for c in CTRL]
            for m, label, nd in metrics]
    doc.table(["Metric", "Fixed-time (Webster)", "Actuated", "Adaptive"], rows,
              caption="Shibuya-type intersection with unbalanced demand.",
              widths_cm=[5.0, 3.6, 3.6, 3.6])
    mf = M("shibuya", 1.0, "veh_delay_mean_s", "fixed", "unbalanced")
    ma = M("shibuya", 1.0, "veh_delay_mean_s", "actuated", "unbalanced")
    wf = -change("shibuya", 1.0, "veh_wait_mean_s", variant="unbalanced")
    doc.p(f"The adaptive controller reduces vehicle delay by {mf[0]*100:.0f} ± {mf[1]*100:.0f} % "
          f"compared with the fixed-time plan (better in {mf[2]}/{mf[3]} seeds) and the time "
          f"vehicles spend stopped by {wf*100:.0f} %. Compared with the actuated controller the "
          f"difference in delay ({ma[0]*100:+.0f} ± {ma[1]*100:.0f} %) is not significant. "
          "Throughput is similar for the three controllers, and pedestrians wait about the "
          "same with the adaptive and fixed-time controllers (the differences are within the "
          "confidence intervals), so the priority given to the busy approach does not "
          "penalise pedestrians.")


def _emissions(doc: Doc) -> None:
    doc.h("8.5 Emissions and the question of Barcelona", 2)
    doc.p("SUMO can estimate the emissions of every vehicle with the HBEFA model, which "
          "takes into account the speed and acceleration of the vehicle at every second (a "
          "car that stops and starts again emits more than one that keeps moving). Table "
          f"{doc.tab_no + 1} gives the CO₂ emitted per vehicle while crossing the network.")
    rows = []
    for scn, x, var, label in (("simple", 0.5, "balanced", "Simple, 50 %"),
                               ("simple", 1.0, "balanced", "Simple, 100 %"),
                               ("shibuya", 0.3, "balanced", "Shibuya, 30 %"),
                               ("shibuya", 1.0, "balanced", "Shibuya, 100 %"),
                               ("shibuya", 1.0, "unbalanced", "Shibuya, unbalanced")):
        rows.append([label] + [val(scn, x, c, "co2_g_per_veh", var, 0) for c in CTRL]
                    + [f"{change(scn, x, 'co2_g_per_veh', variant=var)*100:+.0f} %"])
    doc.table(["Case", "Fixed-time", "Actuated", "Adaptive", "Adaptive vs fixed"], rows,
              caption="CO₂ emitted per vehicle [g] (HBEFA model in SUMO).",
              widths_cm=[3.8, 2.9, 2.9, 2.9, 3.0])
    doc.p("Emissions follow the delays: they are lower with the adaptive controller where "
          "it reduces stop-and-go traffic (saturated and unbalanced Shibuya) and slightly "
          "higher where the fixed-time plan keeps vehicles moving better (simple "
          "intersection, Shibuya at intermediate demand).")
    doc.p("At intersections that are saturated or have strongly unbalanced demand, an "
          "adaptive controller can reduce delay and emissions by around 5–15 % compared with "
          "a well-designed fixed-time plan, and by more compared with a simple actuated "
          "controller. Estimating the effect for a whole city such as Barcelona would require "
          "simulating a real part of the city (for example an Eixample corridor) with "
          "measured traffic counts, since a single isolated intersection does not represent "
          "a whole road network.")


def _conclusions_comparative(doc: Doc) -> None:
    doc.h("8.6 Conclusions of the comparative study", 2)
    act_all = [M(s, x, "veh_delay_mean_s", "actuated")[0]
               for s, levels in (("simple", SIMPLE_LEVELS), ("shibuya", SHIBUYA_LEVELS))
               for x in levels]
    doc.p("Going back to the hypothesis of chapter 2 (*an adaptive system based on a "
          "mathematical optimisation model will reduce the mean delay of vehicles compared "
          "with conventional fixed-time systems*), the simulations lead to the "
          "following verdict:")
    doc.bullets([
        "**Partially confirmed.** Against a fixed-time plan designed with Webster’s method, "
        "the adaptive controller reduces vehicle delay only when the intersection is "
        "saturated (7–10 %) or the demand is strongly unbalanced (about 15 %). With light "
        "traffic it performs the same, in the simple intersection it is marginally worse for "
        "vehicles (a few tenths of a second), and in the Shibuya intersection at "
        "intermediate demand (30–40 %) it is clearly worse.",
        "**Confirmed against actuated control.** Compared with SUMO’s actuated controller, "
        f"which represents the actuated signals already present in Barcelona, the adaptive "
        f"controller reduced vehicle delay in {sum(1 for x in act_all if x > 0)} of the "
        f"{len(act_all)} demand levels studied, often by a wide margin.",
        "**Pedestrians benefit.** The explicit pedestrian term makes the biggest difference: "
        "in the simple intersection pedestrians wait around a third less than with the "
        "fixed-time plan at no real cost to vehicles, so the delay per person is lower at "
        "every demand level.",
        "**The model has a clear weak point.** It assumes that a queue always discharges at "
        "the saturation flow. In shared lanes with permissive left turns this is false, and "
        "the controller can keep a green that is not being used.",
    ])
    doc.p("These results are consistent with the scientific literature: "
          "adaptive control is most valuable where demand is high or changes, while for "
          "stable and moderate demand a well-designed fixed-time plan is hard to beat. Although "
          "they come from a virtual environment, they show the real potential, and the real "
          "limits, of this kind of system.")


# --------------------------------------------------------------------------------------
def chapter_11(doc: Doc, f: dict) -> None:
    doc.h("11. Conclusions", 1, page_break=True)
    doc.p("This research project set out to design an adaptive traffic light algorithm based "
          "on a mathematical model and to check, by simulation, whether it improves on the "
          "traffic lights used today. The phase-pressure model developed in chapter 6 "
          "combines two ideas: from queueing theory, the time needed to clear each queue, "
          "N/(μ − λ); and, for pedestrians, a pressure that grows with the number of people "
          "waiting and with their waiting time, with an extra term that prevents anyone from "
          "being forgotten. At every second, the traffic light gives green to the phase "
          "with the highest pressure, within minimum and maximum green times.")
    doc.p("After implementing the algorithm in SUMO, measuring the capacity of the lanes, "
          "calibrating the parameters on separate simulations and comparing it against a "
          "Webster fixed-time plan and an actuated controller with 20 repetitions per case, "
          "the conclusions are:")
    doc.bullets([
        "The adaptive algorithm works: it serves vehicles and pedestrians safely, adapts its "
        "cycle to the demand and never leaves anyone waiting indefinitely.",
        "It is clearly better than a conventional actuated controller in almost all the "
        "situations studied.",
        "Compared with a well-designed fixed-time plan, it is better when the intersection "
        "is saturated or the demand is unbalanced (7–15 % less vehicle delay and more "
        "throughput), equivalent with little traffic, and worse at intermediate demand (30–40 %) in an "
        "intersection with shared left-turn lanes. The hypothesis is therefore only "
        "partially confirmed.",
        "Its main advantage is for pedestrians: in the simple crossing they wait about a "
        "third less without any real cost for vehicles.",
    ])
    doc.p("The work has also taught me something that goes beyond traffic: a result is only "
          "as good as the method used to obtain it. A single simulation, a weak reference or "
          "two programs that measure different things can produce very convincing numbers "
          "that are simply wrong. Measuring everything in the same way, repeating the "
          "experiments and comparing against the best alternative is what makes a result "
          "trustworthy, even when it is less spectacular.")
    doc.p("Finally, this project is only a first step towards intelligent and coordinated "
          "traffic management. The next steps would be to correct the weak point found "
          "(estimating how fast each queue is really moving instead of assuming the "
          "saturation flow), to take into account the cost of each phase change, and to "
          "extend the model to networks of coordinated intersections, possibly with "
          "machine-learning techniques. Overall, the project shows that the combination of "
          "mathematics, computer simulation and technology can be a key tool for building "
          "more efficient, safer and more sustainable cities, as long as the results are "
          "tested honestly.")
