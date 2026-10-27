Flow board (Lean study K1), group `R10-FLOW-BOARD` (lane IN), one of the seven groups under the #2715 tracker, which closes when the last of them merges. The programme's throughput against the owner's demand of one roster group merged per hour was measured nowhere, so no flow change could show it worked.

This adds `merge_throughput.py flow`: it reads git alone -- the first-parent log of the tree, the review/verdict bus refs through `review_strength`'s `PREFIX_RE`/`VERDICT_RE` grammar, the roster through `roster_lib` -- and prints, per rolling hour and per 24 h, roster groups closed against takt 1.0, fly-ins closed, main moves split group-carrying/record/roster-edit/fly-in, first-pass fix-review yield with its blocked-class mix, and lead time per size, plus a WIP-by-lane snapshot. The bus is read with one `git log` over every review ref, not `review_strength.load()`'s per-ref reads; the two readers return the same verdict set at this head. `state_docs.py` publishes the board as `FLOW-BOARD.md`, second in `DOC_NAMES`, so the beat carries it beside the plan table. A source that cannot be read prints UNAVAILABLE with its reason, never a zero. `.github/workflows/governance.yml` already ran `merge_throughput.py --self-test` in the instrument-self-tests job; the diff adds only a comment there naming the flow arms.

The roster's carries this PR discharges: self-test hygiene (b), the fixture builds any git repository through `tests/throwaway_git.py` (`tests/throwaway_git.py --check` prints `0 raw git init or clone site(s) refused`); (c), the diff adds no push site; (d), `## Red checks` below. (a) does not arise: no seat-selftest mutant is added. Carry 1 names the pre-study, not work. Carries 2, 3, 5 and 6 remain and are routed in `## Forward-carry`.

The fixer's scoped gate passed at this head; its mode line and `tests/structure.py`'s ratchet are re-derived in `## Figures`, and the selected scripts' run is the fixer's.

Size: `tools/audit/merge_throughput.py` grows 780 added lines (778 net) -- over `fixer.md`'s ~400 guide -- because the six measure families, the markdown renderer and the CLI land in the one file the group names; the brief names that file and no new one, and no tracked file is added.

## Head

`4c62b9804c2974aca296ca8dd4cc8d5717cc3e71`: the reviewed code head `c35a4e313f62838b12706de23f3e2658fd3fc11d` with `origin/main` at `67178dc6a589cf95d2ce7cff36d8bbf17343e8dc` merged in by the orchestrator (no conflict; the merge changes none of the four files). The base is `git merge-base origin/main 4c62b98` = `67178dc6a589cf95d2ce7cff36d8bbf17343e8dc`. Everything below was measured at this head, over `67178dc6a...4c62b9804`.

## Mutation proof

The fixer's five mutants, re-run at this head; each reds a named `--self-test` arm:

- deleting the `record_prefix` branch -> `FAIL flow: main moves split group/record/roster/fly-in: got (1, 0, 1, 2), want (1, 1, 1, 1)` and `FAIL flow: --record-prefix fix/ reclassifies the group and roster merges: got (1, 0, 2), want (0, 2, 2)`.
- zeroing the close sum -> `FAIL flow: roster groups closed: got 0, want 1` and `FAIL flow board renders '1 / 24.0'`.
- removing the critical-set test -> `FAIL flow: WIP by flow lane: got {'A': 0, 'B': 1, 'C': 0, 'F': 1}, want {'A': 1, 'B': 0, 'C': 0, 'F': 1}`.
- `judged = window` -> `FAIL flow: first-pass yield is the first verdict's kind: got (1, 2), want (0, 1)`.
- returning zeros for an absent bus -> `FAIL flow: no review refs reads UNAVAILABLE, not zero: got ((0, 0), False), want (None, True)` and `FAIL flow: ...and the reason names the bus: ''`.

Failing test first: the fixer reports that the arms were added before the production code and failed rc=1 with `NameError: name 'Path' is not defined`; the pre-fix state does not exist at this head, so that arm is the fixer's report and not re-run here.

## Null control

