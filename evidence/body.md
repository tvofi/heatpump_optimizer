Flow board (Lean study K1), group `R10-FLOW-BOARD` (lane IN), one of the seven groups under the #2715 tracker, which closes when the last of them merges. The programme's throughput against the owner's demand of one roster group merged per hour was measured nowhere, so no flow change could show it worked.

This adds `merge_throughput.py flow`: it reads git alone -- the first-parent log of the tree, the review/verdict bus refs through `review_strength`'s `PREFIX_RE`/`VERDICT_RE` grammar, the roster through `roster_lib` -- and prints, per rolling hour and per 24 h, roster groups closed against takt 1.0, fly-ins closed, main moves split group-carrying/record/roster-edit/fly-in, first-pass fix-review yield with its blocked-class mix, and lead time per size, plus a WIP-by-lane snapshot. The bus is read with one `git log` over every review ref, not `review_strength.load()`'s per-ref reads; the two readers return the same verdict set at this head. `state_docs.py` publishes the board as `FLOW-BOARD.md`, second in `DOC_NAMES`, so the beat carries it beside the plan table. A source that cannot be read prints UNAVAILABLE with its reason, never a zero. `.github/workflows/governance.yml` already ran `merge_throughput.py --self-test` in the instrument-self-tests job; the diff adds only a comment there naming the flow arms.

The fix review blocked the first handoff at `8f05b74d` on five blocks, and four were the rule below read as false in a different source. Now: an unreadable roster at `--roster-ref` or at a roster commit, and an unreadable `critical-path.json`, print UNAVAILABLE with the reason instead of a traceback or a lane-A zero (`roster_lib.roster_shape`, `critical_path_read`, `flow_closed`'s per-commit state, `flow_wip`'s refusal of a None critical set); and every period window is closed at both ends in all three measures that carry one -- main moves, roster closures, and bus verdicts -- so the default render, which ends at a ref tip's own committer time, counts the event at that tip. The fifth was a classification the diff owed: `tests/entities.py` runs `state_docs.py --self-test`, which runs this generator, so entities.py newly opened `tools/audit/merge_throughput.py` -- a read under the `tools/audit/` INERT prefix the committed table never listed. It leaves the prefix through `tests/closure.py`'s `INERT_EXCEPT`, the route its four state-doc siblings already take, and the re-derived `tests/closures.json` carries the entry, so an edit to the generator selects `tests/entities.py`. `## Red checks` answers that red with its command.

The roster's carries this PR discharges: self-test hygiene (b), the fixture builds any git repository through `tests/throwaway_git.py` (`tests/throwaway_git.py --check` prints `0 raw git init or clone site(s) refused`); (c), the diff adds no push site; (d), `## Red checks` below. (a) does not arise: no seat-selftest mutant is added. Carry 1 names the pre-study, not work. Carries 2, 3, 5 and 6 remain and are routed in `## Forward-carry`.

The fixer's gate could not be scoped at this head: the diff changes `tests/closure.py`, a gate file, so `closure.py select` prints `MODE: FULL -- every test script runs, nothing is scoped out` ("tests/closure.py changes the gate itself, so every closure is suspect"). The brief that dispatched this fix forbids a full `prepr.sh` (the gate pool is contended and `field coverage` alone takes minutes), so the full suite is CI's at this head; the scripts this diff can reach were run directly and are listed in `## Figures`.

Size: `tools/audit/merge_throughput.py` grows +990/-2 -- over `fixer.md`'s ~400 guide -- because the six measure families, the markdown renderer, the CLI and the review's four UNAVAILABLE paths land in the one file the group names; the brief names that file and no new one, and no tracked file is added.

## Head

`3bd284f744e372f2440b1f6faa31e3b1708f085f` merges origin/main `ea36188c3` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`4f2297e1db1b447bdc336f86fd62506a1c4b53bd` merges origin/main `a0e7664ea` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`d218ef37858f5cdbe16a3ad1059050085baa65b6`: `8f05b74d4603c29b73eadeaf1c29b821d1f45b1b` with the five blocks of `verdict/2883` fixed. The base is `git merge-base origin/main d218ef37858f5cdbe16a3ad1059050085baa65b6` = `67178dc6a589cf95d2ce7cff36d8bbf17343e8dc`. Everything below was measured at this head, over `67178dc6a589cf95d2ce7cff36d8bbf17343e8dc...d218ef37858f5cdbe16a3ad1059050085baa65b6` (three-dot, so main's own newer commits are not read as this branch's).

