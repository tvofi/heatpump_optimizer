R11-SEAM-governance-text (ADR-010): policy and programme prose with a false or unresolvable sentence, re-truthed against the code it describes. Text only; no instrument code (architect note). Policy files: merges on the owner's approving review.

Findings fixed: D6-s5-01, D6-s5-02 (with D6-s5-04 merged in), D6-s5-03, D6-s5-05, D6-s5-06, D6-s5-07, D6-s5-08, D6-s7-02, D11-s2-04, D15-s1-02. D6-s2-02 and D6-s2-03 (merged into D6-s5-02) are not fixed here: Forward-carry. No finding reads 0 at the base.

Decisions:
- D11-s2-04: each duplicated mandate stays in its owning file and the copy becomes a pointer: the cost inequality in `defect-root-cause.md` (`root-cause.md` points), the retirement constraint in `standing-tick.md` (`standing-roster.md` points), the merge-tree check in `claim-files.md` (steward `SKILL.md` points), the owner's D4/D5 brief in `D4.md`/`D5.md` (the criteria files point). `RULINGS.md` drops, by its own rule (1), the 2026-10-24 entry `D11.md` states and the 2026-11-13 d5/d6 quote `D6.md` states. Owner's-words briefs (`D4.md`, `D5.md`, `D6.md`, `D11.md`) are untouched. Left for the owner: the `CLAUDE.md`/`orchestrator.md` section 8 pair (recorded deliberate), the four criteria files' shared provenance sentence, and the decision-history pairs (0001/0006, 0007/0009), which are records.
- D15-s1-02: step 2 names the gate `debug_ingest.py` runs (stage 2 over the replay half; its stage 2b is the planted-credential arm) and, over the rest of the download, a credential-key rule accepting the `**REDACTED**` marker. The finding's coordinate rule for the rest is not stated: `D15.md` sits at its `policy_lint.mjs --budgets` token cap with this sentence; the replay half's coordinates are `export.violations`'. No production change (the finding's scope).
- D6-s7-02: each of the nine sentences re-truthed, or rewritten as a pointer to the file owning the rule; the `web-fix-wave.js` sentence describes the log only (the finding names the stop a lead outside it).
- Caps: `policy_lint.mjs --budgets` refused the first wording in `D15.md`, `tests/README.md`, `writing-for-agents.md` and `orchestrator.md`; each sentence was cut to a pointer, no cap raised.
- Alternatives lost: deleting the stale plan sections (they carry protocol a fresh session reads); restating the gate-lock sets in `tests/README.md` (a copy of `gate-scoping.md`'s lists, the duplication D11-s2-04 removes).

## Head

`9a2cb31001706c9abf4f65763ad88441de0930b8`, measured against origin/main `bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f` (2026-11-18T13:34Z).

## Mutation proof

No in-tree check reads these sentences (the findings' shared mechanism), so the proof is the finder harnesses and the companion below. Reverting `dev/governance/rules/gate-scoping.md` and `dev/governance/dimensions/D15.md` to the base: companion `s5_02_rewrite_path_exists=0`, `s1_02_step2_scopes_replay_half=0`, `s1_02_step2_accepts_marker=0`; `node tools/policy/rules_sync.mjs --check` refuses (`2 file(s) out of date`), which is generated-copy drift, not the stale path. Restored.

## Null control

At the base `bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f` every finding reproduces (Figures, left of each arrow); `claims.py --only c_main_guards` reads true at both ends (the finder's own null control); `claims.py --only c_brief_exclude` null arm `claude_symbol_found_null_control=0`.

## Figures

Harnesses from the plan export `819aa2e354b4e5baaf824b8568fd72bea8168a75` (`$EXPORT/dev/audit/rounds/round11`), cwd = tree root, `PYTHONPATH=tests/hastub PYTHONUTF8=1`; base `bc658f9d` -> head `9a2cb310`.
- `$EXPORT/dev/audit/rounds/round11/D6/s5/claims.py --repo . --only <c>`: for c_mock, c_fix_review_j5, c_round4_d6, c_brief_exclude, c_handover_docs, c_unleased, c_instrument_dirs, c_worktree_apply, `false_or_stale[...]` 1 -> unit gone (`checked_units=0`): the harness locates the wrong sentence, so the head is read by the companion. c_event_hub: `false_or_stale[tools/audit/archscore/ABOUT.md]` 1 -> 1: the harness searches the basename `event_hub_writes.py` and the citation is now the path it names nearest; companion `s5_08` reads the property.
- Seam rule `$EXPORT/dev/audit/rounds/round11/D6/s5/assemble.py --repo .` (the s5 directory copied to the tree root, removed after): `false` 3 -> 0, `stale` 6 -> 1; the one stale row is the c_event_hub row above.
- `$EXPORT/dev/audit/rounds/round11/D6/s2/probes.py --probe gov_paths`: `gov_paths` 2 -> 2 (`fixer.md:104`, `orchestrator.md:73`; Forward-carry).
- `$EXPORT/dev/audit/rounds/round11/D6/s7/plan_claims.py --repo .`: lines starting `WRONG` 9 -> 0.
- `$EXPORT/dev/audit/rounds/round11/D11/s2/policy_health.py --list`: `dup_units` 16 -> 10, `rulings_overlap` 1 -> 0; the 10 left are the dispositioned pairs above (1 deliberate, 8 decision history, 1 provenance sentence).
- Companion `python3 -I companion.py <tree>` (sha1 `9c214369c10aae463525185f6ed01ef9487f2e24`, text below), base -> head: s5_01_only_mock_claims 1->0, s5_01_fix_review_j5_pointers 1->0, s5_02_rewrite_path_exists 0->1, s5_03_stated_minus_applied 1->0, s5_04_names_docs_as_handover_home 1->0, s5_05_one_lease_wording 1->0, s5_06_listed_dirs_absent 15->0 (15 -> 6 listed), s5_07_documented_flags_unparsed 1->0, s5_08_cited_resolves 0->1, s1_02_step2_scopes_replay_half 0->1, s1_02_step2_accepts_marker 0->1. `s5_04_names_living_handover` reads 0 at both ends: the sentence now names no location, the paragraph's first sentence does.
- `node tools/policy/policy_lint.mjs`: rc 0 at both ends, `TOTAL: 0 error(s)`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2732 ENTITY CHECKS PASSED` at the head.
- `tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED`, scope `tests/entities.py`.
- D15-s1-02's `privacy_gate.py --bundle B` not run: it needs a debug bundle not in the tree.
<!-- figure-block: scope-line mb=bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f head=9a2cb31001706c9abf4f65763ad88441de0930b8 -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

<details><summary>companion.py</summary>

```python
"""Companion for R11-SEAM-governance-text: apply each finding's property to the text at a tree.
usage: python3 companion.py <tree>   (prints RESULT lines; no conclusion printed)"""
import re, sys, pathlib, subprocess
T = pathlib.Path(sys.argv[1]); rd = lambda p: (T / p).read_text()
ex = lambda p: (T / p.rstrip('/')).exists()
def res(k, v): print(f"RESULT {k}={v}")
a = rd("dev/audit/README.md")
res("s5_01_only_mock_claims", a.count("only `unittest.mock` use"))
res("s5_01_fix_review_j5_pointers", a.count("`briefs/fix-review.md` §9"))
m = re.search(r"A gate run rewrites `([^`]+)`", rd("dev/governance/rules/gate-scoping.md"))
res("s5_02_rewrite_path_exists", int(ex(m.group(1))))
m = re.search(r"tracked tree \(not ([^)]*)\)", rd("dev/governance/rules/brief-citations.md"))
stated = set(re.findall(r"`([^`]+?)/?`", m.group(1)))
lint = rd("tools/policy/brief_lint.mjs"); e = re.search(r"SYMBOL_GREP_EXCLUDE\s*=\s*\[([^\]]*)\]", lint)
applied = set(x.lstrip(':!').rstrip('/') for x in re.findall(r"'([^']+)'|\"([^\"]+)\"", e.group(1)) for x in x if x)
res("s5_03_stated_minus_applied", len({s.rstrip('/') for s in stated} - applied))
w = rd("dev/governance/rules/writing-for-agents.md")
res("s5_04_names_docs_as_handover_home", w.count("exactly one handover under `docs/`"))
res("s5_04_names_living_handover", int("exactly one handover, `dev/programme/HANDOVER.md`" in w and ex("dev/programme/HANDOVER.md")))
r = rd("tests/README.md")
res("s5_05_one_lease_wording", r.count("every other script runs unleased"))
i = rd("tools/audit/seat/INSTRUMENTS.md"); m = re.search(r"(Directories here that are records|The records are not here).*?indexes them", i, re.S)
dirs = [d for d in re.findall(r"`([^`]+/)`", m.group(0))]
here = m.group(0).startswith("Directories here")
missing = [d for d in dirs if not ex(("tools/audit/seat/" + d) if here else d)]
res("s5_06_listed_dirs", len(dirs)); res("s5_06_listed_dirs_absent", len(missing))
h = rd("dev/programme/HANDOVER.md"); g = rd("tools/audit/worktree_gc.sh")
flags = set(re.findall(r"`worktree_gc\.sh[^`]*?(--[a-z-]+)", h)) | set(re.findall(r"`worktree_gc\.sh`[^.]*?\(`(--[a-z-]+)`", h))
flags |= set(re.findall(r"\(`(--[a-z-]+)` previews\)", h))
res("s5_07_documented_flags_unparsed", len([f for f in flags if f + ")" not in g and f + "|" not in g and f not in re.findall(r"--[a-z-]+\)", g) and f"{f})" not in g]))
ab = rd("tools/audit/archscore/ABOUT.md"); m = re.search(r"R10-LIVESTATE carries the 41 -> 38 control\s*\(`([^`]+)`\)", ab)
cited = m.group(1); hits = subprocess.run(["git","-C",str(T),"ls-files"],capture_output=True,text=True).stdout.split()
res("s5_08_cited_resolves", int(cited in hits or sum(1 for f in hits if f.rsplit('/',1)[-1] == cited) == 1))
d = rd("dev/governance/dimensions/D15.md"); m = re.search(r"2\. \*\*Privacy gate\.\*\*[^\n]*", d)
res("s1_02_step2_scopes_replay_half", int("replay half" in m.group(0)))
res("s1_02_step2_accepts_marker", int("REDACTED" in m.group(0)))
```
</details>

## Approval

Awaiting the owner's approving review.

## Red checks

none

## Forward-carry

- D6-s2-02, D6-s2-03 (`fixer.md:104`, `orchestrator.md:73` cite `docs/decisions/`): unfixed pending an orchestrator ruling. Respelled at `dev/governance/decisions/`, `node tools/policy/policy_lint.mjs` exits 1 with `FIXTURE VACUOUS: checkCitationPresence reported 0 of 2 earned exclusions`: its arm B elides `EXCLUDED_BECAUSE_CITED` keys by their `docs/decisions/` spelling, so a citation at the live path is never elided. The fix moves those keys (or the elision) to the live path, instrument code this group's architect note bars. Control: at this head, with both citations as at the base, it exits 0. Carry: dismissed: held for the orchestrator's ruling on instrument code; D6-s2-02 and D6-s2-03 stay open in the round register
- D11-s2-04's mechanisation (a `policy_lint` class over text_ledger units refusing a new verbatim cross-file unit) is not built: the architect note bars instrument code. Carry: dismissed: architect note for R11-SEAM-governance-text bars instrument code; the proposal stays in the round register for proposal triage
- D6-s7-02's lead (`web-fix-wave.js`'s merge chain does not stop on a red main) is outside the finding by its own scope. Carry: dismissed: the finding names it a lead to D11-s2, already in the round register

## Friction

- frugal-inline-guard: contradiction: the brief's "do your work inline, with no subagents" met the frugal guard's inline-read budget; ruled by the orchestrator's inbox line 1 (delegate discovery reads to haiku/sonnet workers). Carry: dismissed: ruled by the orchestrator's inbox line 1
