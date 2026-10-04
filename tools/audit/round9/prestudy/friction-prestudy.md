# Pre-study: friction remedies — benefit/cost (R9-FR-1)

tvofi, 2026-10-04. Round-9 study seat R9-FR-1, per the roster entry on
`origin/handoff/audit-r9-fixplan`. No fix PRs from this seat. Inputs: the
friction-triage seat's six verdicts and stats
(`/Users/timmalmstrom/hpo-seats/friction-triage/scratch/friction-triage/`, run
at `9a51f6d72` on 2026-10-04 ~11:12Z) and its per-issue comments on #1807
#1825 #1826 #1855 #1860 #1881. All measurements in this document were taken in
the worktree `/Users/timmalmstrom/hpo-seats/r9-fr-study/wt` at
**`origin/main` = `1913f0dd7` (tag `v6.7.16`)**. Raw sweep outputs:
`/Users/timmalmstrom/hpo-seats/r9-fr-study/scratch/fr-study/sweep-*.txt`.

Every figure's command is in §7. Every histogram figure is a run with
`GITHUB_TOKEN=$(gh auth token)` and exit code 0; the merge-enumeration GAP line
(failure count) is `GAP: 0` in every run quoted. The no-token null was
re-demonstrated this seat, not carried from the triage: without `GITHUB_TOKEN`
the same command prints the skip line `the commit-to-PR map could not be
fetched (GITHUB_TOKEN is not set); ... UNCHECKED this run, not confirmed empty`
and refuses the histogram (sweep output above, rc=0 with the skip) — the
phantom-zero guard is live.

## 1. The sweep: four tag windows

`node .claude/workflows/policy_lint.mjs --stats --since <tag>` at `1913f0dd7`,
one run per tag. The windows are cumulative (tag..origin/main), so per-tag-window
counts are derived by differencing — sound because each merged pull request is
counted in exactly one tag window (its merge commit sits between exactly one
adjacent tag pair):

| run | merges in window | notes |
|---|---|---|
| `--since v6.7.13` | 56 | cumulative W13+W14+W15 |
| `--since v6.7.14` | 25 | cumulative W14+W15 |
| `--since v6.7.15` | 11 | W15, now closed by the `v6.7.16` stamp |
| `--since v6.7.16` | 0 | the stamp sits at origin/main HEAD; empty window, reported as a real zero over 0 merges |

W13 = v6.7.13→v6.7.14 (56−25 = 31 merges), W14 = v6.7.14→v6.7.15 (25−11 = 14),
W15 = v6.7.15→v6.7.16 (11). **W15 is the first window closed since this study
began** — the triage seat ran while it was one day old, so its "v6.7.15" column
was a partial window; this study's W15 column supersedes it.

### Full friction histogram (distinct PRs / entries)

Verdict classes, cumulative runs (left) and derived per-window (right):

| verdict class | since v6.7.13 | since v6.7.14 | since v6.7.15 | W13 | W14 | W15 |
|---|---|---|---|---|---|---|
| merge (passing, not rework) | 55/72 | 25/31 | 11/13 | — | — | — |
| **root-cause-unanswered** | 15/23 | 9/15 | 1/3 | 6/8 | 8/12 | 1/3 |
| **head-moved** | 13/16 | 6/6 | 2/2 | 7/10 | 4/4 | 2/2 |
| **harness** | 5/5 | 5/5 | 2/2 | 0/0 | 3/3 | 2/2 |
| **mutation** | 3/3 | 2/2 | 2/2 | 1/1 | 0/0 | 2/2 |
| **mutation-vacuous** | 2/2 | 1/1 | 0/0 | 1/1 | 1/1 | 0/0 |
| **mutation-survivor** | 1/2 | 1/2 | 0/0 | (1 PR/2 entries in W13∪W14; differencing cannot split it) | | 0/0 |
| mutation FAMILY | **6/7** | **4/5** | 2/2 | ≥2/≥2 | ≥1/≥1 | 2/2 |
| defect | 2/2 | 2/2 | 2/2 | 0 | 0 | 2/2 |
| body | 2/2 | 2/2 | 0 | 0 | 2/2 | 0 |
| evidence, vacuous-check, instrument | 1/1 each | 1/1 each | 1/1 each | 0 | 0 | 1/1 each |
| class-open, other, claims, null-control | 1/1 each | 1/1 each | 0 | 1/1 each | 0 | 0 |
| closures-under-scoped, closures, contract, ci-red | 1/1 each | 1/1 each | 0 | 1/1 each | 0 | 0 |
| honesty, security, provenance, barrier | 1/1 each | 0 | 0 | 1/1 each | 0 | 0 |

