Fix review: merge bcce9c14b440f60315bb28646e9417f9ca200180

bus-nonce: 09679636dffe6fbec1f562cda1b41fef

## Round

Round 1 of this review seat for #2994 (no earlier verdict on this PR was read).

## Findings

- Surviving mutant: `roster_lib.DESIGN_SIZES = ("L", "XL")` -> `("L",)` passes every self-test (roster_lib 52/0, orchestrator_tick 218/0, roster_edit 125/0, cloud_dispatch 100/0). XL eligibility is unpinned: R10-L2 (XL) in the tick fixture is a null control by its undispatched predecessor, and the dispatch fixture has only an L group. Wanted: one XL arm in cloud_dispatch's group checks (designer accepted / fixer refused without verdict). Evidence ev/mut-m4-*.txt, ev/mut-m4b-*.txt. Carry: R10-FLOW-DESIGN-STAGES
- Surviving mutant: bus.sh `push-design-verdict` revise grammar `\ revise\ ([0-9a-f]{40})\ [a-z-]+$` -> `\ revise\ ([0-9a-f]{40}).*$` passes bus self-test 110/0; no arm pins that a `revise` line needs its `<class>`, nor that a well-formed `revise` is accepted. Evidence ev/mut-m9-bus-revise-grammar.txt. Carry: R10-FLOW-DESIGN-STAGES
- `cloud_dispatch.design_approved` fetches `design-verdict/<group>` and reads `FETCH_HEAD:verdict.md`; bus.sh's own header comment (and append_commit) records that FETCH_HEAD is per-worktree state another fetch may overwrite between fetch and read. Reading the verdict by the sha `ls-remote` answered would close the same race here. Carry: R10-FLOW-DESIGN-STAGES
- Case mismatch between readers: `orchestrator_tick.designs_owed` lowercases the `design/*` names and the group id, while `bus.sh` and `cloud_dispatch` match `design/<group>` case-sensitively. A designer pushing `design/r10-big` for group `R10-BIG` silences `DESIGN OWED` while the fixer dispatch still refuses and the design reviewer finds nothing to review. Carry: R10-FLOW-DESIGN-STAGES
- The body's first figure is spelled `python3 tools/audit/seat/bus.sh --self-test (bash)`; run as written it exits 1 with SyntaxError (ev/bus.sh.selftest first run superseded); under `bash` it gives the quoted 110 checks, 0 failed. Carry: dismissed: wording slip only, figure re-derived under bash
- Carries 4-20 and the closing harness note route back to R10-FLOW-DESIGN-STAGES itself (carry_audit: 23 routed, 0 bad destination). When this merges and the group's stage closes to done, those items sit on a done group; the orchestrator must re-home or keep the group open. Carry: R10-FLOW-DESIGN-STAGES
- Pre-existing break, confirmed at base eec56f244 and at head: `dev/audit/harnesses/r10_flow_dispatch_mutants.py` aborts with "wait-line-dropped's pattern occurs 0 times" (ev/null-control-base.txt, ev/dispatch-mutants-head.txt). Not this diff's; the body carries it. Carry: R10-FLOW-DESIGN-STAGES

## Evidence

- RESULT head measured: bcce9c14b440f60315bb28646e9417f9ca200180, still the tip of fix/r10-flow-design-stages at verdict time (ls-remote). The body names authored code head 1322fcf5e and this merge head; the head's last commit merges origin/main eec56f244.
- RESULT roles freshness: `git diff $(merge-base)...origin/main -- dev/governance/roles/` empty.
- RESULT review packet: rendered locally, Refusals none; advisory only HPO_BUS_TRAIN_STATE unset.
- RESULT merge: `git merge-tree --write-tree origin/main(e77418f9b) bcce9c14b` exit 0, tree 43687d00e (ev/merge-tree.txt).
- RESULT VERSION, manifest, RELEASE_NOTES, roles and golden fixtures untouched in the three-dot diff (ev/untouched.txt); no claim file touched, so step 4 has nothing to compare.
- RESULT figures re-derived at head: bus.sh (bash) 110/0, cloud_dispatch 100/0, orchestrator_tick 218/0, roster_edit 125/0; additionally roster_lib 52/0, roster_sync 75/0 (ev/*.selftest.txt). entities/structure/prepr were not re-run here: they are covered by CI's closures, fast, and policy lanes, all green.
- RESULT mutation proof (the body's three, re-run): m1 `if not design_approved` -> `if False`: 4 FAIL, matching the body's names; m8 bus `[ "$tip" = "$sha" ] || die` -> `true || die`: 1 FAIL; m7 tick dropping `not rl.needs_design(g)`: 2 FAIL. All killed.
- RESULT own mutants: m2 approve-any-sha (1 FAIL), m3 design role for any size (1 FAIL), m5 predecessor gate (2 FAIL), m6 stage gate (2 FAIL), m10 bus no-tip guard (1 FAIL) all killed; m4/m4b and m9 survived (Findings).
- RESULT null control at base: `cloud_dispatch.py --role designer` refused (argparse "invalid choice: 'designer'", rc 2; the body's quoted wording "role must be one of" is the render-path message, so the refusal is the same but the text differs).
- Finder's harness: none is named or committed for this group. This is a tooling group (decision 0014 mechanisation); the self-test arms and my mutants are the instrument. I built no harness of my own beyond the mutant script in this transcript.
- Class: the body states one seam per instrument (bus writer, dispatch gate, tick line, stage vocabulary) and names no enumeration rule. The design-ref readers I found are bus.sh design_tip, cloud_dispatch design_tip/design_approved, and orchestrator_tick designs_owed/design_builds; all are in the diff or pre-existing. The case-handling split is the one inconsistency (Findings).
- CI at head (check-runs API, 37 runs, all concluded): every run success, skipped or neutral (CodeQL neutral); no red check, so step 11 owes nothing (ev/check-runs.txt). tests/mutation green; this diff writes no custom_components/ line, so it draws no production mutant.
- Architecture: arch-score success; the additions reuse append_commit and roster_lib, and there is no budget file or closures change in the diff.
