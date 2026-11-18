# Extended edition

English edition of the research project extended after the award. It is a copy of the
[award-winning edition](../award-winning-edition/) with one addition:

* **Max-pressure (Varaiya, 2013)** as a third reference controller: description in section
  7.4.3, calibration in 7.5, results in chapter 8 (sections 8.2–8.6), and the related sentences
  of the abstract, the conclusions (chapter 11) and the declaration on the use of AI.

The rest of the text is unchanged. Every number is read from `simulation/results/`, so the
document is regenerated after re-running the simulations:

```bash
cd English/extended-edition/source
../../../.venv/bin/python build_thesis.py
```

It needs LibreOffice (`soffice`) and Poppler (`pdftotext`) to compute the page numbers of the
table of contents (see the installation guide in the main README).
