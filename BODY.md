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

681a0d90890c269508924867e0f5f84689ef4ed9

prepr: passed rc=0 at 681a0d90890c269508924867e0f5f84689ef4ed9 (scoped)

## Fix review round 1, answered

`Fix review: blocked e99d63a6731b38d991bb372490a01b8b2f2c89d6 probe-fail-open` (verdict at 90a7613b19adfe4e100993b3388f77f113a0d439), item by item. No finder harness exists for this group; the harness at both ends is the reviewer's two reproductions, run unchanged (`## Figures`).

1. **An unanswered question passed.** `Host.run` now answers `(exit, stdout, stderr)` with no exit (`None`) for a command that could not be run or did not return, and the probe passes a question only on the answer that is a no. The work-tree question passes only on git's exit 128 carrying `not a git repository` (`LC_ALL=C`), so a missing git, a timeout, and any other failure (measured: `detected dubious ownership` is also exit 128) refuse with `git did not answer whether the private root ... is inside a work tree`. `git credential fill` passes on exit 0 with no password or on git's own `could not read Username|Password`, and refuses otherwise with `` `git credential fill` did not answer ``. A `gh` behind the shim that cannot be run or does not return refuses with `a gh on PATH did not answer whether it holds a login`. The rule enumerating the class's seams is `grep -n "view\.run(" tools/audit/seat/owner_only.py` above the self-test mark: three sites, each closed in this diff.
2. **An absent owner path passed.** `Host.readable` is replaced by `Host.reach`, which tells `absent`, `denied`, `open` and `unknown` apart, and `owner_path_refusal` passes an identity directory or deploy key only when it exists and is closed: an absent one refuses with `does not exist: an absent path proves nothing about the owner's keys`, an unreported state refuses, and a directory that lists refuses even when empty (the old `if names:` passed it). The probe runs inside `launch`, twice, so `launch` refuses a mistyped `--owner-identity` or `--deploy-key` through it; a second existence check in `launch` would be the same rule written twice. The same absent-or-unreadable confusion in the home's credential directories is closed (`cannot be listed`). Seams: `grep -n "view\.reach(\|view\.listing(\|view\.mode(" tools/audit/seat/owner_only.py`; each site now distinguishes the absent answer, `HPO_IDENTITY_DIR` and the root's mode already refused it. One limit is not closable from the seat account and is in the docstring's WHAT THE PROBE CANNOT SEE: a path mistyped below a directory the account cannot enter reads as closed exactly as the real one does.
3. **class-open, credential holders.** The probe no longer samples names. A variable refuses when a segment of its name ends TOKEN, SECRET, PASSWORD, PASSWD, CREDENTIAL(S), AUTH or APIKEY, or is PAT, KEY or PEM (`CREDENTIAL_WORD`, case and delimiter blind), or is one of `TOKEN_VAR`; the one exemption is the model credential, by the name `launch` now records in `probe.json`, and a `TOKEN_VAR` name is never exempt. `PUSH_AUTH` refuses. `merge_train.py`'s `gh auth token` reads a logged-in `gh`, which the probe's `gh auth status` line already refuses, now also when unanswered. The enumeration and each name's disposition are in `## Figures`. Alternatives that lost: adding `PUSH_AUTH` to the list (the block's instance, not its class); refusing every variable outside the launcher's allow-list (the session's own harness adds variables no list here can name, so the Prepare-step probe would refuse every run); refusing by the value's shape (a base64 header has none).
4. **Two archive shapes raised.** `archive_refusal` judges both before anything is written: a file member that is the archive's own directory (`.`, `a/..`) and a path that is both a file and a directory (`a` with `a/b`, either order, or with a directory entry `a/`). `safe_extract` also answers for whatever the rules do not name: a member the file system will not write (measured with a 300-character name) is refused as `a member cannot be written (<error>)` and what was written before it is removed, so the scan records the refusal, marks the item and completes.
5. **A transient error was final.** `each()` kept every state, so a unit whose read answered an error was never read again. Only an answer is kept now (`answered`: ok, gone, size, not a sha, no check suite, a refused archive); at a new pass every other state is dropped beside the cleared `not_reached` lines, so the unit is read again, once per pass. The reviewer's delegated stub reproduction (a 502 on the check-suite read, a healthy second pass) is the arm `transient`.

The verdict's note on a figure is corrected in `## Figures` (regex-written dimension lists). Its non-blocking findings keep the destination it gave them.

