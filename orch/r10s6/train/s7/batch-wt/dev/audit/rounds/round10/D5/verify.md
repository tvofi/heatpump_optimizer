# D5 round 10 -- verifier report (single verifier, V1/V2/V3)

Scope note: by the user's instruction for this run ("the d3 verifier need not re-run any test but can use reasoning"), finder harnesses were NOT re-executed. V1 "reproduced" values are therefore static re-derivations, not harness runs; perturbation and null-control arms were not run and are recorded as not run. V2 values come from my own grep/read of the tree at handoff/audit-r10-register.

| id | vote | severity | V2 independent value | reachable | class | seam_rule enumerates |
|---|---|---|---|---|---|---|
| D5-s1-01 | verify | low | manifest name "Heat Pump Cost Optimizer" vs docs/configuration.md:23 "Heat Pump Optimizer"; strings.json:49 "Enter thermal values directly" vs 4 doc sites with "(expert)" -> 5 mismatches | yes (config flow UI) | new | not checked |
| D5-s2-01 | verify | low | docs/dashboard-card.md:828 "v6.6.8" vs card CARD_VERSION "7.0.0"; :832 claims the release step keeps them in step | yes (browser console) | new | not checked |
| D5-s3-01 | verify | low | `money_currency` occurs once in *.py: coordinator.py:1976 comment; 0 code tokens | n/a (comment) | new | not checked |
| D5-s3-51 | verify | low | services.py: 13 `async_register(` calls; __init__.py:80,:266 "twelve services", :365 "twelve handlers and the eleven"; services.py:1 "thirteen" holds -> 4 of 5 wrong | n/a (comments) | I5 (prose-count census family) | not checked |

Attacks: README/setup mermaid sites wrap the label with `<br/>`; still the same non-existent "(expert)" text, so counted. No refutation found for any finding.
