# Pre-study: the merge path's wall clock — `prepr`, the PR gate, and main's post-merge CI

Round-9 pre-study seat `r9-mergepath-prestudy`, dispatched by the orchestrator on
tvofi's request (the critical merge path's wall clock — `prepr`, the PR CI gate,
main's post-merge CI — with attention to the heavy scripts: reuse, scoping,
parallelisation). Study only — no fix PRs from this seat, no production file
changed, no budgets file touched. Baseline **`origin/main` = `6be88834e`**
(2026-10-10, the merge of #2125). The representative merge measured throughout
is **#2071** (`fix/live-diag`, merged 2026-10-10T06:38:11Z, merge commit
`7cd5a588c`): a production-code pull request (6 `custom_components/` files,
`tests/features.py`, `tests/entities.py`), merged as a batch of one through
`merge_train.py`, whose head already contained main. Worktree
`/Users/timmalmstrom/hpo-seats/r9pre-mergepath/wt`; CI numbers read from the
API/logs, each cited by run id and job id; local numbers timed on this 8-core
box under the seat venv. `tests/derive_closures.sh` full runs stayed in CI
(`gate-scoping.md`); locally only `prepr` and single `--single --record-only`
invocations were timed, as the brief allows.

tvofi's standing directions this study designs around: up to **four concurrent
heavy scripts** on this 8-core box (2026-10-10), and CI polling at ~300 s to
protect the shared GitHub quota (2026-10-07).

## 0. What the two sibling pre-studies established, and what is new here

The closures pre-study (`177bb01c3`) measured the **full** closures arm
(30–55 min; `boost_drift_replay.py` 55 %; lanes (e); (a2)/(a1) sound; (b)/(d)
refused). The coverage/fast pre-study (`69e374393`) measured the **push** arms
of `fast`/`coverage` (52–61 min; `boost_drift_replay.py` 81–86 % of the
critical lanes; it runs in BOTH). Neither measured the path **end to end**, and
neither measured the arm this study finds is the PR gate's critical lane: the
**scoped** closures arm, which is serial. Everything below is measured on the
whole path; where a figure is a sibling's it is cited, not re-derived.

## 1. The budget, end to end (one representative merge, #2071)

| stage | wall | critical lane | source |
|---|---|---|---|
| (i) local `prepr` (no body) | **34 m 24 s** (14-script scoped set) | step 6b closures recordings, serial (~30 m of it) | timed below |
| (ii) PR CI gate (run `37992668815`, head `61617145f`, 2026-10-09T21:18:44Z) | **52 m 27 s** | `closures` 52 m 04 s | jobs API |
| — `fast (3.14)` scoped | 29 m 47 s | suite step 1750 s, `boost_drift_replay.py` 1725 s | job `114030591952` |
| — `coverage` | 30 m 58 s | `boost_drift_replay.py` traced 1460 s | job `114030591963` |
| — `closures` scoped | **52 m 04 s** | serial re-record 51 m 18 s over 24 scripts; `boost_drift_replay.py` 27 m 13 s | job `114030702792` |
| — `mutation` | 19 m 48 s | (no `boost_drift_replay.py` run — measured, 0 lines) | job `114030591960` |
| (iii) serial wait, green→merge | 8 h 27 m | owner/train decision latency — not machine time; stated, not counted | 22:11:11Z→06:38:11Z |
| (iv) main CI (run `38031625988`, head `7cd5a588c`) | **52 m 21 s** | `fast (3.14)` full 52 m 16 s | run 06:38:14→07:30:35Z |
| — `fast (3.14)` full | **52 m 16 s** | `boost_drift_replay.py` 2241 s | job `114153594008` |
| — `coverage` full | 49 m 33 s | `boost_drift_replay.py` traced 2333 s | job `114153593911` |
| — `closures` full (3 lanes) | 27 m 57 s | `boost_drift_replay.py` recorded 876 s (06:45:21→06:59:57) | job `114153594029` |
| train poll granularity | ≤300 s per wait | `POLL_SECONDS = 300` | `merge_train.py:168` |

