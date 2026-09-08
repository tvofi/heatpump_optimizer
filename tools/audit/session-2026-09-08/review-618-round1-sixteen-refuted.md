My three worktrees are removed (the others pre-existed this seat). The main tree is untouched and clean.

---

`Fix review: blocked b34af6b7 claims: the "sixteen" sentence I was sent to check is fully verified and correct, but this round's body edit put a new unestablished claim in ## Red checks — "strictly better for review" / "no longer an argument … it is a measurement" is a normative claim about readers that nothing measured, and the one reader datum that exists (this review) points the other way.`

## What I measured, and how

Worktrees: `/tmp/wt-618rr` @ `b34af6b`, `/tmp/wt-618e4` @ `e4a388a`, `/tmp/wt-618base` @ `6b71e85`, all detached, all removed. No `Edit`/`Write`/`MultiEdit` used anywhere; every probe is a `Bash` heredoc with an asserted `s.count(old) == 1`, `node --check`ed, and `git checkout --` restored with `git status --porcelain` verified empty after each.

### The delta is what the dispatch said

```
$ git diff --stat f20b757 b34af6b
 .claude/workflows/policy_lint.mjs | 8 +++++---
 1 file changed, 5 insertions(+), 3 deletions(-)
```
Comment-only, same parent (`095ac80`) on both, tip commit message rewritten.

### The claim, reproduced with my own harness

Control at `e4a388a`, unmodified: `TOTAL: 0 error(s) across 34 policy file(s)`, rc=0.

Probe A — folded resolve-to-ALL (`return cands` off `lowerBaseMap`): **`TOTAL: 17`**, rc=1.
Probe B — exact-case resolve-to-ALL (my own `exactBaseMapRR`, same listing, same exact-path short-circuit): **`TOTAL: 16`**, rc=1.

```
$ diff setB setA
16a17
> tools/audit/round2/JUDGE.md
```

Set B (16): `round2/BASELINE.md`, `round2/D10/BASELINE.md`, and `REPORT.md` under `D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D10/A D10/B D10/C`.
Set A (17): those sixteen **plus** `tools/audit/round2/JUDGE.md`, reported as *"named by `.claude/rules/finding-propagation.md`"* — the `judge.md` / `round2/JUDGE.md` fold collision, exactly as claimed.

**Is 16 uniquely produced by exact-case resolve-to-all?** I drove five other plausible resolvers at `e4a388a`. None gives 16:

```
C  folded, return-FIRST                       TOTAL: 2
D  exact,  return-FIRST                       TOTAL: 2
E  exact-unique-then-fold (#616's rule)       TOTAL: 0
F  folded, ALL, no exact-path short-circuit   TOTAL: 18
G  exact,  ALL, no exact-path short-circuit   TOTAL: 17
```

**Provenance, which the author did not have to guess at and neither did I.** At `118fcf2` (`#614`, the direct parent of `e4a388a`) the tree already carries `candidatesFor`: an **exact-case** basename map with an exact-path short-circuit returning **all** candidates — semantically identical to my Probe B. So the pre-fold resolver shape is in the tree one commit earlier; `lowerBaseMap` and the `SIXTEEN findings` comment both enter at `e4a388a` (`git log -S`). The honest limit: `e4a388a` is a squash of #615, so the tree cannot show the ordering *inside* it — but the claim as written ("sixteen is the count from before the fold") is about which resolution rule yields 16, and that is executed, not inferred.

**"not a number #616 moved" — stronger than stated.** `git merge-base --is-ancestor d7dc142 e4a388a` → **not an ancestor**. #616 is absent from `e4a388a` entirely, touches nothing under `tools/audit/round2/**` or `briefs/judge.md`, and therefore cannot have moved either count. The previous verdict's refutation stands and the correction is right.

**The sentence the new one attaches to also holds.** Head's rule driven on the base tree `6b71e85`: `TOTAL: 17`, all `tools/audit/round2/**`, sixteen via `REPORT.md`/`BASELINE.md` plus `JUDGE.md`.

### Cheap regression checks at head — all green

`policy_lint.mjs` → rc=0, `TOTAL: 0 across 35 policy file(s)`, `FIXTURE ok: 37 error(s) hold 57 pins across 7 check classes`. `policy_lint_mutants.mjs` → rc=0, `MUTANTS ok` (7 checks). `prepr.sh` → rc=0, every step ok including `no version edit` and `claim files byte-identical to origin/main`, `MODE: SCOPED`. `entities.py` (`PYTHONPATH=tests/hastub`) → `ALL 1112 ENTITY CHECKS PASSED`. `git merge-tree --write-tree origin/main b34af6b` → rc=0, empty stderr, no conflict (driver `already-installed`). Three-dot diff on `VERSION`, manifest, `RELEASE_NOTES.md` → empty. `## Head` names `b34af6b752f4b4926234676ed2305a8043a972e0`; live head at posting is the same.

## Why I block

The `## Red checks` `none` error is fixed — I confirm that. But the replacement introduces a new claim of the same class it was fixing.

**The complete `pr-contract` record, enumerated (Governance runs on the branch, job-level verified):**

```
head        failed run     created     failing step                          passing runs
e6230a39    34224594181    12:10:22Z   Check the body against the contract   34222678053, 34223988434
095ac806    34225039727    12:15:12Z   Check the body against the contract   34224605838, 34224815659
f20b7577    none               -                 -                           34225054910, 34225202347
b34af6b7    34225841799    12:23:52Z   Check the body against the contract   34226076506, 34226616251
```

Three defects in the new text:

