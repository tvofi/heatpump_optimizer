# D4 round-10 verification (single verifier, three lenses)

Owner ruling for this pass: the verifier does not re-run tests and may rely on reasoning. No harness was executed;
every vote below is therefore by reasoning over the finder's recorded outputs and the card source, and no number here is
a fresh measurement.

| id | vote | severity | basis |
|---|---|---|---|
| D4-s1-01 | verify | medium | A 3.5-unit stroke with no wider hit path yields a few-px band at any viewBox scale; finder's perturbation (stroke 30 -> band 52.75 px) moves the right way. Reachable in real HA (layout editor is card code, not stub). Keyboard route `pipeKb` keeps it medium. Class: new (small-target / bbox-blind instrument). Seam rule covers pipes only, not other SVG stroke-only targets. |
| D4-s3-01 | verify | low | Inline legend lacks the dialog's `anyData` gate; perturbation `savingsTile || !anyData` -> 0 is consistent. Reachable on a fresh install before the first plan. Class: new (inline/dialog divergence). |
| D4-s3-02 | weaken | low | Ratio >1 is plausible (chart font scales with SVG viewBox while title is fixed px); perturbation 13 px cap -> 0.88. Cosmetic hierarchy issue, not a functional defect; the setup seam is a second seam the perturbation does not cover. |