(#2071's merge landed 17 s after #2010's — `run` steps merge a queue back to
back — so its push run overlapped #2010's own `38031613597`, whose closures
job measured 40 m 10 s on the faster runner class. Both runs are cited; the
table carries #2071's own.)

**Machine wall for one merge ≈ `prepr` + 52 m + 52 m + ≤10 m of polls ≈
1 h 45 m of gate time plus the local run.** The decision window (iii) dwarfs it
but is the owner's, not the gate's. Merges inside one train landing are
concurrent (the docstring's accepted residual: a later merge lands before the
earlier merge's push run finishes); the SUSTAINED cadence bound is the next
train's step 0, which admits nothing until every required context at main's
tip is green — at today's cadence (7 main merges, 7 push Tests runs of
40–61 min, the measured run walls) that is **one train per ~40–61 min**, and every stage's critical
lane is a lane that carries `boost_drift_replay.py` (PR: closures 52 m; push:
fast 52 m; batch proof: closures 54 m 45 s).

**Local `prepr` decomposition (timed on this box, probe diff
`custom_components/heatpump_optimizer/notifier.py` + `tests/features.py`,
scoped case, 14 scripts).** Two timed runs: the full script
(**34 m 23.7 s** wall, 20:12:49→20:47:13Z) and the same with
`PREPR_SKIP_CLOSURES=1` (**4 m 07.7 s**, rc 0 — every other step green).

| component | wall | notes |
|---|---|---|
| steps 0–6a and 6c–7 (every non-recording step) | **4 m 07.7 s** | `PREPR_SKIP_CLOSURES=1` run; `closure.py select` alone 0.63 s, `affected` 0.13 s |
| **step 6b — scoped closures recordings, serial `--single` loop** | **~30 m** (34:23.7 − 4:07.7) | 14 scripts; `features.py` alone 22:20→22:37 = **17 m** under contention |

Caveats stated plainly. The box was concurrently recording two sibling seats'
closures work (one recording `boost_drift_replay.py` into its own out-dir, one
running a `--short-replay` arm), so both walls are upper bounds for a quiet
box — and honest ones for this round's reality. And one artifact of the study
itself: this study switched the worktree's HEAD mid-run (to start this
document on a clean branch), which changed `tests/features.py` under the
running recording and made that recording exit 1 — prepr correctly refused
step 6b as "failed while being recorded"; the WALL is valid, the refusal is
mine, not the tree's (the `PREPR_SKIP_CLOSURES=1` run passed every step it
ran, rc 0).

The shape matches CI exactly: everything except step 6b is ~4 minutes; step 6b
is the scoped scripts' run time, serially, because `closures_line` loops
`derive_closures.sh --single` one script at a time (`tools/pr/prepr.sh:487`).
On a diff that reaches `boost_drift_replay.py` — 57 of the package's ~60
production modules are in its 83-file closure (`tests/closures.json`), so
essentially every production diff does — the loop pays that script's local
recording too: **[BOOST-LOCAL]** measured for the identical `--single
--record-only` invocation prepr and CI both use.

## 2. Duplication audit — the core question

