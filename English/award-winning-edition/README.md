# Award-winning edition — FROZEN, DO NOT MODIFY

This folder holds the English translation of the research project exactly as it won the
**first prize of the Premi Enginyer Pompeu Fabra 2026**:

* `Urban traffic optimisation - adaptive traffic lights (EN).docx`
* `Urban traffic optimisation - adaptive traffic lights (EN).pdf`
* `source/` — the scripts that generated them.

**Nothing in this folder may be edited, regenerated, renamed or deleted.** It is the reference
version of the awarded work. Any new content (new controllers, new results, corrections) goes
into [`../extended-edition/`](../extended-edition/).

## Reproducing it

The `.docx` and `.pdf` are the reference; the source code is kept only to document how they were
made. It cannot be rebuilt from this folder as it is:

* the scripts expect to live in `English/source/` (their original location), and
* they read `simulation/results/`, which has changed since (for example, the max-pressure
  results added after the award).

To rebuild it exactly, check out commit `bcffdd8`, where the scripts and the results are in
their original state, and run `English/source/build_thesis.py` there.