## Mutation proof

Every mutant is one predicate; the check that must go red is named beside it in the table that holds it.

- New instruments carry their table in their own self-test (`MUTANTS`, one per predicate, each run in a copy): `python3 -I tools/audit/seat/owner_only.py --self-test`, `python3 -I tools/audit/seat/corpus_mirror.py --self-test`, `python3 -I tools/audit/leak_detectors.py --self-test`, `python3 -I tools/audit/seat/finder_overlap.py --self-test`. Each prints `ok   mutant killed: <name> (by '<case>')` per mutant and ends `ok (with mutants)`.
- Edits to existing instruments: `python3 -I dev/audit/harnesses/owner_only_mutants.py`, which applies each mutant in a detached worktree of HEAD and runs that group's check. Groups: `drivers` (the owner-only branch, the probe refusal, the literal return and the reply schema of both workflow scripts, against `check-wave-script.mjs`), `ref_privacy`, `fold_ledger`, `gh_read`, `gh_calls`, `shim` (against the harness's P5 arm). It ends `RESULT mutants=<n> survived=0`.
- The design's named targets and where each is: the owner-only branch and literal return in each driver (`drivers`); each probe line (`owner_only.py`'s table); the read test in the shim (`shim`); the id-shape class (`ref_privacy`); the owner-only test in `seat_pair` and in `estimate` (`finder_overlap.py`'s table: `owner-only seat`, `owner-only estimate`); the namespace assertion, the floor comparison and the cursor write (`corpus_mirror.py`'s table: `namespace exit`, `floor`, `cursor write at a pause`, `cursor write per page`).

Round 1's guards, each one predicate in the same two tables, with the arm that goes red (`python3 -I tools/audit/seat/owner_only.py --self-test`, `python3 -I tools/audit/seat/corpus_mirror.py --self-test`; both end `ok (with mutants)`):

- item 1: `work tree unanswered`, `work tree any 128`, `work tree any exit`, `credential unanswered`, `credential any exit`, `credential said no`, `gh unanswered` (fixture arms), and `run unanswered`, `run timeout`, `run stderr` (the real `Host`: `host: with no git on PATH`, `host: a git that does not return in time`, `host null`).
- item 2: `absent owner path`, `unreported state`, `a listing is a read`, `open path`, `identity by name`, `home dir unlistable`, and on the real `Host` `absent owner path, real` and `denied is not open`.
- item 3: `credential class`, `auth word`, `segments`, `any case`, `word ends a segment`, `token var`, `model exempt`, `model by record`, `record written`, `record passed`.
- item 4: `directory itself`, `file and directory`, `ancestors`, `never raises`, `partial removed`. item 5: `no answer is asked again`, `an answer is kept`, `an error is no answer`, `refused is an answer`, `gone is an answer`.

One mutant survived and was removed with its clause, not triaged: `rc is not None and` in the credential line was implied by the empty stderr an unrun command carries. The members `size`, `not a sha` and `no check suite` of `ANSWERED` have no mutant: each is decided from a row already stored, with no call a second pass could be seen to repeat.

The spelling corpus of the name rule is `name_corpus()` in `owner_only.py`'s self-test: every word alone and at the start, middle and end of a name, over three delimiters and three cases, glued behind a prefix, plus the variables this tree's writers read; its null half is each word running on into a longer one. Its sizes: `python3 -I -c "import sys; sys.path.insert(0,'tools/audit/seat'); import owner_only as o; print(*map(len, o.name_corpus()))"`.

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
- Round 1, the probe: `host null: a sound account through the real Host and the real git is refused nothing` runs the real `Host` over a real private root, owner paths that exist with mode 0, and the real git, and is refused nothing; the fixture arms `probe null: the account the launcher builds`, `probe null: git saying it could read no username or password has answered` and `probe null: a name where the word runs on into a longer one` are the nulls of items 1 and 3. Where the test runs as root, which reads through any mode, the kernel's refusal of the three owner paths is stood in for at `Host`'s `_access` and `_listdir` (the class `Sealed`); as another user the plain modes do it.
- Round 1, the mirror: `archives null: nested files, a directory entry and a repeated ancestor extract whole`; `transient null: the pass that re-reads it reads no answered unit again`; `archives: a refused archive is an answer, and a later pass does not download it again`.
- The mirror: with no limit answer one pass reads every page once; three mapped ref namespaces exit 0; a well-formed archive extracts whole.
- Base graders: `git show origin/main:tools/policy/check-wave-script.mjs` run against this head's two workflow scripts passes whole, so the drivers land under the grader `pr-contract` restores.

