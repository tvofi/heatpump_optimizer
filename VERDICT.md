Fix review: blocked 25418620f9fb39304e82dceea3ce8d2114ad018f body-stale: the code is verified; the body says the diff lists 5 files and adds no tracked file, but head adds dev/programme/delivery/2216.md (6 files), and the PR title is a merge-commit subject
bus-nonce: 144abe036456788098c24ed159a20c8f
reviewer: r10-ratchet-reviewer
round: 1

Measured head 25418620f9fb39304e82dceea3ce8d2114ad018f (re-read at post time: unchanged). Merge base c698d504a09424cda69e43e5f3cde97fbedb3a70; roles/ diff vs origin/main empty (contract current).

RESULT red-run-artifacts run=38639862216 fast=15 closures-lane rows (tests/x.py x4, p1-p4 x2, q1-q3) + 2 fast mode; closures file=34 real + 1 foreign fast; coverage file=20 real + 1 foreign fast. Fixture names untracked (git ls-files). Real = 34+20 = 54.
RESULT grade base (c698d504a) on run 38639862216 own artifacts: GREW script_runs_per_push 69 (budget 68), rc=1 -- reproduces the red.
RESULT grade head on the same artifacts: ok script_runs_per_push 54 (budget 68), 17 rows not counted, rc=0.
RESULT grade over the rebuilt 38-artifact window + run (same jq/zip layout as the ci-ratchet job): base per_push 69 GREW, full_case_pr 67; head per_push 54, full_case_pr 54, 209 foreign rows dropped.
RESULT real-row safety: per-run breakdown over all 15 runs in the window: every dropped row is a fixture (tests/x|p|q*.py) or a nested `fast mode` line; zero real script rows dropped; full-case classification of every PR run identical base vs head.
RESULT layout: every window file and this run's downloads are ci-metrics-{fast,closures,coverage}.tsv (38 artifacts: 14/10/14); no file would hit the names-no-lane refusal.
RESULT nested writers: none legitimate. rec() and metric_line() are shell functions run in subshells/background lanes (inherit the shell-local); derive_closures, run.sh and coverage_tree each unset before spawning any child. No Python reads HPO_CI_METRICS.
RESULT mutants (reviewer harness: the three new checks copied verbatim from head entities.py, evidence/three_checks.py): M1 lane filter removed KILLED; M2 unnamed file guessed KILLED; M3 derive_closures no unset KILLED (2 checks); M4 run.sh no unset KILLED; M5 coverage_tree no unset KILLED; M7 rec writes env var KILLED; M8 read-after-unset KILLED; M6 run.sh unset left only in a comment SURVIVED (the emitter check is a substring grep; only derive_closures.sh has a behavioural check) -- an instrument weakness, not blocking.
RESULT entities.py at head (PYTHONPATH=tests/hastub): rc=0, ALL 2316 ENTITY CHECKS PASSED, the three new checks ok.
RESULT budgets: tests/ci_budgets.json and every *_budgets.json untouched; not a raise. VERSION/manifest/notes untouched. No claim files touched.
RESULT check-runs at head (API, 23:42Z): 22+ success; nightly-status failure (main's, answered in body, diff does not reach replay); fast (3.14) and closures still in_progress; coverage and coverage-ratchet success; pr-contract success x2; mutation success (diff writes no production line, so no mutant drawn).
RESULT code-owned paths: tests/run.sh, tests/derive_closures.sh -> tvofi's approving review still required.

Body: Head section names 25418620f (matches). `a77faf30d` is named as the red run's commit, which is correct, not a stale base (base cited is c698d504a, the real merge base). Stale at head: the "Diff" figure says 5 files and "no tracked file is added"; head is 6 files with A dev/programme/delivery/2216.md (the self row added after the body). PR title is "Merge remote-tracking branch 'origin/main' into fix/ci-ratchet-script-runs-per-push", which a squash would put on main. Repair is body + title only; no head move needed, so every number above carries.
