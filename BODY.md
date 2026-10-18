Part of #201

The orchestrator's recurring sweep lived only in one session's timer prompt, and its post-compaction policy check was a shell script in that session's scratch. Decision 0013 says an instrument the programme runs belongs in the tree. This change puts both there, written so any session or round can rebuild them.

- `tools/audit/seat/sweep_template.md`: the sweep's steps in order, with every session value a named `{{placeholder}}`. Its `## Placeholders` table is the only registry of those names. Each step names the instrument it runs by tree path and the rule file it carries out (`orchestrator.md`, `nudge.md`, `CLAUDE.md`). It restates no policy and calls itself a usage guide, as `INSTRUMENTS.md` does.
- `tools/audit/seat/sweep_render.py`: fills the template from a JSON overlay. It refuses, with exit 1 and nothing written, in these cases: a placeholder the overlay leaves unfilled, empty or non-scalar; a placeholder or overlay key the table does not declare; a declared name the sweep never uses; a cited `tools/`/`tests/`/`dev/`/`.github/` path or `CLAUDE.md` that is not in the tree; and a home directory in the rendered text that does not lie wholly inside one overlay value. The home-directory check uses `ref_privacy.py`'s `HOME_DIR` grammar, which owns that concern; the renderer does not keep a second copy of it.
- `tools/audit/seat/policy_reread_check.py`: the session script's predicate, with paths passed as arguments. It prints OK when the stamp is later than the newest `compact_boundary` in the transcript, and OWED otherwise. It parses the JSON `subtype` field instead of grepping the text, compares parsed instants (the old check cut off the compaction's fractional seconds), and fails closed. `--write-stamp` writes the stamp in the format the check reads.
- `.github/workflows/governance.yml`: both self-tests run in `instrument-self-tests` next to `tmp_paths.py` and `ref_privacy.py`. A self-test that runs nowhere can only be run by a seat that remembers it. The renderer's self-test renders the tracked template, so a step that cites an instrument the tree has since removed turns that job red at the next pull request.
- `tools/audit/seat/INSTRUMENTS.md`: an entry for each of the three new files.

Alternatives not taken: (a) a placeholder list kept inside `sweep_render.py`. That would be a second registry next to the table, and the two could drift apart. (b) Refusing only the macOS home prefix. `HOME_DIR` covers both the macOS and the Linux home-directory forms, and `tmp_paths.py` already imports the same grammar. (c) Leaving the self-tests unwired, which saves one workflow edit but leaves nothing to run them. The cost of (c)'s alternative, which this change takes: the workflow file sends this pull request serial on the train (`merge_fastpath.py`).

Classification: all three files are INERT under the existing `tools/audit/` prefix of `tests/closure.py`'s `INERT` list, so `tests/closure.py` needs no edit (figures below). The orchestrator writes the delivery row.

## Head

7990789797b40077be84249dc0c136421e3c2c42 (origin/main 5a41a56696c6bd6245b7cc1261a39a5057ba6bb0, the merge base, at 2026-10-18T15:57:44Z)

## Mutation proof

Each mutant edits one predicate in a committed tree, runs that file's `--self-test`, and is restored with `git checkout -- <file>` plus `git diff --quiet` before the next one. All 12 are killed (self-test rc=1). The failing check names:

