_Requested by **tvofi**_

R11-PRE-SECURITY-PRIVACY, part 1 of 2 (the design's required split, design/R11-PRE-SECURITY-PRIVACY at 8f52783880f93747270fd34403a2ed076c19a3fc, `Design review: approve`). This part builds the channel of an owner-only audit dimension and declares none: no brief, no scopes entry, no `CLAUDE.md` row, no budget row. Part 2 adds the dimension itself, after this merges, because `pr-contract` grades a pull request with the base's graders.

What it builds. A dimension whose `dev/audit/config/scopes.json` entry carries `owner_only: true` publishes nothing. The closure is structural, not a filter: no stage of such a run has a public output to write to, and no process of it holds a credential that writes.

- `.claude/workflows/audit-find.js`, `.claude/workflows/audit-verify.js`: a public round or box dispatches no seat of such a dimension and records nothing of it; a run handed `args.private_root` dispatches only those seats, each replying a path and a done flag, runs no collector, leads, intake, register, sweep, fold, issue, roster or record step, and returns its arguments and a fixed sentence.
- `tools/policy/check-wave-script.mjs`: holds the declaration equal across scopes.json, the briefs with a `## Owner-only` heading and `audit-verify.js`'s literal set; drives both scripts over a fixture dimension D99; keys the two `D18-s1` schema controls on the D18 brief existing.
- `tools/audit/seat/owner_only.py` (new): the launcher and the probe. `tools/audit/seat/corpus_mirror.py` (new): the one process that reads GitHub. `tools/audit/leak_detectors.py` (new): candidate spans, written only under the private root.
- `tools/audit/seat/ref_privacy.py`: the class `owner-only-id`. `tools/audit/seat/shims/seat-gh`: an owner-only mode. `tools/audit/fold_ledger.py`: `check` and `fold` refuse such a record. `tools/audit/seat/finder_overlap.py`: no twin and no estimate for such a seat; `estimate` now requires `--scopes`.
- `tools/audit/seat/gh_read.py`, `tools/audit/seat/gh_calls.py`: the conditional read, the budget floor, calls per bucket.
- `dev/audit/harnesses/owner_only_channel.py` (new), wired into `governance.yml` with the three new self-tests.

Carry 0 (the owner's API-limit requirement), by clause, and where each is built:

- every read through `gh_read.py`'s read rule, never a raw loop: `corpus_mirror.py` reads only through `gh_read.read_conditional` and `gh_read.retry`, and its gate stops it before any call that is not `is_read` or `is_query` (its arms `reads only` and `gate`).
- bulk sources first: history, refs, deleted content and the wiki by `git` (no API call); lists at 100 per page; GraphQL batches of 50 items.
- every page cached with its ETag and re-read with `If-None-Match`, a later round from a cursor: the arm `incremental`.
- `rate_limit` read before each batch, a floor on core and graphql, the secondary limit honoured, one stream: `gh_read.py`'s `BATCH`, `MIN_GAP_S`, `FLOOR_SHARED` (argued in its docstring) and `FLOOR_OWN`; the arms `budget`, `floor`, `pause` and `resume`.
- the planted rate-limit answers (a 403 naming the secondary limit, a spent core bucket) under which the scan pauses and resumes from its cursor without losing or repeating an item, with the null control: the arms `pause: ...`, `resume: ...`, `scan null`, `crash`, and the two cursor-write mutants.
- the command that counts calls per bucket: `gh_calls.py --top` now prints the bucket table; `corpus_mirror.py cost` prints the scan's own.
- NOT done here, said plainly: the measured cost of a full first scan and of an incremental round, and the brief's statement of the budget. The first needs a read credential this seat does not hold (see `## Figures`); the second is the brief, which is part 2. The nightly slice window is the orchestrator's, by the design.

This body describes the channel only. No seat of this group looked for a finding, and none is quoted.

## Head

e99d63a6731b38d991bb372490a01b8b2f2c89d6

## Mutation proof

Every mutant is one predicate; the check that must go red is named beside it in the table that holds it.

- New instruments carry their table in their own self-test (`MUTANTS`, one per predicate, each run in a copy): `python3 -I tools/audit/seat/owner_only.py --self-test`, `python3 -I tools/audit/seat/corpus_mirror.py --self-test`, `python3 -I tools/audit/leak_detectors.py --self-test`, `python3 -I tools/audit/seat/finder_overlap.py --self-test`. Each prints `ok   mutant killed: <name> (by '<case>')` per mutant and ends `ok (with mutants)`.
- Edits to existing instruments: `python3 -I dev/audit/harnesses/owner_only_mutants.py`, which applies each mutant in a detached worktree of HEAD and runs that group's check. Groups: `drivers` (the owner-only branch, the probe refusal, the literal return and the reply schema of both workflow scripts, against `check-wave-script.mjs`), `ref_privacy`, `fold_ledger`, `gh_read`, `gh_calls`, `shim` (against the harness's P5 arm). It ends `RESULT mutants=<n> survived=0`.
- The design's named targets and where each is: the owner-only branch and literal return in each driver (`drivers`); each probe line (`owner_only.py`'s table); the read test in the shim (`shim`); the id-shape class (`ref_privacy`); the owner-only test in `seat_pair` and in `estimate` (`finder_overlap.py`'s table: `owner-only seat`, `owner-only estimate`); the namespace assertion, the floor comparison and the cursor write (`corpus_mirror.py`'s table: `namespace exit`, `floor`, `cursor write at a pause`, `cursor write per page`).

