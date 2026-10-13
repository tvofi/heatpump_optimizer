<!-- Landed from handoff/r9-friction-study @ c8a6be1cf; paths and file:line citations are as measured at its baseline origin/main 86dbf0ca1, before the R9-RO reorganisation moved tools/audit/round9/ under dev/audit/rounds/round9/. Body transcribed verbatim; this comment is the only added line. -->
# Pre-study round 2: friction remedies — benefit/cost (R9-FR-1)

Study seat R9-FR-1, re-dispatched 2026-10-05 with #1951 added to the issue set.
Round 1 (`friction-prestudy.md`, this directory, commit `8eab7dfd` at
`1913f0dd` = `v6.7.16`) folded R9-FR-2 (#1860, merged as #1891) and R9-FR-3
(#1825, merged as #1892). This round re-measures everything at
**`origin/main` = `86dbf0ca`**, 2026-10-05 ~21:20Z, in
`/Users/timmalmstrom/hpo-seats/r9-fr-1/wt`. Raw outputs:
`/Users/timmalmstrom/hpo-seats/r9-fr-1/scratch/`. Every figure's command is in
§8. The triage seat's scratch (`/Users/timmalmstrom/hpo-seats/friction-triage/`)
and round 1's (`r9-fr-study/scratch/`) are gone from disk; nothing below is
carried from either — round 1's per-window figures are re-derived and agree
(§1).

## 1. The sweep: five tag windows

`GITHUB_TOKEN=$(gh auth token) node .claude/workflows/policy_lint.mjs --stats
--since <tag>` for v6.7.12 … v6.7.16, rc=0 and `GAP: 0` each. Per-window
distinct-PR counts by differencing the cumulative runs (each merged PR lies in
exactly one window). W16 = `v6.7.16..86dbf0ca`, **open** (no stamp since). Keys
under 2 in every window are omitted; **bold** = at or over threshold 3.

| kind | key | W12 | W13 | W14 | W15 | W16 |
|---|---|---|---|---|---|---|
| merges | (`STATS:` line) | 31 | 31 | 14 | 11 | 29 |
| verdict class | head-moved | **14** | **7** | **4** | 2 | 0 |
| verdict class | root-cause-unanswered | 0 | **6** | **8** | 1 | **6** |
| verdict class | mutation | **4** | 1 | 0 | 2 | 0 |
| verdict class | harness | 0 | 0 | **3** | 2 | 0 |
| verdict family | mutation (family) | **4** | 2 | 2 | 2 | 0 |
| friction rule id | tools/audit/briefs/fixer.md | **4** | **3** | 2 | 2 | 0 |
| friction rule id | .claude/rules/gate-scoping.md | 2 | **5** | **3** | 1 | 0 |
| friction rule id | .claude/rules/ratchet-budgets.md | 2 | 0 | 1 | 0 | 2 |
| friction family | environment (family) | 0 | **3** | 2 | 0 | 0 |

Round 1's W13/W14/W15 columns (merges 31/14/11; root-cause-unanswered
6/8/1; head-moved 7/4/2) re-derive identically — the instrument changed under
R9-FR-3 (family rows added) without moving an id row.

Rework baseline, from each run's `STATS ROUNDS` line, differenced: first-verdict
`merge` 18/31, 19/31, 2/14, 4/11, **21/29**; repairs after a `blocked` 13, 14,
27, 12, **9**; head-moved re-verifications 25, 10, 4, 2, **0** (W12…W16). W16 is
the best window measured. Of its 10 `blocked` verdicts, **8 are
root-cause-unanswered** — the one class over threshold, and #1951's subject.

**Null control (no token):** the same `--since v6.7.16` run with
`GITHUB_TOKEN` unset prints `skip merge-enumeration … UNCHECKED this run, not
confirmed empty`, `STATS: 0 merged`, `WOULD OPEN: 0` — the phantom-zero guard
is live, so the zeros above are counts, not fetch failures.

**Second control (self-declared ids):** every merged PR in every window carries
a `## Friction` section (31/31/14/11/29), but the share declaring ≥1 entry fell
to **4/29 in W16** (15/31, 12/31, 9/14, 4/11 before; ~8 of W16's 29 are
record/autofix PRs that declare `none` by nature). W16's zeros on *friction rule
ids* (fixer.md, gate-scoping.md) are therefore weak evidence of a fix. Verdict
classes are written by the reviewer, not self-declared, and do not share the
bias: W16's 0 head-moved is strong evidence.

## 2. #1951: what root-cause-unanswered is made of now

All 8 W16 entries (6 PRs; matches the bot's "6 … 8 entries") were enumerated
per PR (§8 cmd 3) and the check-runs read at each blocked head (cmd 4).

**Every one names a red standing at the reviewed head itself.** R9-FR-2's arm
(`tools/audit/prepr.sh` "the ancestry red-check arm") enumerates
`git rev-list $base..<remote head ref>` — commits *already pushed* — so it
cannot see a red the handoff push itself produces, by construction. It is not
failing; its scope is the second block on a red already shown, and W16 has no
repeat block on the same red. FR-2 merged 2026-10-04T11:26Z, 20 min after the
v6.7.16 stamp, so W16 is effectively its first window.

In all 7 distinct blocked heads the failing run had `completed_at` **before**
the block was posted (3–63 min); `pr-contract` was red at 5 of them, stale-green
at one (#1957: it ran before `closures` failed and its re-run was cancelled — the
R9-RC-PRCONTRACT class, owned by the in-flight R9-RC-PRCONTRACT-FIX), and not yet
re-run at one.

Since v6.7.12 the class is 21 PRs / 31 entries (equals the tool). Classified by
the check the block names (cmd 5):

| check named | W13 | W14 | W15 | W16 | PRs | local detector before the push? |
|---|---|---|---|---|---|---|
| budget-raise-gate | 1 | 0 | 0 | 2 | #1856 #1942 #1948 | **yes, offline**: the raise is a pure function of the diff (`file_raises`); red by design until the owner approves |
| typing | 0 | 0 | 1 | 2 | #1874 #1958 #1959 | **yes, given the pinned interpreter** — Mac seats lack it (§3) |
| no-copies | 0 | 1 | 0 | 0 | #1865 (+#1959, named in its body) | **yes**, seconds; in no local path today |
| closures (other) | 1 | 2 | 0 | 1 | #1846 #1852 #1864 #1957 | no: INERT-read and under-scope findings need CI's Linux recording (#1957's own answer) |
| nightly-status | 2 | 3 | 0 | 0 | 5 PRs | n/a — exemption wording fixed; 0 since W14 |
| base-pinned grader | 1 | 0 | 0 | 1 | #1847 #1886 | no: the base copy is the grader by decision 0013 |
| fast (3.14), mutation, briefs | 4/6/1 | … | … | 0/1/0 | — | per-check; mutation's drive cost is R9-FR-7's |

Repair cost per entry: block → next verdict on the same PR, median **80 min**
over all 31 entries. The 7 entries a pre-push detector would have caught (the
three "yes" rows) cost 11, 27, 68, 80, 134, 269, 753 min — median 80, sum 1342
— and **4 of W16's 8 entries** are in that set. For the budget rows the repair
was body-only; for typing and no-copies it was a code commit owed anyway, so the
saving is the review round and CI cycle spent on a head the seat could have
measured, not the repair.

The rejected alternative for the budget row: exempting `budget-raise-gate`
from `fix-review.md` step 11 as `nightly-status` is. It is a policy edit
(owner approval; the labelled mandate covers only to 2026-10-09T12:00Z) and it
drops the body's record that a raise is pending — refused in favour of an
instrument.

## 3. Verdicts

### #1951 root-cause-unanswered — **FOLD as two instrument groups** (R9-FR-11, R9-FR-12)

- **R9-FR-11 — the Mac seat recipe builds the pinned typing interpreter.**
  `tools/audit/seat/cloud-setup.sh` builds `venv-ha` from
  `tests/requirements-typing.txt` and exports `HPO_TYPING_PYTHON`;
  `tools/audit/seat/seat_venv.sh` builds `venv-ci` only, and the seat shim
  exports nothing. Measured on this seat: `tests/typing_ruler.py` under the
  seat venv prints `census NOT checked here (HPO_TYPING_PYTHON unset)` and
  passes. The ruler's closure covers 70 production files, so the scoped gate
  already selects it; only the interpreter is missing. #1958 and #1959 were Mac
  seats (bodies cite `/Users/` paths and `HPO_TYPING_PYTHON`); #1959's own
  answer names this gap as state (c). **Benefit:** 2 of W16's 8 entries,
  80 + 753 min. **Cost:** ~mirror of `cloud-setup.sh`'s two pins/export lines
  into a 100-line script; standing ~1 min census per scoped gate run (#1959's
  figure, unmeasured here — this seat has no pinned venv); one-off disk for
  the Home Assistant wheel — **the risk**, since the environment family's
  W13/W14 entries include Mac disk-full; the fixer measures and states it.
  Instrument in `tools/`, not code-owned, no policy edit. Sonnet: the cloud
  recipe is the oracle.
- **R9-FR-12 — `prepr.sh` predicts two head reds offline.** (a) A diff that
  raises any budget leaf (`file_raises`, read at the merge base, as CI's gate
  restores it) feeds `--red budget-raise-gate` to the body check `pr-contract`
  runs, so a silent `## Red checks` is refused before the push. (b) A diff
  touching a `.py` under `tests/` or `custom_components/` runs `python3
  tests/closure.py no-copies` — today only `tests.yml`'s `closures` job runs it.
  **Benefit:** budget 3 PRs (2 in W16: 11 + 27 min, body-only), no-copies 1–2
  PRs (68 min). **Cost:** (a) one pure call, sub-second; (b) measured 11.8 /
  15.4 / 27.7 s wall, 4.6 s user, on this loaded Mac, per prepr run that
  touches Python. Cost test for (b) alone, volume an **estimate** (~3 prepr
  runs × ~20 Python-touching PRs per window, not measured): ≈ 20 min/window of
  wall-clock against 68 min × 0.5 occurrences/window (2 PRs over W13–W16)
  ≈ 34 min/window — marginal win, taken because it rides (a)'s step and file. `prepr.sh` is not code-owned; `budget_raise_gate.py` and
  `closure.py` are, and are called, not edited. Opus: `prepr.sh` and its
  self-test are where R9-FR-2 went three review rounds.
- **Kills class or instance?** Together, the three "yes" rows of §2: 7 of 21
  PRs since v6.7.12, 4 of 8 W16 entries. The residual (closures recordings,
  base-pinned graders, real fast/mutation reds) has the gate as its cheapest
  detector — recorded, nothing built.
- **Closing #1951:** both groups say `Part of #1951`; the orchestrator closes it
  on the second merge, naming both PRs and the re-measurement command `node
  .claude/workflows/policy_lint.mjs --stats --since <the tag after them>`.
  The bot re-files per window, so a recurrence re-opens it on its own.

### #1807 head-moved — **CLOSE BY RE-TRIAGE** (round 1: refuse the ruleset)

Round 1's refusal stands, and its "number that changes the answer" moved the
other way: 14 → 7 → 4 → 2 → **0** PRs per window, and W16's `STATS ROUNDS`
records **0** re-verifications of a head moved after `merge` over 29 merges.
Verdict class, so not subject to §1's declaration bias. Disposition: close
naming this measurement and `node .claude/workflows/policy_lint.mjs --stats
--since v6.7.16`; the bot re-files if a window reaches 3. Caveat for the
comment: W16 is open.

### #1826 tools/audit/briefs/fixer.md — **REFUSE stands; close with the condition**

4 → 3 → 2 → 2 → 0. No window since W13 reaches 3; W16's 0 is a self-declared id
under a 4/29 declaration rate, so it does not prove a fix — it also shows no
recurrence. Round 1's condition (≥3 PRs in one full window naming the **same
step**) is unmet. The 4 bare-`fixer` entries (#1800 ×2, #1818, #1885) stay
unresolved to the contract **by design** (`policy_lint.mjs` lines 2561–2590: a
bare role name names a seat or dispatch brief as readily as the contract), and
read as heterogeneous: step 5's stress wait, a stale carry, step 5's
local-only wording, a Mac-only closures check. Folding them in would not reach 3
in any window.

### #1855 .claude/rules/gate-scoping.md — **REFUSE stands; close with the condition**

2 → 5 → 3 → 1 → 0. Round 1's condition (≥3 PRs in a full window, or ≥3
declarations naming the lease/queue) is unmet. Same declaration caveat.

### #1825, #1860, #1881 — closed; delivery check

#1825 closed by #1892 (R9-FR-3) — family rows print in every run above. #1860
closed by #1891 (R9-FR-2) — the arm is in `prepr.sh`. **Both merged after
`v6.7.16` and no stamp has run since (`VERSION` 6.7.16), so neither is carried by
a release yet**: the next stamp's notes must name #1891 and #1892. #1881 closed
by re-triage; harness is 2 → 0 (W15 → W16).

## 4. Unfiled classes over threshold

No window W12–W16 has an unfiled key at ≥3; the bot files per open window
(#1951's body: window `v6.7.16..origin/main`). Over cumulative windows three
unfiled keys cross:

- **`.claude/rules/ratchet-budgets.md`** — 5 PRs since v6.7.12, never more than
  2 per window, heterogeneous: #1816 the `--pin-killed` drive cost (R9-FR-7
  since parallelised it); #1818, #1851, #1942 per-file token caps at zero
  headroom (35 of 42 capped files sit at zero on lines or tokens today); #1958
  a `methods_over_150` move paid without a raise. The band (#1070, `97d9bdb3`)
  covers aggregates only, and `ratchet-budgets.md` states why per-file caps get
  none. The friction is the designed price of a one-sided ratchet. **REFUSE**;
  changes at ≥3 PRs in one window naming the same cap.
- **`fixer` (bare)** — §3 #1826. **REFUSE**.
- **`environment` family** — 0 / 3 / 2 / 0 / 0. Round 1's condition (≥3 in the
  next full window) failed in W15 and W16. **REFUSE; drop from watch.**

## 5. Findings recorded, not folded

1. **`.claude/rules/defect-root-cause.md`'s "Qualifies" example is false in
   the tree.** It says `no-copies` "runs locally in under a second … Cheaper
   detector: an edit-time hook. Countermeasure built." At `86dbf0ca` no hook,
   `prepr.sh`, `preflight.sh` or `run.sh` line runs it (only `tests.yml` line
   1818), `git log -S no-copies -- .claude/hooks .claude/settings.json` is empty,
   and it measured 11.8–27.7 s here. R9-FR-12 builds the detector in `prepr.sh`;
   rewording the example is a policy edit for the owner, carried into
   R9-FR-12's brief so its body raises it.
2. **Round 1's dispositions never reached the issues.** #1807, #1826, #1855
   carry only the triage verdicts (2026-10-04T09:1xZ) and bot below-threshold
   comments; round 1's refusals are on no issue. §3 supersedes them.
3. **`R9-RO-6` moves `tools/audit/prepr.sh` and `tools/audit/seat/`** (wave 23,
   not started). The proposal adds `R9-FR-11` and `R9-FR-12` to its `after` so
   the move lands on the edited files, not under them.

## 6. The fold set

Exact roster entries, plus the one roster edit (§5.3), in
`tools/audit/round9/prestudy/friction-prestudy-r2-groups.json` on this branch.
`node .claude/workflows/brief_lint.mjs <that file>` passes with 0 errors; its
null control — the same file with one anchor phrase and one path broken —
reports exactly those 2 errors (§8 cmd 10). The briefs name this document in
prose, not by path: it is on this branch only, and a path citation would fail
the linter wherever the roster is linted. Both groups are wave 2, independent of
each other, no owner gate. The file also carries the seven issue dispositions
of §3 and R9-FR-1's own `resume` update, for the orchestrator to apply.

## 7. Summary

| issue / key | W13 / W14 / W15 / W16 (PRs) | remedy | verdict | binds |
|---|---|---|---|---|
| #1951 root-cause-unanswered | 6 / 8 / 1 / 6 | Mac typing venv; prepr budget + no-copies predictions | **FOLD R9-FR-11, R9-FR-12** | instruments in `tools/`; 4 of W16's 8 entries |
| #1807 head-moved | 7 / 4 / 2 / 0 | none | **CLOSE by re-triage** | verdict class at 0 over 29 merges |
| #1826 fixer.md | 3 / 2 / 2 / 0 | simplification pass | **REFUSE, close with condition** | no window ≥3 since W13 |
| #1855 gate-scoping.md | 5 / 3 / 1 / 0 | instrumented lease | **REFUSE, close with condition** | no window ≥3 since W14 |
| #1825 / #1860 / #1881 | — | delivered / re-triaged | closed; **#1891, #1892 unreleased** | next stamp names them |
| ratchet-budgets.md (unfiled) | 0 / 1 / 0 / 2 | none | **REFUSE** | per-file caps band-free by design |
| environment family (unfiled) | 3 / 2 / 0 / 0 | none | **REFUSE, drop** | round 1's condition failed twice |

## 8. Figure index

All in `/Users/timmalmstrom/hpo-seats/r9-fr-1/wt` at `86dbf0ca`; scripts and
outputs in `../scratch/`.

1. Sweep: `GITHUB_TOKEN=$(gh auth token) node .claude/workflows/policy_lint.mjs --stats --since <tag>` for v6.7.12–16 → `sweep-<tag>.txt`; table by `python3 ../scratch/census_table.py ../scratch` → `census-table.md`. Rounds: the `STATS ROUNDS` line of each, differenced.
2. Null: same for v6.7.16 with `GITHUB_TOKEN` unset → `null-notoken-v6.7.16.txt`.
3. Per-PR verdicts: `python3 ../scratch/verdicts.py v6.7.16` (and `v6.7.12`) → `verdicts-<tag>.tsv` (first-parent commits → `/commits/<sha>/pulls`, then each PR's issue comments and reviews, `^Fix review:` lines). Cross-check: 31 root-cause-unanswered entries over 21 PRs since v6.7.12, 8 over 6 since v6.7.16 — the tool's own figures.
4. Check-runs at each blocked head: `gh api "repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs?per_page=100" --paginate` filtered to failures, `pr-contract`, `budget-raise-gate` → `checkruns-blocked-heads.txt`.
5. Classification and latency: `python3 ../scratch/rcu_classify.py ../scratch/verdicts-v6.7.12.tsv` → `rcu-classified.md`.
6. Friction declarations and coverage: `python3 ../scratch/friction_decl.py v6.7.12` (keys via `policy_lint.mjs --normalize-friction-keys`; entry counts equal the tool's) and `python3 ../scratch/friction_coverage.py` → `friction-coverage.tsv`.
7. Repairs: `git log --format='%h %an %s' <blocked>..<next head>` per pair (§2's body-only vs code repairs); `## Red checks` sections via `gh pr view <n> --json body` → `red-checks-sections.txt`.
8. Typing gap: `~/.local/state/hpo/venv-ci/bin/python tests/typing_ruler.py` (not-checked line); `tests/closures.json` closure of `tests/typing_ruler.py` (70 production files); `rg -n HPO_TYPING_PYTHON tools/audit/seat/`.
9. no-copies: `/usr/bin/time -p ~/.local/state/hpo/venv-ci/bin/python tests/closure.py no-copies` ×3; `rg -n no-copies .claude/hooks .claude/settings.json tools/audit/prepr.sh tools/audit/preflight.sh tests/run.sh` (empty) and `.github/workflows/tests.yml:1818`; `git log -S no-copies -- .claude/hooks .claude/settings.json` (empty).
10. Budgets: `node .claude/workflows/policy_lint.mjs --budgets` → `budgets.txt`; zero-headroom count over its per-file rows. Brief lint: `node .claude/workflows/brief_lint.mjs tools/audit/round9/prestudy/friction-prestudy-r2-groups.json`.
