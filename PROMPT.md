CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-prepr-cap-slot, at head c3a279e3252a8b57bb00b5a677318cd4fe20387f. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name seat && git config user.email seat@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch c3a279e3252a8b57bb00b5a677318cd4fe20387f for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-prepr-cap-slot before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-prepr-cap-slot, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-prepr-cap-slot, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-prepr-cap-slot <body.md>`, which pushes refs/heads/handoff-body/r10-prepr-cap-slot; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-prepr-cap-slot`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-prepr-cap-slot. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
INTERIM TOOLCHAIN: this environment's cached venvs are behind the locks (numpy, scipy, homeassistant, measured 2026-11-04). Before any measurement or golden run: `bash tools/audit/seat/cloud-setup.sh` and then `bash tools/audit/seat/cloud-setup.sh --check`; also confirm `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'` against tests/requirements-ci.txt. If it cannot be refreshed say so in the body; CI remains the authority for goldens. Medium effort.

Fixers return only by refs, handoff/<topic> and body_push.sh; open no PR, post no comment; no Claude footers; no host paths.

SLOT-ARM PART of R10-PREPR-CAP: 19 carries are open on the roster; this part takes 11 of them: 25, 26, 23, 12, 16, 20, 6, 24, 19, 7, 15 (slot-take timing 25, 26, 23; refusals before the slot 12, 16, 20; prepr cost and its pins 6, 24, 19, 7, 15). The other open carries (9, 10, 11, 13, 14, 18, 21, 27) are a later part. Order inside the part: 26 and 25 first (they are one change), then 23, then the rest. The group brief below describes the slot-counted lease already merged; do not rebuild it.

`tools/pr/prepr.sh` runs unleased and each seat starts one independently, so the tick read 8+ concurrent preprs (each spawning its nested `--self-test`) and load hit ~168 on 8 cores; `nudge.md` §8's "up to four" is advisory — the tick counts and flags it, nothing blocks a fifth.

Take the gate lease beyond `stress.py`: `tests/gate_lock.py` gains a **slot-counted lease beside the exclusive one** — default **4** slots (a slot-count environment override, clamped to ≤ 4 without the owner), taken FIFO with the existing lease/expiry/orphan-steal machinery, released on exit; `needs-lease` grows a third answer **`slot`** beside `lease`/`none`. `prepr.sh` takes **one slot for its whole life** and exports a slot-label environment variable so its heavy steps (self-test ~172 s, mutants drive ~127 s, the scoped closures recordings) run *inside* that slot and do not re-acquire; `tests/derive_closures.sh` takes a slot only **standalone** (else two seats' four-lane derives stack to eight). The exclusive lease stays exclusive for the scripts whose numbers are comparable only alone — `stress.py` and, within the mutation pool, `harness_headers.py`. The rule: **machine-measuring ⇒ exclusive; multi-minute CPU-bound ⇒ join the four slots; seconds ⇒ no lease** (`structure.py` ~11.5 s and `layout.py` ~17 s are the seconds side; the recordings ≥ 69 s are the minutes side). `gate-scoping.md` and `nudge.md` §8 state the scope and that the lease — not the tick's count — is the enforcement.

**Measure first** (finding-propagation.md, carried from the lead): the run must show prepr taking and releasing a slot, four concurrent preprs admitted, a fifth queued, and a nested heavy step *not* re-acquiring; an independent reviewer is owed (this is the orchestrator's own instrument).

**Forward-carried:** (1) `gate-scoping.md` is policy and sits at its per-file line cap — the prose is line-neutral or the cap is re-recorded with the owner's approval; (2) `dev/governance/rules/*` is the canon and `.claude/rules/`, `.cursor/rules/` regenerate via `rules_sync`; (3) `nudge.md` is policy — the owner reviews it before merge.

**Identity and flow:** the seat pushes refs only, through `tools/audit/seat/handoff_push.sh` and `tools/audit/seat/bus.sh`; every GitHub write is the orchestrator's (decisions 0011 and 0013). Work from fresh `origin/main` in your own worktree under your ABSOLUTE scratch directory; stop only PIDs you started. Follow `dev/governance/roles/fixer.md`: failing test first, mutation proof, the finder's harness at both ends, a null control for every quantified claim, `GATE_SCOPE` auto, `tests/structure.py` before push. Every figure above is a snapshot at the finding's baseline: re-derive it at your merge base. Owner gate: **policy — `dev/governance/rules/gate-scoping.md` and `dev/governance/roles/nudge.md` need the owner's approving review.** Models: fixer sonnet, reviewer opus. Closing: the pull request names #2267 in prose with a closing keyword; the orchestrator verifies it closed after the merge.

After: none

Carry 6: From #2853 (R10-FLOW-JIDOKA p2) review 6434442876, item bbb4d32f, re-verified by the s9 residual sweep at origin/main 92588d581 (2026-11-01). Measured: tools/pr/prepr.sh step 6g triggers on `pinned_touched "$CR.paths" "$CLAIMS_DOCS"` (lines 338 and 3882) with CLAIMS_DOCS = README.md and docs/*.md only (295-296), while CLAIMS_INPUTS (314-334), the copy of what dev/audit/rounds/round4/D6/claims.py itself reads, also names DISCLAIMER.md, LICENSE, NOTICE, VERSION, hacs.json, .github/workflows, custom_components (strings.json, translations, services.yaml, manifest.json, the card JS), tests/entities.py and the rest. So a diff to strings.json or the card that moves the register skips 6g ("no change to README.md or docs/*.md", rc 3) and can reach CI stale under PREPR_SKIP_CLOSURES=1, #2609's class. The R10-FLOW-JIDOKA destination the review named is done. Fix: trigger 6g on the generator's read set (CLAIMS_INPUTS plus the generator itself and its directory), keeping the copy derivation as is; re-measure 6g's cost on such a diff against carry 6's 5 s cap. Failing test first: in prepr.sh's 6g self-test, a changed-paths file naming only custom_components/heatpump_optimizer/strings.json runs claims_reg_line (rc 0 or 1, not 3; it returns 3 today). Null control: a diff touching only tests/features.py, outside the read set, still skips with rc 3.

Carry 7: STRANDED CARRY 3 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 6; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: #2853 Forward-carry: "Carries 4, 7, 9 and 16, the base-pinned replay ... Not built" (roster [3],[6],[8],[15]); no live carry.

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
From #2625 (R10-RCA-BODY-LINT), RCA section 7: tools/pr/prepr.sh runs check-wave-script.mjs and the agreement lane from the branch copy, while governance.yml's wave-script job restores every pinned grader from the base before running them, so a branch that edits a pinned grader can pass prepr and go red in CI (P2a hit this). Fix shape is raise_red's: run the base's copy offline beside the branch's. Quick-check only (tvofi ruling: JIDOKA adds no full CI suite to prepr). Control: a branch editing a pinned grader so its base copy fails is refused by prepr.

Carry: R10-PREPR-CAP

Carry 12: STRANDED CARRY 19 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 10; triage id: P-N; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "Carries 11, 12 and 14, the --body-check parity extensions ... plus one grammar owner for ## Forward-carry. Not built".

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
P-N (triage batch 6): extend prepr.sh --body-check (what body_push.sh runs) so a return is refused for the classes open_pr's prepr still refuses it for: (a) run the agreement lane (agreement_py.py, local git only); (b) feed step 6d's unpinned-site list (ci_predict output body_push already holds) to the step-7d '## Unpinned sites' disposal check; (c) predict 'budget-raise-gate not named in ## Red checks' from the diff touching *_budgets.json. Failing fixture first per class, each with a null control (clean head passes, disposed sites pass). Do NOT run full prepr in body_push (M1 rejected in its header). Measure each refusal's base SHA first: a fixer cut before 2fe11ffbc is not a gap. Instances 2026-10-23: ORCH-LEDGER (agreement, 3 unregistered), INPUT-STALENESS (10 unpinned), #2620 r5 (budget-raise-gate unnamed).

Carry: R10-PREPR-CAP

Carry 15: STRANDED CARRY 22 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 15; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "Carries 4, 7, 9 and 16, the base-pinned replay ... Not built" (roster [3],[6],[8],[15]); no live carry.

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
From #2529 (body, item 8c6a3e6f), routed by routing audit 1 (2026-10-24): its destination R10-CI-LAYOUT is done and did not implement it (prepr.sh:2996 runs the head's .claude/workflows/field_coverage.mjs, not the base's registry over the head; no other pre-push step does). defect-root-cause: unenforced: a program added beside a pinned grader is refused by the base's `field_coverage` registry on the pull request that adds it, and no pre-push instrument runs the base's registry over the head, so the red surfaced only in CI.

Carry: R10-PREPR-CAP

Carry 16: STRANDED CARRY 23 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 20; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "Carries 15 and 21 ... Partly answered ... the rest of both jobs is not modelled".

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
Re-homed from #2772 body item 0a016c98 (R10-TRAIN-UPGRADE is done; orchestrator ruling 2026-10-25). The cheaper detector for the `tests / fast (3.14)` red: prepr should predict that red before handoff, so it no longer reaches CI first. Answer it as a jidoka stop at prepr, or record why no cheaper detector exists (defect-root-cause.md cost test).

Carry: R10-PREPR-CAP

Carry 19: STRANDED CARRY 26 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 24; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: 12 seat self-tests adopting pr_bounded: neither #2838 nor #2853 lists it built; no live carry.

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
From R10-UPDATE-PR-SIGNALS (#2825): the 12 seat self-tests outside that group's files that do not enter through pr_bounded -- body_patch, bus, ci-watch, cloud-setup, delivery_row, failure_logs, handoff_push, heartbeat, merge_pr, seat_venv, tick_loop and train -- must adopt the bound, a bound that survives a group KILL.

Carry: R10-PREPR-CAP

Carry 20: STRANDED CARRY 27 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 26; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "The round-1 census's HEAD-ONLY class needs a predicting detector. Not built".

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
From R10-FLOW-JIDOKA (#2838): the round-1 census's HEAD-ONLY class needs a predicting detector, not a reading one; step 7c can only read reds on commits already pushed.

Carry: R10-PREPR-CAP

Carry 23: STRANDED CARRY 56 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-RCA-BODY-LINT, index 0; triage id: dev/programme/triage/s6-batch39.md#P208; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: P208, appended after #2625 merged; no early `## Head` arm before the heavy slot in tools/pr/prepr.sh at origin/main (`git grep -n "P208"` empty; the body check runs at step 7).

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
Check the body's `## Head` before the expensive steps, not only at step 7 (P208/V128, from R10-BUFFER-STORE's 40-minute scoped prepr that took the heavy slot and then refused the body at `## Head` -- the local buffer-store log puts `REFUSE pr-body` before `ok figures`/`ok carry`/`ok unpinned sites` -- and from R10-FLOW-BOARD's body re-take that named `c35a4e313` against `4c62b9804`). `tools/pr/prepr.sh` must run the same `## Head` arm, the one that checks the body names the sha `git rev-parse HEAD` prints, before step 1b takes the heavy slot, and keep the step-7 call (the body check at 3435) because the head can move during the run (`update_pr.sh`/`open_pr.sh` merge `main` before pushing). Constraints: no second parser -- the early arm invokes the existing body check earlier and prints the same refusal line the late one does; the `## Approval` arm, keyed on the path list, may stay late because it needs the diff; `tools/audit/seat/body_push.sh`'s early body gate keeps its behaviour; self-test arms: a body whose `## Head` names another sha refuses before 1b's slot is taken, and a matching body runs every step exactly as today (null control). triage: dev/programme/triage/s6-batch39.md#P208

Carry: R10-PREPR-CAP

Carry 24: STRANDED CARRY 63 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, #2853 Forward-carry (never landed on the roster); triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: routed "Carry: R10-FLOW-JIDOKA"; the roster holds no "pinned by no check" text (count 0); JIDOKA done.

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
- Step 6g's repaired cost is pinned by no check: `prepr-13` guards that the derivation runs, not what it costs, so reintroducing a per-target interpreter would put 6g back over the 5 s cap with nothing failing; the margin at this head is 0.87 s CPU (4.13 against 5.0). Carry: R10-FLOW-JIDOKA

## Friction

none

Carry: R10-PREPR-CAP

Carry 25: Owner-ordered (tvofi, 2026-10-31, "do all of them"; evidence: triage batch 95 P346's deferral). tools/pr/prepr.sh takes a heavy slot at step 1b, before step 2 knows the gate scope. A prepr whose scope selects 0 scripts still queues for a slot: triage batch 95's own 0-script prepr waited 25 min 55 s in slot-take (2026-10-31). Build: derive the scope first; take the heavy slot only when the scope runs a script, or when a later heavy step (stress, mutation, card browser) needs it. A nested heavy step still joins the slot it inherits through HPO_SLOT_LABEL. Measure first, and state the rule: over today's prepr logs, count the 0-script runs and their slot waits. Control: a 0-script prepr reports no slot-take wait and the same verdict as before; a scoped prepr still takes its slot.
Evidence, triage batch 95 P346 (owner-ordered, at 56361734d): of 35 completed prepr logs, 29 ran no heavy step and held the slot a median of 0.9 min. The 8 of those with an exact start waited a median of 11.4 min for the slot (max 39.1). Caveat: the sample is mostly triage-seat logs; fixer preprs log under other names and are under-sampled, so re-count with them included.

Carry 26: From tvofi, 2026-11-01 ("does all of the opens really need a re run of the heavy scripts in prepr ... or can it be scoped"). Found: tools/pr/prepr.sh section 1b takes a heavy slot (gate_lock.py slot-take) for the WHOLE run before heavy_plan/heavy_skip have decided whether any heavy step runs. So a run whose heavy steps are all skipped by reachability still waits in the 4-slot FIFO (measured 36-107 min per run after 06:00 CET on 11-01, 12+ queued) to run seconds of light checks. Fix: run the light steps unleased; take the slot lazily, just before the first heavy step that heavy_skip/selftest_owed/the scoped gate does not skip, and keep it to the end; a run that skips every heavy step never takes one. Keep the fail-safe that a failed plan derivation runs every heavy step (and so takes the slot). Failing test first: a diff that reaches no heavy step completes prepr without a slot-take. Null control: a diff reaching the self-test takes exactly one slot before that step. Measure before and after: slot-wait minutes per prepr over a day.

(Roster carry indexes not in this brief: 0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 13, 14, 17, 18, 21, 22, 27: marked done/dismissed/moved, or left to a later part. Indexes above are the roster's.)
