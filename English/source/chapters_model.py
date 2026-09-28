"""Chapters 6 (mathematical model) and 7 (simulation), revised in the 2026 edition."""

from __future__ import annotations

from pathlib import Path

from docbuilder import Doc

IMG = Path(__file__).resolve().parent / "images"


def chapter_6(doc: Doc, f: dict) -> None:
    doc.h("6. Mathematical model of the adaptive control system", 1, page_break=True)
    doc.p("To optimise traffic at an intersection by means of its traffic lights, I have "
          "developed an adaptive mathematical model based on *phase pressure*:")
    doc.bullets([
        "The main objective is to prioritise vehicles without forgetting pedestrians, "
        "guaranteeing safety and fluidity.",
        "The model is general, applicable to any type of intersection and adaptive in real "
        "time, without depending heavily on traffic predictions, given the great "
        "variability of traffic.",
    ])

    doc.h("6.1 State space and definition of variables", 2)
    doc.p("Consider a single intersection regulated by a finite set of compatible signal "
          "phases. The system is modelled in discrete time, with a step of one second:")
    doc.equation(r"t=0,1,2,\ldots\qquad t\in\mathbb{N}", numbered=False)
    doc.p("Let X(t) be the state vector of the system at time t:")
    doc.equation(r"X(t)=\left\{N_i(t),\ \lambda_i(t),\ \mu_i,\ N_v^j(t),\ T_v^j(t),\ F(t)\right\}")
    doc.p("where:")
    doc.bullets([
        "**Nᵢ(t)**: number of vehicles in the queue of lane i at time t. *How it is obtained:* "
        "vehicles detected in the last "
        f"{f['detection_zone']:.0f} m before the stop line, as a camera or a long loop "
        "detector would see them. Example: if there are 7 cars in that zone of lane 1 at "
        "t = 2, N₁(2) = 7.",
        "**λᵢ(t)**: arrival rate of vehicles (vehicles/s) at lane i. *How it is obtained:* "
        "number of vehicles that have *entered* the lane during the last "
        f"{f['arrival_window']} s, divided by {f['arrival_window']}. Example: if one "
        "vehicle arrives every 5 seconds, λ₁ = 0.2 veh/s.",
        "**μᵢ**: service rate (saturation flow) of lane i: the number of vehicles per "
        "second that leave a long queue when the light is green. It is a property of the "
        "lane and was measured in the simulator (section 7.2): "
        f"μ = {f['mu']:.3f} veh/s ≈ {f['mu_vph']} veh/h.",
        "**N_v^j(t)**: number of pedestrians waiting at crossing j at time t (people "
        "standing on the waiting area in front of that crossing). Example: if 5 "
        "pedestrians are waiting at crossing 1, N_v¹ = 5.",
        "**T_v^j(t)**: waiting time of the pedestrian who has waited longest at crossing j. "
        "Example: if the oldest pedestrian at crossing 2 has been waiting for 40 seconds, "
        "T_v² = 40.",
        "**F(t)**: active phase at time t.",
    ])

    doc.h("6.2 Definition of the dynamic prioritisation functional", 2)
    doc.p("To decide which phase to activate, a pressure functional is associated with each "
          "phase k:")
    doc.equation(r"P_k\left(X(t)\right)=s_k\left[\sum_{i\in C_k}w_i\,\frac{N_i}{\mu_i}\,"
                 r"\frac{1}{1-\rho_i}+\sum_{j\in V_k}\left(\beta N_v^j+\gamma T_v^j+"
                 r"\delta\,\max\left(0,\,T_v^j-T_{crit}\right)\right)\right]", fontsize=14)
    doc.equation(r"\rho_i=\min\left(\frac{\lambda_i}{\mu_i},\ \rho_{max}\right),\qquad "
                 r"\rho_{max}=" + f"{f['rho_max']}", numbered=False)
    doc.p("where Cₖ is the set of lanes served by phase k and Vₖ the set of pedestrian "
          "crossings that phase k opens.")
    doc.h("6.2.1 Derivation and explanation", 3)
    doc.p("To understand the functional as easily as possible, it is explained term by term.")
    doc.h("6.2.1.1 Phase compatibility factor (sₖ)", 4)
    doc.p("sₖ ∈ [0, 1] indicates whether the phase is safe to activate: 1 means the phase is "
          "completely safe and 0 that it is incompatible (for example, vehicles that would "
          "cross each other). It multiplies the whole pressure, so an unsafe phase has zero "
          "effective pressure. Which phases are safe is decided with graph theory, using the "
          "conflict graph of the junction (section 6.2.2). Only safe phases are ever defined, "
          "so every candidate phase has sₖ = 1, and the transitions between them (amber, "
          "all-red, pedestrian clearance) are imposed separately (section 7.3).")
    doc.h("6.2.1.2 Vehicle pressure", 4)
    doc.equation(r"\sum_{i\in C_k}w_i\,\frac{N_i}{\mu_i-\lambda_i}=\sum_{i\in C_k}w_i\,"
                 r"\frac{N_i}{\mu_i}\,\frac{1}{1-\rho_i}", numbered=False)
    doc.p("This part of the model computes the pressure exerted by vehicles:")
    doc.bullets([
        "**wᵢ** gives priority to main or busier roads (in this study all lanes have wᵢ = 1, "
        "so that no road is favoured by hand).",
        "**Nᵢ/μᵢ** is the time needed to discharge the queue if no new vehicles arrived.",
        "**1/(1 − ρᵢ)** corrects that time for the vehicles that keep arriving while the "
        "queue is being discharged.",
    ])
    doc.p("*Derivation.* While lane i has green, vehicles leave the queue at rate μᵢ and new "
          "ones join it at rate λᵢ, so the queue shrinks at the net rate (μᵢ − λᵢ). The time "
          "needed to clear a queue of Nᵢ vehicles is therefore")
    doc.equation(r"W_i=\frac{N_i}{\mu_i-\lambda_i}=\frac{N_i}{\mu_i}\cdot\frac{1}{1-\lambda_i/\mu_i}"
                 r"=\frac{N_i}{\mu_i}\cdot\frac{1}{1-\rho_i}")
    doc.p("The factor 1/(1 − ρ) is the same one that appears in queueing theory: in an "
          "M/M/1 queue with utilisation ρ = λ/μ, the mean number of customers in the system "
          "is L = ρ/(1 − ρ) and the mean time in the system is W = 1/(μ − λ) (Little’s law). "
          "In both cases, the closer the arrivals get to the service capacity, the faster "
          "the delay grows, and it tends to infinity as ρ → 1.")
    doc.p("To keep the pressure finite when the measured arrivals approach or exceed the "
          f"capacity, ρ is capped at ρ_max = {f['rho_max']}, which limits the factor to "
          f"{1/(1-f['rho_max']):.0f}.")
    doc.p("With this form the vehicle term has a clear physical meaning: it is measured in "
          "seconds and is the (weighted) time the phase would need to serve its queues. We "
          "can interpret that the more vehicles, the more saturation or the more important "
          "the road, the more pressure the phase will have.")
    doc.h("6.2.1.3 Pedestrian pressure", 4)
    doc.equation(r"\sum_{j\in V_k}\left(\beta N_v^j+\gamma T_v^j+\delta\,\max\left(0,\,"
                 r"T_v^j-T_{crit}\right)\right)", numbered=False)
    doc.p("This part computes the pressure exerted by pedestrians. The weights (β, γ, δ) ≥ 0 "
          "convert people and seconds of waiting into the same units as the vehicle term, "
          "and act as the “prices” that decide how much vehicle time the system is willing "
          "to give up for pedestrians:")
    doc.bullets([
        "**β N_v^j**: each waiting pedestrian adds β units of pressure.",
        "**γ T_v^j**: long waits are penalised, even if only one person is waiting.",
        "**δ max(0, T_v^j − T_crit)**: extra pressure once the oldest pedestrian has waited "
        "more than the critical time T_crit. It grows without limit, so sooner or later it "
        "exceeds any vehicle pressure: no pedestrian can be left waiting indefinitely "
        "(*starvation* is impossible).",
    ])
    doc.p(f"The values used are β = {f['beta']:g}, γ = {f['gamma']:g}, δ = {f['delta']:g} and "
          f"T_crit = {f['t_crit']:g} s. How they were chosen is explained in section 7.5.")

    conflict_graph_section(doc, f)

    doc.h("6.3 Control policy", 2)
    doc.p("The decision policy of the system is defined as:")
    doc.equation(r"F(t+1)=\underset{k}{\arg\max}\ P_k\left(X(t)\right)")
    doc.p("subject to the time constraints")
    doc.equation(r"T_{min}\leq T_{phase}\leq T_{max}")
    doc.p("This rule is a local maximisation policy: at every second, the phase with the "
          "highest instantaneous pressure is activated, and each green lasts a minimum and "
          "a maximum time. Precisely:")
    doc.bullets([
        f"Before T_min = {f['t_min']} s the current green is never interrupted (it also "
        "guarantees pedestrians enough time to start crossing).",
        "Between T_min and T_max, the controller switches to the phase of highest pressure "
        "if its pressure is strictly greater than that of the current phase.",
        f"At T_max = {f['t_max']} s it switches to the other phase with the highest "
        "pressure, provided that phase has any demand at all; if nobody is waiting "
        "elsewhere, the current green continues.",
        "Every switch runs a safe transition: pedestrian clearance, amber and all-red "
        "(section 7.3). During the transition no new decision is taken.",
    ])
    doc.p("The system is therefore a control mechanism with full state feedback.")

    doc.h("6.4 Interpretation in terms of optimisation", 2)
    doc.p("We can consider the overall cost of the system:")
    doc.equation(r"C(t)=\sum_{i}N_i(t)+\alpha\sum_{j}N_v^j(t)")
    doc.p("This functional represents the weighted total number of users waiting. The policy "
          "does not explicitly solve min C(t) over the whole horizon, but it acts as a "
          "greedy approximation: at each moment it serves the group of users whose waiting "
          "would be most costly, which reduces the accumulated cost locally. This is the "
          "same principle as *max-pressure* control (Varaiya, 2013), for which it has been "
          "proven that serving the phase of greatest pressure keeps queues bounded whenever "
          "the demand is within the capacity of the intersection.")

    doc.h("6.5 Theoretical properties of the model", 2)
    doc.h("6.5.1 Non-negativity", 3)
    doc.p("Since all variables and weights are non-negative and ρᵢ < 1, it holds that "
          "Pₖ(X(t)) ≥ 0 for every phase.")
    doc.h("6.5.2 Sensitivity to saturation", 3)
    doc.p("If λᵢ → μᵢ, the factor 1/(1 − ρᵢ) grows rapidly (up to the cap 1/(1 − ρ_max)), "
          "increasing the pressure. This allows situations close to collapse to be detected "
          "and served first.")
    doc.h("6.5.3 Limit behaviour", 3)
    doc.p("If λᵢ(t) → 0 for all i, then Nᵢ(t) → 0 and the pedestrian terms also vanish, so "
          "every pressure tends to zero and the controller simply rests in the current green "
          "without oscillating.")
    doc.h("6.5.4 No starvation", 3)
    doc.p("Because the δ term grows linearly without limit after T_crit, and because every "
          "green is limited to T_max, every phase with demand is served within a bounded "
          "time. In the simulations, the longest pedestrian wait observed is reported in "
          "chapter 8 as a check of this property.")

    doc.h("6.6 Limitations of the model", 2)
    doc.p("Despite the results obtained in simulation, the proposed algorithm has certain "
          "intrinsic limitations that must be considered for a future real implementation:")
    doc.bullets([
        "**Local optimum vs. global optimum:** the algorithm is designed to maximise flow at "
        "a specific intersection based on the immediate sensor data. However, an "
        "improvement at a specific point (local optimum) can create bottlenecks at adjacent "
        "intersections, not necessarily guaranteeing the best performance for the whole "
        "road network (global optimum).",
        "**Sensitivity to calibration and oscillations:** the system depends on the weights "
        "given to each variable (pedestrians vs. vehicles). If these parameters are not "
        "properly calibrated for the street, the system may switch phases too often and "
        "lose efficiency because of the transition times. Section 7.5 describes how they "
        "were calibrated in this study, and chapter 8 shows their effect.",
        "**Myopic decisions:** the controller only sees the current queues. It cannot know "
        "that a platoon of vehicles is about to arrive, so it may cut a green just before "
        "it would have been most useful.",
        "**Complexity in high-density networks:** extending this model to a city like "
        "Barcelona would require an inter-node coordination architecture. Without "
        "communication between neighbouring traffic lights, “green waves” could be broken, "
        "since each light would take selfish decisions based only on its own pressure.",
        "**Human factor and external variables:** the SUMO simulation assumes rational "
        "behaviour. In reality, variables such as pedestrian offences, badly parked "
        "vehicles obstructing sensors or weather conditions introduce noise that the "
        "current algorithm does not directly take into account.",
        "**Dependence on sensor infrastructure:** the feasibility of the project is tied to "
        "the accuracy of data capture. Errors in computer-vision systems or induction loops "
        "could lead the model to wrong decisions, requiring fail-safe protocols (reverting "
        "to a fixed cycle) not developed at this stage.",
    ])
    doc.p("These limitations do not invalidate the model, but they define its scope and open "
          "lines for future research.")


