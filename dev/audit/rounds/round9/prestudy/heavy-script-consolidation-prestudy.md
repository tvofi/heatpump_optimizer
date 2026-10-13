# Pre-study: consolidating the heavy scripts' repeated runs — which of the 7 is really redundant

Round-9 investigation seat `r9inv-consolidate`, dispatched on tvofi's question:
the merge-path wall-clock pre-study (`handoff/r9-mergepath-prestudy`,
`547d25b71`) measured `tests/boost_drift_replay.py` running **7× per merge**
and concluded *"no run is a byte-identical tree re-grade except a batch's last
entry"*. This study attacks that conclusion, re-derives the count from real
runs, and judges each consolidation mechanism sound or refused. Study only —
no fix PR, no production file changed, no budgets file touched. Baseline
**`origin/main` = `a74520020`** (2026-10-11). Worktree
`/Users/timmalmstrom/hpo-seats/r9inv-consolidate/wt`. Every CI figure below is
read from the API/logs cited in §8; the full suite and
`tests/derive_closures.sh` were not run locally (forbidden off Linux,
`gate-scoping.md`).

The method, per the brief: for each of the 7 runs, name the tree, the decision
and the consumer; then judge each pair; then each mechanism — with the rule
that **a silent failure is an automatic refuse**.

## 1. Is the 7× count right? Re-derived from real runs