Two mutants first survived and each gained a killing arm: the pause-time cursor write (lists were already saved per page, so only a pause inside a per-item read loses work without it: the arm `pause in a per-item read`), and `gh_read.py`'s spent-bucket return (the arm `one resetting inside the schedule`).

## Unpinned sites

`prepr.sh`'s diff mutants (`MUTANT_CMD="sh -c 'python3 -I tools/audit/fold_ledger.py --self-test && python3 -I tools/audit/leak_detectors.py --self-test --no-mutants'"`; it draws the first 40 added `.py` lines in file order, all in `tools/audit/fold_ledger.py`). The survivors left are lines of that file's own self-test, not of its rule, each read:

- the drawn nonce's length (`secrets.token_hex`): any length plants a nonce; no behaviour to pin.
- `os.makedirs(..., exist_ok=True)` for the scratch scopes directory, deleted: `_plant` has already made `dev/audit/config`, so the call is redundant in the fixture and harmless to drop.
- the arm `a survivor of one that no class holds`, deleted whole, and two `expect` calls deleted: a deleted assertion cannot fail; the rule each pins is killed by `owner_only_mutants.py`'s `fold_ledger` group.
- `owned(True, "D15")` read as `owned(False, "D15")` in the D15 null control: both are valid nulls (a D15 record passes whether or not another dimension is declared).

A survivor in the rule itself (an early return on an empty set, equivalent to the loop finding nothing) was removed with the line, not triaged.

## Null control

- The unmodified tree: `git stash; node tools/policy/check-wave-script.mjs` is not the control here, since the base holds no owner-only rule to turn off. The controls are per arm, inside each instrument, and are the lines that begin `null` or `null control`.
- Drivers: the same fixture dimension with the flag removed, or false, is dispatched and its finding reaches the intake prompt; the same canary under a D15 seat reaches the collector's push prompt and the return value; with the dimension out of `audit-verify.js`'s set the same finding reaches the judge, the register writer and the return value.
- `finder_overlap.py`: the same seat with the flag removed or false is admitted and its twin path printed; a D15 seat of the committed scopes is admitted beside an owner-only dimension.
- `fold_ledger.py`, `ref_privacy.py`, the shim: the same canary under a D15 id is folded, passes the guard and lands on a scratch origin; with the shim's mode unset the same write reaches the stub `gh`.
- The writers (design row P5b): with a throwaway identity directory the same command no longer stops on its fail-closed line. This is weaker than the design's wording (the canary reaching a stub `curl`): reaching `curl` needs each writer's full fixture (an open pull request, a verdict, a contract), which only its own self-test builds. `remerge_main.sh` reads no key itself on its non-fork path, so its null is `app_push.sh`'s; `stamp.py`'s null reads its own `push_key_problem`, because past that rule the stamp would run for real.
- The mirror: with no limit answer one pass reads every page once; three mapped ref namespaces exit 0; a well-formed archive extracts whole.
- Base graders: `git show origin/main:tools/policy/check-wave-script.mjs` run against this head's two workflow scripts passes whole, so the drivers land under the grader `pr-contract` restores.

## Figures

