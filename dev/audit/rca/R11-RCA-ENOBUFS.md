# R11-RCA-ENOBUFS: Node git readers kept the 1 MiB default buffer while the tree listing grew past it

Root-cause seat beside the hotfix `fix/hotfix-brief-lint-maxbuffer` (#3840, code head
`54700c2fe4`, test-first commit `0d40b70c9d`). It runs beside that fix and lands no code.
Measured at `origin/main` `4ebd430fbf` on 2026-11-21. The prototype and its runs are outside the
tree, in `hpo-orch/r10s6/r11/proto/RCA-ENOBUFS/` (`buffer_scan.mjs`, `runs.txt`).

## 1. The defect, reproduced

Node's `execFileSync` stops a child at `maxBuffer`, and the default is 1,048,576 bytes. Past it
the call throws `spawnSync git ENOBUFS`. At `origin/main` three git readers in `tools/policy/`
set no `maxBuffer`:

- `brief_lint.mjs` `treeListing` (line 116), which runs `git ls-files` or `git ls-tree -r --name-only <rev>`;
- `brief_lint.mjs`'s `git` helper (line 76), which serves `refFiles`, `assertGrepExcludeBounded` and the `git grep -l` reads;
- `agreement.mjs`'s `git` helper (line 43), which serves `governanceCode` and `mergeSubjectGuard`'s listing.

These are the byte sizes of `git ls-tree -r --name-only` at each commit:

