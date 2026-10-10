Fix-review evidence for PR #2125, branch fix/r9-closures-inert-prestudy.

HEAD MEASURED: e8e8615d8a3f1d5d829b2d290f33c61539d887a7
(ls-remote confirmed unchanged at verdict time.)

1. DIFF (three-dot, merge-base...HEAD):
   - dev/programme/delivery/2125.md | 1 + (new file, the PR's own delivery row)
   - tests/closures.json            | 1 +
   Total: 2 files changed, 2 insertions(+), 0 deletions.
   The closures.json line, inserted between
   "dev/audit/rounds/round9/fixplan/gen.py" and
   "dev/audit/rounds/round9/rca/1747/b8_replan_blocked.py"
   (i.e. fixplan/ < prestudy/ < rca/, the entry's existing ASCII sort order):
       "dev/audit/rounds/round9/prestudy/boost_drift_refit.py",

2. LINE IDENTITY AND PARSE:
   CI's defect line named exactly:
     tests/harness_headers.py: dev/audit/rounds/round9/prestudy/boost_drift_refit.py
   The added line is character-for-character that path.
   python3 -I json.load(tests/closures.json) parses.
   inert_reads['tests/harness_headers.py'] now holds 541 paths; the added
   path is present; ir == sorted(ir) is True.

3. CI AT THE HEAD (check-runs API, head e8e8615d8a3f...):
   closures: SUCCESS at head e8e8615d8a3f1d5d829b2d290f33c61539d887a7
   (check-run completed 2026-10-10T18:27:39Z; job 114276979238 in run
   38073939251 — "Re-record the closures" then "Fail if tests/closures.json
   under-approximates" both passed). CI's own re-derive at this head is the
   verification; no local re-derive attempted (forbidden off Linux).
   All other checks at this head green or skipped:
     pr-contract success, mutation success, briefs success, typing success,
     closure-scope success, arch-score success, fast (3.14) success,
     coverage success, browser success, nightly-status success,
     delivery-status success, wave-script success, budget-raise-gate success,
     CodeQL neutral, everything else skipped.

4. BODY: names main's red `closures` check at 969c3a5c8, quotes the
   `INERT READS UNDER-APPROXIMATED` output verbatim including
   `tests/harness_headers.py: dev/audit/rounds/round9/prestudy/boost_drift_refit.py`,
   and answers it in `## Red checks` by CI's own re-run of the recording
   comparison at this head. Truthful against the check-runs API: the only
   check that went red in the range is main's closures; no gate check at
   this PR's heads went red unanswered.
