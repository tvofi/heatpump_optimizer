# `role_pack.py`

- `role_pack.py` (tools/policy/) — renders one seat's policy pack: its
  contract under `dev/governance/roles/` (`fixer`, `fix-review`, `designer`,
  `design-review`, `root-cause`, `verifier`, `judge`, and `finder` for
  `COMMON.md`), every rule under `dev/governance/rules/` whose `paths:` globs
  the contract or `INSTRUMENTS.md` matches, and the `INSTRUMENTS.md` entry
  lines whose instrument the contract names, each framed and byte-equal to its
  file. CLAUDE.md is left out: the harness has already loaded it.
  `.claude/hooks/session-start.sh` writes the pack to `git rev-parse
  --git-path role-pack-<role>.md` and prints one `role pack:` line when
  `HPO_SEAT_ROLE` names a role; unset, the hook's output is unchanged. A file
  rather than the hook's stdout, because Claude Code keeps at most 10,000
  characters of hook output in context. An Agent-tool subagent runs no
  SessionStart hook, so a local seat's brief names `render <role> --out
  <path>` itself. When: a seat brief that would otherwise tell a seat to read
  its contract and this guide. `check [<role> ...] [--pack FILE]` refuses a
  paraphrased line, a missing or extra block, a line outside every frame and a
  pack larger than the files it frames; `--self-test` drives every role and
  one mutant per rule. Refusal: an unknown role exits 2, naming the roles.
