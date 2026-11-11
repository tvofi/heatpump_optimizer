# R9-CODEQL-SARIF-FIRST: the first taint answer theorized the source and burned a CI cycle

**Instance.** #2163, alert 36 (`py/clear-text-logging-sensitive-data`, sink
`pin()`'s FAIL print). The first fix (`be1567c76`) restructured the wiring
pins' `${{ }}` literals — a theory about the source taken from the query's
model, not from the alert. The alert fired again at the fixed head; the SARIF
threadFlow (analysis 1945791419, merge ref `6055c3b1`) named the real source
all along: `coverage_trust_cli()`'s return (the CLI reads the `.measured-by`
marker from disk), flowing through the pin's `detail` f-string to the print.
The second fix (`daa041adc`) cut the modeled path by construction: the detail
is constant text naming the rerun command, the pin's asserted condition
unchanged, and the pin-strength mutants were re-run red at the fixed head.

**Process state: (b)** — the cheaper detector existed and was not used: the
SARIF threadFlow is one API read and names the source; the theory came
first. **Countermeasure** (worker instruction, no code): any future
clear-text-logging answer starts with the alert's threadFlow, not the rule's
model — stated in #2163's Friction and pinned here so it survives the body.
**Cost test.** cost = one SARIF read per answer (seconds). Defect cost = one
CI CodeQL round per occurrence (tens of minutes, plus a review round).
P(recurrence) = every future CodeQL answer. Pays.
