Fix review: blocked d7c830c2fa99ee2428f86aa469a7da540f21eeb9 carry-missing: the class search the body names as landed in dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md is not in that file

Round 1.
seat: review-2074
bus-nonce: c80e7807aafda8dcaf43b91957f7a61d
Measured at `d7c830c2fa99ee2428f86aa469a7da540f21eeb9` in a detached worktree at
`/Users/timmalmstrom/hpo-seats/review-2074/wt`; merge base `b2b6acd64` = `origin/main`
at review (three-dot and two-dot diffs coincide). Contract read at this head:
`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is
empty, so the copy I executed is current.
Evidence: /Users/timmalmstrom/hpo-seats/review-2074/evidence

## What is blocked, and why it is one edit

The mechanism is sound — every number below re-derives, and the detector fails on the
defect and passes on the fix. The block is on the **record the PR lands**: the body
points a later reader at the RCA document for two findings that are not in it, and the
class's own table contradicts the count the document opens with.

1. **The class search is not in the landed document** (`carry-missing`, primary).
   The body's `## Forward-carry` states: "The RCA's other same-shape causes
   (`record-autofix` has no `if:`; `closures-autofix` is `pull_request`-only so a
   schedule-run staleness has no repair lane) are **named in the RCA doc**". They are
   not. `grep -n -i "record-autofix\|closures-autofix\|class" dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md`
   returns nothing (exit 1). The only copy is
   `/Users/timmalmstrom/hpo-seats/rca-nightly-red/RCA.md` §3 — an out-of-tree scratch
   file, which is precisely what `defect-root-cause.md`'s "Where it is recorded" exists
   to prevent ("a pull-request body or comment can be deleted or its author retired"),
   and `root-cause.md` §3/§6 make the class search part of the deliverable, §6 adding
   "with the reproduction **and the class search** added". Neither seam has another
   destination in the tree: `record-autofix`'s live rows (#1957/#1962/#1974) are about
   its identity and lookup, not its missing job-level `if:` on `schedule`/`push`;
   `closures-autofix`'s live row (#1868) is about reporting a left-behind failure, not
   about being `pull_request`-only. `finding-propagation.md`'s Enforcement is the
   obligation this fails: "The producing PR does not merge until the carry is **in the
   tree**. Its body names the file and the stage that received it, so a reviewer opens
   the destination rather than taking the claim." I opened it. Fix: add the diagnosing
   seat's §3 to the RCA doc (or, if they are to stay the orchestrator's, name a
   destination that exists and correct the body). One section, no code.
