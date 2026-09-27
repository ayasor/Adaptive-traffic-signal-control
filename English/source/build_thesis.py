"""Build the English edition of the thesis (.docx) from the simulation results.

    ../../.venv/bin/python build_thesis.py

Every number in chapters 6-8 is read from simulation/results, so the
document can be regenerated whenever the simulations are re-run.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "simulation"))

from atsc import adaptive, programs, scenarios  # noqa: E402
from atsc.pressure import RHO_MAX, PedestrianWeights  # noqa: E402

import results_data as R  # noqa: E402
from chapters_end import ai_declaration, annexes, bibliography  # noqa: E402
from chapters_model import chapter_6, chapter_7  # noqa: E402
from chapters_results import abstract_results, chapter_8, chapter_11  # noqa: E402
from chapters_static import (abstract, chapter_1_2, chapter_3,  # noqa: E402
                             chapter_4_5, chapter_9_10, contents, front_matter)
from docbuilder import Doc  # noqa: E402

sys.path.insert(0, str(ROOT / "simulation"))
import run_experiments  # noqa: E402
import tune  # noqa: E402

OUT = ROOT / "English" / "Urban traffic optimisation - adaptive traffic lights (EN).docx"


def facts() -> dict:
    sat = R.saturation()
    tun = R.tuning()
    best = tun["best"]["adaptive"]
    act = tun["best"]["actuated"]
    tuned = run_experiments.TUNED["adaptive"]
    assert (tuned["t_max"], tuned["t_crit"], tuned["ped_scale"]) == \
        (best["t_max"], best["t_crit"], best["ped_scale"]), "TUNED differs from tuning result"
    w = PedestrianWeights()
    seeds = max(r["seed"] for r in R.runs())
    import sumo  # type: ignore
    version = Path(sumo.__file__).parent.joinpath("..").resolve()
    try:
        from importlib.metadata import version as v
        sumo_version = v("eclipse-sumo")
    except Exception:  # pragma: no cover
        sumo_version = str(version)
    n_grid = len(tune.T_MAX) * len(tune.T_CRIT) * len(tune.PED_SCALE)
    rel = best["relative_J"]
    tuning_text = (
        f"The best combination was T_max = {best['t_max']} s, T_crit = {best['t_crit']:g} s "
        f"and the base pedestrian weights (multiplier {best['ped_scale']:g}). Several "
        "neighbouring combinations (T_max and T_crit between 90 and 120 s) gave practically "
        "the same result, so the choice is not sensitive to small changes. Relative to "
        "Webster, the person-delay of the tuned adaptive controller on the tuning seeds was "
        + ", ".join(f"{k.replace('@', ' at ')}: {v:.2f}" for k, v in rel.items())
        + f" (mean {best['mean_relative_J']:.2f}; values below 1 mean less person-delay than "
        f"Webster). For the actuated controller the best maximum green was {act['t_max']} s "
        f"(mean {act['mean_relative_J']:.2f}).")
    param_rows = [
        ["Pressure saturation factor", "1/(1 − ρ), ρ ≤ 0.95"],
        ["Service rate μ", f"{sat['mu']:.3f} veh/s (measured)"],
        ["Arrival rate λ", f"vehicles entering the lane / {adaptive.ARRIVAL_WINDOW} s"],
        ["Queue Nᵢ", f"vehicles in the last {adaptive.DETECTION_ZONE:.0f} m"],
        ["Lane weights wᵢ", "1.0 (all lanes)"],
        ["T_min", f"{programs.T_MIN} s"],
        ["T_max", f"{best['t_max']} s (tuned)"],
        ["Amber / all-red", f"{scenarios.AMBER} s / {scenarios.ALL_RED} s"],
        ["Pedestrian clearance", f"{scenarios.SIMPLE.ped_clearance} s"],
        ["β, γ, δ", f"{w.beta:g}, {w.gamma:g}, {w.delta:g}"],
        ["T_crit", f"{best['t_crit']:g} s (tuned)"],
    ]
    return {
        "mu": sat["mu"], "mu_sd": sat["sd"], "mu_vph": sat["veh_per_hour"],
        "rho_max": RHO_MAX, "detection_zone": adaptive.DETECTION_ZONE,
        "arrival_window": adaptive.ARRIVAL_WINDOW,
        "beta": w.beta, "gamma": w.gamma, "delta": w.delta, "t_crit": best["t_crit"],
        "t_min": programs.T_MIN, "t_max": best["t_max"], "t_max_actuated": act["t_max"],
        "amber": scenarios.AMBER, "all_red": scenarios.ALL_RED,
        "ped_clearance": scenarios.SIMPLE.ped_clearance,
        "c_min": programs.C_MIN, "c_max": programs.C_MAX,
        "seeds": seeds, "sumo_version": sumo_version,
        "grid_t_max": tune.T_MAX, "grid_t_crit": tune.T_CRIT, "grid_ped_scale": tune.PED_SCALE,
        "grid_size": n_grid, "tuning_text": tuning_text, "param_rows": param_rows,
        "webster_table_no": 2, "webster_rows": webster_rows(sat["mu"]),
    }


def webster_rows(mu_value: float) -> list[list[str]]:
    rows = []
    for name, scales in run_experiments.DEMAND.items():
        scn = scenarios.SCENARIOS[name]
        mu = {ln: mu_value for p in scn.phases for ln in p.lanes}
        for scale in scales:
            plan = programs.webster(scn, scenarios.vehicle_demand(scn, scale), mu)
            label = "Simple" if name == "simple" else "Shibuya"
            greens = " / ".join(f"{g:.0f} s" for g in plan.greens)
            if name == "simple":
                greens = f"veh {plan.greens[0]:.0f} s / ped {plan.greens[1]:.0f} s"
            rows.append([label, f"{scale * 100:.0f} %", f"{sum(plan.flow_ratios):.2f}",
                         f"{plan.lost_time:.0f} s", f"{plan.cycle:.0f} s", greens])
    scn = scenarios.SHIBUYA
    mu = {ln: mu_value for p in scn.phases for ln in p.lanes}
    plan = programs.webster(scn, scenarios.vehicle_demand(
        scn, 1.0, run_experiments_unbalanced()), mu)
    rows.append(["Shibuya (unbalanced)", "—", f"{sum(plan.flow_ratios):.2f}",
                 f"{plan.lost_time:.0f} s", f"{plan.cycle:.0f} s",
                 " / ".join(f"{g:.0f} s" for g in plan.greens)])
    return rows


def run_experiments_unbalanced() -> dict:
    from atsc.runner import UNBALANCED
    return UNBALANCED["shibuya"]


def render_pdf(docx: Path, outdir: Path) -> Path:
    import subprocess
    outdir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(outdir),
                    str(docx)], check=True, capture_output=True)
    return outdir / (docx.stem + ".pdf")


def heading_pages(pdf: Path, headings: list[tuple[int, str]], first_body_page: int) -> dict:
    """Find the page on which each heading starts (searching in order)."""
    import subprocess
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], check=True,
                          capture_output=True, text=True).stdout
    pages = text.split("\f")
    norm = [" ".join(p.split()) for p in pages]
    first = " ".join(headings[0][1].split())
    hits = [i for i, pg in enumerate(norm) if first in pg]
    # the first hit is the table of contents itself; the body starts at the second
    out, cur = {}, hits[1] if len(hits) > 1 else max(first_body_page - 1, 0)
    for _, h in headings:
        key = " ".join(h.split())
        for i in range(cur, len(norm)):
            if key in norm[i]:
                out[h] = i + 1
                cur = i
                break
    return out


def build(f: dict, toc_entries=None, toc_pages=None) -> Doc:
    doc = Doc()
    front_matter(doc)
    abstract(doc, abstract_results())
    contents(doc, toc_entries or [(1, "x")] * 40, toc_pages or {})
    body = doc.new_section()
    doc.running_header_and_page_numbers(body)
    chapter_1_2(doc)
    chapter_3(doc)
    chapter_4_5(doc)
    chapter_6(doc, f)
    chapter_7(doc, f)
    chapter_8(doc, f)
    chapter_9_10(doc)
    chapter_11(doc, f)
    bibliography(doc)
    annexes(doc)
    ai_declaration(doc)
    return doc


def main() -> None:
    import tempfile
    f = facts()
    # pass 1: find the headings and the pages they land on
    first = build(f)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        entries = [h for h in first.headings
                   if h[1] not in ("Acknowledgements", "Abstract")]
        probe = build(f, entries, {})
        probe.save(tmp / "probe.docx")
        pages = heading_pages(render_pdf(tmp / "probe.docx", tmp), entries,
                              first_body_page=7)
    missing = [h for _, h in entries if h not in pages]
    if missing:
        print("warning: headings not found in PDF:", missing)
    doc = build(f, entries, pages)
    doc.save(OUT)
    pdf = render_pdf(OUT, OUT.parent)
    print(f"saved {OUT}\nsaved {pdf}")


if __name__ == "__main__":
    main()
