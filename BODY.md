The root-cause record for the friction residue #2561 left unmeasured. It lands
no production code and no policy file: it measures the five keys at this
group's merge base, gives each a named cause, a process state, a cost test and
a countermeasure or a recorded refusal, and dispositions the three carries
(#2452's census cost, #2479's cross-run count, #2612's row) and the two keys the
brief did not scope (#2593, #2597) plus the four issues the roster added in this
window (#2410, #2660, #2784, #2855).

A closing keyword for 2410, 2593, 2597, 2660 and 2784 is owed at open: this body
cannot carry the five lines yet. `pr-contract` refuses to close a roster issue
no group names in `fixes` (`orchestrator.md` section 10), and at `6eb552157` this
group's `fixes` is empty, so `prepr`'s preflight and `body_push.sh` both refuse
them. Land the roster edit (`roster_edit.py`: this group's `fixes` = those five),
then add the five keywords with `body_patch.sh` before the merge. That deadlock
is the record's own cause in miniature: the seat that produced the carry cannot
write the roster that must receive it.

#2428 is already closed; #2429, #2436, #2437, #2438 and #2855 stay open because
their countermeasures are drafted and routed, not landed.

## Head

`581079f20a536c0261158bc86f49f5b10e88f617`: the authored code head. It adds two commits to the previous
code head `fbfa72a1d92f77a1271838b4691806f3aa7267c1`, which was one commit on `6eb552157`: `carry-2733.json` (the two
`Carry: #2733` items, #2875 and #2855's key) and its `tests/closures.json` entry. The merge base and
`origin/main` at measurement is `6eb552157`. Nothing merges main. Every figure in the record was taken at
`6eb552157`; the histogram window is `v7.0.4..origin/main` with `v7.0.4` at `b448d260`.

## Mutation proof

n/a: no check, test or production line changes. The two instrument
demonstrations this record proposes are owed by their fixers (record section 3,
A1 and A2): `rosterIssues()` goes 1 → 76 indexed issues and a carry file at
covered issue 2492 flips accepted → refused, with control 999999 accepted under
both. Nothing here is executable, so there is no line to mutate; the controls
are recorded and re-runnable by the commands under Figures.

## Null control

- The unmodified tree's `node tools/policy/brief_lint.mjs` prints `TOTAL: 0
  error(s) across 48 file(s)` (47 carry files and the round-3L roster), and its
  own acceptance assert refuses `carry-990004.json` against the fixture
  `wave-probe-groups.json` — the live-group arm is green on a fixture and blind
  in production.
- `rosterIssues()` with no argument indexes 1 issue (457); with
  `dev/programme/rosters` passed it indexes 76.
- The unmodified tree accepts a carry file at issue 2492 (rc=0) and refuses it
  when the programme roster is passed; control issue 999999 is accepted both
  ways; control issue 457 is refused by the shipped index.
- On the window's 205 group-destination finding items, the id-in-brief predicate
  fires 205/205 and the PR-number predicate fires 193/205, 29 of them on PRs
  never blocked at all.
- The histogram's literal `other` row is 2 PRs / 3 entries; the wave's `other`
  route is 52 PRs / 67 entries.

## Figures

- `node tools/policy/policy_lint.mjs --stats --since v7.0.4`: 218 merged PRs,
  173 carrying a parsable verdict, 12 would-open lines; rc=0 in 669 s. Saved as
  `dev/audit/rca/harness-friction/stats_v7.0.4.txt`, one host path in its second
  line scrubbed to the `~` form `ref_privacy.py scrub --write` prescribes.
- `python3 -I dev/audit/rca/harness-friction/rounds.py <window per-PR fetch
  directory>`: 132 blocked rows over 84 PRs and its SUM lines. Saved as
  `dev/audit/rca/harness-friction/blocked_rounds_v7.0.4.tsv`; the fetch is
  `gh api --paginate .../issues/<n>/comments` and `.../pulls/<n>/reviews`, first
  line of each body with `created_at`/`submitted_at`.
- `python3 -I dev/audit/rca/harness-friction/rounds.py --stats
  dev/audit/rca/harness-friction/blocked_rounds.tsv`: rc=0, stdout 0 bytes — the
  brief's named invocation is vacuous, because the script takes a directory.
- `node --input-type=module -e "import {rosterIssues} from './tools/policy/brief_lint.mjs'; console.log(rosterIssues().size)"`:
  `1`; with `'dev/programme/rosters'` passed, `76`.
- `python3 -I tools/audit/fold_ledger.py check`: `47 classes, 749 instances,
  121 in-tree judge survivors (rounds [8, 10]), 125 rca entries`, `0
  violation(s)`. Main prints 124 rca entries; this diff adds
  the one `_rca` entry.
- `node tools/policy/policy_lint.mjs --budgets`: unchanged by this diff (no
  policy file is touched).
- `python3 -I tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc=0.
- `python3 -I tools/audit/carry_audit.py check --body <this body>`:
  `CARRY-AUDIT: 17 finding item(s): 17 routed, 0 unrouted, 0 bad destination(s)`,
  rc=0.
- `python3 -I tools/audit/archscore/gate.py --base 6eb552157 --head HEAD --body
  <this body>`: `PASS: dS +0.0000 NULL, no gate metric rose`.

## Red checks

`prelude`: GitHub API rate limit ("RATE-LIMITED reset_epoch=1793140725", run
40595111242), transient; cheaper detector: none (HANDOVER trap 44: rate-limit
403s arrive as red lanes; the repair is a re-run, not a code change). `gate`
and `pr-contract` are red only through it. The 132 block rows it measures are
merged PRs' history, not this head's.

## Forward-carry

- **A1, the roster index.** `rosterIssues()`'s no-argument path reads
  `roster_lib.ROSTERS_DIR` as well, so the live-group refusal fires in CI.
  Carry: R10-FLOW-TOOLKIT-MODEL (the carry text is on handoff/audit-r10-roster at `ba973babd`; #2733 has no live group)
- **A2, the merge-time fold.** The orchestrator writes each `Carry: <GROUP>`
  body item's id into the destination group's brief before merging, with the
  post-fold id assertion. Carry: R10-FLOW-TOOLKIT-MODEL
- **The derived `other (untaught)` friction family** in `statsFamilies`, which
  folds 46 untaught spellings over 52 PRs into one threshold row (46 after the
  #2410 subtraction). Carry: #2436
- **The `root-cause` family** (`root-cause-unanswered`, `root-cause-detectable`,
  `root-cause-unrecorded`) in the same map: union 6 PRs, family 3, fires.
  Carry: #2437
- **#2479's cross-run count** is supplied by the record's section 5 (per check,
  over the window); its policy sentence is the owner's. Carry: #2437
- **#2875 is unowned** — an open friction issue no roster group lists, the
  routing audit's subject; carried in `dev/programme/carries/carry-2733.json`.
  Carry: #2733
- **The ci-autofix wait bound and the measured-pin rule** land in
  `.claude/rules/ci-autofix.md` after the owner's approval. Carry: #2429
- **The carry-control enumerator lint** in `brief_lint`, and the sentence that a
  ruling's destination is a `Carry:` marker, land in `tools/policy/brief_lint.mjs`
  and `dev/governance/roles/`. Carry: #2438
- **#2612's row** (a seat cannot land a carry into a brief or a roster) is
  dispositioned by the record's section 8 as section 3's cause; it does not stay
  with `R10-BRIEFS-FOLD`, which is done and did not implement it. Carry: #2438
- **#2855's key** is dispositioned in the record; the mechanism is #2733's, carried in the same file.
  Carry: #2733
- **#2452's census cost** is a recorded refusal: the cheaper detector is the
  spelling list the census replaced. Carry: dismissed: cheaper census is the spelling list that failed

## Friction

- `rounds.py`: unenforced: the group's brief names `rounds.py --stats`, which is
  not a mode; the invocation exits 0 with zero bytes and would read as a
  measurement. Carry: R10-ROUND-PLAYBOOK
- `brief_lint`: unenforced: rosterIssues() and the no-argument roster list read
  .claude/workflows and the carries directory, never dev/programme/rosters; 1 of
  76 live-group issues is indexed and a carry file at a covered issue is
  accepted rc=0. #2561 recorded the same defect and routed it to #201, where no
  text about it landed. Carry: R10-FLOW-TOOLKIT-MODEL
- `policy_lint.mjs`: unclear: the threshold's unit is the class spelling, so 46
  untaught words over 52 PRs and three root-cause words over 6 PRs aggregate to
  no filing. Carry: #2436
- `ci-autofix.md`: unclear: "wait for the bot" has no terminating condition when
  the bot's own job stalls, and a body may state a pin it has not measured (3 PRs
  in the window; #2834 names a CI round and a fixer round). Carry: #2429
- `finding-propagation.md`: unenforced: a carried control's figures and statistic
  are not required to name an enumerator, and the producing seat cannot write the
  destination brief (5 PRs in the window). Carry: #2438
- `roster`: stale: the group's own carry names seven issues; the roster holds
  eleven, and the four it omits all fired in this window. Carry: dismissed: all eleven dispositioned in the record




