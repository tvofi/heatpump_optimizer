Triage batch 58 records two owner decisions of 2026-10-28 against rulings already made. It moves neither earlier file and depends on no open review. It is the next rolling batch under V182, after batch 57 (#2932).
- **P271 (P266 owner answer, verbatim "keep cancelling them, yes"): ACCEPT, as P266 ruled it.**
  - The superseded-run sweep also cancels superseded runs on CP and hotfix PRs.
  - A run at a PR's live head is never superseded, and main's runs are never cancelled.
  - P266, P267 and P268 already say this, so no carry or roster op changes.
- **P272 (P270 owner order, "fix cache proposals 1-6 asap", "also fix the side defects"): REJECT, for P270's own candidate carry.**
  - The V184 measurement refutes brief ordering and fixed boilerplate, so R10-FLOW-DESIGN-STAGES takes no reorder carry.
  - The six measured gaps (ranked ~45-55M, ~20-25M, ~20-25M, ~5.8M, ~3-5M and ~2M eq/day) and the side defects are owner-ordered.
  - Four fly-ins carry them: R10-FLY-CACHE-PROMPTS, R10-FLY-PREPR-SUMMARY, R10-FLY-INSTRUMENTS-SPLIT and R10-FLY-SWEEP-DEFAULTS. Their briefs cite the owner order, not this file. The roster gate refuses a citation of a ruling that is not an ACCEPT, and P270 reads DEFER while P272 reads REJECT.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`2fcad6f7710f72c9b1e7683a08afd9f744ef03e9`; the file is the whole diff against `b0b2d7697f8c5baaef2c082d9bf3242b57249e68`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` (line 455).
- On the committed file, it reads P271 as `ACCEPT` and P272 as `REJECT`.
- A text citing `#P272` is refused as `not an ACCEPT ruling (REJECT)`. That refusal is why the fly-in briefs cite the owner order.

## Null control

With the file absent, a text citing it returns `the triage ruling dev/programme/triage/s6-batch58.md is not on the roster branch or origin/main`.

## Figures

- V184 measurement: `~/hpo-orch/r10s6/proposals.md:1009-1011`.
- 300 s wait defaults: `tools/audit/seat/ci-watch.sh:290`, `tools/audit/seat/merge_train.py:486` and `tools/pr/prepr.sh:2549`/`:3285`.
- Roster `54bd827cf` carries none of the four fly-ins. Their queued `append-group` lines (`s7/roster-queue-s7.txt:175-178`) are `#refused`, because they pass free text where the op takes a group JSON path (`seat-ledger.md:2088-2089`).

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