Friction rule ids (distinct PRs / entries):

| friction rule id | since v6.7.13 | since v6.7.14 | since v6.7.15 | W13 | W14 | W15 |
|---|---|---|---|---|---|---|
| **.claude/rules/gate-scoping.md** | 9/12 | 4/5 | 1/1 | 5/7 | 3/4 | 1/1 |
| **tools/audit/briefs/fixer.md** | 7/10 | 4/5 | 2/3 | 3/5 | 2/2 | 2/3 |
| **environment (+seat-environment)** | 5/6 | 2/2 | 0/0 | 3/4 | 2/2 | 0/0 |
| .claude/rules/ci-autofix.md | 2/2 | 2/2 | 1/1 | 0 | 1/1 | 1/1 |
| .claude/rules/writing-for-agents.md | 2/2 | 0 | 0 | 2/2 | 0 | 0 |
| defect-root-cause.md, SEAT-COMMON-worktree, CLAUDE.md, structure-ratchet, fixer_step3/step3, ratchet-budgets.md, fixer, resume.note_file, fixer.step6, fix-review, codeowners_gap, ci-autofix.closures | 1/1 each | (see raw) | (see raw) | — | — | — |

WOULD-OPEN per run: since v6.7.13 → 7 (root-cause-unanswered, head-moved,
harness, mutation, gate-scoping.md, fixer.md, **environment**); since v6.7.14 →
5 (the same six minus environment, plus nothing new); since v6.7.15 → 0;
since v6.7.16 → 0.