def chapter_7(doc: Doc, f: dict) -> None:
    doc.h("7. Simulation of the adaptive traffic lights", 1, page_break=True)
    doc.h("7.1 Creation of the digital environment", 2)
    doc.p("To test the algorithm, it is first necessary to create the environment in which to "
          "simulate it. This was done with SUMO (Simulation of Urban MObility).")
    doc.h("7.1.1 Simulation of Urban MObility (SUMO)", 3)
    doc.p("SUMO is open-source software designed for urban traffic simulation (López et al., "
          "2018). It makes it possible to build road environments and to simulate the "
          "behaviour of every vehicle and pedestrian individually (microscopic simulation) on "
          "a given road infrastructure. It can be connected to external algorithms through "
          "the TraCI interface, programmable in Python, which allows traffic lights to be "
          "controlled and statistics to be collected during the simulation. I chose SUMO "
          "because it focuses on customisable infrastructures, allows the traffic lights to "
          "be controlled as the algorithm requires, and produces objective data that are key "
          f"to evaluating the adaptive system. The simulations use SUMO {f['sumo_version']}.")
    doc.h("7.1.2 Development of the road infrastructure", 3)
    doc.p("More than one type of intersection was developed, since each has different "
          "characteristics and traffic dynamics. This diversity makes it possible to "
          "evaluate the signal systems more realistically and to check to what extent the "
          "proposed solutions adapt to different contexts. All the networks were designed by "
          "me with SUMO’s network editor (netedit).")
    doc.h("7.1.2.1 Simple intersection: two-way road with a pedestrian crossing", 4)
    doc.p("This configuration is the most basic case: a two-way road with a single "
          "pedestrian crossing connecting the two pavements. It is an elementary scenario "
          "that allows the minimum functioning of the traffic lights and the direct "
          "interaction between vehicles and pedestrians at a specific point to be analysed.")
    doc.image(IMG / "fig08_simple.png", "The simple intersection in SUMO.", 15)
    doc.p("It contains a two-way road with one lane per direction (speed limit 50 km/h), a "
          "pavement on each side, a pedestrian crossing (6.4 m long) and a traffic light "
          "with two phases: vehicles green, or pedestrians green. The demand, taken from the "
          "route file, is:")
    doc.bullets([
        "A random flow of vehicles in each direction, with an insertion probability of "
        "0.3 per second (on average 1,080 vehicles/hour per direction).",
        "Four random flows of pedestrians, with probability 0.03 per second each, starting "
        "on either pavement; half of them cross the road and half continue along their "
        "pavement.",
    ])
    doc.h("7.1.2.2 Multiple intersection: two-way road with several pedestrian crossings", 4)
    doc.p("This model extends the previous case by incorporating several pedestrian "
          "crossings (five) on the same stretch of two-way road, each with its own traffic "
          "light. Vehicles must therefore compete with several pedestrian flows along the "
          "same stretch.")
    doc.image(IMG / "fig09_multiple.png",
              "Multiple intersection (two-way road with several crossings) in SUMO.", 15)
    doc.p("For this network a specific adaptive algorithm was not developed: the main "
          "challenge here is the coordination between consecutive traffic lights (“green "
          "waves”), which is a network problem beyond the single-intersection model of this "
          "project (see section 9.2). It is therefore not included in the comparison of "
          "chapter 8.")
    doc.h("7.1.2.3 Shibuya-type intersection", 4)
    doc.p("Inspired by the Shibuya crossing (Tokyo), this configuration is a four-arm "
          "intersection where vehicles and pedestrians move in several directions (without "
          "the diagonal crossing). It is especially complex, since each arm has a single "
          "lane per direction shared by left-turning, straight and right-turning vehicles, "
          "and pedestrians cross the four arms.")
    doc.image(IMG / "fig10_shibuya.png", "The Shibuya-type intersection in SUMO.", 15)
    doc.p("It contains four two-way arms (one lane per direction), pavements on both sides, "
          "four pedestrian crossings (one per arm) and one traffic light with two phases: "
          "north–south vehicles together with the crossings parallel to them, and east–west "
          "vehicles with their parallel crossings. Turning vehicles must give way to "
          "pedestrians on the crossing they cut, and left-turning vehicles must also give "
          "way to oncoming traffic. The demand defined in the route file is:")
    doc.bullets([
        "Three vehicle flows per arm (left, straight and right), each with probability 0.07 "
        "per second: 0.21 veh/s ≈ 756 vehicles/hour per approach, 3,024 vehicles/hour in "
        "total.",
        "Seven pedestrian flows of 0.07 people per second each, starting from the western "
        "arm towards the other arms (about 1,760 pedestrians/hour).",
    ])
    doc.p("This demand deliberately represents a collapsed intersection: as chapter 8 shows, "
          "no signal plan can serve it, because vehicles waiting to turn left in a shared "
          "lane block everyone behind them.")

    doc.h("7.2 Measuring the saturation flow μ", 2)
    doc.p("The model needs the service rate μ of each lane. Instead of choosing it by hand, "
          "it was measured in SUMO with the "
          "standard queue-discharge method: the lane is kept red for 90 s until a long queue "
          "forms, then it gets green and the vehicles leaving the lane between 5 s and 35 s "
          "after the start of green are counted (the first seconds are excluded because of "
          "the start-up lost time). Repeated over 36 green periods, the result is")
    doc.equation(r"\mu=" + f"{f['mu']:.3f}" + r"\pm" + f"{f['mu_sd']:.3f}" +
                 r"\ \mathrm{veh/s}\ \approx\ " + f"{f['mu_vph']:,}".replace(",", r"{,}") +
                 r"\ \mathrm{veh/h}", numbered=False)
    doc.p("which is very close to the typical saturation flow of an urban lane given in "
          "traffic engineering manuals (about 1,800 veh/h). All approaches in both networks "
          "have the same geometry, so this value is used for every lane.")

    doc.h("7.3 Implementation of the adaptive controller", 2)
    doc.p("The algorithm is connected to SUMO through TraCI. Every simulated second, the "
          "controller:")
    doc.bullets([
        f"reads each incoming lane: the vehicles in the last {f['detection_zone']:.0f} m "
        f"(Nᵢ) and the vehicles that entered the lane during the last {f['arrival_window']} s "
        "(to compute λᵢ);",
        "reads each crossing: the pedestrians waiting on the waiting area in front of it "
        "(N_v^j) and the longest waiting time among them (T_v^j);",
        "computes Pₖ for every phase with the equation of section 6.2 and applies the "
        "policy of section 6.3;",
        "sets the state of every signal explicitly with `setRedYellowGreenState`.",
    ], numbered=True)
    doc.p("The transition between two phases is generated automatically by comparing the two "
          "signal states, so it is always safe and identical for the three controllers:")
    doc.bullets([
        f"**Pedestrian clearance ({f['ped_clearance']} s):** crossings that lose their green "
        "turn red first, while vehicles keep their current signal. The duration is the "
        "crossing length divided by a design walking speed of 1.2 m/s, so that anyone who "
        "has just stepped onto the crossing can finish.",
        f"**Amber ({f['amber']} s)** for the vehicle movements that lose green.",
        f"**All-red ({f['all_red']} s)** before the new green starts.",
    ])
    doc.h("7.4 Reference controllers", 2)
    doc.p("To know whether the adaptive algorithm is good, it must be compared with what "
          "traffic engineers would actually install. Two references are used; both use "
          "exactly the same phases and transitions as the adaptive controller.")
    doc.h("7.4.1 Fixed-time plan (Webster)", 3)
    doc.p("For every scenario and demand level, the cycle length and the green times are "
          "computed with Webster’s method (section 4.1.2) from the expected flows and the "
          "measured μ. In the simple intersection, the pedestrian phase has no vehicle flow, "
          "so it receives the minimum walk time of 10 s, which is counted as lost time for "
          f"vehicles. The cycle is limited to {f['c_min']}–{f['c_max']} s, as is usual in "
          "practice; when the flow ratios add up to 0.95 or more (an oversaturated "
          f"intersection) the maximum cycle of {f['c_max']} s is used. Table "
          f"{f['webster_table_no']} shows the resulting plans.")
    doc.table(["Intersection", "Demand", "Y = Σyₖ", "Lost time L", "Cycle C", "Greens"],
              f["webster_rows"], caption="Fixed-time plans computed with Webster’s method "
              "(greens include the pedestrian clearance during which vehicles keep moving).",
              widths_cm=[3.2, 2.0, 2.2, 2.4, 2.2, 4.0])
    doc.p("All three controllers apply the same minimum-green rule: every phase shows its "
          f"full green for at least T_min = {f['t_min']} s *before* its transition starts. "
          "In the Shibuya intersection, vehicles keep their green during the pedestrian "
          "clearance that follows, so the shortest possible vehicle green is "
          f"{f['t_min']} + {f['ped_clearance']} s.")
    doc.h("7.4.2 Actuated controller (SUMO)", 3)
    doc.p("SUMO includes a gap-based actuated controller: detectors placed before the stop "
          "line extend the green while vehicles keep arriving less than 3 s apart, between a "
          f"minimum green of {f['t_min']} s and a maximum green (the same T_max as the "
          "adaptive controller). It represents the actuated signals already used at some "
          "points in Barcelona (section 3.3.2.1). In the simple intersection the pedestrian "
          "phase has no detector, so it is served every cycle for 10 s, as at a crossing "
          "without a push button.")

    doc.h("7.5 Calibration of the controller parameters", 2)
    doc.p("The adaptive controller has free parameters: the maximum green T_max, the critical pedestrian time T_crit and the "
          "pedestrian weights β and γ. They decide how the controller balances vehicles "
          "against pedestrians, so they were chosen systematically with a grid search:")
    doc.bullets([
        f"T_max ∈ {{{', '.join(str(x) for x in f['grid_t_max'])}}} s, T_crit ∈ "
        f"{{{', '.join(f'{x:g}' for x in f['grid_t_crit'])}}} s, and a multiplier of "
        f"{{{', '.join(f'{x:g}' for x in f['grid_ped_scale'])}}} applied to β and γ "
        f"(base values β = 2, γ = 0.2, δ = {f['delta']:g}): {f['grid_size']} combinations.",
        "Each combination was simulated in four representative cases (both intersections, "
        "at low and at full demand) with three **tuning seeds** (101–103). These seeds are "
        "never used in the evaluation of chapter 8 (seeds 1–"
        f"{f['seeds']}), so the reported results are not fitted to the data they are "
        "evaluated on.",
        "The objective is the total **person-delay**: 1.2 × (sum of vehicle delays) + (sum "
        "of pedestrian waiting times), where 1.2 is the average occupancy of a car. It "
        "counts one second of a person waiting the same whether that person is in a car or "
        "on foot. It is expressed relative to the Webster plan in each case and averaged "
        "over the four cases.",
        "The same grid of maximum greens was applied to the actuated controller, so that it "
        "is calibrated as carefully as the adaptive one.",
    ])
    doc.p(f["tuning_text"])
    doc.table(["Parameter", "Value"], f["param_rows"],
              caption="Parameters of the adaptive controller.", widths_cm=[7.5, 7.5])


