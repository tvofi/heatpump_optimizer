CLOUD DESIGN REVIEWER seat for tvofi/heatpump_optimizer, topic R10-COP-GATE, at head cabfaadc3a13f61eaf0303918c7b1d5beda9c07c. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/design-review.md from main, and follow it exactly. Review the design at refs/heads/design/R10-COP-GATE, SHA dc18f2f8582bbfcc782c94e6f407c2df9d2ffba6: `git fetch origin dc18f2f8582bbfcc782c94e6f407c2df9d2ffba6` and open a detached worktree there. The base the note names is judged against cabfaadc3a13f61eaf0303918c7b1d5beda9c07c. Rerun nothing; there is no code.
Output: write verdict.md, whose first line is exactly `Design review: approve dc18f2f8582bbfcc782c94e6f407c2df9d2ffba6` or `Design review: revise dc18f2f8582bbfcc782c94e6f407c2df9d2ffba6 <class>` (the class is lower-case letters and dashes), and run `bash tools/audit/seat/bus.sh push-design-verdict R10-COP-GATE <verdict.md>`, which pushes refs/heads/design-verdict/R10-COP-GATE and refuses a design that has moved; that push is the return signal. You may push only to that ref. Write no design, open no pull request and push no code.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
DESIGN REVIEWER seat for R10-COP-GATE part D (CRITICAL PATH), at design head dc18f2f8582bbfcc782c94e6f407c2df9d2ffba6 (design/R10-COP-GATE, `dev/programme/designs/R10-COP-GATE-D.md`, with the probes under `dev/programme/designs/R10-COP-GATE-D-probes/`). Contract: dev/governance/roles/design-review.md at origin/main.
The design covers carry 12: the learned top reaching the plan. Its parts:
- A new pure ruling in draw_range.py decides the range a solve may book. coordinator.py wires it into _solve_hubs and arbiter_inputs, and publishes it from _learning_view.
- The learned top L replaces the configured maximum only when L < (1 - AGREE_TOLERANCE) * cfg_max; otherwise the configured figures stand byte for byte. The minimum becomes min(cfg_min, top).
- There is a reason code per case.
- No threshold changes.
Attack it:
(1) The two invariants the probe shows. The learned top must never be written into the live configured params, or the fold key cuts a 60-sample window to 1. The arbiter must map the plan's steps against the same band the solve used, or a 3.0 kW top step writes 42.50 degC instead of 55.0. Re-run `band_probe.py` against part 6's head (handoff/r10-cop-gate-p6, f40be9c9).
(2) Is "no threshold change" true? The group's architect note forbids a threshold change, but this changes what the plan books. Rule whether the scope ruling is sound.
(3) The decision not to absorb the `_propagated_slab` lead.
(4) The order (after R10-CEILING-PROBE and part 6) and the hunk overlap with part 6.
(5) The ratchet payment: moving one helper out of the class.
Return `Design review: approve <sha>` or `Design review: revise <sha>` with the revise points. Put your verdict on the ref your bus nonce names.