| commit | listing bytes | under 1,048,576 |
|---|---|---|
| `2ab3a56582` (#3822's last green head) | 1,030,967 | yes |
| `4ebd430fbf` (`origin/main`) | 1,033,586 | yes |
| `89ec15b79b` (#3822 head, finder box D3-u1a) | 1,074,652 | no |
| `4b0f3eb96a` (#3824 head, finder box D3-u1c) | 1,069,422 | no |

Each PR added about 40 KB of listing, which crossed the cap. Neither PR touches the readers.
In CI run 44939097064 (#3822 at `89ec15b7`), `--log-failed` holds 58 `ENOBUFS` lines across
six jobs: `tests / briefs` (39), `governance / env-matrix` (7), `governance / policy-docs` (4),
`governance / instrument-self-tests` (4), `governance / wave-script` (2) and
`pr-contract / pr-contract` (2). The hotfix's own finder harness gives the same split: at the
base, main lists fine and both PR heads throw `ENOBUFS`; at `54700c2fe4` all three list.

## 2. Named cause

**Each git reader carried its own `execFileSync` options, and nothing tied them to the size of
what they read.** The 64 MiB cap already existed in two places: `policy_lint.mjs`'s `git` helper
since #608 (2026-09-07) and `counts.mjs`'s since #672 (2026-09-09). It was a per-call option
that each new helper had to restate, and three helpers did not.

Measured at each helper's introduction:

| reader | introduced | listing then | share of 1 MiB |
|---|---|---|---|
| `brief_lint.mjs` `git` | 2026-09-04 (`0b42121411`) | 17,162 | 1.6% |
| `agreement.mjs` `git` | 2026-10-02 (`282731eaed`) | ~164,275 (10-01) | 16% |
| `brief_lint.mjs` `treeListing` | 2026-11-05 (`64fd552732`) | 564,030 | 54% |

The first-parent listing on main grew from 20,402 bytes (2026-09-07) to 1,033,586
(2026-11-21). That is 421 KB from 11-08 to 11-21 (32 KB a day) and 288 KB in the last six days
(48 KB a day). `tests/mutation_ledger/` is 552,886 bytes of it (53%) and `dev/audit/` is
356,425 (34%). The product (`custom_components/heatpump_optimizer`) is 5,989.

**The reported cause is the right one, and it reached one site more than the proposal named.**
`PROPOSAL-brief-lint-treelisting-maxbuffer.md` named `treeListing` only. The hotfix's sweep added
the two `git` helpers. `refFiles` runs with `allowFail`, so on an overflow it would have returned
a silently empty listing rather than a red. That is the more dangerous reach, and the shared
`gitRead` closes it.

## 3. Process state: (d)

**The process was sound and its precondition changed underneath it.** When each reader was
written, the default buffer held its input with room to spare: 1.6% and 16% of the cap for the
two `git` helpers. `treeListing` started at 54%. No rule, role contract or check names
`maxBuffer`: `git grep -il maxbuffer` over `dev/governance`, `.claude/rules`, `CLAUDE.md` and
`RELEASE_NOTES.md` returns nothing. The input then grew about 60-fold, mostly from round
artefacts (mutation ledger slabs, audit round evidence), and nothing measured the margin.

Why the other states do not fit:
- **Not (a):** "no process existed" would make the countermeasure a new rule. But the default was
  a correct choice at 17 KB. What broke was the size it assumed, and nothing noticed that size
  change. That is (d).
- **Not (b):** nothing required a cap, so there was nothing to disobey. The two guarded helpers
  are earlier authors' local choices, not a rule that later authors skipped.
- **Not (c):** no check of buffer headroom ran and misjudged.

Following `defect-root-cause.md` for (d), the countermeasure has to make the process notice its
own precondition. The hotfix does most of that by deletion. `counts.mjs` now exports `gitRead`
with `GIT_MAX_BUFFER`, and the three private option sets route through that one unit. The cap is
now one constant that a reader inherits, not something each author must remember.

## 4. Class search

- The hotfix enumerator is `git grep -nE "['\"](ls-files|ls-tree)['\"]"` over Node files in
  `tools/`, `tests/` and `.claude/`, plus a scanner over every Node `*Sync` call with no
  `maxBuffer`. The body disposes each line.
- This seat's own sweep is `buffer_scan.mjs`. In every Node file under `tools/`, `tests/` and
  `.claude/` that names `ls-files` or `ls-tree`, it lists each sync `git` call whose call text
  has no `maxBuffer`:
  - `origin/main`: 14 calls, rc 1;
  - `0d40b70c9d`: 16, rc 1 (the test-first commit adds two fixture calls);
  - `54700c2fe4`: 13, rc 1.
  - The three named readers (`agreement.mjs:43`, `brief_lint.mjs:76`, `brief_lint.mjs:116`)
    are present at the base and gone at the head.
  - The 13 calls left are not tree-sized. They are fixture plumbing in throwaway repos
    (`mktree`, `commit-tree`, `hash-object`, `update-index`), `merge-base --is-ancestor` with
    stdio ignored, `merge-tree --write-tree` (one tree id), and `git show` of
    `figure_registry.json` (848 bytes).
- `tests/card_drift.mjs`'s `git` helper has no cap. It serves only `rev-parse` and `merge-base`.
- Under `dev/audit/` (round harnesses, frozen), the uncapped readers list `ls-files tools
  .claude/workflows` (29,106 bytes) and `git log --first-parent` windows. Neither is near the cap.
- Python `subprocess` has no buffer cap, and shell pipes have none. Both are outside the class.
- History: `git log --all --grep=ENOBUFS` finds only the hotfix commit. `RELEASE_NOTES.md` names
  neither `ENOBUFS` nor `maxBuffer`. This is the first instance, and the class carries no barrier.

## 5. Cost test

**cost(defect), this instance** (wall clock; a lower bound, since #3840 is unmerged at
2026-11-21T23:35Z):

- **Pull requests reddened: 2**, #3822 and #3824, both finder-box landings on the round's
  critical path.
- **Red CI runs: 7**: four on #3822 (`c8775dec` ×3 and `89ec15b7` ×1) and three on #3824. Each
  carries six `ENOBUFS` jobs.
- **Blocked time:** each PR has been blocked from the first `ENOBUFS` job (env-matrix,
  19:17:17Z) to now, about 4.3 h each, so **about 8.6 PR-hours** and still rising.
- **Fix seat:** about 2.2 h, from the proposal (21:19Z) to the report (23:31Z). About 55 min of
  that was a full prepr that was not owed, and 45 min was a full `brief_lint.mjs` run at load ~44.
- **Total so far: about 11 wall-hours**, plus the re-runs both PRs owe after #3840 merges.

**P(recurrence)**, measured class frequency: 1 instance in the programme's history, 0 before.
The expensive shape needs a reader whose cap an unrelated PR's growth crosses, and the fix
removes both halves of that:
- Every tree-sized reader now shares the 64 MiB `GIT_MAX_BUFFER`. At the last six days' 48 KB a
  day, the listing reaches it in about (67,108,864 − 1,033,586) / 49,152 ≈ **1,344 days**. That
  is far beyond any one release cycle.
- A new uncapped reader written today fails on its author's first run, because the listing
  already exceeds 1 MiB. Its cheapest detector is its own PR's self-test, which is the same gate
  that would catch it. That is the "does not qualify" shape in `defect-root-cause.md`.

**P per release cycle ≈ 0** for the shape that cost 11 hours, so `cost(defect) × P` ≈ 0.

**cost(countermeasure), the candidates:**
1. **Delete.** Done by the hotfix: three option sets now route to one `gitRead`. No standing cost.
2. **Self-repair.** None applies. A buffer overflow cannot be retried into success.
3. **Narrow / a new refusal.** A lint refusing an uncapped sync `git` call. `buffer_scan.mjs`
   is that refusal's syntactic core, and its **null control fails**: on the healthy head it
   still fires 13 times. A gating form would need argv classification, or an allowlist of 13
   call sites that every fixture edit must maintain. The standing cost is per-edit maintenance
   plus about 1 s a run. It protects against a shape whose own PR's first run already catches it.
4. **A headroom sentinel.** A test asserting `listing < GIT_MAX_BUFFER / k`. This is the
   precondition-noticing form that (d) asks for. It would have warned on 2026-11-19 at 903,376
   bytes (86% of 1 MiB). Against a 64 MiB cap it buys nothing for about 1,300 days.

## 6. Decision: recorded refusal

No countermeasure beyond the hotfix's shared `gitRead`, which is the delete rung and addresses
state (d) by making the cap one inherited unit. Rungs 3 and 4 fail the cost test: the standing
cost is above zero and `cost(defect) × P(recurrence)` is about zero per release cycle.
`buffer_scan.mjs` stays a prototype for class sweeps and is not proposed as a gate. Its null
control is the evidence that a syntactic form cannot gate without an allowlist.

**Revisit trigger:** reopen rung 4 if the listing on main passes 16 MiB (25% of
`GIT_MAX_BUFFER`), or if a second `ENOBUFS` from any reader reaches a PR it did not touch.

**Forward-carry for the planner** (`finding-propagation.md`): the size driver of the listing is
`tests/mutation_ledger/` (53%) and `dev/audit/` (34%). Every tree-wide git read pays for them,
`brief_lint.mjs`'s per-symbol `git grep` included (about 45 min a full run at load ~44, per the
hotfix report). That is a D9 or D13 question for the round's plan, not part of this fix.

No `bugclasses.json` entry: one instance and no class. No policy file is edited.