Runs per merge, counted first. For one production-code merge (reach-PR,
batch of one, as #2071):

| heavy work | local `prepr` | PR CI | main CI | total runs |
|---|---|---|---|---|
| `boost_drift_replay.py` | 1 (step 6b record) | 3 (fast 1725 s, coverage 1460 s, closures 1633 s) | 3 (fast 2241 s, coverage 2333 s, closures 876 s) | **7** |
| `features.py` | 1 (record) | 3 (fast 552 s, coverage 488 s, closures 548 s) | 3 (fast 649 s, coverage 751 s; closures lane off-path) | 6–7 |
| `entities.py` | 1 (record) | 3 (fast 123 s, coverage 117 s, closures 342 s) | 3 (fast 124 s, coverage 177 s; closures lane off-path) | 6–7 |
| `harness_headers.py` | 1 (record) | 3 (fast 191 s; closures 227 s; coverage off-set) | 3 | 6–7 |
| `stress.py` | 0 (left to CI by `closure_lane`) | 1 (fast, serial after lanes) | 1 | 2 |

In minutes for the dominant script: **`boost_drift_replay.py` costs 10 268 s =
2 h 51 m of CI lane time per merge** (4818 s PR-side at 21:18Z + 5450 s
push-side at 06:38Z, both slow-class runners; the same morning's fast-class
arm measured half that — the covfast ×2 band), plus the local recording — for
ONE merge of ONE pull request. A batch proof adds a further full closures arm
(one more recording, 54 m 45 s job wall on `batch/20261010-152646-1`) plus a
scoped `fast` (`boost_drift_replay.py` again if the union diff reaches it),
amortised over the batch's entries.

**Which of the 7 are redundant?** Counted honestly, none is a byte-identical
tree re-graded twice — with three deliberate near-misses that are the actual
findings:

1. **prepr step 6b vs the PR `closures` job: the same recordings, taken
   twice, on purpose.** Both derive the same scoped set from the same
   three-dot diff (`closure.py affected`) and run the same `--single
   --record-only` invocations. The local run is the designed *cheaper
   detector* (find `UNDER-SCOPED` before the push, not after) — but it is not
   cheap: for a reach-diff it costs the full local recording of
   `boost_drift_replay.py` and friends, serially, on the seat's box, and CI
   then pays the same sum again on the PR. This is the one duplication with a
   clean sound reuse (§3 r1).
2. **main's CI vs the PR's CI: not the same tree.** `7cd5a588c`'s tree differs
   from `61617145f`'s by 70 files (main moved: #2010 merged in between), so
   the push run graded a tree no run had graded. The narrow exception is a
   batch's **last** entry, whose merge tree equals the proved `batch/<tag>`
   tree exactly (the train's own docstring accepts main's run "grades it
   again"). Skipping that one push run is refused (§3 r4).
3. **`fast` and `coverage` both run `boost_drift_replay.py`** — the covfast
   pre-study's §1.4, measured here again on the PR side (1725 s untraced +
   1460 s traced) and confirmed: different questions (verdict vs line-set),
   refused as a merge by that study; not re-argued.

## 3. Reuse opportunities, each with its safety analysis

**(r1) Memoise prepr step 6b against `(HEAD, script, closures table,
interpreter, discovery listing)` — sound, local-only, the one to build.**
A seat re-runs `prepr` on every body edit and every push (`app_push.sh:255`
runs it per push), and between two runs at the SAME head the recording inputs
are unchanged — a recording is a pure function of the tree, the script's
recorded argv, the interpreter, and the files its discovery globs reach
(`harness_headers.py` rglobs `dev/audit/rounds/round*`, the #2109 class).
What must be true: the memo key carries all four — including a digest of the
UNTRACKED file listing under the discovery roots, which is exactly the input
that can change while HEAD does not. What fails if it is not: prepr prints
"covered" for a recording CI would refuse — the local early warning only,
because the PR `closures` job re-derives everything regardless; the gate
property (red on the PR, red within one merge on main) is untouched. The memo
is local state under `$HPO_STATE_DIR`, never committed — it is not the refused
CI-side cache (closures pre-study (b)), whose key had to contain the answer:
here the recording is re-taken on any key miss and CI re-takes it always.
Saving: the full step-6b cost on every re-push/re-body at an unchanged head —
for a reach-diff that is the dominant local minutes of every seat iteration.

**(r2) The coverage per-script reuse chain — working by design, with a
measured miss class worth one look.** PR `coverage` is *supposed* to restore
main's push-run measurement and re-measure only reached scripts. On #2071 it
did not: the exact key restored ("Cache restored from key:
coverage-per-v1-Linux-23d354970…" at 21:18:56Z), main's push run at that base
had completed green 4 m 35 s earlier (`37985506586`, coverage job finished
21:14:21Z), and the job still measured every script ("No per-script coverage
for 23d354970…: measuring every script") — the third observed instance of the
class the covfast pre-study flagged (§7, run `38069955370`). The fallback is
fail-closed and the property held (the job measured more, not less), so this
is a bounded cost, not a hole: for a reach-PR the miss costs the non-reached
scripts' traced time (~10 min here); for a skip-PR it turns a ~4 m job into a
~31 m one. The countermeasure owed is diagnostic, not architectural: make the
marker-refusal branch print the marker it read (it prints the script text;
the observed refusal's output line never appeared in the log), so the next
instance is attributable in one look.

**(r3) Reuse the PR run's verdict on main's push when the trees are
identical — REFUSED.** The merge commit's tree equals the PR head's only when
main did not move under the PR (#2071's did not qualify: 70 files). And even
where it does, the push run is rule 1's unscoped detector AND the producer of
the per-script coverage entry the next PRs restore (keyed at each main
commit); skipping it starves the reuse chain into permanent misses — the
covfast pre-study's (ii), concurred with here on end-to-end evidence.

**(r4) Skip the last batch entry's push run (tree identical to the proof) —
REFUSED.** It would save one 40 m run per batch and nothing else; it breaks
the same detector-and-producer argument as (r3), and the train's own residual
note already accepts the overlap as the price of the proof grading every
entry's tree.

**(r5) Reuse a sibling job's output inside one CI run — already the design
where sound** (`closure-scope` feeds `closures`; coverage's restore feeds its
scope; `coverage-ratchet` grades `coverage`'s artifact in 8 s). No further
in-run reuse exists that does not merge the refused (i) of the covfast study.

## 4. Scoping reasonableness

- **Nothing runs work its diff cannot reach, except by explicit design:**
  the PR `fast` gate ran `MODE: SCOPED -- 22 script(s) run, 11 scoped out`
  with each scoped-out script named and its reason printed (measured in
  `114030591952`); prepr's step 2 printed the same `MODE: SCOPED` line
  locally. The push/full arms are rule 1's price.
- **The one genuinely unscoped lane is the batch proof**: a
  `workflow_dispatch` has no PR base, so `closures` runs the FULL arm for a
  batch diff whose entries were each scope-checked (54 m 45 s on
  `batch/20261010-152646-1`). That is PR 1's (a1), already specified and
  sound (fail-closed to full); this study's addition is in §5 — (a1) must
  land with the scoped-arm lane fix or the scoped proof pays a serial sum.
- **Is any gate running LESS than its safety property needs?** No instance
  found; the `skip`-blind-spot class (INERT-prefix file a discovery glob
  reads) is PR 1's (a2), already specified. The coverage marker trust check
  correctly refused/distrusted and over-measured rather than under-measured
  (§3 r2).
- **prepr step 6b duplicates the PR closures arm by design** (the cheaper
  detector); its cost is the subject of (r1), not of scoping.

## 5. Parallelisation optimality — the study's main new finding

**The scoped closures arm is serial, and it is the PR gate's critical lane.**
The PR `closures` job's scoped step is a `while read` loop of
`derive_closures.sh --single` (`tests.yml`, "Re-record the closures" scoped
branch) — one script at a time, no lanes. Measured on #2071: **24 scripts,
51 m 18 s serial**, of which `boost_drift_replay.py` alone is 27 m 13 s. Three
same-day full arms, with lanes, measured 40 m 10 s (#2010's push, job
`114153557227`), 27 m 57 s (#2071's push, job `114153594029`) and 54 m 45 s
(the batch proof) across the ×2 runner band. The structural point survives the
band: **a serial loop's wall is the SUM of the selected recordings (51 m 18 s
measured), a lane-balanced arm's wall is the MAX of its lanes — so the scoped
arm pays more than the full arm for strictly less work whenever the scoped set
spans more than one heavy script, and no runner-speed fix can change that
floor.** prepr step 6b has the same serial shape locally
(`tools/pr/prepr.sh:487`), where the owner's direction allows four concurrent
heavy scripts and the loop uses one.

The soundness argument is already in-tree (R9-F10.15, cited by both
siblings): which lane records a script changes WHEN it is recorded, not WHAT
it opens — one recording file per script per out-dir. The constraints a
parallel scoped runner must keep are the documented ones inside
`derive_closures.sh`: `plan_view.py` before the card scripts that read its
payload, and driver/driven-child pairs in one lane.

**Lane balance elsewhere, measured:** `fast` scoped on a reach-PR is
`boost_drift_replay.py`'s lane (1725 s of a 1750 s critical total — 98 %);
`coverage` runs two lanes (`W5P_LANES=2`) with the script inside the "rest"
lane (covfast (iv) fixes this); the full closures arm's lane 3 is the
closures pre-study's (e). `mutation` (19 m 48 s) never runs
`boost_drift_replay.py` (measured: zero mentions in its log) and is not on
any critical lane. **Locally**, `tests/run.sh` caps itself at
`min(nproc, 3)` lanes — the owner's four-slot direction means `GATE_JOBS=4`
is available to any seat today without a code change, and prepr 6b / the CI
scoped arm are the two loops still at one.

**The train's 300 s poll adds ≤300 s per wait (average 150 s)** against a
40–61 min critical lane — under 7 %, and the interval is the owner's quota
direction (~15 seats share the API budget; 2026-10-07). Not a lever; leave
it. The serial structure it serves (proof → merges → push runs) is already
batched (R9-RO-12); the residual serialization is main's push run itself,
which is the detector.

## 6. The two planned pull requests, resolved against this study

**PR 1 (closures (e) + (a2) + (a1)): KEEP ALL THREE, RESCOPE (e) to cover
the scoped arm too, and couple (a1) to that rescoping.**
- (e) as specified rebalances only the FULL arm's three lanes. The arm this
  study measured as the PR gate's critical lane is the SCOPED arm, and it is
  not lane-shaped at all — it is a serial loop paying sum ≥ max. Rebalancing
  the full arm without it leaves the worst lane (52 m) untouched: the PR gate
  stays at 52 m while the push arm drops to ~30 m. Same file
  (`tests/derive_closures.sh`), same R9-F10.15 argument, same sharding data
  (`recorded` seconds) — one lane-runner, three callers (full arm, CI scoped
  arm, prepr 6b).
- (a1) without the scoped-arm fix is a regression risk in the making: a
  scoped batch proof pays the SERIAL SUM of its selected recordings — for a
  batch whose union diff reaches the heavy scripts, that is the 51 m-class
  sum again, worse than the 54 m full arm it replaces only by luck. (a1) and
  the scoped runner belong in one PR.
- (a2) keep unchanged: it moves the #2109 incident class from main to the
  PR, and nothing in this study changes its analysis.

**PR 2 (coverage/fast (vi-a) + (iv)): KEEP BOTH PARTS, EXTEND (vi-a)'s proof
obligation to the closures read set.**
- (iv) keep: measured again here (coverage's critical lane carries the
  script; two lanes today).
- (vi-a) keep, and widen its acceptance test: the closures pre-study's §4e
  follow-up ("a cheaper recording invocation opening the same read set") is,
  on this study's numbers, worth MORE than its coverage-side saving. The
  closures recording of `boost_drift_replay.py` runs on every PR gate
  (27 m 13 s), every prepr 6b, every push full arm (876–1236 s across the
  runner band) and every batch — if the short-replay invocation is proven to open a **byte-identical
  read set** on Linux CI (the R9-F10.14 shape of proof, one more equality
  than vi-a's line-set proof), the same knob cheapens the recording
  everywhere, through `closure.py`'s recorded-argv rule, with no change to
  what any check compares. Without this extension, PR 2 speeds coverage and
  fast but leaves the PR gate's critical lane (closures scoped, 52 m) and
  prepr's local cost untouched.
- (vi-b) — speed the ~288-solve replay itself — remains the only lever that
  helps `fast`'s verdict lane (1725 s PR / 1174 s push). Neither planned PR
  covers it; commission it as the prioritised fixer PR after (vi-a), as the
  covfast study ordered.

**Supersession statement (per the coordinator's instruction): neither planned
PR is dropped or replaced.** PR 1 is rescoped as above (its (e) extended to
the scoped arm; (a1) coupled to it); PR 2 is kept with (vi-a)'s proof widened.
The one genuinely NEW instrument this study adds is (r1), the local prepr
memo — it is not in either planned PR and belongs in neither: it touches only
`tools/pr/prepr.sh`, and its safety case (§3) is independent.

## 7. Cost test (root-cause.md §4)

The recurring cost is gate time per merge: today's measured machine wall is
~1 h 45 m + local prepr per merge, at 7 merges and 7 push runs
(40–61 min each) in one day, with `boost_drift_replay.py` alone at 2 h 51 m
of CI lane time per merge and the PR gate's critical lane at 52 m.

| lever | engineering cost | measured / bounded saving | risk |
|---|---|---|---|
| R1 scoped-arm lanes (CI + prepr 6b, ≤4 local slots) | one lane-runner in `tests/derive_closures.sh`, two call-site edits | **~21–24 min off every reach-PR gate** (52→~31 m: the scoped wall becomes max(27 m boost, ~10 m rest)); same order off prepr 6b locally | none to any guarantee (R9-F10.15); CPU contention bounded by existing timeouts, measured on landing |
| PR 1 (e) full-arm rebalance | as specified there | ~21 min × every full arm (~8/day) | none (closures pre-study) |
| PR 1 (a1) batch scoping (+R1) | as specified there | up to 54 min per batch proof when scoped | fail-closed default already specified |
| PR 2 (vi-a) short-replay + read-set proof | knob + two proofs (line set, read set) | up to ~45 min/coverage run AND ~27 min/PR-closures-arm AND the local 6b recording AND ~20 min/full arm — the largest single lever after R1 lands the lanes | loud on failure (ratchet floor / UNDER-SCOPED compare); refused, not widened, if either equality breaks |
| (r1) prepr 6b memo | `tools/pr/prepr.sh` only | the whole local heavy cost on every re-push at an unchanged head | weakens only the local early warning; CI unaffected |
| PR 2 (iv) third coverage lane | one lane-split edit | ~12 min per coverage run | contention, measured on landing |
| (vi-b) speed the replay | fixer PR, mutation proof + null control | up to ~35 min/fast, ~40/coverage, ~25/closures per arm | must be proven, not assumed |
| scope/skip main's push run; CI recording cache; nightly-only full; poll < 300 s | — | large | refused: rule 1, the coverage producer, closures (b), the quota direction |

## 8. Recommendation, ordered, with the smallest first PR for each

**R1 first** (scoped-arm lane runner): it is the PR gate's critical lane, it
is the same machinery PR 1's (e) already needs, and no other lever touches
the 52-minute wall every reach-PR pays. *Smallest first PR*: add a
`--scripts-from <file>` mode to `tests/derive_closures.sh` that shards the
listed scripts across ≤3 CI lanes (≤4 locally) by descending `recorded`
seconds, preserving the documented order constraints inside one lane; switch
the workflow's scoped step and prepr's `closures_line` to it (`--single` and
`PREPR_RECORD` interfaces unchanged). *Acceptance*: one reach-PR whose
closures job wall is ≤ max(selected recordings) + setup on two runs, all
recordings present, `check --partial` verdict byte-unchanged. *Drivability*:
same jobs, same inputs, same `--record-only`/`--single`/`--out-dir` surface —
nothing a seat or CI invokes changes.

**Then PR 1 as planned, with (e) using R1's runner and (a1) landing R1's
runner in the dispatch arm.** Its own acceptance tests as specified in the
closures pre-study §6, unchanged.

**Then PR 2, with (vi-a)'s acceptance widened to the read-set equality.** As
specified in the covfast pre-study §6, plus: on Linux CI, at one head, the
full and short invocations of `tests/boost_drift_replay.py` produce
byte-identical read sets in the closure recording; if they differ, the knob
is refused for closures and kept only where its line-set proof held.

**(r1) any time — smallest independent PR in this list:** `tools/pr/prepr.sh`
step 6b memo under `$HPO_STATE_DIR`, keyed on (HEAD, script,
`tests/closures.json` hash, interpreter version, untracked-listing digest of
the discovery roots). *Acceptance*: a second prepr at an unchanged head
completes 6b in seconds and the verdict line names the memo; creating an
untracked file under `dev/audit/rounds/round9/` invalidates it.

**Then commission (vi-b)** as the fixer PR. **Refuse**: everything in the
cost-test table's last row.

## 9. What could not be measured, and why

- **A quiet-box local prepr wall.** The box concurrently ran two sibling
  seats' recordings during timing (one recording `boost_drift_replay.py`
  into its own out-dir, one running a `--short-replay` arm); every local
  figure is an upper bound under contention and is marked as such.
- **The local `boost_drift_replay.py` recording's uncontended wall** — same
  reason; CI's 1236–1766 s recorded bounds are the authority.
- **The coverage marker-miss mechanism** (§3 r2): the refusal's output line
  never reached the log, so the third instance is observed but not
  attributed; the diagnostic countermeasure is the fix, not a re-derivation
  here.
- **Batch-amortised per-merge cost**: only one batch's proof jobs were read
  end to end (`38064024146`, failed on the known #2109 incident); the
  19:45Z batch (`38081141948`) was still running at capture time.

## 10. Every figure's provenance

- PR run `37992668815` (#2071, head `61617145f`, synchronize, 2026-10-09
  21:18:44Z): job list and jobs `114030591952` (`fast`), `114030591963`
  (`coverage`), `114030702792` (`closures`), `114030591960` (`mutation`) —
  walls from the jobs API; the scoped re-derive's per-script `[HH:MM:SS]
  record/done` lines, `MODE: SCOPED -- 22 script(s) run, 11 scoped out`, the
  manifest totals (1750 s / `boost_drift_replay.py` 1725 s), the coverage
  `ran/reused` lines and both cache lines, all read from the downloaded job
  logs.
- Push run `38031625988` (#2071's merge commit `7cd5a588c`, 2026-10-10
  06:38:14Z): jobs `114153594008` (`fast` 52 m 16 s, `boost_drift_replay.py`
  2241 s), `114153593911` (`coverage` 49 m 33 s, traced 2333 s, "No per-script
  coverage for 7cd5a588c: measuring every script" — correct on a push, it
  produces the base), `114153594029` (`closures` 27 m 57 s, recorded
  06:45:21→06:59:57); run wall from the run record. The overlapping
  #2010 push run `38031613597` (head `1b72ca19f`, 06:38:02Z, wall 40 m 14 s;
  closures 40 m 10 s, job `114153557227`) is the full-arm comparison wall.
- Base-commit push run `37985506586` (head `23d354970`): coverage job
  finished 21:14:21Z, success — the §3 r2 timing.
- Batch proof `38064024146` (`batch/20261010-152646-1`, dispatch): jobs
  `114247906174` (closures 54 m 45 s), `114247938099` (fast 5 m 09 s).
- Merge cadence: `git log --merges` on `origin/main` (7 main-side merges on
  2026-10-10; #2071's tree delta 70 files vs `61617145f`);
  `.../actions/runs?branch=main&event=push` filtered `name=="Tests"` (7).
- Branch iteration cost: `.../actions/runs?branch=fix/live-diag` — 8
  pull_request Tests runs (2 success) over 9 heads.
- Local timings: `bash tools/pr/prepr.sh` on a probe branch (never pushed)
  with the seat venv first on PATH; `closure.py select` and `affected` timed
  inline (0.63 s / 0.13 s); step-6b behaviour read from the running loop's
  out-dir file timestamps and `ps`.
- Scope sets, closures, recorded seconds: `tests/closure.py affected` /
  `select` at `6be88834e`; `tests/closures.json` (`boost_drift_replay.py`:
  83-file closure, 57 production modules, recorded 1489.6 s).
- Train structure: `tools/audit/seat/merge_train.py` (`POLL_SECONDS = 300`
  at :168; `wait_ci` polls; batch docstring for the accepted residual);
  `tools/pr/prepr.sh` (`closures_line` serial loop at :487; `closure_lane`'s
  lease/CI delegation); `tools/pr/app_push.sh:255` (prepr per push);
  `.github/workflows/tests.yml` (scoped/full arms, coverage key/restore/
  marker/save, `closures` scoped `while read` loop); `tests/run.sh`
  (`min(nproc, 3)` lanes); `tests/derive_closures.sh` (three lanes, order
  constraints); ruleset 23698884 (17 required contexts — `coverage` is not
  one).
- Sibling pre-studies' figures are cited at their own provenance sections,
  not re-derived: `177bb01c3` (closures), `69e374393` (coverage/fast).