- The channel harness, every arm: `python3 -I dev/audit/harnesses/owner_only_channel.py` prints one line per arm, `RESULT arms=<n> failed=0` and `OWNER-ONLY CHANNEL HELD`.
- The grader: `node tools/policy/check-wave-script.mjs`; its `-- The owner-only dimensions` block is new.
- `check_scopes.py` and the planned shape (design note n1): the harness's SCOPES arms. An empty file universe resolves to one pseudo-file, so (step, source) cells are proved and `check_scopes.py` needs no change: the planned five seats pass, a planted overlap and a planted orphan on the axis are refused by cell.
- Readers of scopes.json and an unknown key (design note n10): `git grep -l "scopes.json" -- tools .claude tests`; `check_scopes.py` passes over an entry carrying `owner_only` (the SCOPES null arm), and the four readers of the key return one set (the SET arm).
- Sibling seams, by the design's commands, each with its disposition:
  - credential holders, `git grep -l -E "mint_token|openssl dgst -sha256 -sign|GIT_SSH_COMMAND" -- tools`: seven writers, each an arm (closed in this diff); `tools/pr/app_mint.sh` and `tools/audit/seat/remerge_main_selftest.py` named as no writer. The harness fails when this command and its list part.
  - regex-written dimension lists, `git grep -l -e '1\[0-' -- .claude/workflows tools/policy tools/audit dev/audit/config dev/governance tests tools/ci`: `finder_overlap.py` no longer among them (closed: any number, admission by scopes membership); the schema and its generated block are part 2's, with the brief.
  - values returned to a launching session, `git grep -n "^return \|^  return ownerOnlyStatus" -- .claude/workflows/audit-find.js .claude/workflows/audit-verify.js`: the public returns are unreachable from an owner-only run (closed: the grader's return-value arms).
  - push sites: `python3 -I tools/audit/seat/ref_privacy.py --check`; `audit-verify.js` is registered as naming a push only to forbid it. The mirror, the launcher and the detectors hold no push site.
- Architecture score: `python3 tools/audit/archscore/score.py --diff origin/main` (no product module changes).
- Not measured, and why (design figures F3 to F7): the first scan's and an incremental round's calls per bucket. This seat may call GitHub for search only and holds no read credential, so `corpus_mirror.py` has run against a stub alone. The enumerators stand: `python3 -I tools/audit/seat/corpus_mirror.py cost --private-root <dir>` and `python3 -I tools/audit/seat/gh_calls.py --top --since <scan start>`. The brief (part 2) names the floor and the batch as `gh_read.py`'s constants, never a literal.

<!-- figure-block: scope-line mb=030a4d377f9f26f5b8befe5721d86aea454f29e0 head=e99d63a6731b38d991bb372490a01b8b2f2c89d6 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

- Part 2 (the brief with its `## Owner-only` heading, the `CLAUDE.md` row, the scopes and rotation entries, D18 in `DIMS` and in `audit-verify.js`'s set, the schema patterns, the `COMMON.md` sentence, budgets) is the split part the approved design names; it lands after this merges. Until then the real owner-only set is empty and every refusal here is inert outside its fixtures. Carry: R11-PRE-SECURITY-PRIVACY
- The first real scan confirms each endpoint's shape (design note n7) and records F3 to F7; it needs the read credential on the owner's machine. Which identity the mirror holds (a read-only App with `--own-identity`, or the shared token under the 60 % floor) is routed to the owner by the design. Carry: R11-PRE-SECURITY-PRIVACY
- The seat account (creating it, and making the identity directory and the deploy key unreadable to it) is the owner's act; without it `owner_only.py probe` refuses and no owner-only seat runs. The two-account run is proved once on the owner's machine and its probe line stays in the private root (design note n8). Carry: R11-PRE-SECURITY-PRIVACY
- Whether a temporary private fork's merge honours the ruleset on `main` (design note n4) was not confirmed: it needs a scratch advisory, which this seat cannot open. Carry: R11-PRE-SECURITY-PRIVACY
- `tools/audit/seat/finder_overlap.py estimate` now requires `--scopes`; its instrument page carries the new command. An orchestrator's saved command line without it is refused with rc 2. Carry: dismissed: the instrument page carries the new command, which is where an orchestrator reads it
- `tools/ci/selftest_closures.json` gains four measured steps (`owner-only-launcher`, `corpus-mirror`, `leak-detectors`, `owner-only-channel`), recorded here under strace; main's push re-measures them. Carry: dismissed: the drift check on main's push owns it

## Friction

none