def conflict_graph_section(doc: Doc, f: dict) -> None:
    cg = f["cg"]
    sh, si = cg["shibuya"], cg["simple"]
    doc.h("6.2.2 The conflict graph: which phases are safe?", 3)
    doc.p("The factor sₖ hides a real question: which movements can have green at the same "
          "time without putting anyone in danger? Graph theory answers it precisely, and it is "
          "the classical way traffic engineers design signal phases (Stoffers, 1968).")
    doc.p("A **graph** G = (V, E) is a set of vertices V joined by edges E. For a junction:")
    doc.bullets([
        "each **vertex** is a movement controlled by the traffic light: a vehicle movement "
        "(for example “from the north, turning left”) or a pedestrian crossing;",
        "two vertices are joined by an **edge** when the movements **conflict**: their paths "
        "cross or merge, so they cannot both move freely at the same time.",
    ])
    doc.p("Not every conflict is equally serious, so the edges are of two kinds:")
    doc.bullets([
        "**strong conflicts**, which only the signal can separate: vehicles coming from "
        "perpendicular approaches, or a vehicle that drives straight across a pedestrian "
        "crossing;",
        "**weak conflicts**, which can be resolved by giving way: a left turn yielding to "
        "oncoming traffic, two movements merging into the same exit, or a turning vehicle "
        "yielding to the pedestrians on the crossing parallel to it. Both movements may "
        "have green together (in SUMO, the yielding one shows a lower-case g).",
    ])
    doc.p("A set of vertices with no edge between any two of them is called an **independent "
          "set**. A phase Mₖ (the set of movements it gives green to) is safe exactly when it "
          "is an independent set of the graph of strong conflicts E_s (otherwise sₖ = 0):")
    doc.equation(r"s_k=1\ \Leftrightarrow\ \{i,j\}\notin E_s\quad\forall\, i,j\in M_k")
    doc.p("Choosing the phases is then a **graph colouring** problem: give every vertex a colour "
          "so that two vertices joined by an edge never share a colour. Each colour is a phase, "
          "and the smallest number of colours that is enough is the **chromatic number** χ(G), "
          "the minimum number of phases the junction needs.")
    doc.p("Both conflict graphs were built automatically from the SUMO network files (which "
          "store, for every pair of movements, whether they conflict), and their chromatic "
          "numbers were computed exactly with a backtracking algorithm:")
    doc.table(["Junction", "Vertices", "Strong edges", "Weak edges", "χ (strong only)",
               "χ (all conflicts)"],
              [["Simple crossing", si["n"], si["strong"], si["weak"], si["chi_s"], si["chi_all"]],
               ["Shibuya-type", sh["n"], sh["strong"], sh["weak"], sh["chi_s"], sh["chi_all"]]],
              caption="Conflict graphs of the two junctions.",
              widths_cm=[3.6, 2.2, 2.4, 2.4, 2.6, 2.8])
    doc.image(IMG / "fig_conflict_graph.png",
              "Conflict graph of the Shibuya-type junction. Each vertex is a movement, coloured "
              "by the phase that serves it; solid edges are strong conflicts and dashed edges "
              "are weak ones. No solid edge joins two vertices of the same colour: both phases "
              "are independent sets.", 10.5)
    doc.p(f"The results explain the design of both junctions. In each of them χ = "
          f"{sh['chi_s']} for the strong conflicts, so two phases are enough, and the two "
          "phases used in this project (vehicles / pedestrians in the simple crossing; "
          "north–south / east–west in the Shibuya-type junction) are a valid colouring: a unit "
          "test checks that no phase contains two movements with a strong conflict.")
    doc.p(f"The Shibuya-type junction also shows the price of that choice. If weak conflicts "
          f"were not allowed either, the chromatic number would rise to {sh['chi_all']}: every "
          f"movement would need a fully protected phase, which would roughly double the time "
          "lost in transitions. Two phases are only possible because left-turning vehicles "
          "are allowed to go at the same time as oncoming traffic and give way to it. Those "
          f"{sh['weak']} weak edges are precisely where the junction breaks down at high demand: "
          "a left-turning car that waits for a gap blocks the single shared lane behind it "
          "(section 8.3).")
