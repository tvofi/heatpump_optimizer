Fix review: merge 498c2ab0429d7a6d2ef8d239e3945fe15ff70690

bus-nonce: 457ba2ab1a3535dff6e66cb034c56585

Round 1 (first review). An RCA PR judged by root-cause.md; measured at head 498c2ab0429d7a6d2ef8d239e3945fe15ff70690, still the PR head at verdict time (`git ls-remote origin refs/pull/3429/head`).

## Evidence

- RESULT census: `dependabot_stale_hash.py` at the Dependabot heads bffd45a03a, da3a5cfb8b and 4182e75d77 prints moved=46/17/7 and stale=3/5/1, with the stale pins exactly those in the RCA table; rc 1 (ev/harness.txt).
- RESULT census controls: re-apply commits 20fc628eee, b9c009a6b3 and a555d52ae8 print stale=0; npm and actions heads #3087, #3321, #3322 and #3413 print files=0 stale=0; rc 0.
- RESULT --tree: exposed=17 over files=5 and rc 1 at d08ed31049, 699f4d9ef4, the head and origin/main. The 17 package names match section 4. On a scratch worktree of d08ed31049 with `==` replaced by a space on comment lines (2 files changed): exposed=0, rc 0. Runtime real 0m0.062s, against the body's 0.052s; same order.
- RESULT null control, re-derived by the reviewer's own script (ev/nullctl.py, ev/null_control.txt) over the 70 moved pins. Comment holds `name==oldversion` and pin stale: 9. Comment holds it and pin fresh: 1 (pyjwt, the full-stop boundary case). No such comment and stale: 0. No such comment and fresh: 60. Under the body's "comment-rewritten" rule the split is 9 of 9 stale against 0 of 61, which reproduces; the `-U0` comment diff per PR equals the stale set pin for pin.
- RESULT planted-by: `git log --reverse -S` names cef18e0803 (coverage echo), 2ca7fb20e3 (cryptography override), 20fc628eee (acme, python-dateutil, sqlalchemy, uv) and b9c009a6b3 (homeassistant). That matches section 2, and gives "5 of the later 6" from #3147.
- RESULT mutation proof: the body's two mutants were re-run (M1 stale comparison -> False; M2 `False and re.search`), and so were M3 (drop hash equality) and M4 (drop the comment filter). Each prints `self-test FAIL` with rc 1. Two precision guards survive the self-test; see Findings. ev/mutants.txt.
- Process state (c) is argued from the measured re-apply cleanliness plus the planted-by commits. Not-(b) and not-(d) are argued, not measured; acceptable for an RCA.
- Cost test: the guard's standing cost is re-measured. The section 5 wall-clock table (red hours, re-apply open times, CI run counts, review rounds) comes from the GitHub API and was not re-derived by this seat: unverified (fix-review step 8). The build-A verdict does not turn on it, because A's recurring cost is about 0.05 s.
- Forward-carry: present on origin/handoff/audit-r10-roster add34472b2 in dev/programme/rosters/wave-r10-groups.json, inside the group with pr 3426 (R10-DEPENDABOT-3414-COMPAT). It states its control: exit 1 at its parent, exit 0 at its head. carry_audit at the head: 1 routed, 0 unrouted.
- Claims and versions: the diff touches no golden, no claim file, no VERSION, no manifest and no RELEASE_NOTES (three-dot). The new file is classified INERT in tests/closures.json.
- Merge: `git merge-tree --write-tree origin/main <head>` rc 0; the LEDGER-MERGE driver resolved tests/closures.json (ev/merge_tree.txt).
- CI: `merge_train.py classify 498c2ab0429d7a6d2ef8d239e3945fe15ff70690 --pr 3429` rc 0 `GREEN ... pending: none red: none` at 03:10:04Z (ev/classify.txt). The earlier red `gate` runs were the transient deferral the brief names; the final gate is not red. `## Red checks: none` is therefore correct against the owed set (ev/owed_reds.txt).
- No finder's harness was named (RCA seat). The instrument is the RCA seat's own, committed in this diff, and disclosed as such in the body.

## Findings

- Follow-up: two precision guards in `dependabot_stale_hash.py` survive `--self-test` and leave every real figure unchanged (17 exposed; stale 3/5/1). M5 removes `exposed`'s `(?<![\w.-])` lookbehind, which would admit a `foo==` inside `xfoo==`. M6 removes `parse`'s name normalisation, which `exposed` relies on to match `python_dateutil`/`Python-Dateutil` spellings. Neither is reached by today's locks, and the harness is INERT and ungated in this PR. Carry: dismissed: no current lock line separates them and the instrument is ungated here; the stage that wires `--tree` into the suite owns its tests.
- Follow-up: RCA section 2's null-control bullet says "9 moved pins carry a comment occurrence of `name==oldversion` and 61 do not". Read literally, that is 10 against 60, because pyjwt's `pyjwt==2.15.0.` is such an occurrence; 9/61 holds under the "rewritten" rule the bugclasses entry and the body use. The next bullet discloses pyjwt as the boundary case, so no fact is hidden. Carry: dismissed: wording only, disclosed in the following bullet, conclusion unchanged.

## Friction

none