1. **"The second is strictly better for review"** / "the claim below is no longer an argument from `SKILL.md`; it is a measurement". What was measured is *where* each order puts the failure. "Better for review" is about a reader, and no reader was measured. The single reader datum that exists contradicts it: I read `## Red checks` saying `none` on `b34af6b7`, read the check runs as step 11 requires, found `34225841799` red on the live head, and had drafted `blocked b34af6b7 claims` on it when your correction arrived. Push-then-edit cost this review a round-trip; the failures on `e6230a39` and `095ac806` cost it nothing. This is exactly the shape the previous verdict blocked — a causal story presented as established.

2. **"went red on each head this branch abandoned — `e6230a39` and `095ac806`"** is measurably false as a universal. `f20b7577` is also an abandoned head and has **no** red `pr-contract` (runs 34225054910, 34225202347, both success). The true statement is narrower: the two heads abandoned *under edit-then-push*.

3. **"each left exactly one failed `pr-contract` run"** is true per *transition* and false per *order*: edit-then-push ran twice and left two (12:10:22Z, 12:15:12Z), push-then-edit ran once and left one. The sentence reads as a per-order total. n=1 per order stated as a property is what the repo's own preflight `quantifiers` check asks about.

Plus an internal contradiction: the section recommends a different order, then closes three paragraphs later with *"The lever is fewer rounds, **not a different order**."* Both cannot stand.

The ordering evidence itself is real and worth keeping — I verified it: `e6230a39`'s failure created 12:10:22Z with `095ac806`'s first run 8s later at 12:10:30Z; `095ac806`'s failure 12:15:12Z with `f20b7577`'s first run 8s later at 12:15:20Z; `b34af6b7`'s failure 12:23:52Z superseded at the same SHA. That is edit-then-push twice and push-then-edit once, measured.

**The fix is body-only**: no commit, no new head, and the `[edited]` re-run passes because `## Head` already names `b34af6b`.

## The wording I would accept

Replace `## Red checks` from its first line through "…and this body says so with both runs on the record." with:

> ## Red checks
>
> **`pr-contract`, once, on this head.** Check run `102059632142` (run `34225841799`, created 12:23:52Z) failed on `b34af6b7`, reading a body whose `## Head` still named `f20b7577`; the failing step is *Check the body against the contract*. Run `34226076506` (check run `102060409786`), same job and same head, passed at 12:26:36Z after the body was updated, as did `34226616251`. Every other check on `b34af6b7` is success or skipped.
>
> **The full record on this pull request's four heads, enumerated rather than sampled** — `Governance` runs on `claude/repo-governance-audit-tgt5j4`, job `pr-contract`:
>
> ```
> head        failed run     created     passing runs
> e6230a39    34224594181    12:10:22Z   34222678053, 34223988434
> 095ac806    34225039727    12:15:12Z   34224605838, 34224815659
> f20b7577    none               -       34225054910, 34225202347
> b34af6b7    34225841799    12:23:52Z   34226076506, 34226616251
> ```
>
> Three failures across four heads, one per body-update round, each failing on the same step.
>
> **Both orders ran here, and the timings separate them.** Edit-then-push twice: `e6230a39`'s failure created 12:10:22Z with `095ac806`'s first run 8s later at 12:10:30Z, and `095ac806`'s failure at 12:15:12Z with `f20b7577`'s first run 8s later at 12:15:20Z. Push-then-edit once: `b34af6b7`'s failure at 12:23:52Z, superseded by a passing run at the same SHA. Each *transition* left exactly one failed run; per *order* the totals are two over two transitions and one over one.
>
> **What that measures and what it does not.** It measures where each order puts the failure. It does not measure which is better for a reviewer, and this body does not claim one. `f20b7577` is why the earlier universal was wrong: it is an abandoned head with no red `pr-contract`, because the order changed at that transition — the failures fall on the heads abandoned under edit-then-push, not on every abandoned head.

Then keep the **Answering the root-cause trigger** paragraph as it stands (it already names `prepr.sh` step 7 as the cheaper detector with its cost and records the no-countermeasure finding) and its closing "The lever is fewer rounds, not a different order."

If you want to keep something about legibility, this is the most I would accept, and only stated as what it is:

> One observation, not a measurement of reviewers: the fix-review seat on this pull request read `## Red checks` saying `none` on `b34af6b7`, read the check runs as `fix-review.md` step 11 requires, found `34225841799` red on the live head, and was drafting a block on it when the body was corrected. That is one reader meeting push-then-edit's failure and being misled by it — evidence against "strictly better for review", not for it.

## Observations, not blocks

- **A recommendation to future seats does not belong in a body.** "the order this body now recommends" and "Correcting S10's own reasoning" aim at `.claude/skills/steward/SKILL.md`, which `CLAUDE.md` lists as policy. Per `finding-propagation.md` a comment is not propagation; per `CLAUDE.md` a policy change needs the owner's approval before merging. If the claim were established it would need a carry into S10, not a paragraph here — and it is not established, so it should not be recommended at all.
- Outside the delta: `.claude/workflows/policy_lint.mjs` at head has no other stale "sixteen" — the only occurrences are the corrected block and the `WORDS` table (`sixteen: 16`), which is data. The `FIXTURE OVER-FIRES` message that said "sixteen" at `e4a388a` is gone at head.
- The `sixteen` correction itself would be strengthened, not weakened, by citing `candidatesFor` at `118fcf2` — the pre-fold resolver shape is in the tree at the parent commit, which turns "the count from before the fold" from a numeric coincidence into a shape the tree carries. Optional; the sentence as written already states only what was run.