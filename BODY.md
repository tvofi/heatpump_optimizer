Part 1 of R10-AGREEMENT-BOOTSTRAP (#3100, stranded carry 35): the grader learns to accept a SHARED_GRAMMARS entry that lands before its grammar's second reader. Closes #3100. This replaces #3166's `bootstrap:` marker, which the round-1 review blocked (verdict/3166): its stale refusal reddened the second reader's pull request under the base-copy grader. Same split as R10-MACHINERY-RATCHETS part 1 (#3165) and R10-BASH-KILL-HOOK part 1 (#3168): graders first, here alone.

The rule. An ordinary disposition (`pair:`, `module:`, `identical:`, `not-a-concept:`) may end ` (awaits <path>)`. At one file such an entry is not DEAD while all of these hold: exactly one file reads the grammar; `<path>` is governance code, absent from the tree, and never on HEAD's history; and the clause landed at most 7 days before HEAD, by committer date on HEAD's first-parent line. Every failed condition reads DEAD with its own reason. Once a second file reads the grammar the entry is an ordinary two-file entry, which main's copy, the one CI pins, accepts unchanged. So the reader's pull request needs no edit to the pinned file. The spent clause is a note, never a refusal. The age bound is fatal only where the registry graded is the one HEAD commits (main's push run, a local run). A pull request that drops an expired entry is graded by the base's copy, which still holds the entry, and reads a note there. Entries without the clause read exactly as before.

Why this rule and not another:
- #3166's `bootstrap:` marker, with a stale refusal at two files. Rejected: a refusal keyed on registry content can only be cured by editing the registry, which CI restores from the base, so the reader's pull request is red (measured below).
- Accept any one-file entry. Rejected: a reader that left would no longer read DEAD, which is a steady-state bypass.
- Accept a one-file entry only in the commit that adds it (a diff against HEAD^1). Rejected: the entry would read DEAD at the next unrelated merge and on every pull request after it, until the reader lands.
- The clause as chosen keys acceptance on facts the grader measures, not on free text: whether the path is in the tree, whether it is in history, and the clause's age. It has no free-text reason to bound. A path that never arrives expires after 7 days. A path that once existed, whether copied from another entry or left behind by a reader, never qualifies.

There is no concrete entry yet. The carry is the grader capability alone: carry 35 records that "Route B avoided it" at 98b532ab1, so no grammar waits on this today. So there is no part 2 to render. #3166 (`handoff/r10-agreement-bootstrap`, the round-1 marker design) should be closed in favour of this pull request. Its saved work stays on that ref, untouched.

## Head

Round 2. Code head: 2e9e217a5d90b42c12c1ef1536b490d3c2943b14 (one commit, `Find the agreement two-PR harness root with the repository helper`, on 37fa2bbb9e54aedf43d9feb24634710509837150, the round-1 PR head; handoff/r10-agreement-bootstrap-p1 at 56905fadf1ed01a07d183daa780b7dc4eade0f26 is its ancestor, so the push is a fast-forward). Handoff head: the same SHA, 2e9e217a5d90b42c12c1ef1536b490d3c2943b14. origin/main has not moved past the merge base 279cb497fa764f89a961d94c87e57f16176c2fcc, so there is no merge and the one prepr run below is the only one. Every figure was taken at 2e9e217a5d90b42c12c1ef1536b490d3c2943b14 unless it says 37fa2bbb.

## Mutation proof

The grader is unchanged (empty diff of `tools/policy/agreement.mjs` against the PR head), so round 1's 16 mutants stand as recorded. This round's one line is proved on the check that caught it: with the old line (`git show 37fa2bbb9e54aedf43d9feb24634710509837150:dev/audit/harnesses/agreement_two_pr.mjs`) `depth_root_seams()` returns the seam; with the new line it returns `[]` (Null control).

## Null control

37fa2bbb, `PYTHONPATH=tests/hastub python3 -c "import sys;sys.path.insert(0,'tests');import harness_headers as h;print(h.depth_root_seams())"` printed `["dev/audit/harnesses/agreement_two_pr.mjs:34: const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..')"]`. 2e9e217a5d90b42c12c1ef1536b490d3c2943b14, same command: `[]`. Full script at 2e9e217a5d90b42c12c1ef1536b490d3c2943b14: `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED`, rc=0; CI at 37fa2bbb read `1 of 112 HARNESS HEADER CHECKS FAILED`.
The two-PR result is unchanged by the fix: `node dev/audit/harnesses/agreement_two_pr.mjs tools/policy/agreement.mjs 'identical:synthetic (awaits {P})'` with the old and the new harness gives rc=0 and TWO-PR HELD at both, and `diff` of the two outputs differs in one line only, the abbreviated SHA of a throwaway-clone commit (`8f5ff9851` against `2e52c1a9b`). Round 1's other controls are unchanged.

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
- Round 2: `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: ALL 112 HARNESS HEADER CHECKS PASSED, rc=0 (the scoped gate skips it for this diff; this is the replay of the failing step of `tests / fast (3.14)`).
- Round 2: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`; it runs `tests/entities.py`: ALL 2592 ENTITY CHECKS PASSED, rc=0.
- Round 2: `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc=0; no `*_budgets.json` in the diff.
- Round 2: `bash tools/pr/prepr.sh <this body>`: PRE-PR rc=0 at 2e9e217a5 (gate mode MODE: SCOPED, claim files byte-identical to origin/main; the closures step skipped by its own rule, not by a flag).
- Round 2: the three-dot name list also holds `tests/closures.json` and `dev/programme/delivery/3173.md`; no claim file, VERSION, manifest version or RELEASE_NOTES.md is in it.

## Red checks

Every concluded red check-run at 37fa2bbb (55 check-runs, one page of 100, all read):
- `tests / fast (3.14)` (125230155835), failure: `1 of 112 HARNESS HEADER CHECKS FAILED`, the depth seam above. Fixed in this diff. Cheaper detector: `depth_root_seams()` in `tests/harness_headers.py`, well under a second against about 160 s for the script; `prepr.sh` leaves the script to CI as a leased script, so it did not catch this. The standing cost is a manual run of `depth_root_seams()` when a harness is added; no countermeasure is built in this repair, which is limited to the one fix.
- `gate` (125248466313, 125247188783), failure: the aggregate, red because `tests / fast (3.14)` is.
- `pr-contract / pr-contract` (125248066261, 125246797487), failure: I did not find its cause (the log tail the API returned holds only checkout cleanup); this body is retaken in full and passes `tools/pr/prepr.sh`.
All other concluded runs are success or skipped.

## Forward-carry

- Carry 35 and the reverse-direction deadlock: as in round 1; the grader is unchanged. Lands in group R10-AGREEMENT-BOOTSTRAP of dev/programme/rosters/wave-r10-groups.json. Carry: R10-AGREEMENT-BOOTSTRAP
- The verdict's age-needle re-dating and mutant M-h are not addressed in this repair round. Carry: R10-AGREEMENT-BOOTSTRAP

## Friction

- fixer: contradiction: the dispatch asks for each verified step to be pushed fast-forward only to `refs/heads/handoff-wip/r10-agreement-bootstrap`, which holds round 1's 85b9b7c76. A part-1 branch cut from origin/main cannot fast-forward it, so no step was pushed there before the handoff refs. Carry: R10-AGREEMENT-BOOTSTRAP

## Re-cut note

Round 2 of the repair, one finding (verdict/3173, `Fix review: blocked 37fa2bbb`): `tests / fast (3.14)` fails `tests/harness_headers.py`, whose depth-seam check refuses `dev/audit/harnesses/agreement_two_pr.mjs:34` (`const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..')`). The fix replaces the depth-counted root with the `repoRoot()` walk the sibling harnesses inline, copied from `dev/audit/harnesses/r9_fr3_family_consumer.mjs`. No allowlist entry; `tests/harness_headers.py` is unchanged. `git diff 37fa2bbb9e54aedf43d9feb24634710509837150 -- tools/policy/agreement.mjs | wc -l` prints 0: the grader is identical to the PR head's. The verdict's other findings (needle re-dating, mutant M-h, the two wording points) are outside this repair's ask and not addressed.

## Unpinned sites

none: the diff adds no `custom_components/` or `tools/` production site (the one changed line is in an inert harness under `dev/audit/harnesses/`, read by `tests/harness_headers.py`).