**The one would-open class no filed issue names is `environment`** (family with
`seat-environment`): 5 PRs/6 entries over since-v6.7.13, at threshold in W13
(3 PRs), 2 in W14, **0 in the closed W15**. Its content, read from the
declaring bodies: seat venv/numpy unavailability for `tests/entities.py`
(#1861, #1848), Mac disk filling mid-run (#1858, #1848), no Docker daemon on
the seat host (#1870), a seat-worktree clone carrying the worktree path as
`origin` (#1871).

### The rework baseline unit

The since-v6.7.14 run's `STATS ROUNDS` line: over 25 merged pull requests
carrying a parsable verdict (25/25 coverage, 0 unparsable), first-verdict yield
6/25 = 0.240, one-round yield 6/25, **39 repairs after a `blocked`**, 6
re-verifications of a head that moved after a `merge`. The W15 run: first-verdict
yield 4/11 = 0.364, 12 repairs after blocked, 2 head-moved re-verifications —
yield improving, rework still ~1 repair per merge. Wall-clock datapoint for one
repair round, from this window's own record: #1874 took four blocked verdicts
(10:12Z harness → 12:57Z root-cause+harness → 13:26Z root-cause+mutation+harness
→ 17:12Z root-cause) before merging at 21:42Z — 11.5 h wall-clock, one seat,
one reviewer. A blocked entry costs ≥1 fixer repair round + 1 reviewer
re-verification; call it 1–2 seat-hours per entry, ~6–12 seat-hours per window
at the W14 peak of the largest class.

## 2. What already enforces the red-check trigger (decisive for #1860)

`pr-contract` CI already enforces the root-cause trigger **for reds standing at
the head** (.github/workflows/pr-contract.yml, "#956" wiring, landed with the
R8-I3 trust work `b6e30297d`): it lists the head's check runs
(`conclusion == "failure"`, excluding the check-run name `pr-contract`), and
passes each name to `policy_lint.mjs --pr-body ... --red <name>` — the same
body that exited 0 with no `--red` exits 1. `pr-contract-rerun.yml` re-runs
when a later red lands.

So why did `root-cause-unanswered` still block 8 of W14's 14 PRs? The W14
blocks, read from the verdict comments (§7 command): #1869 and #1867 cite
mutation reds **at earlier branch commits** (`e43ae8dc9`, `5c69edd8d8`) since
repaired; #1865 closures, #1864 briefs, #1851 fast(3.14), #1852 three lanes —
all reds in the branch's own check-run history, none standing at the reviewed
head; #1863 and #1870 cite **nightly lanes** (`nightly-status`), which grade
main and never appear in the PR's check runs at all. The reviewer's trigger
(`defect-root-cause.md`: "a check that went red **on a commit in the branch**")
is broader than CI's ("red at the head") by exactly two gaps: ancestry reds,
and nightly-lane reds. The class is not enforcement-absent; it is
**scope-different**, and the ancestry gap is the larger share of it (6 of the 8
W14 blocks; the sample is all 8, not a sample).

## 3. Verdicts

### #1860 root-cause-unanswered — prepr.sh ancestry red-check arm — **FOLD** (R9-FR-2)

- **Benefit.** The largest rework class of the sweep: 6/8, **8/12**, 1/3 PRs per
  window; 8 of W14's 14 merges (57%) took a root-cause-unanswered block, each
  ≥1 repair round + re-review. Of W14's 8 blocks, 6 cite reds a branch
  check-run sweep sees (§2) — the arm kills ~6/8 of the class **at push time**,
  before any reviewer reads it, which is exactly what `defect-root-cause.md`
  prefers ("when the defect was found late in CI, a cheaper and earlier
  detector is strongly preferred").
- **Cost.** An instrument PR, and the plumbing already exists twice:
  `pr-contract.yml` already enumerates red check-runs (one `gh api --paginate`
  call, jq key already written and commented) and `policy_lint.mjs --pr-body`
  already accepts one `--red` per name; `prepr.sh` already runs the body check
  (step "pr-body"). The arm extends an existing pattern from the head to the
  ancestry. Comparable landed work: #1879 landed `fixer.md` step 18 +
  `tmp_paths.py` + tracked instruments (`32251f44c`) in one day through three
  fix-review rounds. Estimate: one fixer-day plus 2–3 review rounds. **No
  policy-file edit** — `defect-root-cause.md`'s trigger text already covers a
  detector at any time — so no owner-approval bind and no budget-raise gate.
- **Kills class or instance?** Kills the ancestry share of the class (~75% of
  W14's blocks). The nightly-lane share (2/8) stays with the reviewer; folding
  nightly correlation in would read main's lane status and is refused here as
  scope creep on a first arm.
- Roster group in §4.

### #1825 mutation family fragmentation — family folding in the stats counter — **FOLD** (R9-FR-3)

- **Benefit.** Measurement integrity, not entry removal — state it honestly:
  this remedy removes zero rework by itself. In the since-v6.7.14 window the
  mutation **family** sits at 4 distinct PRs (threshold 3) while every exact id
  is below it (mutation 2, mutation-vacuous 1, mutation-survivor 1): the
  counter opens nothing while the family recurs. The friction programme's
  threshold keys ids, and a class spread across sibling keys is invisible to
  the very instrument that decides when friction becomes an issue. The same
  fragmentation already hid a second family: `environment`/`seat-environment`.
  (Related keying pollution, recorded not folded: #1883's 20:14Z block is a
  README claim mismatch prefixed `harness: class-open` — a verdict-prefix
  choice by a reviewer, not a parser bug; noted for the reviewer contracts,
  and one reason family rows must print the census lines unchanged.)
- **Cost.** Small instrument change in `.claude/workflows/policy_lint.mjs
  --stats` plus acceptance fixtures: half a fixer-day, sonnet-with-oracle (the
  acceptance harness is the oracle), 1–2 review rounds. **No policy-file
  edit.** One consumer to check in the same PR: `friction_issues.mjs` reads the
  stats output and its input contract must not change shape (census lines
  unchanged; family rows are additive).
- **Kills class or instance?** Neither — it restores the instrument's sight.
  The mutation friction itself was substantially countermeasured inside W15
  (`3ec57ba0c`, `0b61a09bd`, `45bdb8c0c`: mutant-phase budgets, timeout-is-no-kill,
  reservation release), which is why the family's W15 count is 2 and falling;
  the fold is what lets the counter *notice* if that trend reverses.
- Roster group in §4.

### #1881 harness — **CLOSE BY RE-TRIAGE, no roster group**

The triage's stated FIXED condition: "`harness` stays below threshold across a
window that predates nothing (all of whose PRs merged under step 18)". **W15 is
now closed and meets it**: 11 merges, every one after #1879 (step 18 +
`tmp_paths.py`) merged 2026-10-03 18:10Z — the earliest W15 merge, #1874, is
21:42Z — and `harness` reads **2/2, below the threshold of 3**, with 0
would-open lines. Both caveats recorded for the closing comment: (a) #1874's
three harness blocks (10:12–13:26Z) predate step 18's landing — friction that
accrued before the countermeasure, merged after; (b) #1883's one post-step-18
`harness:` block (20:14Z) is a README claim mismatch keyed by the reviewer's
prefix, not missing-harness friction (§3 #1825). Disposition: a re-triage
comment closes #1881 naming PR #1879, pin `fixer.md` step 18 + `tmp_paths.py`,
with `node .claude/workflows/policy_lint.mjs --stats --since v6.7.15` as the
re-measurement command. No group; nothing to build.

### #1807 head-moved — platform handoff-freeze enforcement — **REFUSE**

- **The remedy does not fit the measured cause.** The W15 instances were
  classified from the commits between each verdict pair (command in §7): both
  W15 PRs' heads moved because the fixer **merged origin/main into the handoff
  branch** — #1885's `7162a2d8`→`c983b977` is `c983b9778 Merge origin/main
  into handoff/r9-f10-13`, picking up #1888's record-row merge — which is the
  delivery-status protocol's own requirement (`docs/delivery/<N>.md` rows at
  each merge) acting on long-lived branches. A ruleset refusing pushes to
  `handoff/*` heads except the orchestrator's identity refuses the protocol's
  own sync, or funnels every sibling-merge sync through the orchestrator.
- **Trend.** 7 → 4 → 2 distinct PRs per window (rate per merge 0.23 → 0.29 →
  0.18); 2 re-verifications in W15's STATS ROUNDS, against 6 in W14's.
- **Cost.** A ruleset change costs tvofi's hands (ruleset 22628467; the
  `rules/branches` endpoint is not bypass-aware, so carve-outs must be probed
  both arms), and a seat that cannot push cannot repair — deadlock risk on the
  exact branch the freeze guards.
- **The number that changes the answer:** ≥4 distinct PRs in one full window,
  or any full window where the majority of head-moved entries are **non-sync**
  post-freeze seat pushes (classifiable with the §7 inter-verdict-commit
  command). Until then the cheaper lever already in force is the standing one:
  dispatch the reviewer at push and merge promptly after a `merge` verdict —
  #1885's verdict pair is 75 minutes apart, i.e. the re-verification ran
  inside the merge window, not after a stall.

### #1826 fixer.md simplification pass — **REFUSE**

- **The friction is heterogeneous.** Every declaration read names a different
  step or cause: `--pin-killed` refusing on a red baseline (#1874), a
  Mac-only `closures` check (#1885), a cleanup seat deleting scratch (#1874),
  a hang-vs-timeout kill-semantics contradiction (#1880), an unreachable
  harness step for a diagnostic finding (#1870). No single step is named by
  ≥3 PRs in any window; the id's counts are 3/5, 2/2, 2/3 — flat, not growing.
- **The one named contradiction was already countermeasured in-tree:**
  `0b61a09bd` "mutation_table's driver timeout is no kill" and `45bdb8c0c`
  landed in the v6.7.15 window, resolving the #1880 contradiction the
  declaration names.
- **Cost.** A policy-file change: drafting plus the owner's approving review
  (the labelled mandate 5951564627 — verified on #201: scope all, 2026-10-02T12:00Z
  to 2026-10-09T12:00Z, counts at the budget-raise gate — covers approval only
  to 2026-10-09T12:00Z; after that it needs tvofi), against `policy_budgets.json`
  caps, on the tree's densest role contract (`wc -l` 293 lines; 9 unique
`#1NNN` incident citations, `grep -o '#1[0-9][0-9][0-9]' | sort -u | wc -l`). The
  risk is deleting a protection whose incident has rotated out of memory —
  the file's own header says each step exists because a PR failed without it.
- **The number that changes the answer:** ≥3 distinct PRs in one full window
  naming the **same step** of fixer.md. A single named step reaching
  recurrence is a targeted one-paragraph fix, not a simplification pass.

### #1855 gate-scoping.md — instrumented lease / queue — **REFUSE (remedy mismatched to the measured friction)**

- **The declared friction is not the lease or the queue.** All ten declarations
  read (W13–W15, command in §7) name: closures-recording traps (`--single`
  cannot record a first-imported file #1875; hand-record INERT before CI #1864;
  case-insensitive path attribution #1876; `skip-not-under-scoped` naming no
  next step #1864), decision-0013 base-pinning of `.claude/workflows/*.mjs`
  (#1842, #1847), a roster-brief vs recorder mismatch (#1846), a pinned-grader
  step split across prepr steps (#1862), and one Python-3.12-only channel
  (#1874). **Zero name the lease, the queue, or `gate_lock.py`.** An
  instrumented lease attacks ~0 of the measured friction.
- **Trend.** 5 → 3 → 1 distinct PRs per window, and the sub-frictions each
  have ≤2 instances with in-tree routes already (#1071's two-step merge for
  the `--single` orphan check, `32251f44c` tracked instruments, `3ec57ba0c`
  budgets).
- **Cost.** An instrument answering nothing measured, plus any rule-text
  change needs the owner's approving review.
- **The number that changes the answer:** ≥3 distinct PRs in one full window,
  or any window where ≥3 declarations name the lease/queue specifically.

### NEW class: `environment` (family with `seat-environment`) — **REFUSE to fold**

5/6 since v6.7.13 (would-open), but 3 → 2 → **0** per window, and the standing
remedies are already applied at dispatch level: every seat brief names the
pinned venv (`~/.local/state/hpo/venv-ci`, this roster entry included), scratch
lives under `hpo-seats/`, and Docker-bound lanes route to the nightly (which
#1870's declaration itself records as the accepted route). The disk-full
instances are host ops, tvofi's to watch, not a code remedy. **The number that
changes the answer:** the family at ≥3 distinct PRs in the next full window.

## 4. The fold set — exact roster group entries

Apply into `.claude/workflows/wave-r9-groups.json` `groups` (same key set as
the R9-FR-1 entry; `wave: 2`; both independent — empty `after`):

```json
{
  "group": "R9-FR-2",
  "lane": "FIX",
  "issues": [1860],
  "fixes": [],
  "findings": [],
  "covers": [],
  "class": null,
  "wave": 2,
  "fixerModel": "opus",
  "reviewerModel": "opus",
  "effort": "high",
  "fixture": null,
  "owner_gate": null,
  "rca": false,
  "barrier": null,
  "barrier_prototype": null,
  "blocked_on": [],
  "after": [],
  "brief": "tvofi, 2026-10-04 (pre-study R9-FR-1): #1860 — prepr.sh gains an ancestry red-check arm: the fix reviewer's root-cause trigger, moved to push time. New step after 'pr-body': enumerate the commits in $(git merge-base origin/main HEAD)..$(the branch's own remote head ref, via prepr's pr_head_ref — never @{u}, step 7b's rule), call gh api repos/<repo>/commits/<sha>/check-runs per pushed commit with pr-contract.yml's exact key (status completed, conclusion failure, check-run name != pr-contract, sort -u), and pass each red name to the SAME body check pr-contract uses, one --red per name, so one implementation decides 'does the body answer it', not two. Refuse when any red name is unanswered; say skip (never refuse) when gh is absent, the token is unset, no commits are pushed yet, or no commits have check-runs — the arm covers exactly what it can see and prints that boundary. Do NOT copy the nightly-status/delivery-status exemption: it already lives in policy_lint's --pr-body machinery, which the --red flags feed. Extend --self-test with offline check-runs fixtures under .claude/workflows/fixtures/: red-in-ancestry unanswered refuses (failing first), answered passes, no-reds passes, unpushed-head skips. pr-contract re-executes prepr: the arm must be local-only-deterministic in CI (skip line), like PREPR_SKIP_CLOSURES. No policy-file edit — defect-root-cause.md already prefers this detector. Body closes #1860 with the re-measurement command node .claude/workflows/policy_lint.mjs --stats --since <tag>.",
  "resume": {
    "stage": "not-started",
    "branch": "fix/r9-fr-2",
    "commit": null,
    "last_step": null,
    "next_step": "failing self-test fixture first, then the arm, then the null controls",
    "note_file": "handoff/round9/fix/resume/FR-2.md on fix/r9-fr-2",
    "review_branch": null,
    "review_note_file": null,
    "plan": null,
    "log": null,
    "pickup_cloud": null,
    "pickup_local": null,
    "note": null
  }
}
```

```json
{
  "group": "R9-FR-3",
  "lane": "FIX",
  "issues": [1825],
  "fixes": [],
  "findings": [],
  "covers": [],
  "class": null,
  "wave": 2,
  "fixerModel": "sonnet",
  "reviewerModel": "sonnet",
  "effort": "medium",
  "fixture": null,
  "owner_gate": null,
  "rca": false,
  "barrier": null,
  "barrier_prototype": null,
  "blocked_on": [],
  "after": [],
  "brief": "tvofi, 2026-10-04 (pre-study R9-FR-1): #1825 — the stats counter folds verdict-class sibling families so the threshold sees the family, not only the exact id. In .claude/workflows/policy_lint.mjs --stats, declare a family map in one place near the census (mutation: [mutation, mutation-vacuous, mutation-survivor]; environment: [environment, seat-environment]), print one family row per family beside the id rows, and key the would-open logic on families as well as ids. Census lines stay byte-shape-identical (they are the raw record and friction_issues.mjs reads them — verify that consumer in this PR and keep its input contract). Measured hole this closes: the since-v6.7.14 window has the mutation family at 4 distinct PRs (threshold 3) while every exact id is below (2/1/1) — the counter opens nothing while the family recurs. Acceptance under fixtures/policy-loop: a window whose family crosses threshold while no id does asserts the family would-open line and no id line; its null control, a window where nothing crosses, asserts nothing opens. No policy-file edit. Body closes #1825 with the re-measurement command.",
  "resume": {
    "stage": "not-started",
    "branch": "fix/r9-fr-3",
    "commit": null,
    "last_step": null,
    "next_step": "acceptance fixture failing first, then the family map, then the null control",
    "note_file": "handoff/round9/fix/resume/FR-3.md on fix/r9-fr-3",
    "review_branch": null,
    "review_note_file": null,
    "plan": null,
    "log": null,
    "pickup_cloud": null,
    "pickup_local": null,
    "note": null
  }
}
```

## 5. Summary table

| issue | class / id | W13 / W14 / W15 (PRs) | remedy | verdict | what binds |
|---|---|---|---|---|---|
| #1860 | root-cause-unanswered | 6 / 8 / 1 | prepr ancestry red-check arm | **FOLD (R9-FR-2)** | instrument PR, ~1 fixer-day; plumbing exists in pr-contract.yml + --red |
| #1825 | mutation family | 6 / 4 / 2 (cumulative windows) | family folding in the counter | **FOLD (R9-FR-3)** | instrument PR, ~0.5 fixer-day; restores measurement, removes no rework itself |
| #1881 | harness | 0 / 3 / 2 | none — verify FIXED | **CLOSE BY RE-TRIAGE** | W15 closed under step 18 at 2/2 < 3 |
| #1807 | head-moved | 7 / 4 / 2 | ruleset push refusal on handoff/* | **REFUSE** | measured moves are main-syncs the delivery protocol requires; ruleset = tvofi's hands; declining |
| #1826 | fixer.md | 3 / 2 / 2 | simplification pass | **REFUSE** | heterogeneous, no step ≥3 in a window; named contradiction already fixed (0b61a09bd); owner review + caps |
| #1855 | gate-scoping.md | 5 / 3 / 1 | instrumented lease/queue | **REFUSE** | 0 of 10 declarations name the lease; declining; remedy answers nothing measured |
| (new) | environment family | 3 / 2 / 0 | none | **REFUSE to fold** | at 0 in the closed window; standing remedies already in briefs |

## 6. What this study did not do

No fix PRs (roster contract). The #1881 close and the four refusals are
dispositions for the orchestrator to apply on #201 and the issues; this seat
posts nothing to GitHub itself beyond its handoff branches.

## 7. Figure index — every figure's command

Run in `/Users/timmalmstrom/hpo-seats/r9-fr-study/wt` at `1913f0dd7`:

1. Sweeps (all §1 tables): `GITHUB_TOKEN=$(gh auth token) node .claude/workflows/policy_lint.mjs --stats --since v6.7.13` (and `v6.7.14`, `v6.7.15`, `v6.7.16`); rc=0 each; `GAP: 0` each; raw outputs in `scratch/fr-study/sweep-v6.7.1{3,4,5,6}.txt` under the seat scratch.
2. Null (no token): `node .claude/workflows/policy_lint.mjs --stats --since v6.7.15` with `GITHUB_TOKEN` unset — skip line and refused histogram, quoted in the preamble.
3. Merge counts per tag pair: the tool's own `STATS:` lines are the figure of record (56 / 25 / 11 / 0 over the four since-tags; `GAP: 0` recovered-from-subjects each run), and per-window merges derive from them (31 / 14 / 11). Cross-check by merge subjects: `git log --oneline <tag>..<tag> --merges | grep -c '#[0-9]'` gives 40 / 14 / 12 — it disagrees on the two windows carrying re-merge and record-merge shapes (e.g. `Merge commit '<sha>' into fix/...` subjects), which is why the enumeration uses the commit-to-PR API map, not subjects. The stats tool's counts, not the subject grep, are used everywhere in §1.
4. W15 verdict comments (§1 baseline unit, §2 classification): `gh api repos/tvofi/heatpump_optimizer/issues/<n>/comments --jq '.[].body'` over the W15 PR numbers, grepping `^Fix review:`.
5. Head-moved cause classification (§3 #1807): `git log --format='%h %an %s' 7162a2d88e90b3619bf504bce921856c62c4a4ac..c983b9778924a0eefca57e7bb8fbb221462a7570` → `c983b9778 Merge origin/main into handoff/r9-f10-13` (+ wip commits), i.e. a main-sync, not a post-freeze feature push.
6. Friction declarations (§3 content reads): `gh api repos/tvofi/heatpump_optimizer/pulls/<n> -q '.body'` with the `## Friction` section extracted by awk, over the W13/W14/W15 PR numbers from the tag-pair logs.
7. Mandate check (§3 #1826): `gh api repos/tvofi/heatpump_optimizer/issues/201/comments --paginate --jq '.[].body' | grep 5951564627` → "A mandate comment (5951564627, scope all, 2026-10-02T12:00Z to 2026-10-09T12:00Z) counts at the budget-raise gate once #1843 merges."
8. Existing enforcement (§2): `.github/workflows/pr-contract.yml` "List the red checks at this head" step and its `--red` wiring; `git log --oneline -S "List the red checks at this head" -- .github/workflows/pr-contract.yml` → `b6e30297d` (R8-I3).
9. File sizes: `wc -l` on `.claude/rules/defect-root-cause.md` (153), `.claude/rules/gate-scoping.md` (61), `tools/audit/briefs/fixer.md` (293), `tools/audit/prepr.sh` (1428), `tests/gate_lock.py` (846).

Per-window derivation rule (used for every W13/W14/W15 cell): W13 = since-v6.7.13 minus since-v6.7.14; W14 = since-v6.7.14 minus since-v6.7.15; W15 = since-v6.7.15. Sound because a merged PR's merge commit lies between exactly one adjacent tag pair; the one cell it cannot split (`mutation-survivor`) is marked as a union in §1.