2. **The opening count is over-attributed, and one table column mixes a measurement with
   an inference** (`brief-citations.md`/`writing-for-agents`: a stated count the tree
   answers; this sentence is carried from the diagnosing seat's §1, which says the same,
   so it is a correction to the record rather than to the seat's work). The doc's line
   22-24 and the body's line "which reddened four of the six consecutive scheduled runs"
   attribute four nights to **the bound**; the doc's own §1 table (its lines 37-41) shows
   the bound tripping and CI printing its number on **two** nights (10-07 1576 s, 10-08
   2401 s), and for 10-03/04/05 that the bound was only the bare floor with no printed
   timeout — those two nights reddened on the `EXCLUSIVE` null-control arm, which §5
   routes to the owner and this PR does **not** fix, and 10-05 reddened on
   `record-autofix` alone. In the same table the "CI printed" column carries CI's text for
   the two real timeouts and an inferred "pool cost >= 1573 s" (quoted onward with `"`) for
   the three floor nights, so a reader cannot tell which rows are measurements. §4 already
   states the honest family figure ("the bound/**null-control** mechanism fired on 4 of the
   6"). Fix: say which arm, per night, in §1's sentence, and mark the inferred cells as
   inferred — the cost test survives it either way (the bound arm alone is 2/6 = 0.33/night
   against 0 s + seconds of standing cost), so this is accuracy, not justification.
3. **Two figures without their enumerator** (same rule, fold into the same edit): §4's
   "the cron's measured 6 h 19 m - 6 h 53 m dispatch delay" names no command or run ids
   (the diagnosing seat's §2 enumerated four dispatches and the cron string; §7 does not
   carry this one), and §2's "The honest factors run 0.47-3.27" prints a table whose
   minimum is 0.70 and whose only 3.27 attribution is to a night not in the table — a
   reader cannot get 0.47 from anything shown.

## Reported, not blocked: the wiring is unpinned, in an idiom this file already owns

The five new `entities.py` checks drive the functions; none pins the carrier that makes
them matter. `grep -n "pool-seconds\|pool_seconds" tests/entities.py` shows no assertion
against the YAML for `--pool-seconds`, the `if: always()` save, or the cache key, and no
`_MUT_BODY` assertion that `main()` calls `seed_pool_seconds`/`write_pool_seconds` — while
the same file states the reason in its own words two sections earlier: *"The pre-pass is
wired into the driver's main flow: defined-but-never-called is the silent-green shape this
repository keeps finding"* (line 29915), and it then supplies the exact instrument —
`_MUT_BODY = pathlib.Path(_mut.__file__).read_text()`, used at line 30437 for
`"--drain is wired: its slice from drain_pool, its pins written out, the ledger here
untouched"`, and `_MUT_BW_MISSING` at line 31800, ~70 lines after the new checks, for
"Wired, against the YAML: each caller passes a budget under its timeout". So deleting
`--pool-seconds` from `tests.yml` today, or reverting line 3453 back to
`own_s = recorded_seconds()`, leaves all 2239 checks green and the nightly back on 3x a
solo recording — the defect of this PR, restorable without tripping a check.

I did not block on it: no check the PR claims is vacuous, the mechanism works as wired
(I traced the wiring read-to-write: `3436` read, `3453` seed, `3461` record, `3598`
persist, argparse flag confirmed by `--help`), and this is a coverage gap rather than a
moved metric. But it is two pins in the file's existing idiom, in the same round as the
record fixes, and the class this PR is the countermeasure for *is* "a lane that does not
call its own instrument".

One residual, stated so the record is complete and no seat has to re-derive it: a
baseline that **times out** contributes no `measured_pool` entry (`if not run.timed_out`),
so on a cold cache a driver whose pool cost already exceeds 3x its solo recording
forwards the prior seed unchanged rather than learning the bound it just proved too
small. Not a regression — the new bound is ≥ the old one for every driver at every head
(`RESULT seed-never-lowers: PASS`) — and it is the form `RCA` §5 item 2 prescribed, with
the new refusal text naming the remedy for a human. Worth one line in §5 as a named
limitation.

## What I re-measured, and it is real

The dispatch's claims 1-7, each with my own instrument at this head, not the fixer's:

- `RESULT bound-arithmetic: ALL-EQUAL` — with the tree's own `driver_timeout` and
  `seed_pool_seconds` over `git show <head>:tests/closures.json` for the six heads:
  10-03/04/05 (absent recording) -> **1200**, 10-07 (525.3) -> **1576**, 10-08 (800.2)
  -> **2401**, this merge base (1489.6) -> **4469**; and with the pool cost seeded,
  solo 800.2 / pool 1573 -> **4719**, pool 2400 -> **7200**. The bound is exactly
  `max(floor, ceil(3 x max(solo, pool)))` — the fix's arithmetic, not `3 x solo`.
  `evidence/bound_rederive.py`.
- `RESULT seconds-band: UNCHANGED` — `git diff b2b6acd64...HEAD -- tests/closure.py` is
  **0 lines**; `SECONDS_BAND = 2.0` at both ends, `TIMEOUT_SCALE = 3` at both ends. The
  fix decouples the bound from the band as §5 required and re-tunes nothing, so no
  `metric-gamed: seconds band`.
- `RESULT refusal-path-drive: 17 of 17 assertions hold` — I drove `baseline_refusal`
  with a fabricated stale recording (rc 124, stderr `timed out after 2401s`, committed
  `{seconds: 800.2, rc: 0}`): the verdict prints "the baseline TIMED OUT in …", the
  bound, the recording, `= 3.00x the recording, committed rc 0`, "the recording is
  STALE, not the suite", and the re-record remedy, and it does **not** contain "Fix the
  suite first"; a real failing check still says "Fix the suite first" and names the
  check and never says STALE; a mixed baseline prints both arms; the green baseline
  returns `None`; `full -> 1`, `changed -> 0` unchanged from the base. The docstring's
  false claim is qualified ("for a FAILING CHECK"), not deleted, as the RCA prescribed.
  `evidence/refusal_drive.py`.
- `RESULT targeted-block[HEAD]: 0 of 5 failed` / `RESULT targeted-block[REVERTED
  mutation_table]: 3 of 5 failed` — **my step-14 arm**: `tests/mutation_table.py`
  reverted to `b2b6acd64` in my worktree, the five checks run (their own source region,
  `entities.py` lines 31585-31728, execed verbatim — not re-implemented), then
  `git checkout HEAD -- tests/mutation_table.py` and confirmed byte-identical to the copy
  I saved. The three red are exactly the defect checks; the two null controls stay green
  **at both ends**, which is the flat-by-design companion `fixer.md` step 3 owes. So no
  pin is vacuous and no pass is bought by the instrument.
  `evidence/block_HEAD.txt`, `evidence/block_REVERTED.txt`.
- `RESULT seed-never-lowers: PASS` — 42 (solo, pool) pairs plus all 34 drivers in the
  committed table: no seeded bound is below its unseeded bound. `RESULT fail-soft`:
  `pool_seconds(None)`, a missing path, and 10 malformed bodies (`""`, `{not json`,
  `[]`, `{"seconds":"x"}`, `null`, negative, bool, string root, wrong container) each
  return `{}`. `RESULT round-trip: PASS` — `write_pool_seconds` -> `pool_seconds`
  recovers `{boost_drift_replay: 1573.0, features: 772.0}`, file in the canonical
  sorted layout with `head`.
- `RESULT carrier-fires-on-refusal-night: YES` — judged on its merits, and the deviation
  is right. `mutation-ledger`'s job condition is `!cancelled() && github.ref ==
  'refs/heads/main' && (schedule || …)`, `needs: [recheck-gate]` — it runs on the
  schedule whatever its drive concluded, and both the stage step and the
  `actions/cache/save` are `if: always()`, so the measurement is written and saved on
  exactly the night `mutation-ledger-push` would not have run (that job's `needs.mutation-ledger.result
  == 'success'` I re-read at this head: it is the trap the RCA named). The unique-per-run
  key with `restore-keys: pool-seconds-` is the standard "write a new entry, read the
  latest prefix" shape, so the save cannot collide and a re-run just fails soft
  (`continue-on-error: true`). Fail-soft is real at every link: absent restore ->
  `--pool-seconds` path missing -> `{}`; `cp` of a file the run never wrote falls through
  to `||` and the restored seed stays and is re-saved; the write is wrapped so an
  `OSError` warns instead of masking the verdict. And the seed never lowers a bound, so a
  cache miss is today's behaviour, not a smaller one. `actions/cache` needs no write
  grant and no secret: workflow `permissions: {contents: read}`, and `git diff` of the
  workflow adds **no** `secrets.` and no `contents: write` — decision 0011's measuring-job
  invariant holds, and the deviation is better-founded than the carrier the RCA named,
  because that carrier would have widened a policy grant a fixer may not widen.
  I also checked the extra file cannot disturb the writer: `apply_drained` reads only
  `status`/`head`/`pins.json`, the drain dir lives in `runner.temp` outside the checkout,
  and `drain_write_set_problems`/`git add` take explicit paths — so `pool_seconds.json`
  cannot reach `git status`.
- `RESULT null-control-figures: RE-DERIVED` — the tree's own `recorded_seconds()` at this
  head gives 730.5 / 760.6 / 259.6 / 0.9 / 199.0 exactly as §6 states, and every seeded
  bound covers its CI pool cost; `env_drift.py` stays floor-bound at 1200 before the fix
  and rises to 1572 after, covering its 524 s pool cost either way — the fix reads flat
  on it, as claimed.
- `RESULT record: CLEAN-AT-BOTH-ENDS` — `python3 -I tools/audit/fold_ledger.py check`:
  **both** `b2b6acd64` and this head print "28 classes, 549 instances, 39 in-tree judge
  survivors, 101 rca entries / 0 violation(s)" — nothing newly refused. `bugclasses.json`
  moves `RCA-1565-mutation-timeouts` partial->done with `process_state` (c) + the (d)
  arm, `parts_missing: []`, the cost test present, and `in_tree_home` / `doc` citing the
  new path (fold_ledger is what validates that citation, and it passes). `RESULT
  structure: STRUCTURE RATCHET PASSED` at head, and `*_budgets.json`: **0 lines moved** —
  no raise, correctly, since #2074 was dispatched without the owner's. `RESULT orphans:
  []` at both ends, so the new tracked `dev/audit/rca/` file is already classified and
  costs no future full gate.
- `RESULT claims-and-versions: NONE-MOVED` — `tests/golden/claimed_drift.txt` and
  `tests/golden/card_claimed_drift.txt` byte-identical to `origin/main` (0 diff lines),
  `VERSION`, `RELEASE_NOTES.md` and `custom_components/heatpump_optimizer/manifest.json`
  untouched.
- `RESULT mutation-lane: empty scope, read from the log not the conclusion` — job
  `113815002602`: "MUTATION TABLE -- scope changed: no production code line added or
  modified against the base" / "MUTATION TABLE PASSED (empty scope)", and "4623 unpinned
  site(s) of 5891 candidate sites, 4623 at the ratchet base b2b6acd64…" — the count is
  identical at both ends, so the green is "none was evaluated", not "no mutant survived",
  and no ledger or ratchet number moved (`fix-review.md` step 11's separation).
- `RESULT merge-state: CLEAN` — `git merge-tree --write-tree origin/main HEAD` exits 0
  with no driver refusal on stderr; the API's `mergeable_state: blocked` is the draft +
  code-owner review, not a conflict (step 13).

## Step 11, the checks at the head

`nightly-status` is **success** at this head (`113815002358`), as is `delivery-status`,
so no red needs answering there — and the arm that governs is the **non-exempt** one:
this diff touches `.github/workflows/tests.yml`, which is what `nightly-status` reads, so
`defect-root-cause.md`'s exemption for the main-grading reporters does not apply and the
body owed the answer. It gives one, and correctly identifies the red it anticipated as
main's stranded nightly conclusion rather than a regression this diff introduces.
`instrument-self-tests` **success** (`113814674855`) — the lane that pins workflow edits
is green, as is `budget-raise-gate` (`113814674538`), `pr-contract`, `briefs`,
`policy-docs`, `env-matrix`, `closure-scope`, `typing`, `hassfest`, `validate-hacs`,
`browser`, all three CodeQL `Analyze` arms.

Full step-11 state at the head, latest run per name from the check-runs API (polled every
300 s to settle; `evidence/checkruns_final.tsv`, `evidence/ci_poll.log`,
`evidence/ci_required_at_head.txt`, `evidence/fast314_gate_lines.txt`). **CI settled green:
all 17 required contexts present and `success`, none red, none absent.** Run 37928966135 /
37928966128 / 37928966187 / 37928966090 at this head, settled 13:06:14Z.

`fast (3.14)` (job `113815002902`) is the whole-file run I cite rather than repeat: it
printed `GATE_SCOPE: auto`, `MODE: FULL -- every script runs, nothing is scoped out`
(`tests.yml` changes the gate itself, as the body says), then **`ALL 2239 ENTITY CHECKS
PASSED`** and `STRUCTURE RATCHET PASSED`. So the five new checks are green inside the real
2239-check run at this head, and my targeted block run above is the failing arm, not a
substitute for the whole file. Other greens: `closures`, `coverage`, `coverage-ratchet`,
`typing`, `env-matrix`, `briefs`, `policy-docs`, `wave-script`, `pr-contract`,
`closure-scope`, `browser`, `hassfest`, `validate-hacs`, `mutation`, `budget-raise-gate`,
the three `Analyze` arms, `CodeQL`, `delivery-status`, `nightly-status`,
`instrument-self-tests`. Skipped, all expected on a non-main `pull_request`: the four
`*-autofix` lanes, `record`, `recheck-gate`, `slow`, `nightly-ha`, `mutation-nightly`,
`mutation-ledger`, `mutation-ledger-push`, `mutation-pins`, `mutation-pin-plan`,
`delivery-status-publish`.

## Forward-carry

The (iv) arm — honouring `EXCLUSIVE` under `--scope full`, an unpinned-count raise,
`budget-raise-gate` (0013) — **is** carried where the body says it is: the RCA doc §4
"(iv) Not built, routed to the owner" and the `bugclasses.json` countermeasure both name
it and its price (211 s + 430 s x2 lanes, ~21 min/night). That destination exists and I
read it. The class search in blocked item 1 is the one that does not.

## What this round owes

Round 1, so `fixer.md` owes a repair, not a re-cut. All three blocked items are record
edits to one file this PR already adds (`dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md`), plus
the body's two sentences; nothing in `tests/mutation_table.py`, `tests/entities.py` or
`.github/workflows/tests.yml` needs to change for them, and every measurement above stands
unchanged. The wiring pins are offered in the same round, not required by this block.
Route it back to the fixer that authored `955dd09a3`, not to a fresh seat: no production
line is in question.

The head is still `d7c830c2fa99ee2428f86aa469a7da540f21eeb9` when I post (re-read after CI
settled, per step 12), `draft: true`, `state: open`.

## Head discipline

I measured `d7c830c2fa99ee2428f86aa469a7da540f21eeb9`, the PR's head at dispatch and the
SHA its body names under `## Head`. If the head moves under this verdict, the code
numbers above survive only for the SHA named here; the CI paragraph would not.
