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
review, so it is replaced. #3344's first plant failed this check
(`ev/verify-tools/t5-first-plant-caught.log`, roster_edit self-test 2 failed) and was replaced.

## Result

Pending the cloud reviewer returns (`plant.py score`).
