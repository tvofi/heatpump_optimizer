# Response to the design review: revision 1 of the combined CI design (R10-CI-LAYOUT)

Design-revision seat, 2026-10-18. Neither the designers nor the reviewer.

**Inputs, read in full:**
- phase 1, `probe/design-ci-layout` at `b7a76185`;
- phase 2, `probe/design-ci-umbrella` at `7fdd39c4`;
- the review, `probe/design-ci-review` at `f7b28312` (`REVIEW.md`, `ev/`, `tools/`), verdict *revise*;
- policy from `origin/main` at `07a09406`: `CLAUDE.md`, `judge.md`, `ci-autofix.md`,
  `gate-scoping.md`, `orchestrator.md`.

**This commit holds:**
- `DESIGN-P1.md`: PR 1 (phase 1, 2(c) replaced by W1 at its source, plus the `ci.yml` stub);
- `DESIGN-P2.md`: PR 2 (the umbrella);
- `measure/p1/`, `measure/p2/`: the designers' instruments and saved API responses,
  unchanged;
- `measure/rev/`: this seat's instruments and outputs.

Owner rulings applied as made: D-1 approve (refused branch kept specified), D-2
`arch-score` gate-required when the diff reaches `custom_components/`, D-3 keep
`merge_group`, D-4 drop C1 in PR 1 (the proof is shown covered, item 8), D-5 keep O17
with its soundness check, and the variant: a review event re-runs only
`budget-raise-gate` and `gate`. Plan: two PRs, phase 1 first; the fixer phase fans out
to cloud workers per unit, each verifying with `workflow_dispatch` CI (DESIGN-P2.md
section 10).

| item | resolved by | design sections | evidence (re-run here) |
|---|---|---|---|
| 1 | three concurrency lanes; verdict preludes wait for every earlier run; restated rule | P2 2.2, 2.3, 4.3 | `gate_sim.txt` (case E), `verdict_wait.txt` |
| 2 | applicability from the event; prelude must succeed and agree; kind from `run-name`; sources at the live base | P2 2.2, 4.1 | `gate_replay2.txt`, `gate_sim.txt` (B-B4, D) |
| 3 | every code unit, governance/hassfest/validate included, guarded on the prelude's kind | P2 2.2 | `gate_sim.txt` (C, D3) |
| 4 | the rerun hook kept and generalised as `gate-sweep.yml`; `refresh` added; M-2 decides deletion | P2 2.1, 4.1, 4.3, 10 | `gate_sim.txt` (F, every-suite reading; hook ablation) |
| 5 | the gap stated; `pr-contract` waits for code scanning; dispatch writers ref-guarded; the premise made true | P2 1.6, 2.1, 4.3 | `check_writers.txt` |
| 6 | approvals kept; M-3 measures held-run shadowing in U0/U10; tool, nudge.md, INSTRUMENTS.md named | P2 5, 9, 10 | the tree's own measurement (`approve_held_runs.sh:12-15`) |
| 7 | `recheck` and `no-skip` declared on `ci.yml`, passed as `workflow_call` inputs, read as `inputs.*`; `DISPATCH` keeps `-f recheck=true` | P2 2.2, 9, 10 (U5) | static map rows in U5 |
| 8 | W1 at its source in PR 1, every C1 site listed; numbers at measured bare cost; PR 1 specified | P1 2(c), 2(a), 4; P2 3.1, 8 | `c1_sweep.txt`, `c1_consumers.txt` |
| 9 | static half added; `UNREAD` and event mismatch refuse; PR-only jobs get `pull_request` AFTERs | P1 4; P2 10 | `unitcheck2_selftest.txt` (12/12) |
| 10 | section 4.1 is now a module both replays import | P2 4.1, 4.4 | `gate_replay2.txt` (28/28), `gate_sim.txt` |
| 11 | every reader named, each changed or dispositioned | P1 2(a); P2 9 | `readers_triage.txt` |
| 12 | (a) rollback order; (b) forgery pins; (c) source precedence; (d) U9 on `-all`; (e) callee floors | P2 2.1, 4.1, 5, 7, 10 | `gate_replay2.txt` (12(c) rows), `unitcheck2_selftest.txt` (P8) |

