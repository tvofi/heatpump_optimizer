Fix review: blocked 34ce6c99b6bf5dd7f64f6b1d78a6eb6a53460d7e mutation-survivor: dropping --existing-file from unanswered_reds passes the self-test

bus-nonce: afd24510bb5fe52649ee0bfc2f24e0c6

Round: 1 (first review of this head).

## Block

`unanswered_reds` passes two path arguments to policy_lint, and the self-test pins only one of them. Deleting `"--existing-file", str(ef),` from its argv (M2) leaves `review_packet self-test: 46 checks, 0 failed`. The argument is load-bearing. policy_lint's comment says that without it `reporterInputsTouched` counts every delivery row, and every pull request adds its own delivery row; this one adds `dev/programme/delivery/2962.md`. I probed it in `ev/m2_probe.py`: reds = `governance / delivery-status`, a diff that only adds `dev/programme/delivery/9999.md`, and a body whose `## Red checks` is `none`. At the head this returns `[]`. Under M2 it returns `['governance / delivery-status']`.

So M2 brings back the defect this PR fixes, for main's other reporter: every pull request would again be refused whenever main's `delivery-status` is red. The gather-side twin also survives. That is M5, `--diff-filter=a` changed to `--diff-filter=A` in `gather`, with the same effect. The kill is cheap and belongs in this PR: add one self-test arm for a `governance / delivery-status` red over a diff that only adds a delivery row (expect not owed), and its null with that row in `existing` (expect owed). For M5, see the first finding.

## Findings

- `gather`'s wiring of `unanswered_reds` is not pinned by any self-test arm. Replacing the whole call with `red_unanswered = []` (M6) passes 46/46, and so does passing `set()` for `touched`. An empty `--paths-file` makes policy_lint print an ERROR and exit 1. `tool()`'s rc is discarded, so the empty output reads as "no unanswered red": a fail-open. The old call at the base was equally unpinned: the base self-test drives only `refusals()` with hand-made facts. This PR rewrote these lines, though, so the arm is owed here. Either assert on the rc, or derive `existing` and `touched` in a helper the self-test drives over a throwaway checkout. Carry: R10-FLY-PACKET-RED-PATHS
- The fail-open path above cannot be reached through `touched` being empty for a real pull request, because a PR changes at least one file and a failing git read raises UNAVAILABLE (self-test arm). The discarded rc is therefore only reachable through policy_lint's own early ERRORs. Carry: dismissed: no realistic input reaches it beyond the wiring pin owed in the finding above

## Evidence

- RESULT head measured: 34ce6c99b6bf5dd7f64f6b1d78a6eb6a53460d7e; `refs/pull/2962/head` still resolves to it at verdict time. Merge base: ce5940c0d1d8f611a818d53e7fffcafb48b356c1 (= origin/main). `dev/governance/roles/` diff merge-base...origin/main: empty, so the contract is current.
- RESULT mutation proof (the body's M1, `--paths-file` dropped): `FAIL red-unanswered: main's nightly-status red is not owed by a diff touching only a test file`, `46 checks, 1 failed`. Restored: `46 checks, 0 failed`. This confirms the body's figure. Base self-test: `42 checks, 0 failed`, so the body's 42 + 4 is confirmed.
- RESULT M3 (`--base` dropped): 46/46 pass. No arm depends on it, because the self-test's head is not a real commit and the red history is skipped either way. Not graded as a finding.
- RESULT null control (brief): the self-test arm "red-unanswered null: #2954's workflow diff still owes nightly-status" (`.github/workflows/nightly.yml`, `.github/workflows/governance.yml` touched) passes at the head, so a body whose diff touches nightly.yml is still refused on nightly-status. The `tests/nightly_status.py` null passes too.
- RESULT class rule: `git grep -l -E -- '--red\b' -- 'tools/**' '.github/**' '.claude/**'` returns the seven files the body lists. Every policy_lint caller other than review_packet already passes `--paths-file`. `tools/audit/seat/record_row.py:992` also passes `--existing-file`, which the body did not say but which does not change its disposition. No seam is left open.
- RESULT merge: `git merge-tree --write-tree origin/main 34ce6c99…` exits 0 (tree 9fda349b4656c95bd4d752283a062e1a3410ba81). No claim file is touched.
- RESULT VERSION, manifest and RELEASE_NOTES are untouched. The diff is `tools/audit/seat/review_packet.py` and `dev/programme/delivery/2962.md` only.
- CI at this head (check-runs API, read at verdict time): `tests / nightly-status` is failure. That is main's reporter, and this diff does not reach what it reads, so it is not this PR's (fix-review.md 11). `tests / fast (3.14)`, `tests / closures`, `tests / browser`, `governance / env-matrix`, `governance / instrument-self-tests` and `codeql / Analyze (python)` were still in progress. No `pr-contract` run was listed. Everything else that concluded is success or skipped. `tests / mutation` is success, but under `--scope changed` that does not show which mutants were evaluated, and its log was not read. The verdict does not turn on it.
- Not re-derived: the body's prepr `ci predict` output and its `seat_venv.sh` refusal (environment-specific). This seat has no finder's harness to run: the packet names none, and the brief names none beyond the self-test arms.
- Files: `ev/HEAD.txt`, `ev/mutants.txt` (all mutant runs, probe, merge-tree, class rule), `ev/m2_probe.py`, `ev/review-packet.md` (rendered here, `Refusals: none`).
- Not run: `carry_audit.py check` over this verdict. A frugal-routing PreToolUse hook in this seat refused further inline Bash calls, and the hook was not worked around. The head was re-checked through the GitHub API instead: still 34ce6c99b6bf5dd7f64f6b1d78a6eb6a53460d7e.
