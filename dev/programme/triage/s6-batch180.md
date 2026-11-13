# Proposal triage, session s14, batch 180 (P599)

This batch rules `s7/triage-queue-s7.txt` line 278. The bar and the denominators are batch 141's.

Sources:
- origin/main `cbd23f1c8b`.
- The roster at `origin/handoff/audit-r10-roster` (`48ee8ce3a6`), fetched at 09:28Z.
- The verdict bus: `origin/verdict/*`, fetched at 09:25Z. The handoff bodies are `origin/handoff-body/*`.
- `tools/audit/seat/review_strength.py --by class --window d1=2026-11-10T09:00:00Z..2026-11-11T09:30:00Z`.
- Batch 163 (P577), which measured the same class on five heads at 05:01Z.
- No GitHub API calls.

## P599: MUTATION-VACUOUS-DIFF-PASS-REFUSE

Verdict: REJECT both arms:
- (b) a refusing diff-mutant step in `body_push.sh`;
- the expected saving of "one review round on ~35% of fix PRs".

Arm (a) is answered by measurement below. It needs no change.

The proposed step refuses on the generator's survivors. That generator reaches 2 or 3 of the 17
sites reviewers named in 24 h. It would have prevented the block on 1 of the 7 blocked PRs. On a
head where it catches anything, it raises about 23 survivors per real site. This repeats P577's
REJECT and adds two more heads, neither of which the generator can reach. The class keeps its
root cause `dev/audit/rca/R10-RCA-MUTATION-VACUOUS.md`, and no new seat is owed.

Source: queue line 278, 2026-11-11T09:19:12Z, orchestrator s14.

### Before: what the bus says (24 h, d1 window)

- **All reviewed PRs.** 33 reviewed PRs, real-catch incidence 8/33, first-pass yield 10/22 (0.45).
- **Blocks by class.**
  - `mutation-vacuous`: 8 verdicts on 6 PRs, first pass 0/5.
  - `mutation-survivors`: 2 verdicts on 1 PR.
- **Distinct blocked heads in the class:**
  - 3419 (`245ddf7876`);
  - 3423 (two heads);
  - 3425;
  - 3427;
  - 3428 (two heads);
  - 3431 (two heads);
  - 3448 (`185699076f`).
- **Totals.** That is 7 PRs and 10 head-blocks. Across them the reviewers name 17 sites.
- **PR 3442.** It has no verdict ref on the bus, so it is not counted.
- **Share of PRs.** 7 of the 33 reviewed PRs (21%) were blocked in the class. That is the ceiling on
  the proposal's "~35%".

### Arm (a): did the last 20 fixer handoffs run the diff pass?

The count covers the newest 20 `handoff-body/r10-*` refs, from tick-residue to process-slim-p2.
Each BODY.md was grepped:
- **2/20 (10%) ran `mutant_run.py --diff`.**
  - plan-page-residue ran it.
  - suite-env-residue also ran it. It reports "lists no mutant", because the diff touched only
    `tests/` and one shell script.
- **7/20 ran hand-built `--spec` mutants.** These were:
  - arbiter-off-restore;
  - dependabot-3414-compat-p2;
  - review-dispatch-residue-p1;
  - worktree-gc-live;
  - outside-diag-redact-location;
  - outside-dhw-charge-settle;
  - suite-env-residue.
- **11/20 carry no mutant evidence.**
- **`MUTANT_CMD` is set in 0/20.** process-slim-p2 only mentions it.

The low usage is real. The question the ruling turns on is different: would the pass have caught
what the reviewers caught?

### What the generator can reach (mutant_run.py, measured in P577)

The generator only reaches some lines:
- it mutates added `*.py` lines only;
- it skips lines under `tests/` and `dev/`;
- it applies statement-level operators only.

Site by site:
- **3419.** One of its 2 sites is caught, and only uncapped (at positions 50 and 51 of 51). The other
  site is YAML.
- **3425, 3427, 3428, 3431.** These are measured in P577. Together with 3419 they give 2/11 sites at
  cap 40 and 3/11 uncapped. 3431's site is in `tests/harness.py`, which the generator skips.
- **3423 (new): 0 of 2+ sites.** Both are on an awk line inside a shell script, and the generator
  does not read shell.
- **3448 (new): 0 of 4 sites.** The diff is `tools/audit/seat/cloud_relay.sh` alone, which is shell.
- **Total.** 2-3 of 17 sites (12-18%). The step would have prevented the block on 1 of 7 PRs (3419,
  uncapped only). That saves 1 review round in 24 h, against 33 reviewed PRs, which is 3%. The
  proposal expects 35%.

### Standing cost of a refusing step

- **Time.** At the default cap of 40, the step costs 40 × the self-test time per handoff. For the
  measured 1-4 s self-tests that is 40-160 s. A `features_block.py` command costs more. P577's
  uncapped run of one head took 31 s.
- **Noise.** P577 found 47 survivors on the 2 heads that caught anything, against 3 real sites.
  Precision is about 6%.
- **Triage burden.** A refusal would make every survivor a triage record before the handoff. That
  is about 23 records per head on such heads, which is a token cost larger than the one review
  round it saves 3% of the time.

### Bar

- None of the four >20% axes is met.
- Review rounds saved: 3%.
- Right-first-time: +1/22 first-pass reviews, about 4.5 points.
- The step does not remove the slip class, because 14-15 of the 17 sites are outside its reach.

The reach is the binding number. 9 of the 17 sites are shell, YAML or `tests/`, and the generator
reads none of them. Making the pass refuse cannot change that.

### Expected after, if adopted

The class incidence would go from 7/33 PRs to 6/33. The first-pass yield would go from 0.45 to
about 0.50, still under the 0.6 alert.
