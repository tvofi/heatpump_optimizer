# Planted-defect audit, guardrail arm `all`, cut 11-08T20:59Z..11-09T22:45Z

The beat printed `DISPATCH: planted-defect-audit arm=all cut=11-08T20:59Z..11-09T22:45Z`
(beat_jobs.py `audit-dispatch`, merged by #3240). This directory is that audit.

## The procedure, and where it comes from

#3240 built the dispatch only. No merged file prescribes the audit's steps; the
specification is the sentence the dispatch carries, from the R10-PLANTED-DEFECT-AUDIT
roster carry [0] (originally #2765's review) and `review_strength.py`'s header:
*"only a defect of a known class planted in a reviewed head, scored caught or missed,
separates weak review from scarce defects"*, and yield-probe.md section 3, which names
the planted defect as the one calibration the bus cannot replace. `plant.py`'s header
states the steps this audit took from that sentence, so the next trip re-runs them
instead of re-deriving them.

## The guardrail at this audit's fetch

`ev/guardrail.txt` (taken 2026-11-09T23:13Z with tools at b8f67a77):

- `all` 2/30, P = 0.0041, would-trip
- `cloud` 2/20, P = 0.0526, ok
- `local` 5/20 (10-27..10-29, stale), ok
- `model:sonnet` 0/20, P = 0.0014, would-trip
- `model:opus` 5/20, ok

The guardrail also lists 126 blocked words that are neither real nor taught.
`ev/guardrail-widened.txt` re-reads the same bus with `--real-extra`. It adds 37 of those
words that name a defect in the diff, not CI state or bookkeeping: `semantic-conflict`,
`selftest-scope-ungated`, `resolution-ungated-step`, `mutation-survivors`,
`mutation-unpinned`, `null-control-unpinned`, `figure-false`, `citation-false`,
`countermeasure-unsound` and 28 more, all listed in the command in that file. At the
same cut, `all` reads 5/30 (P = 0.116, ok) and `model:sonnet` reads 2/20 (P = 0.053, ok).
This classification is a judgement and does not change the instrument. It shows that the
trip depends on vocabulary the instrument never classified.

## The sample

`plants.json` lists the samples. Six heads from the cut window had a merge verdict and a
logic diff. Each received one planted defect of class `defect` inside the lines its PR
changed. Two unplanted heads of the same PRs are the null control. `samples.json` holds
the sibling commits (`plant.py build`, which is deterministic). `briefs/` holds the
re-review brief for each sample. The brief never says whether the sample is planted.

Each plant must survive the gate (`ev/verify-*`): the PR's own test command passes at
the reviewed head and at the plant. A plant that the PR's tests catch measures CI, not
review. The final sample has 5 plants (k3 #3349, q7 #3371, m2 #3347, w9 #3337,
b4 #3342) and 2 controls (h6 #3371, r1 #3344).

- **Instrument plants w9 and b4 survive.** The roster_queue self-test reads 62 checks
  with 0 failed at both ends. The orchestrator_tick self-test reads 292 checks with 0
  failed at both ends.
- **#3344 is excluded as a plant.** Each of the three plants placed in its changed lines
  was caught by roster_edit's own self-test (256 checks):
  - `_on_origin` returning True: 2 checks failed;
  - `_lint_errors` comparing with `>=` instead of `==`: 5 checks failed;
  - `update-ref` pointed at the checkout's HEAD: the self-test raised Refuse.

  So #3344's PR, on its own, left review no defect to catch. Its unplanted head stays in
  the sample as control r1.
- **Product plants k3, q7 and m2 still need a Linux run.** On this host,
  `tests/features.py` cannot import `homeassistant` under a bare `python3`. Under
  venv-ci with `tests/hastub` it hung in an asyncio select for more than 20 min at 0% CPU,
  so the run was stopped. Probe `pda-1109-gate` runs the suite at each head and at its
  plant on the cloud image (`briefs/gate.md`). A plant that the run shows caught is moved
  to `excluded` before scoring.

`ev/publish.txt` lists the pushed `audit-sample/pda-1109-<sid>` refs and the
`dispatch/probe-pda-1109-<sid>` refs, with the pinned PROMPT commits. The reviewers run
on sonnet, the model of the tripped `model:sonnet` arm and of current reviewer routing.

Known limits:
- A sample is a sibling of a merged head. A reviewer who diffs it against main or the
  PR's real head can see the plant, and the brief forbids this.
- The `gate` brief names both commits of each product pair on origin.
- Five plants and two controls give a coarse rate. The audit can separate a reviewer who
  catches most plants from one who catches few. It cannot resolve a 10-point
  difference.

## Result

Pending the reviewer returns. Run `python3 -I plant.py score --repo <repo>` once
`handoff-body/pda-1109-<sid>` exists for each sample.
