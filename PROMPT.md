CLOUD PROBE seat for tvofi/heatpump_optimizer, topic r10-readme-graphics-r2, at head ca0a6cfbc2e5538e6e2220793831443719ff6e98. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: a read-only probe. Measure what the brief below asks against the tree at ca0a6cfbc2e5538e6e2220793831443719ff6e98 (`git fetch origin ca0a6cfbc2e5538e6e2220793831443719ff6e98`); change no tracked file and send no code to any ref.
Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh r10-readme-graphics-r2 <result.md>`, which pushes refs/heads/handoff-body/r10-readme-graphics-r2; that push is the return signal. A return push carries only your own result tokens.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
DESIGNER seat (round 2 of 3), topic R10-README-GRAPHICS. Your round-1 note is handoff-body/r10-readme-graphics at e995b815. The design review returned revise, at handoff-body/r10-readme-graphics-drev (fe1d5b7f); read it in full.
Fix the one revise point, the "## Roster entry":
- Set `files` to the design's actual edit set: README.md, the new generator script, the sidecar manifest, the diagram PNGs (or their directory), the finder harness under dev/audit/harnesses/, the tests/doc_claims.py and tests/closure.py classification, and the CI wiring. Do not list docs/img/readme/render.mjs unless you edit it.
- Add tests/doc_claims.py to `hot_files`, and tests/closure.py too or a stated reason not to.
- Re-run brief_lint on a scratch roster with the entry appended.
Keep everything else, and carry the reviewer's P2 note (a real 2026.11 instance or a screenshot) into the fixer brief.
Return the note via body_push.sh r10-readme-graphics <note.md>. Never write production code, and never open a PR. If a hook refuses you, stop and report.
