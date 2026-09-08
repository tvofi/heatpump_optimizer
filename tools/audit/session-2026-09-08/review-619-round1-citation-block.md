Worktrees removed, main tree untouched at `785963e`, clean.

---

`Fix review: blocked a5475033 other: four of the five "repointed" citations name d5d8c4a, which does not carry the file — the harnesses are at 757e164, as this branch's own tools/audit/README.md says`

## Setup

```
git worktree add --detach /tmp/wt-619r a547503336446f5bcea2d41da8c6116eaa4593d7   # rc=0
git worktree add --detach /tmp/wt-619base 785963eba411c351c96865abc3f5b6cfd93586d9
```
Both removed and pruned at the end; both were clean (`git status --porcelain | wc -l` = 0). Every file change below was a `Bash` heredoc with `assert s.count(old) == 1` first, reverted with `git checkout --` and the revert confirmed.

Commits in scope — note the third SHA differs from the dispatch prompt (`4873bbd`, not `b5b7339`; content reviewed regardless):
```
a547503  fix: an exclusion the archive emptied, and the list that had no assertion
84f63b4  docs: five citations the archive left pointing at nothing
4873bbd  docs: cut the two READMEs to what no docstring carries
```

Step 12 — head at posting time: `git fetch origin claude/repo-governance-audit-tgt5j4` → `a547503336446f5bcea2d41da8c6116eaa4593d7`. Identical to what I measured. Step 7 — the body names the same SHA. Not head-moved.

---

## THE BLOCK — the citation repair points at the wrong commit

The dispatch's own test: *"a citation repointed to an existing but wrong file is worse than a dead one."* Four of the five are that.

```
tools/audit/round2/D10/B/harness.py            head=no   d5d8c4a=no   757e164=yes
tools/audit/round2/D10/icons_harness.py        head=no   d5d8c4a=no   757e164=yes
tools/audit/round2/D10/check_rules.py          head=no   d5d8c4a=no   757e164=yes

python harness files under tools/audit/round2/D10/:
  a547503    0
  d5d8c4a    0        <- the SHA this branch repointed to
  757e164    6        <- audit-round2-evidence
```

The executable harnesses were deleted from `main` at `72a03f8` ("The round-2 harnesses move to a tag"), long before `d5d8c4a`:
```
$ git log --all --oneline --diff-filter=AD -- tools/audit/round2/D10/B/harness.py
72a03f8 The round-2 harnesses move to a tag, and the judge verdicts get committed at last (#311)
bc6efe4 Round-2 D10: the full quality-scale pass ... (#219)
```
`d5d8c4a` carries `round2/D10/` — 31 files: `REPORT.md`, `RESULTS.json`, `VERDICTS.md`, `PANEL.md`, `check_rules.out`, `judge/`, `coverage/` — **reports and outputs, zero harnesses.**

The tree contradicts the repoint in two places, one of them changed by this very branch:

- `tools/audit/harnesses/README.md` (untouched, at head): *"Round 2's **executable** harnesses were archived earlier and separately, at `audit-round2-evidence` (`757e164`)"*.
- `tools/audit/README.md` (rewritten by commit `4873bbd` in this PR): *"the round-2 numbers were recorded at `c398fc84`, archived at `de668be`, and are **runnable** at `757e164`, which is where `audit-round2-evidence` points today."*

So commit `84f63b4` sent four citations to `d5d8c4a` while commit `4873bbd` on the same branch states that `757e164` is where they run. Verified: `git rev-parse audit-round2-evidence^{commit}` = `757e164d0edc7016e5d00723d911659ea88fea2d`.

The sentences around them are now false, not merely unresolvable:

| citation | text at head | true at `d5d8c4a`? |
|---|---|---|
| `tests/config_flow_steps.py:354` | "Same shape as `tools/audit/round2/D10/B/harness.py` **at d5d8c4a**" | no — file absent |
| `tests/config_flow_steps.py:420` | "exactly what `tools/audit/round2/D10/B/harness.py` **(at d5d8c4a)** ... do" | no — file absent |
| `quality_scale.yaml:4` | "**harnesses:** `tools/audit/round2/D10/` **at d5d8c4a**" | no — directory exists, holds 0 harnesses |
| `quality_scale.yaml:106` | "harness `tools/audit/round2/D10/icons_harness.py` **at d5d8c4a**" | no — file absent |
| `.claude/workflows/web-fix-wave.js:151` | "e.g. `.claude/workflows/wave-ux-groups.json`" | **yes — correct** |