## Mutation proof

Each mutant replaces one production line with the behaviour the review blocked on, and the named `--self-test` arm reds; the file is restored after each (the harness is outside the tree: it applies, runs and restores each mutant, and is not a tracked file). 16 of 16 mutants red the arm that names them: B1a/B1b/B1c, B2, B3 and the two `roster_lib` mutants red the roster, per-commit-state and WIP arms; B4 x3 reds the three closed windows; I0-I5 red the five instrument arms the reviewed body listed. Three of the sixteen abort the self-test with a traceback instead of printing a FAIL line -- that is the reviewed defect (a crash, not a zero) and the harness counts the non-zero exit as red.

## Null control

At `--self-test` the unchanged fixture rendered twice is byte-identical (`ok flow null control: an unchanged fixture reads identical`), and its companion moving `--until` past the events changes the board (`ok flow null control is not vacuous: a moved until changes it`). The fixture pins the counts: 1 group-carrying merge, 1 record, 1 roster-edit and 1 fly-in (`ok flow: main moves split group/record/roster/fly-in` = (1, 1, 1, 1)), 1 roster group closed, one blocked-then-merged verdict (first pass 0/1), one `harness` blocked class. Every arm in `## Mutation proof` is also a null control for the arm next to it: the mutant reds that arm alone and the restored run is green (final `ok: merge_throughput.py self-test` and `roster_lib self-test: 39 checks, 0 failed`). On the live refs no merge fell in the trailing hour at the reviewed head, so the real run's 1 h column reads zeros and the fixture is what pins the split; the real board at this head is byte-identical to the fixer's.

## Figures

- three-dot diffstat, 8 files changed, 1157 insertions(+), 54 deletions(-): `git diff --stat 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc...d218ef37858f5cdbe16a3ad1059050085baa65b6`.
- `tools/audit/merge_throughput.py` +990/-2: `git diff --numstat 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc...d218ef37858f5cdbe16a3ad1059050085baa65b6`.
- 808 non-blank, non-comment added lines in `merge_throughput.py`, and 70 in `roster_lib.py`: `git diff -U0 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc...d218ef37858f5cdbe16a3ad1059050085baa65b6 -- <file> | awk '/^\+/ && !/^\+\+\+/ && $0 !~ /^\+[[:space:]]*$/ && $0 !~ /^\+[[:space:]]*#/' | wc -l`.
- scoped-gate mode line, `MODE: FULL -- every test script runs, nothing is scoped out` (reason: `tests/closure.py changes the gate itself, so every closure is suspect`): `python3 tests/closure.py select --diff 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc`.
- structural ratchet, `STRUCTURE RATCHET PASSED`: `python3 -I tests/structure.py`.
- the flow arms, the fixture's exact counts and the null control: `python3 -I tools/audit/merge_throughput.py --self-test`.
- `roster_lib self-test: 39 checks, 0 failed`: `python3 -I tools/audit/seat/roster_lib.py --self-test`.
- `state_docs self-test: all checks passed`: `python3 -I tools/audit/seat/state_docs.py --self-test`.
- `tests/entities.py` at this head, `ALL 2467 ENTITY CHECKS PASSED` in 2638 s, rc 0: `python3 tests/entities.py`.
- the closure entry itself, from the re-derivation that produced it: `./tests/derive_closures.sh --single tests/entities.py --out-dir <dir>`, whose recording is what the check above reads -- that recording exited 1 on the orphan check while `INERT_EXCEPT` held the file and `tests/closures.json` did not, and the merged entry is what clears it. The derive is the same 1280 s instrument `## Red checks` names; the plain run above is the post-merge one.
- the closures check the red named, green here: `python3 tests/closure.py check --in-dir <dir> --partial` prints `closure: committed closures cover every file this run touched`.
- the real flow board at this head, at the pinned refs the review measured: `python3 -I tools/audit/merge_throughput.py flow --repo . --tree e40806a7d8b024e7090182ea6d1906f45ddf89e2 --roster-ref cfacd3800bb5fa7deb043e6afd7533fa73f3a5d8`.
- architecture score, `Architecture score: dS +0.0000 NULL, gate PASS (no gate metric rose)`: `python3 -I tools/audit/archscore/gate.py --base 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc --head d218ef37858f5cdbe16a3ad1059050085baa65b6 --body <this body>`.
- 0 raw git init or clone sites: `python3 -I tests/throwaway_git.py --check`.