The 7× is correct **for the case it was measured on** — a reach-PR (its diff
inside `boost_drift_replay.py`'s 83-file closure) merged **as a batch of one**
(#2071: no proof under D, so 1 local prepr recording + 3 PR-side + 3
push-side). It is not the average, and it under-counts one thing while
over-stating another:

- **Under-counted: repeated iterations.** A PR's head typically pays its CI
  more than once (#2071's branch: 8 `pull_request` Tests runs over 9 heads),
  and `app_push.sh` runs `prepr` — hence step 6b — **per push and per body
  edit** at an unchanged HEAD. The 7× counts the final head only; a real PR's
  lifetime total is higher, and the body-edit repeats grade a byte-identical
  local tree (the r1 memo's target).
- **Over-stated as a per-merge average: most of the current wave's PRs do not
  reach the script.** Measured on the last completed train event — the batch of
  three #2110/#2111/#2124, proved at 19:46Z, merged 20:42–20:47Z on 2026-10-10:
  the union diff scoped `boost_drift_replay.py` **out** of the proof's `fast`
  ("no changed file is in its measured closure", job `114298156073`) and
  `coverage` **reused** it from the base (job `114298155756`), so the PR side
  and the proof's scoped arms paid **zero** boost runs; only the proof's
  dispatch-arm `closures` (full by construction, job `114298129671`, boost
  recorded 20:00:22→20:29:36 = 1754 s) and the three merges' push runs paid
  it. For that event: **10 boost runs for 3 merges ≈ 3.3 per merge**. Day
  total 2026-10-10: 10 PR merges, 11 push Tests runs → ≈ 33 push-side runs +
  proofs (2) + reach-PR sides (#2071: 3) ≈ **38 runs / 10 merges ≈ 3.8 per
  merge**. The 7× is the reach-PR-alone worst case, and the honest headline
  for "can we consolidate" is that the **push side (3 runs per merge, always,
  whatever the diff) is 80–90 % of the average** — the PR side is already
  scoped to zero for non-reach diffs.

The batch-exception the sibling study named is **confirmed byte-identical,
not approximate**: proof tree `142e9b213` (branch `batch/20261010-194554-1`,
sha `16cccd5ef`) equals the last merge `6918cb4b2`'s tree exactly, and the
last merge's push run re-graded that identical tree 6 minutes after the proof
finished. §3 C2 is built on this.

## 2. The per-run table (reach-PR merged alone; the 7)

Trees: **H** = the PR head's tree; **M** = the merge commit's tree (differs
from H by everything main merged in between — 70 files for #2071).

| # | run | tree | what it informs | who consumes the output | persists? |
|---|---|---|---|---|---|
| 1 | local `prepr` step 6b, scoped `--single --record-only` loop (`tools/pr/prepr.sh:487`) | H | the seat's pre-push early warning (find UNDER-SCOPED before the push) | the seat only; a pass avoids a red push | **no** — `mktemp -d`, `rm -rf` at the end |
| 2 | PR `fast (3.14)`, scoped | H | the suite verdict (required context) | ruleset 23698884 / the merge train | no (manifest in the log) |
| 3 | PR `coverage`, measured scripts only | H | line sets → `coverage-ratchet` grades the budgets (not a required context) | `coverage-ratchet` (8 s job) | coverage.json artifact; per/ **not saved** on PRs (save is push-only) |
| 4 | PR `closures`, scoped re-record + `check --partial` | H | closure under-approximation (required context) | the check; recordings uploaded (3-day retention) for `closures-autofix` | yes, artifact only |
| 5 | push `fast (3.14)`, FULL | M | rule 1's unscoped verdict detector | nobody gates on it; a red means revert-first (`orchestrator.md` §11) | no |
| 6 | push `coverage`, FULL | M | the ratchet on M **and** the per-script base the next PRs restore (key = M, marker `push refs/heads/main`) | the next PRs' restore; `coverage-ratchet` | yes — cache saved under key at M |
| 7 | push `closures`, FULL | M | rule 1's unscoped closure detector | **the in-job 0.2 s check only** — the upload step's `if:` is `pull_request`, so push recordings are **discarded** (measured: job `114309000519` ran no upload) | no |

In a **batch of N** (proved, B case), add: proof run (dispatch) — `closures`
FULL (tree P_n) + `fast`/`coverage` scoped on the union diff; and N push runs
on trees P_1…P_n, of which **P_n's tree is byte-identical to the proof's**.
The intermediate trees P_1…P_{n-1} are graded by nothing else: the proof
graded only P_n, and each PR's own CI graded its head, whose tree differs from
P_i (GitHub's text merge; measured — none of the three heads contained main).

## 3. Pair-by-pair, then the mechanisms

### Same-tree pairs (of the 7)

- **(1,4): same tree, same derivation, same `--single --record-only`
  invocations, different OS and consumer.** Run 1 cannot replace run 4: a
  Darwin recording is not the Linux authority (`gate-scoping.md`: the partial
  union lets it grow but Linux `strace` saw what Darwin cannot), so CI must
  re-record; and run 1's value is the seat's cheap pre-push detector. The
  consolidation is not elimination but **repetition-avoidance at an unchanged
  HEAD — the r1 memo, judged SOUND by the sibling study and confirmed here**
  (the circularity the brief warns about does not arise: the memo key is
  computed from things measurable *before* the recording — HEAD, the committed
  `closures.json` hash, the interpreter, and a listing digest of the discovery
  roots — and a miss re-records; no answer is stored across trees). We add one
  measurement the sibling lacked: the memo's saving is per *push and body
  edit*, and `app_push.sh` runs prepr on each — so a seat that iterates a body
  3× at one head pays step 6b three times today.
- **(2,3), (2,4), (3,4): same tree, different questions.** (2,3) is the
  covfast pre-study's refused (i) — verdict uninstrumented on 3.14 vs line-set
  traced on 3.13, and `features.py`'s #525 heartbeat pair reads ZERO ticks
  under any tracer. Not re-argued. (3,4) is where a sound consolidation was
  missed — see C1 below.
- **(5,6,7): same tree M, three questions** — verdict, line set, read set.
  (6,7) share more than the sibling study credited: both are *measurement*
  lanes (not verdicts), both on Python 3.13, both already instrumented
  (`coverage` under the coverage tracer, `closures` under `closure.py`'s audit
  hook), and on a push **both run `boost_drift_replay.py` to completion on the
  identical tree in the same event** — measured on the batch of three's push
  runs: traced 2042/2869/2608 s AND recorded 1238/1839/852 s of the same
  script on the same trees. See C1.
- **(proof `closures`, push-N `closures`): byte-identical tree AND identical
  invocation AND identical check.** The proof's dispatch arm re-records every
  closure on P_n (`--record-only`, full), runs `check`, and **discards the
  recordings** (upload is pull_request-only); the last merge's push `closures`
  job then re-records the same 34 scripts on the same tree and runs the same
  check. This is the one true byte-identical re-grade, and the sibling study's
  r4 refused the wrong slice of it — see C2.

### C1 — one instrumented run producing both the line set and the read set (SOUND, proof-gated; the largest lane saving)

`coverage`'s traced run of a script and `closures`' recorded run of the same
script are two instrumented executions of the same argv on the same tree
producing two different artifacts (per-script line data; per-script read-set
JSON). Nothing in principle prevents one execution producing both: the audit
hook and the coverage tracer instrument different layers (syscalls-of-Python
vs Python lines) and both are in-process. A per-script composition would let
the `closures` arm **consume the coverage job's execution** for every script
where two equalities are proven on Linux CI at one head:

1. the script is **healthy under both** (rc 0 — the read set of a script that
   died is truncated, and the recording is refused as partial);
2. the recorded **read set is byte-identical** traced-vs-bare, after excluding
   the instrumentation's own opens (coverage's data files and sitecustomize
   live outside the repo; the exclusion rule is the same one `closure.py
   record` already applies to its own out-dir).

Both failures are **loud**: an unhealthy or truncated combined run reddens the
`closures` job as a failed/UNDER-SCOPED recording, and a line set that shrinks
reddens `coverage-ratchet`'s per-module floors — the R9-F10.14 shape of proof,
one more equality than vi-a's. This is not the refused recording cache: **no
answer crosses a tree boundary** — every event still executes the script once
and derives both answers from that execution; the circularity of closures
option (b) (key must contain the `inert_reads` the measurement produces) never
arises. And it is not covfast's refused (i): no verdict lane is instrumented.

Scope limits, stated: `features.py` **cannot** be composed (#525 — it fails
under the tracer), so it keeps both runs; `golden.py` keeps both (closures'
cheap `--only __no_such_scenario__` argv vs coverage's strict full argv —
different invocations by design); `env_drift.py`/`stress.py` are not in
coverage's stage at all. **First PR: `boost_drift_replay.py` only** — it is
healthy under the tracer (rc 0 in every measured coverage run) and is 55–86 %
of every lane it touches. Effect: the PR scoped `closures` arm stops paying
its 27-minute recording (the coverage job already paid the traced run on the
same tree); the push `closures` arm stops paying 850–1840 s per run; the
`closure.py` recorded-argv rule and `coverage_tree.sh`/`derive_closures.sh`
wiring are gate files — **no `*_budgets.json`, no policy**. Wall effect on the
push side: none (coverage is already the critical lane); on the PR side the
closures job becomes dependent on coverage's artifact, so the PR gate's
critical lane becomes coverage's — a real gain only after vi-a/R1 land;
state that honestly. The lane-time saving is immediate and large (§5).

### C2 — the last batch merge's push `closures` job consumes the proof's recordings (SOUND, small, cheap)

The proof's `closures` arm already did, on a byte-identical tree, exactly what
push-N's `closures` arm redoes: full `--record-only` re-record of all 34
scripts plus the same check against the same committed table (same tree ⇒
same `tests/closures.json`). The push job's fast and coverage arms stay —
they are the first verdict/line-set grades of that tree and the coverage
base's producer. Mechanism: the dispatch arm uploads its recordings (its
upload step's `if:` gains the dispatch case) under a name carrying the
**tree hash** (`git rev-parse HEAD^{tree}`, written by the same checkout that
recorded); the push `closures` job computes its own `HEAD^{tree}`, downloads
the artifact by that name, refuses on any mismatch or miss, and **still runs
`closure.py check`** against the consumed recordings — failing closed to a
full re-record on any miss. What must be true: the label and the recordings
come from one run (they do — one upload step), and the check runs unchanged
(it does — the saving is only the re-record step). Failure mode: a mislabeled
artifact (recordings of another tree passing the check) is the one **silent**
case — the #2109 class; it is guarded by the tree-hash key plus a self-test
that a mismatched label is refused, and it requires a bug in a single
well-testable line. Judged sound with that obligation; saves one full
closures arm per batch (~28–55 min lane; measured push-N closures: 27 m 36 s,
job `114309833831`) at zero wall cost (closures is off the push critical
path). Not r4's refusal: r4 refused skipping the whole push run and its
detector/producer roles; the closures arm's recordings have **no consumer
beyond the in-job check** (measured — no upload on push), and the identical
check already ran green 40 minutes earlier or the batch would not have
merged.

### Refused, with the reason

- **Skip/scope the push run itself (r3/r4, reaffirmed on new evidence):** the
  fast arm is rule 1's only unscoped verdict detector, and the coverage arm is
  the per-script base's sole producer (restore key = merge-base commit, marker
  `push refs/heads/main`) — skipping it starves the PR reuse chain
  permanently. A diff-scoped push is the #2109 blind spot by construction
  (INERT-prefix files a discovery glob reads are invisible to the diff).
- **Cancel the intermediate batch merges' push runs (new, considered,
  refused):** runs on P_1…P_{n-1} are nobody's gate and their coverage bases
  are keyed at tips that are main for ~2 minutes (measured: merges 2 m 18 s
  apart), so they look free to drop — but they are the **only** detector for a
  regression in entry i that a later entry masks: the proof graded only P_n,
  which contains the masking change, and the final push run is green by
  hypothesis. Dropping them lets a masked regression land green until the
  nightly — a rule-1 reading change, and the lost detection is silent by
  construction. If tvofi ever rules "one batch = one merge unit" this becomes
  a candidate; until then, refused.
- **CI-side recording cache (closures (b)) and nightly-full (d):** refused by
  the sibling; nothing here changes the verdicts (C1/C2 store no answer across
  trees).
- **Dedupe `fast` and `coverage` (covfast (i)):** refused; not re-argued.

## 4. What the 7× decomposes into after C1+C2+r1

Reach-PR, batch of one: 7 → **5** runs (local memo absorbs body-edit repeats;
PR closures consumes coverage's boost run; push closures likewise) — the
bundle `fast` PR + `fast` push remain verdict lanes, `coverage` PR + push
remain line-set lanes, all four irreducible under the current refusals.
Batch of N: 3 + 3N + ~2 → **3 + 2N + 1**.

## 5. Cost test (root-cause.md §4)

Measured cadence: 10 PR merges and 11 push Tests runs on 2026-10-10; ~2–4
train events/day; the batch-of-three's push side alone cost
1516+2042+1238 + 2176+2869+1839 + 2264+2608+852 = **17 404 s = 4 h 50 m of
`boost_drift_replay.py` lane time for 3 merges**.

| lever | engineering | saving per merge / day | risk |
|---|---|---|---|
| r1 prepr memo (sibling r1, confirmed) | `tools/pr/prepr.sh` only | the whole local step-6b cost per body edit / re-push at an unchanged head (25–50 min each on a reach diff) | weakens only the local early warning; CI unaffected |
| C2 proof-recordings consume | upload-`if` + a tree-hash-named artifact + a fail-closed download in `tests.yml` | ~30 min lane × every batch (~2–4/day) ≈ 1–2 h/day | mislabel is silent ⇒ tree-hash key + self-test obligation |
| C1 composed measurement, boost first | `coverage_tree.sh` + `derive_closures.sh`/`closure.py` recorded-argv + `tests.yml` artifact pass + two Linux byte-identity proofs | PR scoped closures −27 min per reach-PR; push closures −14–31 min × 11 push runs/day ≈ **3–5 h/day of lane time** | loud (UNDER-SCOPED / ratchet floors); refused per-script if either equality breaks |
| R1 scoped-arm lanes (sibling, unchanged) | lane runner in `derive_closures.sh` | 21–24 min off every reach-PR gate wall | none (R9-F10.15) |

## 6. Recommendation, ordered, smallest first PR each

1. **r1 memo** — already specified by the sibling; land it (smallest,
   local-only, independent of everything here).
2. **R1 scoped-arm lanes** — unchanged from the sibling's recommendation; it
   remains the biggest *wall* lever per reach-PR.
3. **C2** — smallest first PR: extend the closure-recordings upload `if:` to
   the dispatch arm with the tree-hash-named artifact; in the push `closures`
   job, try the download before the full arm and fail closed to re-record;
   self-test that a mismatched tree label is refused. Acceptance: one real
   batch whose last merge's `closures` job logs "consumed proof recordings
   (tree <hash>)" and completes in minutes with `check` green; a synthetic
   mismatched artifact re-records.
4. **C1, `boost_drift_replay.py` only** — acceptance: on Linux CI at one
   head, the composed run's read set is byte-identical to the bare recording's
   and its line set to the traced-only run's, and the landed arms are green
   twice; any inequality refuses the composition for that script.
5. **Commission (vi-b)** (speed the replay) — unchanged from the covfast
   order; it remains the only lever for the verdict lanes.

## 7. What could not be measured, and why

- **The audit-hook + tracer composition's overhead and correctness** — needs
  the Linux proof C1 specifies; this box is macOS and a local recording is
  neither allowed nor authoritative.
- **Whether any PR ever restored an intermediate batch tip's coverage base**
  (the 2-minute windows): reasoned from the keying (merge-base commit), not
  exhaustively sampled; the marker check makes a miss fail closed anyway.
- **Today's push run `38119999814` (#2121)** was still in progress at capture
  (its three heavy jobs in flight on a tools/docs-only diff — the rule-1 full
  price, correctly).
- **PR-side boost totals for 2026-10-10 beyond #2071**: verified zero for the
  batch of three's entries via the proof's scoped-out/reused lines; the other
  PRs' arms were not each fetched (the push side dominates the average and was
  fully measured).

## 8. Every figure's provenance

- Batch of three: proof run `38081141948` (`batch/20261010-194554-1`, sha
  `16cccd5ef`, dispatch recheck=true, 2026-10-10T19:46Z) — jobs
  `114298129671` (closures 54 m 22 s; boost recorded 20:00:22→20:29:36;
  full arm, 34 recordings), `114298156073` (fast 16 m 43 s, "MODE: SCOPED --
  15 run, 18 scoped out", boost scoped out), `114298155756` (coverage 16 m 15
  s, boost reused). Merges `507858430` (#2110) 20:42:39Z, `32f65da18` (#2111)
  20:44:57Z, `6918cb4b2` (#2124) 20:46:59Z; trees `8adae01a`/`651dcd99`/
  `142e9b21`; **proof tree `142e9b213` == `6918cb4b2`'s tree** (`git
  rev-parse ^{tree}`); PR heads `fa851d7ea`/`6b21ba530`/`9eed9898b` contain
  neither base nor each other's merges (`git merge-base --is-ancestor`).
- Push runs `38084808934`/`38084956560`/`38085092106`: job ids
  `114309000353`/`114309441686`/`114309833867` (fast, boost 1516/2176/2264 s),
  `114309000372`/`114309441689`/`114309833904` (coverage, "No per-script
  coverage for <sha>: measuring every script", boost 2042/2869/2608 s rc 0),
  `114309000519`/`114309441746`/`114309833831` (closures full, 34 recordings
  each, boost 20:53:06→21:13:44 / 20:57:44→21:28:23 / 20:54:58→21:09:10; no
  upload step ran — pull_request-only `if:`).
- Cadence: `git log --merges` on `origin/main` (10 PR merges 2026-10-10);
  `.../actions/runs?branch=main&event=push` filtered `name=="Tests"` (11 that
  day; `38119999814` on `a74520020` 2026-10-11T07:01Z in progress).
- Machinery read: `.github/workflows/tests.yml` (triggers: push main-only, so
  batch branches fire no push run; the closures job's scoped loop, upload
  `if:`, DOCS_ONLY_FAST arm; coverage key `coverage-per-v1-<os>-<BASE>-py<py>-
  <hashFiles>`, marker `push refs/heads/main <BASE>`, save on push-main only),
  `tools/pr/prepr.sh` (`closures_line` at :487, `closure_lane`,
  `recorder_python`, `closures_verdict`), `tools/pr/app_push.sh` (prepr per
  push), `tools/audit/seat/merge_train.py` (batch steps 0–5, `DISPATCH`
  recheck=true at :178, `POLL_SECONDS = 300`, guard checks tree equality
  only for later merges — push runs gate nothing inside the batch),
  `tests/derive_closures.sh` (lane layout, cheap-argv rules),
  `tools/coverage/coverage_tree.sh` (tracer via `COVERAGE_PROCESS_START`,
  lanes, per-script data), `dev/governance/rules/gate-scoping.md` (off-Linux
  rule: `--single`'s partial union grows, never drops Linux recordings).
- Sibling studies' figures cited, not re-derived: `547d25b71` (merge-path),
  `177bb01c3` (closures scoping), `69e374393` (coverage/fast).