## Figures

- The channel harness, every arm: `python3 -I dev/audit/harnesses/owner_only_channel.py` prints one line per arm, `RESULT arms=<n> failed=0` and `OWNER-ONLY CHANNEL HELD`.
- The grader: `node tools/policy/check-wave-script.mjs`; its `-- The owner-only dimensions` block is new.
- `check_scopes.py` and the planned shape (design note n1): the harness's SCOPES arms. An empty file universe resolves to one pseudo-file, so (step, source) cells are proved and `check_scopes.py` needs no change: the planned five seats pass, a planted overlap and a planted orphan on the axis are refused by cell.
- Readers of scopes.json and an unknown key (design note n10): `git grep -l "scopes.json" -- tools .claude tests`; `check_scopes.py` passes over an entry carrying `owner_only` (the SCOPES null arm), and the four readers of the key return one set (the SET arm).
- Sibling seams, by the design's commands, each with its disposition:
  - credential holders, `git grep -l -E "mint_token|openssl dgst -sha256 -sign|GIT_SSH_COMMAND" -- tools`: seven writers, each an arm (closed in this diff); `tools/pr/app_mint.sh` and `tools/audit/seat/remerge_main_selftest.py` named as no writer. The harness fails when this command and its list part.
  - regex-written dimension lists, `git grep -l -e '1\[0-' -- .claude/workflows tools/policy tools/audit dev/audit/config dev/governance tests tools/ci`: the command still returns `finder_overlap.py`, for the old pattern quoted inside its own mutant table; its rule no longer holds one (closed: any number, admission by scopes membership). The schema and its generated block are part 2's, with the brief.
  - values returned to a launching session, `git grep -n "^return \|^  return ownerOnlyStatus" -- .claude/workflows/audit-find.js .claude/workflows/audit-verify.js`: the public returns are unreachable from an owner-only run (closed: the grader's return-value arms).
  - push sites: `python3 -I tools/audit/seat/ref_privacy.py --check`; `audit-verify.js` is registered as naming a push only to forbid it. The mirror, the launcher and the detectors hold no push site.
- Round 1, the reviewer's reproductions at both ends, run unchanged from the verdict commit (`git show 90a7613b19adfe4e100993b3388f77f113a0d439:ev/repro_probe.py`, and the archive reproduction beside it in that commit's ev directory; the reviewer's instruments, kept out of the tree). At e99d63a6731b38d991bb372490a01b8b2f2c89d6 (the two recorded outputs in the verdict's ev directory): the absent identity path, the root with no git on PATH and `PUSH_AUTH` each end `probe OK` with exit 0, and the two archive shapes raise. At this head: every line of the probe reproduction exits 1 (its fixture names an identity path that does not exist, which is now refused on every line, the former baseline included; the sound-account null is the self-test's `host null`), the no-git line carries both `did not answer` refusals, the `PUSH_AUTH` line carries `the credential variable PUSH_AUTH is set`; the archive reproduction prints `returned "a member's path is the archive's directory"` and `returned "a member's path is both a file and a directory"`, its null `returned ''`, and its two cap lines as before.
- Round 1, the credential variables of the tree. Rule: `git grep -l -I -E "extraheader|x-access-token|[Aa]uthorization|[Bb]earer |GIT_ASKPASS|SSH_ASKPASS|GIT_SSH|sshCommand|credential\.helper|gh auth|with-token|mint_token|openssl dgst|_TOKEN|_PAT\b|PUSH_AUTH|PUSH_URL|_SECRET|PASSWORD|APIKEY|API_KEY" -- tools .github .claude tests dev`, each returned file read for the variables it takes a credential from (a delegated reader's reading of the files; the command and the name check below re-run by this seat). Dispositions, by `owner_only.credential_named`:
  - closed in this diff, refused by name: `PUSH_AUTH` (`tools/pr/merge_main_bot.py`), `PUSH_TOKEN`, `CLOSURES_PUSH_TOKEN`, `AUTH`, `TOKEN`, `HPO_RUNS_PEM`, `RUNS_PEM`, `HPO_LEDGER_PEM`, `LEDGER_PEM`, `HPO_RECORD_PEM`, `RECORD_PEM`, `HPO_APPROVER_PEM`, `APPROVER_PEM` (workflow `env:` blocks; PEM joined the rule from this enumeration), `MINT_KEY`.
  - already guarded: `GH_TOKEN`, `GITHUB_TOKEN`, `GH_ENTERPRISE_TOKEN`, `GITHUB_PAT`, `GITHUB_APP_INSTALL_TOKEN`, `HPO_PUSH_URL` (`TOKEN_VAR`); `SSH_AUTH_SOCK` (its own line); `HPO_IDENTITY_DIR` (must be the empty directory under the root); `gh auth token` in `merge_train.py`, `app_push.sh` and `stamp.py` (a logged-in `gh`, the `gh auth status` line).
  - not credentials: the `*_APPID` variables (identifiers), `USED_PAT` (a flag; refused by name all the same), `GIT_ASKPASS` and `SSH_ASKPASS` (the probe sets them to `true`).
  - a distinct finding, the verdict's fourth, with the destination it names: git configuration carried in the environment or the home (`GIT_SSH_COMMAND`, which `stamp.py` sets itself and reads from no caller, `GIT_CONFIG_COUNT`, a `.gitconfig`, `.netrc`).
  - null control of the name check: `python3 -I -c "import sys; sys.path.insert(0,'tools/audit/seat'); import owner_only as o; print(o.credential_named('PUSH_AUTH'), o.credential_named('HPO_RUNS_APPID'))"` prints `True False`.
- Architecture score: `python3 tools/audit/archscore/score.py --diff origin/main` (no product module changes).
- Not measured, and why (design figures F3 to F7): the first scan's and an incremental round's calls per bucket. This seat may call GitHub for search only and holds no read credential, so `corpus_mirror.py` has run against a stub alone. The enumerators stand: `python3 -I tools/audit/seat/corpus_mirror.py cost --private-root <dir>` and `python3 -I tools/audit/seat/gh_calls.py --top --since <scan start>`. The brief (part 2) names the floor and the batch as `gh_read.py`'s constants, never a literal.

<!-- figure-block: scope-line mb=030a4d377f9f26f5b8befe5721d86aea454f29e0 head=681a0d90890c269508924867e0f5f84689ef4ed9 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

- Part 2 (the brief with its `## Owner-only` heading, the `CLAUDE.md` row, the scopes and rotation entries, D18 in `DIMS` and in `audit-verify.js`'s set, the schema patterns, the `COMMON.md` sentence, budgets) is the split part the approved design names; it lands after this merges. Until then the real owner-only set is empty and every refusal here is inert outside its fixtures. Carry 1, landed on the round roster at 997083e81c7d575c31cbe65339204c5bdda9349a. Carry: R11-PRE-SECURITY-PRIVACY
- The first real scan confirms each endpoint's shape (design note n7) and records F3 to F7; it needs the read credential on the owner's machine. Which identity the mirror holds (a read-only App with `--own-identity`, or the shared token under the 60 % floor) is routed to the owner by the design. Carry 2, landed on the round roster at 997083e81c7d575c31cbe65339204c5bdda9349a. Carry: R11-PRE-SECURITY-PRIVACY
- The seat account (creating it, and making the identity directory and the deploy key unreadable to it) is the owner's act; without it `owner_only.py probe` refuses and no owner-only seat runs. The two-account run is proved once on the owner's machine and its probe line stays in the private root (design note n8). Carry 3, landed on the round roster at 997083e81c7d575c31cbe65339204c5bdda9349a. Carry: R11-PRE-SECURITY-PRIVACY
- Whether a temporary private fork's merge honours the ruleset on `main` (design note n4) was not confirmed: it needs a scratch advisory, which this seat cannot open. Carry 4, landed on the round roster at 997083e81c7d575c31cbe65339204c5bdda9349a. Carry: R11-PRE-SECURITY-PRIVACY
- `tools/audit/seat/finder_overlap.py estimate` now requires `--scopes`; its instrument page carries the new command. An orchestrator's saved command line without it is refused with rc 2. Carry: dismissed: the instrument page carries the new command, which is where an orchestrator reads it
- `tools/ci/selftest_closures.json` gains four measured steps (`owner-only-launcher`, `corpus-mirror`, `leak-detectors`, `owner-only-channel`), recorded here under strace; main's push re-measures them. Carry: dismissed: the drift check on main's push owns it

## Friction

none