At `--self-test` the unchanged fixture rendered twice is byte-identical (`ok flow null control: an unchanged fixture reads identical`), and its companion moving `--until` past the events changes the board (`ok flow null control is not vacuous: a moved until changes it`). The fixture pins the counts: 1 group-carrying merge, 1 record, 1 roster-edit and 1 fly-in (`ok flow: main moves split group/record/roster/fly-in` = (1, 1, 1, 1)), 1 roster group closed, one blocked-then-merged verdict (first pass 0/1), one `harness` blocked class. On the live refs no merge fell in the trailing hour, so the real run's 1 h column reads zeros and the fixture is what pins the split; the real board at this head is byte-identical to the fixer's.

## Figures

- three-dot diffstat, 4 files changed, 844 insertions, 33 deletions: `git diff --stat 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc...HEAD`.
- `tools/audit/merge_throughput.py` +780/-2: `git diff --numstat 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc...HEAD`.
- 646 non-blank, non-comment added lines in `merge_throughput.py`: `git diff -U0 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc...HEAD -- tools/audit/merge_throughput.py | awk '/^\+/ && !/^\+\+\+/ && $0 !~ /^\+[[:space:]]*$/ && $0 !~ /^\+[[:space:]]*#/' | wc -l`.
- scoped-gate mode line, `MODE: SCOPED -- 2 script(s) run, 31 scoped out`: `python3 tests/closure.py select --diff 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc`.
- structural ratchet, `STRUCTURE RATCHET PASSED`: `python3 -I tests/structure.py`.
- the flow arms, the fixture's exact counts and the null control: `python3 -I tools/audit/merge_throughput.py --self-test`.
- `state_docs self-test: all checks passed`: `python3 -I tools/audit/seat/state_docs.py --self-test`.
- the real flow board at this head, 1 h column zeros included: `python3 -I tools/audit/merge_throughput.py flow --repo . --roster-ref origin/handoff/audit-r10-roster --until 2026-10-27T00:00:00Z`.
- architecture score, `dS +0.0000 NULL, no gate metric rose`: `python3 -I tools/audit/archscore/gate.py --base 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc --head 4c62b9804c2974aca296ca8dd4cc8d5717cc3e71 --body <this body>`.
- 0 raw git init or clone sites: `python3 -I tests/throwaway_git.py --check`.

## Red checks

`none`. At the merge base `67178dc6a` the commit's check-runs carry no failure conclusion (`gh api repos/tvofi/heatpump_optimizer/commits/67178dc6a589cf95d2ce7cff36d8bbf17343e8dc/check-runs --paginate`), the nightlies at `67178dc6a` are green, and the branch's two commits have no check-runs before the pull request opens.

## Forward-carry

- The plan-page seam (the roster row's carries 2 and 3): the board is published as a flow-board document beside the plan table through `state_docs.py`, as the group's brief asks, and is not a section of `plan_page.py` drawn from the plan's own model, so "one plan model; the flow board is a section of that page, not a third page" is not met here. Carry: R10-ORCH-PLANPAGE
- The token measurement (the roster row's carry 6, tvofi's 2026-10-24 recommendation (e)): IE = input + 1.25 x cache write + 0.1 x cache read + 5 x output tokens read from the local session transcripts, printed per day, per role and per merged content pull request with the window and transcript count beside each figure, as a flow-board section in `merge_throughput.py` -- not built here. Control: a fixture transcript set with known token counts reproduces its IE, and a set with one seat removed lowers the day figure by that seat's IE; it does not cover cloud seats. Carry: R10-FLOW-TOOLKIT-MODEL
- The owner-gate count (the roster row's carry 5): `orchestrator_tick.py` still flags a gate whose only text is `mandated approval under <id>`; counting such a gate as cleared while a mandate in force (scope all) covers it, option A and test-first, is not touched here. Carry: R10-ORCH-LEDGER

## Friction

- `finding-propagation.md`: contradiction: the group's brief requires the flow board published beside the plan table through `state_docs.py`, while the roster row's carry 3 requires it to be a section of the plan page and not a third page; neither text says which supersedes, so this PR follows the brief and the page integration is carried above. Carry: R10-ORCH-PLANPAGE
