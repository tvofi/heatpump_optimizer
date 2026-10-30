CLOUD PROBE seat for tvofi/heatpump_optimizer, topic r10-readme-graphics, at head d99cadb1235a5e40e250466e656c41c7ce88e641. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: a read-only probe. Measure what the brief below asks against the tree at d99cadb1235a5e40e250466e656c41c7ce88e641 (`git fetch origin d99cadb1235a5e40e250466e656c41c7ce88e641`); change no tracked file and send no code to any ref.
Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh r10-readme-graphics <result.md>`, which pushes refs/heads/handoff-body/r10-readme-graphics; that push is the return signal. A return push carries only your own result tokens.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
PRE-STUDY seat (designer.md's pre-study shape, decision 0014), new topic R10-README-GRAPHICS, tvofi/heatpump_optimizer at origin/main. Contract: dev/governance/roles/designer.md at origin/main. You produce a design note. Never write production code, and never open a PR.
OWNER REQUEST (tvofi, 2026-10-30): "Home assistant marketplace doesn't seem to be able to show some of the README graphics, including the mermaid diagrams. Do a pre-study on converting the front page README graphics to formats that can be rendered in home assistant marketplace, plan how to do it efficiently within the ongoing programme and fold it into the plan. Use real homeassistant 2026.11.0b1 if needed."
Do:
1. Inventory every graphic in README.md (and anything it pulls in): mermaid blocks, SVGs, relative-path images, HTML <img>/<picture>, badges, GIFs. For each, record kind, path or line, size, and whether it renders on GitHub.
2. Measure what the HA marketplace (the HACS/HA store repository view) actually renders. Use real Home Assistant 2026.11.0b1 if needed (pip install homeassistant==2026.11.0b1 in a venv; the frontend's ha-markdown renderer / its markdown sanitizer is the thing to read). Establish with evidence:
   - whether mermaid is supported (expect not);
   - whether relative image paths resolve;
   - whether SVG is allowed by the sanitizer;
   - whether <picture>/dark-mode sources work;
   - the max width.
   Cite the frontend source file and line for each rule, or a rendered screenshot. A rule without evidence is not a finding.
3. Design the conversion:
   - pre-rendered images, e.g. mermaid to SVG or PNG via mermaid-cli, committed with their source;
   - absolute raw.githubusercontent URLs pinned to a tag or branch versus relative paths;
   - light/dark handling;
   - a regeneration check so a diagram source and its image cannot drift. That check is a tracked self-tested instrument or test, wired into CI and classified per tests/closure.py.
   Weigh 2-3 alternatives. Keep GitHub rendering intact. Note D5/D6 docs-claim and tests/entities.py implications, and that README is outside writing-for-agents.md.
4. Plan it into the programme efficiently: size (S/M/L), files and hot files, `after` dependencies against the live roster (git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json), and whether it should fold into an existing group, e.g. a docs or CATALOG/MARKETPLACE-adjacent group such as R10-CATALOG-PR, rather than be a new one. Give a ready-to-append roster group JSON entry (group, lane, kind, size, files, after, brief, fixerModel, reviewerModel). Write its brief so tools/policy/brief_lint.mjs passes: no backticked symbols that don't exist yet, and no literal counts.
Deliverable: the note at handoff-body/r10-readme-graphics via bash tools/audit/seat/body_push.sh r10-readme-graphics <note.md>, with the roster JSON entry in a fenced ```json block under a heading "## Roster entry". If a hook refuses you, stop and report.
