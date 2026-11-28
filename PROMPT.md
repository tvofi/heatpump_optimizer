CLOUD DESIGNER seat for tvofi/heatpump_optimizer, topic r11-ci-3885-rest, at head 98541868add741cd1967a82614d3b3b81b9178ef. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing. Seat key: group=- role=designer dimension=- model=claude-opus-5-5 seat=designer-r11-ci-3885-rest
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render designer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/designer.md from main, and follow it exactly. The base is 98541868add741cd1967a82614d3b3b81b9178ef (`git fetch origin 98541868add741cd1967a82614d3b3b81b9178ef`); name it in the note. Write no production code.
Output: write the note as design.md in a directory of your own and run `bash tools/audit/seat/bus.sh push-design r11-ci-3885-rest <design.md>`, which pushes refs/heads/design/r11-ci-3885-rest; that push is the return signal, and the design/r11-ci-3885-rest tip is the SHA you hand off. You may push only to that ref. Open no pull request, push no handoff ref and write no delivery row.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
Group R11-OUTSIDE-CI-3885-REST: the outside item #3885 (reducing GitHub Actions usage). It is in round 11 and on the critical path as an outside item. Two of the owner's 11-25 items have not landed (#3394 comment 7157667401):

(2) Seeded 30% case sampling in tests/features.py and tests/entities.py on pull requests. The full set still runs on pushes to main and in the nightly run.

(3) Per-case test selection by diff, the parts after P1. P1 merged as #3896: the case splitter, the span recorder and the per-span table. Read the existing design on refs design/r11-ci-3885-queue and design-verdict/r11-ci-3885-queue, plus any design/*case-select* ref.

You are the designer (dev/governance/roles/designer.md). Write the architect note at design/r11-ci-3885-rest covering both items:
- the parts and their order;
- how sampling interacts with case selection;
- the seed source, chosen so a red reproduces;
- the null control: an unsampled run must still select every case on a main push.

Do not write production code. Name each later PR's fix shape and its harness.