## Red checks

`tests / closures` -- check-run 122347694666 at `8f05b74d`, step "Fail if tests/closures.json under-approximates": `INERT READS UNDER-APPROXIMATED: tests/entities.py: tools/audit/merge_throughput.py`. `tests / closures-autofix` is the same red: its repair step was skipped, so no bot commit was coming. Cause: this diff's `state_docs` call makes `tests/entities.py` open a file under the `tools/audit/` INERT prefix, and the pull request added the call without re-deriving the closure. Reproduced and cleared with the same command both ways:

```
./tests/derive_closures.sh --single tests/entities.py --out-dir <dir>
python3 tests/closure.py check --in-dir <dir> --partial
```

At `8f05b74d` (recording of `tests/entities.py`, 1280 s, rc 0) the check prints `INERT READS UNDER-APPROXIMATED: ... tests/entities.py: tools/audit/merge_throughput.py`, rc 1. At this head (re-derived recording and table) it prints `closure: committed closures cover every file this run touched`, rc 0.

Root-cause trigger (`defect-root-cause.md`, `root-cause-detectable: tests/closures`): the cheaper detector is that derive plus check -- the same instrument, reachable before the push; its standing cost measured here is 1280 s, a lane MAX of about 28 min in CI. The fixer's local path had no signal: at `8f05b74d` `tools/pr/ci_predict.py` printed `no closures, fast, wave-script or instrument red predicted against 67178dc6a589 (a data-file read is not seen)` (the fix review's own `ci_predict.txt`), because the new read is a path on a subprocess command line. The process existed and was not followed; the RCA and any process countermeasure are owed by the separate root-cause seat, not by this one. `pr-contract`'s two refusals at 17:47:19Z and 17:50:27Z read the same red off the API and are answered by this section.

No other check was red at `8f05b74d`: `tests / closures` and `tests / closures-autofix` were the only foreign failures, `gate` was in progress and is excluded, and `pr-contract` is the refusal above.

## Forward-carry

- The plan-page seam (the roster row's carries 2 and 3): the board is published as a flow-board document beside the plan table through `state_docs.py`, as the group's brief asks, and is not a section of `plan_page.py` drawn from the plan's own model, so "one plan model; the flow board is a section of that page, not a third page" is not met here. Carry: R10-ORCH-PLANPAGE
- The token measurement (the roster row's carry 6, tvofi's 2026-10-24 recommendation (e)): IE = input + 1.25 x cache write + 0.1 x cache read + 5 x output tokens read from the local session transcripts, printed per day, per role and per merged content pull request with the window and transcript count beside each figure, as a flow-board section in `merge_throughput.py` -- not built here. Control: a fixture transcript set with known token counts reproduces its IE, and a set with one seat removed lowers the day figure by that seat's IE; it does not cover cloud seats. Carry: R10-FLOW-TOOLKIT-MODEL
- The owner-gate count (the roster row's carry 5): `orchestrator_tick.py` still flags a gate whose only text is `mandated approval under <id>`; counting such a gate as cleared while a mandate in force (scope all) covers it, option A and test-first, is not touched here. Carry: R10-ORCH-LEDGER

## Friction

- `finding-propagation.md`: contradiction: the group's brief requires the flow board published beside the plan table through `state_docs.py`, while the roster row's carry 3 requires it to be a section of the plan page and not a third page; neither text says which supersedes, so this PR follows the brief and the page integration is carried above. Carry: R10-ORCH-PLANPAGE

