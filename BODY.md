Round-11 roster record: puts the round-11 roster, `dev/programme/rosters/wave-r11-groups.json`, and the round-10 roster edits main lacks onto main from `handoff/audit-r10-roster`, so the carry audit on main and the merge train's carry pre-flight find the round-11 groups and the issues they own (#3835 routes a finding to #3769, which only the roster branch wires). It closes nothing by keyword and leaves #3394 open.

## Summary

The change is roster state only: two files under `dev/programme/rosters/`. `wave-r11-groups.json` is new (7153 lines, 116 groups) and `wave-r10-groups.json` takes the branch's edits (`git diff --numstat origin/main...HEAD`; a figure that is a function of main's tip is stale once main moves). No production, test or instrument code is touched, and the opener adds the pull request's own delivery row.

The roster branch tip is `320a1ada53e936a559aa6f140e7ea4e2d2e96c73`, a `roster_edit edit-brief`. The range `63c6d1cff9a29ec0c99bcbd5e12c229b61e7c184..320a1ada53e936a559aa6f140e7ea4e2d2e96c73` holds 1381 non-merge commits and one merge (`5522a01722`, the branch's merge of main), and every one touches only `dev/programme/rosters/`: 1281 `roster_edit` ops, 66 `roster_sync:` derivations and 34 `roster:` commits by the orchestrator (the approved round-11 plan's groups).

Once this merges, main's newest roster is round 11, so `roster_lib.round_ref` names `origin/handoff/audit-r11-roster` instead of `origin/handoff/audit-r10-roster`. The orchestrator creates `handoff/audit-r11-roster` at this pull request's merge commit when it merges (a ref to an existing commit, no new content), so the round's roster edits continue on the branch `round_ref` names, on a history without `0bcaf7cdda` (see Head); until it exists, `default_roster_ref` reads main and says so. `handoff/audit-r10-roster` is left as it is.

## Head

`e29c218b4e6fb5c3a5a6cc01a7172a8dbd0a0bfa` is one commit on `origin/main` `63c6d1cff9a29ec0c99bcbd5e12c229b61e7c184` that copies both roster files from the branch tip `320a1ada53e936a559aa6f140e7ea4e2d2e96c73`. The earlier landings #3554, #3555 and #3608 merged the branch instead; this one cannot: the branch's range holds `0bcaf7cdda` (`roster_edit append-group R11-RCA-SELFTEST-TABLE-DRIFT`, 2026-11-16), whose author and committer emails are empty, and the `ref_privacy.py` push guard over `origin/main` refuses any push that carries it (`unnumbered-email`; `body_push.sh` refused the merged head). Rewriting the branch would take a force push of the shared roster branch, so the copy is the landing.

The copy loses nothing a merge would keep. The merge of the same tip into the same main (`12dfa328360b1be44d8615e1d523d4eb488b06f9`, built locally, never the head of a pull request) conflicted in one hunk of `wave-r10-groups.json`: R10-COP-LEARNER-DRAW-FLOOR's `resume.stage`, `carries-open` on main (from #3608's landing of `80c1fb32c7`) against `absorbed` on the branch (set by the branch's merge `5522a01722`, after that landing). Taking the branch's value, as the branch is where the roster seat writes, gives both roster blobs equal to the branch tip's, since every other main-side change was already on the branch; that merge's tree, `f9e030dc425d3728853f8c7beb041db2d16b52d5`, is this commit's tree. The blobs at this head are `wave-r10-groups.json` `8035f823dfb6d3673be8666f9d9fb9336f173a4f` and `wave-r11-groups.json` `0a6ecd9e96fe4e9e12037873f7f3857b1589a0ca`; `git diff 320a1ada53e936a559aa6f140e7ea4e2d2e96c73 HEAD -- dev/programme/rosters/` prints nothing. Read the diff three-dot.

## Mutation proof

n/a: roster state only; no production, test or instrument code.

## Null control

Keyed on the `group` field: `wave-r10-groups.json` has 544 groups on main and 559 at this head (15 added, none removed, 34 of main's changed); `wave-r11-groups.json` has none on main and 116 at this head. Carries summed over groups go from 2308 to 2466 in the round-10 file and from 0 to 655 in the round-11 file. Had the keying been vacuous, a roster that differs would print zero added and changed; it does not.

The carry audit, on #3835's body (head `00b4d4de85bb8a4116b6651c69cfc9077e8f9aad`): at `origin/main` `63c6d1cff9` it prints `BAD-DEST body item 1d6e7396: #3769: #3769 has no owner` and `2 routed, 0 unrouted, 2 bad destination(s)`; in a clone whose `origin/main` carries this tree, with no `handoff/audit-r11-roster`, it prints `4 routed, 0 unrouted, 0 bad destination(s)`, and the same with `handoff/audit-r11-roster` present.

## Figures

- `git diff --numstat origin/main...HEAD` prints `1259 354` for `wave-r10-groups.json` and `7153 0` for `wave-r11-groups.json`, two files.
- `node tools/policy/brief_lint.mjs` at this tree: `TOTAL: 0 error(s) across 40 file(s)`.
- `python3 tools/pr/ci_predict.py` at this tree predicts no closures, fast, governance or instrument red.
- `python3 tools/audit/carry_audit.py check --body <#3835 body>` as in Null control.

## Red checks

None known at this head; the orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
