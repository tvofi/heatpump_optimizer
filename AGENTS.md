# AGENTS.md

A harness that loads this file and not `CLAUDE.md` (ZCode, Codex) is still
inside this repository's policy: the index is `CLAUDE.md`, at the root, and it
binds this seat from the first action here. Read it before acting; this file
defers to it everywhere and states no policy of its own.

Three load rules, for a seat with no `CLAUDE.md` in context: `.claude/rules/`
is generated from `dev/governance/rules/` and binds when a read matches its
`paths:` globs; roles are `dev/governance/roles/*.md`, dimensions
`dev/governance/dimensions/*.md`; `.cursor/rules/*.mdc` is generated the same
way, and a hand edit of either copy is drift `--check` refuses.
