Part 1 of R10-AGREEMENT-BOOTSTRAP (#3100, stranded carry 35): the grader learns to accept a SHARED_GRAMMARS entry that lands before its grammar's second reader. Closes #3100. This replaces #3166's `bootstrap:` marker, which the round-1 review blocked (verdict/3166): its stale refusal reddened the second reader's pull request under the base-copy grader. Same split as R10-MACHINERY-RATCHETS part 1 (#3165) and R10-BASH-KILL-HOOK part 1 (#3168): graders first, here alone.

The rule. An ordinary disposition (`pair:`, `module:`, `identical:`, `not-a-concept:`) may end ` (awaits <path>)`. At one file such an entry is not DEAD while all of these hold: exactly one file reads the grammar; `<path>` is governance code, absent from the tree, and never on HEAD's history; and the clause landed at most 7 days before HEAD, by committer date on HEAD's first-parent line. Every failed condition reads DEAD with its own reason. Once a second file reads the grammar the entry is an ordinary two-file entry, which main's copy, the one CI pins, accepts unchanged. So the reader's pull request needs no edit to the pinned file. The spent clause is a note, never a refusal. The age bound is fatal only where the registry graded is the one HEAD commits (main's push run, a local run). A pull request that drops an expired entry is graded by the base's copy, which still holds the entry, and reads a note there. Entries without the clause read exactly as before.

Why this rule and not another:
- #3166's `bootstrap:` marker, with a stale refusal at two files. Rejected: a refusal keyed on registry content can only be cured by editing the registry, which CI restores from the base, so the reader's pull request is red (measured below).
- Accept any one-file entry. Rejected: a reader that left would no longer read DEAD, which is a steady-state bypass.
- Accept a one-file entry only in the commit that adds it (a diff against HEAD^1). Rejected: the entry would read DEAD at the next unrelated merge and on every pull request after it, until the reader lands.
- The clause as chosen keys acceptance on facts the grader measures, not on free text: whether the path is in the tree, whether it is in history, and the clause's age. It has no free-text reason to bound. A path that never arrives expires after 7 days. A path that once existed, whether copied from another entry or left behind by a reader, never qualifies.

There is no concrete entry yet. The carry is the grader capability alone: carry 35 records that "Route B avoided it" at 98b532ab1, so no grammar waits on this today. So there is no part 2 to render. #3166 (`handoff/r10-agreement-bootstrap`, the round-1 marker design) should be closed in favour of this pull request. Its saved work stays on that ref, untouched.

## Head

56905fadf1ed01a07d183daa780b7dc4eade0f26 merges origin/main 279cb497fa764f89a961d94c87e57f16176c2fcc into d3f3e326e87a5a9da5765d7206657503dfa51de3, with no conflict. d3f3e326e had itself merged origin/main 8fcaf47e1d6989b6c5f2a053aaa0f2b79c24067a into the code head dfde8a04c34047a09b3bae88f1ef0def3531b099. Main moved twice during the prepr runs, landing #3165 and #3168: policy_lint.mjs, field_coverage.mjs and two delivery rows, none of them this diff's files. The code head was cut from origin/main dfb4ce2b52fafb340e0320bc2efb870099a53884 in three commits: 82f333b9c adds the rule; 27da92651 moves the own-registry test before the age read (see Mutation proof, M10); dfde8a04c classifies the harness as an inert read of tests/harness_headers.py (`python3 tools/pr/ci_predict.py --apply-inert`). Every figure below was re-taken at 56905fadf.

## Mutation proof

Every probe keys on the message text, not on a count. Each production predicate was deleted and the self-test re-run (`node tools/policy/agreement.mjs --self-test`); all 16 mutants are KILLED, and the restored file holds 233 of 233:
- M1, the acceptance rule deleted (`if (!w)` → `if (true)`): 12 FAIL, including "two pull requests: an awaiting entry lands before its reader, and every step reads what it must".
- M2, the reader-that-left check deleted: FAIL "a reader that left is not awaited: a clause naming a path HEAD once held reads DEAD", plus the two-PR arm (step PR D).
- M3 to M8: the in-tree, governance-path, one-reader, kind, shallow and unknowable-age checks deleted. Each fails its own message-keyed probe.
- M9, the age bound deleted: FAIL "a clause past the bound reads DEAD on a registry HEAD commits".
- M10, the base-copy leniency deleted: FAIL "a clause past the bound is a note on a pull request that edits the registry, so dropping the entry is green".
- M11, the spent-clause note deleted: FAIL "a spent clause at two files is a note, never a refusal".
- M12 to M15, `headHistory`'s git reads mutated (`existed` returns null, `days` returns 0, `days` dates a clause HEAD dropped, `own` is always true, `shallow` is always false): each fails its "headHistory over real commits" probe, run in the self-test's throwaway repository.

The same mutants were also run through the harness, with real commits: M1 is BROKEN at main2 push and PR C, M2 at PR D, M9 at mainU push, and M10 at PR C. The first cut of 82f333b9c let the harness's M10 survive: the cure pull request's `-S` hit was the removal commit itself, so the age read 0. 27da92651 fixes that: the own-registry test now runs before the age, and an age HEAD's file cannot anchor is unknowable.

Failing first: the 16 new discovery probes spliced into origin/main's agreement.mjs fail 13 (215 of 228). The 3 that hold are the null controls below.

## Null control

- Arm (a), no steady-state bypass. The positive probe ("a one-file entry awaiting a reader that never existed, inside the bound, is accepted") is the null for each DEAD probe beside it: the same tree and registry with one condition flipped. A one-file entry with no clause reads `no longer spans two files`, the message unchanged.
- Arm (b), the two-PR sequence. With the same sequence and an entry that names no awaited reader (`identical:synthetic`), the arm is red at main2 push and only there. The reader's pull request without the entry on its base reads `UNREGISTERED`. Both hold at origin/main as well, so they are controls, not new behaviour.
- On the real registry, the full lane (`--py-json`) prints byte-identical output (seconds stripped) under origin/main's grader and under this head's, both over this head's tree: `RESULT divergent=0 unregistered=0 dead=0 refused=0`. The harness shows the comparison can differ: a synthetic awaiting entry reads DEAD at main2 push under main's grader and is accepted under this head's.

## Figures

- `node tools/policy/agreement.mjs --self-test`: SELF-TEST 233 of 233 probes held (origin/main: 212 of 212).
- `node dev/audit/harnesses/agreement_two_pr.mjs tools/policy/agreement.mjs 'identical:synthetic (awaits {P})'`: TWO-PR HELD, rc=0. Every step reads its expected verdict: main1, PR A, main2, PR B (graded by main2's registry), main3 and PR C are clean; PR D (the reader leaves) reads `DEAD ... which existed at <sha>: a reader that left is not awaited`; mainU (8 days on) reads `DEAD ... past the 7-day bound`.
- `node dev/audit/harnesses/agreement_two_pr.mjs <(git show e96ff8d23690b2371229d9bcf2188eda8b1af0a5:tools/policy/agreement.mjs) 'bootstrap:second reader lands in #9999'`: TWO-PR BROKEN at PR B by main2, main3 push, PR D by main3, mainU push. This is the round-1 design. PR B reads `REFUSED ... declared bootstrap but ... already read it`, which reproduces verdict/3166's two-PR simulation. PR D shows the marker bypassing DEAD for a reader that left, and mainU shows it never expiring.
- `node dev/audit/harnesses/agreement_two_pr.mjs <(git show origin/main:tools/policy/agreement.mjs) 'identical:synthetic'`: TWO-PR BROKEN at main2 push, PR C by mainU. That is carry 35's deadlock at origin/main.
- Main's copy, the way CI grades this branch: `git show origin/main:tools/policy/agreement.mjs > tools/policy/agreement.mjs`, then `python3 -I tools/policy/agreement_py.py --out <json>` and `node tools/policy/agreement.mjs --py-json <json>`: `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`, rc=0. Its `--self-test` printed SELF-TEST 212 of 212 probes held, rc=0. The file was then restored with `git checkout`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. No `*_budgets.json` is in the diff.
- `bash tools/pr/prepr.sh <this body>`: PRE-PR rc=0 at 56905fadf (gate mode `MODE: SCOPED`, claim files byte-identical to origin/main, agreement lane `AGREEMENT ok`).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`; the one it runs, `PYTHONPATH=tests/hastub python3 tests/entities.py`, printed `ALL 2592 ENTITY CHECKS PASSED`, rc=0.
- Claim files, VERSION, the manifest version and the RELEASE_NOTES.md heading: none is in `git diff --name-only $(git merge-base origin/main HEAD)...HEAD`, which lists only `tools/policy/agreement.mjs` and `dev/audit/harnesses/agreement_two_pr.mjs`.

## Red checks

none at this head: no CI has run on a handoff ref. The predecessor head #3166 e96ff8d23690b2371229d9bcf2188eda8b1af0a5 carries `codeql / Analyze (python)`, cancelled at the runner after about 45 minutes in query evaluation, and `gate`, failed only on that cancellation. The cancelled job was not re-run, so it is a runner cancellation on a diff that touches no Python. The cheaper detector: none exists. A runner cancellation is not a defect a check could catch earlier, so no countermeasure is owed. This pull request supersedes that head.

## Forward-carry

- Carry 35, the bootstrap deadlock of a shared grammar under a pinned grader: built in this diff as the `(awaits <path>)` clause. There is no part 2: no grammar waits on an entry today. Carry: dismissed: built in this diff, nothing left.
- The reverse direction is still a deadlock. A pull request that removes the second of two readers of a registered grammar reads DEAD under the base copy, and dropping the entry in the same pull request does not help, because CI restores the registry from the base. Measured by this harness at origin/main: `PR C by mainU` reads `DEAD ... no longer spans two files` with `identical:synthetic`. The same would hold for any two-reader entry that loses one. This pull request's leniency covers only the age bound. A general rule (DEAD fatal only where the registry graded is HEAD's own) would cover it, but it is wider than this group's ruling. Lands in group R10-AGREEMENT-BOOTSTRAP of dev/programme/rosters/wave-r10-groups.json. Carry: R10-AGREEMENT-BOOTSTRAP

## Friction

- fixer: contradiction: the dispatch asks for each verified step to be pushed fast-forward only to `refs/heads/handoff-wip/r10-agreement-bootstrap`, which holds round 1's 85b9b7c76. A part-1 branch cut from origin/main cannot fast-forward it, so no step was pushed there before the handoff refs. Carry: R10-AGREEMENT-BOOTSTRAP