One fact beyond the review changed the design most, and it is recorded in the tree:
`tools/policy/budget_raise_gate.py:604` (#2009) says "GitHub's ruleset refuses a merge
while any suite at the head carries a non-success run". Phase 2 assumed the newest
`gate` binds. Revision 1 is built and scored to be right under both readings (see
item 4).

---

## Review item 1

**The review:** one `CI-<pr>` group for code and verdict events loses runs. GitHub keeps
one pending run per group and a new one cancels it whatever `cancel-in-progress` says.
So an edit landing 0-4 s after a push replaced the pending code run (case E), and
anyone able to review could cancel one. P2:479-481 claimed the opposite.

**What changed** (DESIGN-P2.md 2.2, 2.3, 4.3):
- **Three lanes per PR in one `concurrency:` block.** Code events (`opened`,
  `synchronize`, `reopened`, a retarget) go to `CI-code-<pr>`, body edits to
  `CI-edit-<pr>`, reviews to `CI-review-<pr>`. Bot-sent and dispatch runs keep run-id
  groups, as today. An event can now only replace or cancel an older event of its own
  kind, whose work the newer one repeats with fresher inputs. It can never touch a code
  run. `cancel-in-progress` is true in every PR lane for a non-bot sender.
- **The prelude's wait is kept and made sound.** Phase 2 waited for "code runs",
  which cannot be identified before they start. A verdict prelude now waits until
  every earlier `ci.yml` run at the head (lower run id, not held) has completed. It
  needs no kind, and it cannot cycle, because a run only ever waits for runs with a
  lower id. It also orders the `gate` checks.
- **P2:479-481 restated** against the documented rule (4.3).

**Evidence:**
- `python3 -I measure/rev/gate_sim.py`, case E (push while the old head runs, edit
  2 s later):
  - revision 1 passes under all three readings;
  - phase 2 as written ends FAIL "no code verdict at this head", stuck until the next
    push.
- Cost, `python3 -I measure/rev/verdict_wait.py measure/p2/raw`:
  - 18 of 21 verdict events would wait, median 1406 s, max 3450 s;
  - **8.07 runner-hours over 22 heads** (8.10 without the lanes' cancel-in-progress).
  - This is runner time, not wall clock, and DESIGN-P2.md R-2 states it.
  - The cheaper alternative was rejected: it puts `arch-score` on every PR's critical
    path, 62 s.

## Review item 2

**The review:**
- A retarget queued behind a running run, then an edit, cancelled the retarget. The
  edit run then carried the old-base code run, so the gate went green with no code run
  at the new base (case D).
- The runs API cannot tell a past run's kind.
- The gate took applicability from the prelude it judged, so a planted `pr=''` passed
  (case B).
- `prelude` was never required to succeed.

**What changed** (DESIGN-P2.md 2.2, 4.1, `measure/rev/gate_model.py`):
- **Applicability from the event.** The gate derives `kind`, `pr` and `base` from
  `github.event_name`, `.action`, `.changes.base`, the payload or the dispatch inputs.
  The body units are owed whenever the *event* names a PR.
- **The prelude must conclude `success`**, and its `kind`/`pr` must equal the gate's
  own derivation.
- **A dispatch is re-verified by the gate itself.** A named PR must be open and headed
  by this SHA. An unnamed dispatch at a PR head fails.
- **Kind is recorded at creation, by `run-name`**, returned as `display_title`. It is
  present even for a run cancelled before any job. An artifact, the review's example,
  would be missing for exactly those runs.
- **Sources must have judged the PR's live base.** Case D becomes a FAIL until the
  retarget's own run decides. Separate lanes mean the edit can no longer cancel the
  retarget anyway.

**Evidence:**
- `measure/rev/gate_replay2.txt`, perturbations:
  - prelude failed → FAIL;
  - prelude `pr=''` → FAIL;
  - a source at another base, or a retarget since → FAIL.
- `measure/rev/gate_sim.txt`:
  - plants B, B2, B3, B4, I2, I3 are refused under all three readings; phase 2
    refuses none;
  - case D is a correct FAIL under revision 1, while phase 2 is green for 6952 s with
    the code red at the new base.

## Review item 3

**The review:** governance, hassfest and validate were guarded on
`action != 'edited'`, so a retarget (a code event) skipped them. Its gate was then
always red (case C).

**What changed** (DESIGN-P2.md 2.2): every code unit is guarded on
`needs.prelude.outputs.kind == 'code'`. Phase 2's W4 (no prelude edge for those three)
is withdrawn. They gain a prelude and a queue hop (about 10 s) on paths that end
minutes before `tests`, so the critical path does not move.

**Evidence:** `gate_sim.txt`. Case C (retarget, code green at the new base) and D3
(retarget behind a waiting edit) pass under all readings. Phase 2 FAILs both.

## Review item 4

**The review:** deleting `budget-raise-gate-rerun.yml` contradicts a measurement in the
tree. Keep a re-run hook until U8 shows the review run's `gate` binds. It must re-run
the code run's `budget-raise-gate`, `pr-contract` and `gate`, because phase 2's gate
reads only its own run.

**What changed** (DESIGN-P2.md 2.1, 4.1, 4.3, 10):
- **The hook is kept, as `gate-sweep.yml`.**
  - Trigger: every `CI` completion whose latest `gate` is green at a PR head.
  - Action: it re-runs the `gate` job of every older run at that head whose `gate` is
    not green.
  - It keeps today's file discipline: default-branch checkout, program restored,
    `python3 -I`, `actions: write, contents: read`.
  - Loop-free: it never re-runs its trigger or a green `gate`, and a red re-run
    triggers nothing.
- **Why only `gate` is re-run, and why that meets the item.** The premise "the gate
  reads only its own run" is replaced: in 4.1 the gate reads, for every unit, the
  newest run at the head that evaluated it. After an approval the code run's re-run
  `gate` reads the review run's green `budget-raise-gate` directly. Re-running the
  units themselves would re-run nothing the verdict needs, and `rerun-failed-jobs`
  would also re-run a failed `tests` lane, a flake retry nobody asked for.
- **The review's finding is wider than one hook.** The tree records both readings of
  the merge box:
  - `budget_raise_gate.py:604` (#2009): any red suite at the head blocks;
  - the body-edit practice of `arch-score.yml` and `pr-contract.yml`: a newer run
    answers an older red.
  So every `gate` at a head must converge on the head's current verdict. Revision 1
  adds a **defer rule**: a gate is red while any other run at its head is unfinished.
  It also adds `refresh`, a job in every PR-event run that re-runs the head's earlier
  green `gate` jobs, so an event cannot leave a stale green.
- **M-2** (U0/U8, on a live probe PR) measures which reading GitHub uses. If an older
  red `gate` does not block beside a newer green one, PR 2 deletes `gate-sweep.yml`.
  Otherwise, or if the reading is not decisive before the cut-over, it ships
  (DESIGN-P2.md R-8).
- P2:818-823's fallback is corrected.

**Evidence** (`gate_sim.txt`):
- Under the every-suite reading:
  - phase 2 fails case F (approval of a raise): the code run's red stays;
  - revision 1 passes.
- Revision 1 agrees with the oracle 16/16 under each of the three readings.
- **Ablations, the hooks' own null control:**
  - without the sweep, the every-suite reading agrees on only 9/16;
  - without `refresh`, the longest false-green window grows from 11 s to 2048 s, on
    the retarget case.
- `gate_replay2.txt`: an older red code-run `gate` re-judged after a newer green code
  run → pass; after only a newer edit (its own code red) → still FAIL.

## Review item 5

**The review:** `pr-contract-rerun.yml`'s deletion rested on "no workflow outside the
umbrella writes a check at a PR head". Code scanning's `CodeQL` check
(`github-advanced-security`) is at 17 of 22 heads. It is red at 2, each time after the
last `pr-contract` had concluded.

**What changed** (DESIGN-P2.md 1.6, 2.1, 4.3):
- **The gap is stated.** Two writers broke the premise: code scanning, and a manual
  `workflow_dispatch` of any standalone workflow on a PR branch.
- **`pr-contract` waits for code scanning** before it lists reds:
  - for each CodeQL leg this run's (or the source run's) `codeql` unit uploaded, it
    polls `code-scanning/analyses?ref=<PR ref>&sha=<head>` until that category's
    analysis exists;
  - it needs `security-events: read`, is bounded at 10 minutes and fails closed;
  - it then lists reds with no app filter, as today, so the code-scanning red is owed
    an answer.
  - No policy exclusion is needed. U6 plants a code-scanning alert to show it listed.
- **Dispatch writers are closed.**
  - The units lose their standalone `workflow_dispatch`.
  - `nightly.yml`, `merge-main.yml`, `release.yml` and `pages.yml` guard every job on
    `refs/heads/main` (release and pages: or a `v*` tag).
  - `entities.py` pins both.
- With both done, the premise is true, so the deletion stands.

**Evidence:** `python3 -I measure/rev/check_writers.py measure/p2/raw`:
- the only two writers at the 22 heads are GitHub Actions and code scanning;
- the code-scanning check concludes within −8 to +63 s of the first analysis job's end
  (median −6 s);
- it concluded after the last `pr-contract` at 9 of 17 heads, twice red (`acf14d8f22`,
  `b931d0f44a`), which reproduces the review's two.
- `pr-contract` needs `codeql`, whose run ends a median ~750 s before Tests' (1306 s
  against 2059 s, `durations.txt`), so the wait costs about nothing on the critical
  path.

## Review item 6

**The review:** phase 2 deleted the held-run approvals as harmless, against
`approve_held_runs.sh:12-15` (PR #1276: a held `Tests` run's check "shadowed the
dispatched one in the merge box"), and never named the tool, `nudge.md:85`,
`INSTRUMENTS.md:36` or `hpo-runs`.

**What changed** (DESIGN-P2.md 5, 9, 10):
- **The approvals are kept, retargeted to `ci.yml`, until measured:**
  - the three autofix jobs' and `merge-main`'s approve steps stay;
  - so do `approve_held_runs.sh`, `nudge.md:85`, `INSTRUMENTS.md:36` and the
    `hpo-runs` identity;
  - one dispatch (`ci.yml -f pr -f base`) replaces four.
- **M-3** (U0 and U10) measures on a draft probe PR:
  - (a) whether an App push and a `GITHUB_TOKEN` push leave a held `ci.yml` run;
  - (b) what `statusCheckRollup` and `check-runs?filter=latest` report for `gate`
    with a held run beside a green dispatched one.
- The approvals and the 4-of-22 duplicate code runs go **only** if (a) finds no held
  run or (b) shows no shadowing. The tool and the two policy lines are retired in the
  same PR. W2's saving is not claimed until then.
- The tool, `nudge.md:85`, `INSTRUMENTS.md:36` and `hpo-runs` are named in section 9.

**Evidence:** the tree's own measurement, quoted in DESIGN-P2.md 5, against the
contradicting notes (`ci-autofix.md` 2026-10-15 vs `merge-main.yml` 2026-10-09) and
phase 2's 0 `action_required` runs. No measurement here can settle shadowing; it
needs a live PR, which M-3 is.

## Review item 7

**The review:** `ci.yml` declared only `pr`. `lane-proofs` and the `laneskip` step read
`github.event.inputs.recheck`/`no-skip`, which in a callee is the caller's payload. And
`merge_train.DISPATCH` dropped `-f recheck=true`.

**What changed** (DESIGN-P2.md 2.2, 9, 10):
- `ci.yml`'s `workflow_dispatch` declares `pr`, `base`, `recheck` and `no-skip`, all
  optional strings. PR 1's stub declares the same four, so dispatches validate before
  PR 2.
- `tests` receives `recheck` and `no-skip` as `workflow_call` inputs.
- `tests.yml` reads `inputs.recheck`/`inputs.no-skip` with `github.event_name ==
  'workflow_dispatch'`. Inside a callee that is the caller's event.
- `DISPATCH = (("ci.yml", ("-f", "recheck=true")),)`.
- U5's runtime half adds dispatch pairs with `-f recheck=true` (lane proofs and lane
  skip run) and `-f no-skip=true` (every lane runs). Its static map lists each changed
  `if:` row.

**Evidence:** the static instrument refuses any `if:` change the map does not admit
(`unitcheck2_selftest.txt`, P4). The U5 map admits exactly these rows and prints each
before and after.

## Review item 8

**The review:**
- The redundancy holds only if the composition is removed at its source in the same
  PR. `coverage_tree.sh:190-200` would keep paying `strace`.
- The 239.1 s "upper bound" is not one: CI measured 221/430/424/480 s bare. At that
  cost V1 gains a median 264/232 s, not 342 s, and "V1 is as fast" is false.
- PR 1 left `composed-proof` in `nightly.yml` and `REQUIRED_LANES`.

**What changed:**
- **W1 at its source, in PR 1** (DESIGN-P1.md 2(c)). Every site that
  `sh measure/rev/c1_consumers.sh origin/main` lists (10 files) has its change:
  - `coverage_tree.sh`'s `COMPOSED` list and composed branch go, so no `strace` runs
    in `coverage`;
  - `tests.yml`'s three C1 sites go, and so does the `composed-proof` job;
  - `derive_closures.sh`'s `COMPOSED_CONSUMED` case goes;
  - `closure.py`'s `COMPOSED`/`CHEAP_ARGV_OR_ENV`/`composed_verify` and two
    subcommands go;
  - two files are deleted;
  - `entities.py`'s pins go, and a no-C1-token pin is added;
  - `python3 tests/closure.py prune` repairs the three phantom closure entries;
  - two self-test fixtures that only borrow the name are kept, and the PR body shows
    that `c1_consumers.sh HEAD` lists only them.
  - Phase 2's "can later delete" is withdrawn.
- **The proof is covered** (D-4's condition). `composed-proof` compared a recording
  consumed from `coverage` with a bare one. With nothing producing or consuming a
  traced recording, `closures` records every script bare, through the same `rec()`
  path every other script and every C1 refusal took. No second recording is left for
  the property to compare.
- **The numbers at measured cost** (DESIGN-P1.md 2(c), DESIGN-P2.md 1.1, 3.1, R-6):

  | bare cost charged | V1 median gain | runs slower | worst | V2 |
  |---|---|---|---|---|
  | 239.1 s | 342 s | 1/24 | −163 s | 343 s |
  | 427 s | 264 s | 2/24 | −351 s | 343 s |
  | 480 s | 232 s | 2/24 | −404 s | 343 s |

  - V1's median gain equals V2's at a 148 s bare cost and reaches zero only at 1065 s.
  - "Upper bound" and "as fast" are withdrawn. V1 is chosen for what it deletes.
  - The unmodelled `strace` offset only helps V1.
- **PR 1 specified:**
  - `composed-proof` neither moves to `nightly.yml` nor joins `REQUIRED_LANES`;
  - the schedule-only coverage-restore check and the nightly-arm upload go;
  - `tests.yml` goes 27 → 19 ids and `nightly.yml` carries 6;
  - the ci.yml stub is part of it (DESIGN-P1.md 2(a), 4).

**Evidence:**
- `python3 -I measure/rev/c1_counterfactual.py measure/p2/raw` reproduces every row and
  summary line of phase 2's `c1_counterfactual.txt` at the default 239.1 s, adding one
  line that names the cost charged.
- `--boost 480` reproduces the review's `ev/c1_counterfactual_boost_480.txt` the same
  way.
- `--sweep` → `c1_sweep.txt`.
- `c1_consumers.txt` is the source inventory.

## Review item 9

**The review:** the per-unit null control saw only executed step names. A deleted job,
deleted skipped steps and a gutted body all passed (rc 0 on three plants). `UNREAD ==
UNREAD` passed, and U4/U6/U7/U8 compared a dispatch AFTER with a `pull_request` BEFORE.

**What changed** (DESIGN-P1.md 4; DESIGN-P2.md 10; `measure/rev/unitcheck2.py`):
- **The static half**, which parses the workflow files before and after:
  - one row per job, hashing `if`, `needs`, `permissions`, `environment`, `strategy`,
    `outputs`, … ;
  - one row per step, hashing `run`, `uses`, `with`, `if`, `env`, … , whether or not
    any run executed the step;
  - a `|floor` row (top-level permissions) and a `|triggers` row;
  - all under a closed map of `renames`/`dropped`/`gained`/`changed`, where each
    admitted change is printed before and after;
  - several files merge with `+`, and a composite action's steps are a pseudo-job, so
    PR 1's move of `nightly-ha` into `.github/actions/` is compared too.
- **The runtime half refuses (exit 2)** when a permission header is `UNREAD`, or when
  the two runs differ in event or sender class.
- **Every PR-only job gets a `pull_request` AFTER**: a draft probe PR per unit, against
  a twin draft PR on main's layout pushed by the same identity.
- PR 1's own null control uses both halves.

**Evidence:** `python3 -I measure/rev/unitcheck2.py self-test measure/rev/fixtures/tests.yml measure/p1/raw 39158300302`
→ `SELF-TEST ok (12/12)`:
- **pass, as they should:** the null and a key-order reserialisation;
- **fail, as they should:**
  - the review's P1 (a job deleted), P2 (every conditional step of `fast` deleted) and
    P3 (a step gutted under its name);
  - a changed `if:`, a widened job grant, a widened file floor;
- **pass, as they should:** a mapped drop and a mapped change;
- **refuse, as they should:** `UNREAD` and a dispatch-vs-`pull_request` pair.

## Review item 10

**The review:** `gate_replay.py`'s 22/22 replayed a newest-check-per-name rule. It had
no applicability, no carry, no kind and no push exemption, so it was no null control
for 4.1.

**What changed** (DESIGN-P2.md 4.1, 4.4):
- Section 4.1's predicate is now `measure/rev/gate_model.py`. `tools/ci/gate.py` ports
  it line for line, and U0 drives the port with both replays.
- `gate_replay2.py` imports it and replays:
  - **history:** each of the 22 heads as one `ci.yml` `pull_request` run, against the
    ruleset; D-2's input comes from `reaches_cc.py` (git);
  - **perturbations;**
  - **event paths:** push exemption, edit carry, other base, retarget,
    cancelled-pending and its replacement, unreadable title, held run, a re-judged
    older gate.
- `gate_sim.py` replays 22 timed event sequences (verdict, retarget and dispatch cases)
  through the documented concurrency rule and both hooks. It scores both layouts
  against an independent oracle under three readings of the merge box. The review's
  `gate41_model.py` was the starting shape for the phase-2 arm.

**Evidence:**
- `gate_replay2.txt`: history **agree 22/22**, 0 differ; 28 of 28 rows `ok`;
  `GATE-REPLAY2 rc 0`.
- `gate_sim.txt`, `GATE-SIM rc 0`:
  - revision 1 is 16/16 under each reading and refuses 6/6 plants;
  - phase 2 as written is 12/16, 12/16 and 10/16, and refuses 0/6;
  - the longest false-green window is 11 s under revision 1 and 6952 s under phase 2.

## Review item 11

**The review:** readers neither design named:
- `approve_held_runs.sh`, `nudge.md:85`, `INSTRUMENTS.md:36`;
- `nudge.md:93`;
- `defect-root-cause.md:143`;
- `ci_script_seconds.py:37`;
- `superseded_runs.py:55-56`;
- the code-scanning writer;
- and, in substance, `orchestrator_tick.py:921-925`.

**What changed:**
- **DESIGN-P2.md 9** gains a row for each, marked (rev1):
  - the tick's classification uses `gate_required` ∪ `{gate}`, so a red required unit
    is not printed as "nightly/record class";
  - `nudge.md:93`'s stamp precondition becomes the `ci.yml` push run's `gate`;
  - `ci_script_seconds.py` and `merge_throughput.py` read `CI` push runs after PR 2
    and `Tests` before it;
  - `superseded_runs.py` gains `ci` and compares per lane by `display_title`;
  - `autofix_statuses.sh:29` lists `ci.yml` runs.
- **DESIGN-P1.md 2(a)** names `defect-root-cause.md:143` and `r10_replay_loopnorm.py`
  (the `slow` lane moves to `nightly.yml`).

**Evidence:**
- `measure/rev/readers_triage.txt` re-runs the review's `readers_diff.sh` against the
  revised corpus. Every remaining unnamed live file was read by hand and given a
  disposition.
- The historical record (`dev/archive`, `dev/audit/rca`, rounds, delivery rows,
  `RELEASE_NOTES.md`) and the generated `.cursor/rules` are excluded, with the reason.
  The exclusion is checked: the 19 of those files that code references were read too.
  One, `dora_keys.py`, reads "Tests" by name over a fixed past window; it is added to
  section 9.

## Review item 12

- **(a) Rollback order** (DESIGN-P2.md 7): restore the saved ruleset **first**, then
  revert PR 2. The revert's head writes no `gate`, so it can merge only under the 17
  contexts.
- **(b) One forgery point** (DESIGN-P2.md 2.1, 9):
  - `entities.py` pins that no workflow but `ci.yml` defines a job id or `name:`
    `gate`, and exactly one job there does;
  - it also pins that no workflow grants `checks: write`.
  - With every standalone dispatch ref-guarded (item 5), no other run on a PR branch
    can write a `gate`.
- **(c) Which side wins** (DESIGN-P2.md 4.1): a run is a source only for units its
  kind owns. So a carried unit's jobs always win over this run's skipped caller row of
  the same name. A unit this run owns and skipped is the newest source, and the gate
  fails SKIPPED; it is never filled from an older run. Shown in `gate_replay2.txt`:
  "code rows skipped HERE, carried" → pass; "hassfest skipped in the NEWEST run that
  owns it" → FAIL.
- **(d) U9 is not independent** (DESIGN-P2.md 10): U9's scoped-gate control runs on
  `probe/ci-layout-all`; its self-test perturbations may run on its own ref.
- **(e) Callee floors** (DESIGN-P2.md 5):
  - each callee keeps its top-level `permissions:` floor, which is what a callee job
    without its own block receives, capped by the caller;
  - the static half's `|floor` row refuses an unmapped change (self-test P8);
  - M-4 reads the received token in U1/U5.

---

## The specific rulings the review made

- **D-1, refused branch** (the review: phase 2 did not handle it). DESIGN-P1.md 5 and
  DESIGN-P2.md 5 now specify it:
  - `record-autofix` stays in the called `tests.yml` with `environment: record-writer`;
  - its environment secrets come from the environment and its repository secrets are
    passed explicitly;
  - `tests.yml` keeps `schedule:` for it alone, and other jobs gain
    `github.event_name != 'schedule'`;
  - the gate requires `tests / record-autofix` **on push only**, so `stamp.py` keeps
    refusing on it.
- **Permissions and secrets.** The caller grants are unchanged except `pr-contract`'s
  `security-events: read` (item 5) and `refresh`'s `actions: write`. `HPO_RUNS_*` stay
  until M-3 (item 6). R-3 (environments) stays unverified; it is an owner check before
  PR 1 merges (DESIGN-P1.md R-3).
- **Bot loop guards.** The autofix jobs stay `pull_request`-only. `gate-sweep.yml` is
  the one `workflow_run` re-runner. It re-runs only `gate` jobs, never its trigger,
  never a green one. That is the review's `stale_run` concern, carried.
- **pr-contract's `edited` trigger** is now an edit-lane verdict event, safe once items
  1-3 hold, as the review conditioned.

## Instruments changed or added, and re-run here

| instrument | run | result |
|---|---|---|
| `measure/rev/gate_model.py` | imported by the two below | – |
| `measure/rev/gate_replay2.py` | `python3 -I measure/rev/gate_replay2.py measure/p2/raw measure/rev/reaches_cc.txt` | `GATE-REPLAY2 rc 0`; history 22/22 |
| `measure/rev/gate_sim.py` | `python3 -I measure/rev/gate_sim.py` | `GATE-SIM rc 0` |
| `measure/rev/unitcheck2.py` | `… self-test measure/rev/fixtures/tests.yml measure/p1/raw 39158300302` | `SELF-TEST ok (12/12)` |
| `measure/rev/c1_counterfactual.py` | default, `--boost 480`, `--sweep` | default reproduces phase 2's rows; 480 reproduces the review's; plus one line naming the cost |
| `measure/rev/c1_consumers.sh` | `sh measure/rev/c1_consumers.sh origin/main` | 10 files |
| `measure/rev/check_writers.py` | `python3 -I measure/rev/check_writers.py measure/p2/raw` | 2 writers |
| `measure/rev/verdict_wait.py` | `python3 -I measure/rev/verdict_wait.py measure/p2/raw` | 8.07 runner-hours / 22 heads |
| `measure/rev/reaches_cc.py` | from a full checkout | 15 of 22 heads resolved; for the other 7 the history replay runs both ways and both agree |
| `measure/rev/readers_triage.txt` | the review's `readers_diff.sh` against the revised corpus, plus hand reading | every live file dispositioned |

`measure/rev/fixtures/tests.yml` is `origin/main`'s `tests.yml` at `07a09406`, saved so
the self-test reproduces off-tree. Phase 2's superseded `gate_replay.py`,
`c1_counterfactual.py` and `unitcheck.py` are kept unchanged in `measure/p2/` as the
record the review re-ran.

## Still unmeasured, and who measures it

These are measured by the fixers, in U0, U1, U5, U8 and U10, on probe refs. None is
assumed in either direction.
- **M-1:** `run-name` is returned as `display_title`, including for a run cancelled
  while pending.
- **M-2:** which `gate` binds when several exist at one head. It decides
  `gate-sweep.yml`.
- **M-3:** whether held runs occur, and whether one shadows a dispatched `gate`. It
  decides the approvals and W2.
- **M-4:** reusable-workflow facts: names, inherited event, caller cap, callee floor,
  call latency.

Where a probe PR cannot read M-2 or M-3 decisively, PR 2 ships the safe side and
re-measures inside the freeze (DESIGN-P2.md R-8).