- M1 `sweep_render.py`: the host-path `raise` becomes `pass`. FAIL `a home directory written in the template is refused`, FAIL `a home directory straddling template text and a value is refused`.
- M2: span containment `a <= start and end <= b` becomes overlap `a <= end and start <= b`. FAIL `a home directory straddling template text and a value is refused`.
- M3: `if bad:` becomes `if False:`. FAIL `a cited instrument that is not in the tree is refused`.
- M4: `if unknown:` becomes `if False:`. FAIL `an overlay key the table does not declare is refused as unknown` and `a sweep placeholder the table does not declare is refused as unknown`.
- M5: `if unused:` becomes `if False:`. FAIL `a declared placeholder the sweep never uses is refused`.
- M6: `if missing:` becomes `if False:`. FAIL `an omitted placeholder is refused as unfilled`.
- M7: the `isinstance(v, bool)` arm is dropped. FAIL `a boolean value is refused`.
- M8 `policy_reread_check.py`: `if read_at > now:` becomes `if False:`. FAIL `a stamp ahead of the clock is OWED`.
- M9: `read_at > last` becomes `read_at >= last.replace(microsecond=0)`, the old script's truncation. FAIL `a stamp in the same second but before the compaction's fraction is OWED`.
- M10: the newest-wins comparison is dropped, so the first compaction binds. FAIL `a stamp between two compactions is OWED: the newest one binds (null control for OK)`, FAIL `a stamp in the same second ...`.
- M11: the `subtype` test is dropped, so any JSON line that contains the marker counts. FAIL `a quoted compact_boundary inside a message is not a compaction`.
- M12: the non-JSON refusal becomes `continue`. FAIL `a non-JSON line naming compact_boundary is OWED`.

Baseline with no mutant: `sweep_render self-test: 21 checks, 0 failed` and `policy_reread_check self-test: 15 checks, 0 failed`.

## Null control

Every refusal arm has a passing arm next to it in the same self-test. The tracked template renders from a complete overlay with every placeholder filled. A minimal template renders. A home directory supplied by an overlay value renders, while the same text written in the template is refused. A cited path that exists passes, arguments included. A stamp after the newest compaction is OK, as is no compaction with a valid stamp.

Against the live session: on this session's transcript and stamp, `policy_reread_check.py --transcript <session.jsonl> --stamp <orch>/policy-read.stamp` printed `OK (read 2026-10-18T15:46:25Z > compaction 2026-10-18T15:23:48.517Z)` rc=0. The session script it replaces printed `POLICY OK (read 2026-10-18T15:46:25Z > compaction 2026-10-18T15:23:48.517Z)` rc=0 on the same inputs.

## Figures

- Gate scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`). Changed files (5): `.github/workflows/governance.yml`, `tools/audit/seat/INSTRUMENTS.md`, `tools/audit/seat/policy_reread_check.py`, `tools/audit/seat/sweep_render.py`, `tools/audit/seat/sweep_template.md`. The rule is the mode line, not the count.
- What `scope.run` names, plus `tests/run.sh`'s `run_always` checks, run at this head with `PYTHONPATH=tests/hastub`: `python3 tests/entities.py` printed `ALL 2347 ENTITY CHECKS PASSED`, `python3 tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`, `python3 tests/closure.py selftest` printed `ALL 115 closure shrink pins PASSED`, `python3 tests/layout.py` printed `layout self-test: ok`, and `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. Every run exited rc=0.
- Classification: `closure.is_inert(<f>)` is True for each of the three new files and for `INSTRUMENTS.md`. Null control: a made-up file name under custom_components/ gives False. `closure.orphan_files()` returns 0 files.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries at HEAD`. `python3 -I tools/audit/seat/ref_privacy.py --check`: `547 line(s) added since 5a41a56696c6 judged, 0 refused`.
- Host text in the diff. Rule: `git diff <base>...HEAD`, filtered to added lines with an extended grep for either home-directory prefix, the account name, or the session temp root's name, returns no line (rc=1). Null control: the same pattern counts 2 lines in the session prompt this template replaces. The self-test's planted home directory is built at run time from separate string pieces, so no tracked line contains it.
- Render from this session's overlay (kept in scratch, not tracked): `sweep_render.py --overlay <overlay.json> --out <prompt.txt>` printed `wrote 19 lines` rc=0. With `tick_log` removed it printed `REFUSED unfilled: the overlay omits `tick_log`` rc=1. With `bus.sh` changed to a path that does not exist in a template copy it printed REFUSED citation (that renamed path, cited and not in the tree) rc=1.
- Seams of the class "a step names an instrument that does not exist". The rule is `sweep_render.citations(<template>, ROOT)`: every backticked `tools/`, `tests/`, `dev/`, `.github/` path or `CLAUDE.md` in the template, checked against the checkout. It returns none on the tracked template. Its null control is the planted `gone.sh` citation, which is refused. Not covered: a role file cited by its bare name, as in the header prose (`orchestrator.md`). The sweep body cites every role file by its full path, so those citations are checked.

## Red checks

none

## Unpinned sites

`prepr.sh` step 6d: the new files are under `tools/audit/` and no tests/ mutation lane reaches them. Each of the 12 mutants above is killed by its file's self-test, which now runs in `instrument-self-tests`.

## Forward-carry

none. The template is the place later sessions take the sweep from, and `INSTRUMENTS.md` names it.

## Friction

none

## Approval

The diff touches no `POLICY_GLOBS` path, so `checkPrBody` does not require this section. It is here because the brief asked for it on the grounds that the template reads like a brief: it orders the orchestrator's turn. It restates no rule and defers to `orchestrator.md` and `nudge.md` where they disagree. The orchestrator approves under mandate 6175172275.
