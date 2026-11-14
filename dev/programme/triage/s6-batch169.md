# Proposal triage, session s14, batch 169 (P584)

This batch records one orchestrator ruling made 2026-11-11 under mandate 6715477401 (scope
all): main is red, and the ruling builds the hotfix and its class barrier as one new group.

Sources:
- origin/main `a7628041dc`. Every line number below is at that commit.
- The failing job 130352715261 of workflow run 42968587919, and its `selftest-closures`
  artifact (`gh run download 42968587919 -n selftest-closures`), as diagnosed by the
  orchestrator's main-red seat.

## P584: SELFTEST-SCOPE-UNION

Verdict: ACCEPT, as a new group R10-HOTFIX-SELFTEST-SCOPE-UNION: class hotfix, size S,
fixer and reviewer opus, two parts. No live group owns `tools/ci/selftest_scope.py` or
`tools/ci/selftest_closures.json` (roster read at the time of ruling: every group listing
them is done).

Source: the orchestrator's main-red intake, 2026-11-11, ruled under the mandate.

Instances:
- **The red.** Step `drift` ("Refuse a self-test read set the committed table misses") of
  `governance / instrument-self-tests` prints `selftest_scope check: 111 gated step(s), 6
  refusal(s)` at `a7628041dc` (job log of 130352715261). It has been red on every completed
  main push since PR 3315 added it. The refusal counts were 37, 1, 32, 33 and 6 (check-runs
  per sha over `git log --first-parent origin/main`).
- **Cause 1, a new read without its table entry.** PR 3379 added the read of
  `dev/governance/roles/fix-review.md` in `review_packet.py:921` (`step12`). It did not touch
  the table, so verdict-bus and review-packet miss it.
- **Cause 2, a re-record replaces.** `record` (`selftest_scope.py:701`) does `entries.update`
  per step (`selftest_scope.py:743`). That replaces a step's read set with what one recording
  saw. PR 3419's off-push re-record dropped reads that only a main push makes: prepr's
  `.gitattributes`, `tests/env_drift.py`, `tools/merge/ledger_merge.py` and git `branch`, and
  the `-c` probe of open-pr, pr-args and update-pr.
- **Why no pull request is refused.** `SELFTEST_TRACE` is set only on push
  (`governance.yml:297`), and the drift step is guarded on it (`governance.yml:1496`). On a
  pull request the step is skipped, so it judges nothing before a merge.
- **The class.** This is at least the third hotfix of the self-test scope class, after
  R10-HOTFIX-MAIN-SELFTESTS, R10-HOTFIX-SELFTEST-SCOPE-HANG and
  R10-HOTFIX-PREPR-SELFTEST-DARWIN (roster, all done). By `defect-root-cause.md` it owes a
  barrier, not another entry fix.

Cost:
- Part 1: one JSON file, 9 added entries, no code. It has no cap row.
- Part 2: `tools/ci/selftest_scope.py`, possibly `.github/workflows/governance.yml`, and one
  detector. These are CI and instrument code, outside `custom_components/`. Severity is high
  and the class is hotfix, so the machinery bar does not apply.

Binding: main is red on every push, and the merge train reads main as GREEN only because the
context is not required. Every merge until part 1 lands carries the red. Every re-record
until part 2 lands can recreate it.

Rule per instance:
- **Part 1.** Add the 6 measured misses to the existing entries (artifact minus table, per
  step). Never replace the table with the artifact. Keep prepr's `required-contexts.json`
  and git `fetch`.
- **Part 2.** `record` unions with the prior entry, and a separate explicit operation drops a
  read. A pre-merge detector refuses a pull request that adds a read to a gated self-test
  without the table entry; PR 3379's diff is the positive case, and a pull request adding no
  read is the null control. Running the drift step on pull_request is decided with numbers
  (strace install and traced-run wall time from the main-push jobs, against the gate's
  budget), then wired or refused with those figures.