Fifth one verified good: `wave-1b-groups.json` ABSENT at head, `wave-ux-groups.json` present, sentence true.

This is worse than the dead state it replaced. A reader who runs `git show d5d8c4a:tools/audit/round2/D10/B/harness.py` gets "path does not exist"; a reader who takes the citation at face value concludes the harness was deleted outright rather than moved to a tag that still runs it. The PR's own "Limits" section says *"Each now names a path that exists"* — for four of the five, it does not.

### Exact replacements I would accept

`tests/config_flow_steps.py:354`
```
# Same shape as tools/audit/round2/D10/B/harness.py at 757e164, so what this pins is
```
`tests/config_flow_steps.py:420`
```
    tools/audit/round2/D10/B/harness.py (at 757e164) and tests/entities.py do.
```
`custom_components/heatpump_optimizer/quality_scale.yaml:4`
```
# harnesses: tools/audit/round2/D10/ at 757e164). Updated as fixes land.
```
`custom_components/heatpump_optimizer/quality_scale.yaml:106`
```
      harness tools/audit/round2/D10/icons_harness.py at 757e164). #558 D4 added state
```
`.claude/workflows/web-fix-wave.js:151` — leave as landed.

(`at audit-round2-evidence (757e164)` is equally acceptable; the bare SHA matches `harnesses/README.md`'s own instruction to cite the SHA, not the name.) Re-verify after editing with `git cat-file -e 757e164:<path>` per citation — that is the check `84f63b4` did not run.

---

## Everything else I drove, and it holds

### The exclusion fix — mutation matrix, driven myself

`node --check .claude/workflows/brief_lint.mjs` → rc=0 before every run.

| state | rc | line |
|---|---|---|
| null control (unmodified head) | **0** | `EXCLUDE ok: 1 symbol-search exclusion(s), each naming a prefix the tree has, none of the load-bearing ones dropped` |
| `[':!.claude', ':!tools/audit/round2']` | **1** | `EXCLUDE VACUOUS: [":!tools/audit/round2"] in SYMBOL_GREP_EXCLUDE match no tracked file...` (ceiling) |
| `[]` | **1** | `EXCLUDE VACUOUS: SYMBOL_GREP_EXCLUDE has lost [":!.claude"]...` (floor) |
| `[]` **and** `FLOOR = []` (ceiling only) | — | `EXCLUDE ok: 0 symbol-search exclusion(s)` ← **the ceiling cannot see an empty list** |
| `assertGrepExcludeBounded` → early `return 0`, dead prefix restored | **0** | *silence* — no EXCLUDE line at all |
| `['.claude']` (`:!` dropped → pathspec becomes an *include*) | **1** | floor fires |

The witness row reproduces: with the assertion neutered and the dead prefix back, `brief_lint` is rc=0 and prints nothing. That is the state `origin/main` is in. The assertion is load-bearing, not decorative.

**Why an empty list fails on the floor and not the ceiling — confirmed, not assumed.** Row 4 is the control: with the floor emptied too, the ceiling prints `EXCLUDE ok` on a fully vacuous configuration. `dead = SYMBOL_GREP_EXCLUDE.filter(...)` over `[]` is `[]`, so `if (dead.length)` never fires. That is exactly the reason the body gives.

One honest correction to the body's framing: at this head the empty-list mutant is caught by **two** detectors, and one of them pre-existed this PR. Row 3's full output also shows
```
FIXTURE VACUOUS: 931dffe acceptance pins missing:
  [W1-G9] symbol: wood_share_vec_parity
```
— the `wave-1b-931dffe.json` acceptance already pins a symbol that only resolves when `.claude` is excluded. The floor is still worth having (it names the failure directly and survives a change to that fixture's symbols), but "a ceiling alone is half the answer" is half true here: the other half was already covered, incidentally.

### Attacking the ceiling's predicate — 31 pathspec forms against git's real semantics

Probe: `predicateSaysDead(e)` verbatim from the PR vs ground truth `git ls-files -- . <e>` dropping nothing.

```
pathspec                              predicate  git-truth  verdict
:!.claude                             false      false      AGREE
:!tools/audit/round2                  true       true       AGREE
:!tools/audit          :!tools/audit/ false      false      AGREE
:!tests/README.md      :!VERSION      false      false      AGREE
:!tests/READ                          true       true       AGREE   <- partial path segment
:!tools/audit/roun                    true       true       AGREE   <- partial path segment
:!tools/audit/round2/*                true       true       AGREE
:(exclude)tools/audit/round2          true       true       AGREE
:!VERSION/   :!docs/HANDOVER.md/      true       true       AGREE
:!.CLAUDE    :!nonexistent-dir        true       true       AGREE
:!*.md                                true       false      FALSE POSITIVE (fail-closed)
:!tests/*.py                          true       false      FALSE POSITIVE (fail-closed)
:(exclude).claude                     true       false      FALSE POSITIVE (fail-closed)
:(exclude,icase).CLAUDE               true       false      FALSE POSITIVE (fail-closed)
:!./.claude  :!/.claude  :!:.claude   true       false      FALSE POSITIVE (fail-closed)
:!.claude/*                           true       false      FALSE POSITIVE (fail-closed)
```

**Answering the dispatch's question directly: I found no "dead but passes" form.** The partial-path-segment case the dispatch flagged agrees with git in both directions, and it must: `f.startsWith(prefix + '/')` can only be true when `prefix` is a complete run of path components, which is precisely git's literal-pathspec rule. Every disagreement is in the safe direction — a glob or long-form `:(exclude)` entry would be reported dead and turn the gate red, visibly, rather than pass while excluding nothing. The predicate is exact for the literal-prefix forms the list actually uses, and constrains the list to those forms.

### Attacking the floor

The body's stated limit is real, and I confirmed it: adding a live `:!docs` to `SYMBOL_GREP_EXCLUDE` only → rc=0, `EXCLUDE ok: 2 symbol-search exclusion(s)`. Unprotected, exactly as admitted.

**Is the limit worse than stated? In one direction yes, in another no.**
- *Better than implied*: the floor cannot rot silently. `FLOOR ⊆ EXCLUDE` is enforced and every `EXCLUDE` entry must be live, so transitively every floor entry is live. A dead floor entry is impossible without the ceiling firing first.
- *Worse than stated*: deleting an entry from **both** lists in one diff passes green (row 4 above), and the body frames the floor as "records what the check cannot lose" without noting that the record itself is deletable in the same commit. Both cases are one-diff-visible and the printed count (`0 symbol-search exclusion(s)`) does not hide it. The admission is honest; I would call the framing slightly generous, not misleading. Not a block.

### Does the exclusion change move any finding? Body's claim confirmed

Body: *"the dropped pathspec excluded nothing, so `brief_lint` reports the same errors on both fixtures."* Driven:
```
$ diff <null control> <dead prefix restored>
53c53
< EXCLUDE ok: 1 symbol-search exclusion(s), ...
---
> EXCLUDE VACUOUS: [":!tools/audit/round2"] ...
```
One line, and it is the new assertion's own. `TOTAL: 0 error(s) across 4 file(s)` and `FIXTURE ok: 13` identical on both sides. Claim verified.

**But base→head is not flat, and the body does not say so.** `brief_lint` at `785963e` vs at `a547503`:
```
20c20
< WARNING [W1-G5] path:line: tools/audit/README.md:244-255: no anchor text extracted...
---
> ERROR   [W1-G5] path:line: tools/audit/README.md:244-255: line 244 is past end of file (216 lines)
33c33
< -- 12 error(s), 4 warning(s)      >  -- 13 error(s), 3 warning(s)
```
Cause is the README cut (250 → 215 lines), not the exclusion change. It stays green (13 ≥ 9 required, and `tools/audit/README.md:244-255` is not among `REQUIRED_931DFFE`'s nine pins), so no gate moves. Reporting it because the body's "No finding changes" reads broader than what it measured.

### The README cuts — spot-checked well past three scripts

Claim tested: everything deleted is carried by a docstring or an in-file comment.

| deferral the new README makes | verified |
|---|---|
| `validate.py`, `edge.py`, `plan_view.py` "carry no docstring" | **true** — `ast.get_docstring` returns `None` for all three, and the README keeps their full descriptions |
| `stress.py`'s budget rationale "lives in the `#:` comments" | **true** — 306 `#:` lines; every named fact present, including the verbatim phrase `property of the recording`, `STRESS_SOLVE_CEILING_MS` (2), `STRESS_DETECTION_TARGET` (1), `2.3` (5), `#286` (4), `#287` (8), `OMP_NUM_THREADS` (3) |
| `env_drift.py`: "the comment block above `FIXTURE_DIR` carries each level's definition ... and the measurement that decided each cut" | **true** — read it; carries levels 1/2/3, the `2ab9b84` measurement (34 fixtures / 14461 leaves), the "fires on 6" vs "fires on 9" cut, the `[]` collapse, the residual gap. More detail than the README had |
| `env_drift.py` docstring "names the five, and states the claim rules ... and the refusal of a ref that resolves to `HEAD`" | **true** — all five fixtures named; `claims-for:`, inherited-list refusal, `--claims-only`, stale vs not-evaluated, cache key; `HEAD` refusal at docstring L89 and `SELF-COMPARISON:` at L1643 |
| `golden.py`'s `resolve_mode` / `assert_invariants` docstrings | **true** — `resolve_mode` gives all three rules incl. why unset means `drift`; `assert_invariants` gives "pins *possibility*", "runs on both record and check" |
| `closure.py` docstring: how a record is taken, which two instruments, why a hand-kept table is untrustworthy | **true** — audit hook + `sys.modules`, and verbatim "A hand-maintained table would rot on the first refactor and nobody would notice" |
| `closure.py`'s `INERT` / `GATE_FILES` / `SLOW_GATED` tuples "each with its reason beside it" | **true** — all three present with multi-line reasons, plus `INERT_EXCEPT` |
| `ha_contract.py` "disposition constants near the top state what each disposition obliges" | **true** — `FAITHFUL`/`DIVERGENT`/`UNVERIFIED`/`SIMPLIFIED`/`HOLDER` each with its obligation inline, plus `Entry.__doc__` on `absent` |
| `run.sh`'s `UNWIRED TEST` loop "with a reason on each entry" | **true** — read the `case` block; every one of the 8 exclusions carries its reason |
| `card_drift.mjs` header: what it renders, differential rationale, claim file | **true** — 38-line header, all three, plus the `docs/img` staleness warning |
| `backtest.py` docstring "names its three baselines" | **true** — always-on / night tariff / greedy cheapest hours |
| `rolling.py` — the deleted "drives the coordinator's own estimator, not a copy" | **true** — `tests/rolling.py:109-111` verbatim |
| `optimality.py`, `features.py`, `entities.py` bullets deleted wholesale | **true** — each docstring covers the deleted content (entities' four catches; optimality's floor/challengers/margin/two-zone gap; features' mechanism-vs-outcome rationale) |

**Two things genuinely not in any docstring**, and I am calling them noted-not-blocking rather than silently passing them:
- `features.py`'s enumeration of the twelve feature modules (staleness watchdog … virtual battery). The docstring says "the v2.8.0 feature modules" without listing them. Every term is still greppable in the file (`staleness` 14, `defrost` 143, `virtual battery` 3, `away` 118 …) except `price shape` and `comfort learning`, which appear under other spellings.
- `card.mjs`'s "seven series, entity discovery by `plan_kind`, the expanded dialog, legend scaling, reason codes in the tooltip, shading of estimated prices, what-if debounce". The new README makes no deferral claim for this one. All terms are in the file (`plan_kind` 12, `debounce` 3, `legend` 139, `tooltip` 43).

Both are inventories of a file's own assertions, where the file is the authority and cannot go stale against itself; neither is a fact about the world that now lives nowhere. That is a judgement call and it is mine, stated so a later seat can disagree with it.

`tools/audit/README.md` — the removed known-bad entries are proven, not asserted. I re-added one:
```
ERROR [known-bad] entry no longer fires: citations|tools/audit/README.md|path `tmp/plandata.json`:
  not in the tree, and no tag SHA is. It was fixed, so delete the entry; the list may only shrink.
KNOWN-BAD: 13 of 14 recorded defect(s) still present     rc=1
```
So both deletions were mandatory and both underlying defects are genuinely gone.

**One thing in that file is a rule change, not a cut, and the body does not name it.** Base: *"The judge rejects a timing or memory RESULT whose `thread_factor` exceeds 1.05 **or whose `load1` exceeds 1.5**."* Head: *"`load1` is quoted, not gated."* The base file also carried a later section saying `load1 <= 1.5` is unattainable, so the file contradicted itself and the head resolves it in favour of the measured section — the right direction. But `tools/audit/README.md` is named in `CLAUDE.md` and is therefore policy, and "this changes what a seat must do" is the honest description. It belongs in the body under its own heading, not inside "cut to what no docstring carries". Not the block; surfacing it so the owner sees it before merge.

### The delta broke nothing

```
policy_lint.mjs            rc=0   TOTAL: 0 error(s) across 35 policy file(s)
                                  FIXTURE ok: 37 error(s) hold 57 pins across 7 check classes
                                  KNOWN-BAD: 13 of 13 recorded defect(s) still present, 25 occurrences
policy_lint_mutants.mjs    rc=0   MUTANTS ok: [checkIndex, checkDuplicates, checkBudgets,
                                  coverageOverTree, namedDocsOverTree, orphanCapsOverTree, checkProvenance]
rules_sync.mjs --check     rc=0   RULES-SYNC ok
brief_lint.mjs             rc=0   TOTAL: 0 across 4; FIXTURE ok 13 / FIXTURE ok 9; GUARD ok; EXCLUDE ok
check-wave-script.mjs      rc=0   26 passed, 0 failed;  scope 4 roster(s), 59 group(s), 4 distinct stage(s)
policy_lint.mjs --hooks    rc=0   TOTAL: 0 across 35
bash tools/audit/prepr.sh  rc=0   every step ok, MODE: SCOPED, "no version edit", claim files byte-identical
tests/structure.py         rc=0   STRUCTURE RATCHET PASSED
tests/entities.py          rc=0   ALL 1112 ENTITY CHECKS PASSED
```
rc read from the command itself, never through a pipe.

Three-dot against the merge base `785963e` (`git merge-base origin/main a547503` = `785963e`):
```
VERSION, manifest.json, RELEASE_NOTES.md          empty
tests/golden/claimed_drift.txt, card_claimed_...  empty  (byte-identical to origin/main)
.claude/workflows/policy_budgets.json             empty  (no cap moved)
```

Conflict — measured, not read off a status field. `python3 tests/env_drift.py --install-merge-driver` → `MERGE-CLAIM: already-installed`; `git merge-tree --write-tree origin/main a547503` → **rc=0**, tree `30027305...`, stderr empty. No conflict on any path.

`## Red checks: none` — **accurate**, read from `get_check_runs`, not the body. 21 runs: 16 success (`fast (3.13)`, `fast (3.14)`, `browser`, `typing`, `briefs`, `closures`, `closure-scope`, `wave-script`, `policy-docs`, `pr-contract`, `hassfest`, `validate-hacs`, `CodeQL`, 3× `Analyze`), 5 skipped (`slow`, `nightly-ha`, `recheck-gate`, `closures-autofix`, `claims-autofix`). No `defect-root-cause` trigger; nothing owed.

Forward-carry `none` — consistent with the diff; nothing here narrows a later stage, refuses a technique or removes an option.

### Two body numbers I could not re-derive (contract step 8)

- **`fragments_sync --check` ok.** There is no such script. `ls .claude/workflows/` at head and at base shows no `fragments_sync.mjs`, and `git grep -l fragments_sync` returns exactly one file at both ends — `docs/decisions/0003-enumerate-what-you-may-ignore.md`, a prose mention. The command in that null-control line cannot have run. (The dispatch prompt asked me to run it too and inherited the same error.)
- **`ALL 1114 ENTITY CHECKS PASSED`.** I measure **1112** at head *and* 1112 at base. The body's figure matches neither end. Both ends pass, so nothing functional turns on it, but the number as printed is not reproducible here.

### Minor, non-blocking

`brief_lint.mjs:159` still opens *"Two directories are excluded from 'does this symbol exist anywhere':"* while the list now holds one. The paragraph below explains the deletion, so it is not wrong on the facts, only on the count in its first clause.

---

## Verdict

`blocked`. The exclusion fix is sound and its assertion is genuinely load-bearing — the mutation matrix, the ceiling-predicate attack across 31 pathspec forms, and the floor attack all hold, and I found no way to make a dead exclusion pass. The README cuts are honest: every deferral I checked resolves, and the two known-bad deletions are provably earned. The blocker is the middle commit alone: `84f63b4` sent four citations to `d5d8c4a`, a commit that carries none of them, while the same branch's `tools/audit/README.md` says they are runnable at `757e164`. Fix those four lines as written above, re-verify each with `git cat-file -e 757e164:<path>`, and this is a merge — nothing else in the diff needs to move.