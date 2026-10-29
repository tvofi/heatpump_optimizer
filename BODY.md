R10-FLY-REFPRIV-HOME-SEGMENT: `tools/audit/seat/ref_privacy.py`'s `home-directory` class now matches a home directory only as a whole path, not as a substring. A cloud seat runs with `HOME=/root`. Before this fix, any added line citing `dev/governance/roles/root-cause.md` contained the substring `/root`, so the class refused it. That is how `body_push.sh` came to refuse #2872's `dev/audit/rca/R10-RCA-COP-PARTLOAD.md:3` and block that PR.

- New `_home_re(home)`: the escaped home, not preceded by `[\w.-]` and not followed by `[\w-]` or by a `.` that starts a longer segment. `_leaks` (case-folded) and `scrub` (case-insensitive) both call it, so the guard refuses the same spans that `scrub` rewrites.
- These still refuse: `/root/.cache/x`, a bare `/root`, `/root.` at the end of a sentence, `'/root/wt'`, `file:///Users/<name>/x` and a macOS home that differs only in case.
- These now pass: `roles/root-cause.md`, `x/root/y` and `a.root/z`. `/Users/<name>s/x` is still refused, but by `host-path` and no longer by `home-directory`.
- The module docstring's `home-directory` line now says "as a whole path".
- The `account-name` class did not cause this: `root` is in `PUBLIC_ACCOUNTS`, and `Identity.made` drops public names.

## Head

`65ad0e0a31ca6fc1b6d83a41af5ec5af8174b42a`, cut from origin/main `d074b94b0626d2a66014e0629946c850ab283e05`, which was also origin/main's tip at 2026-10-29T11:17:04Z. Every figure below was taken at this head.

## Mutation proof

The self-test runs `python3 -I tools/audit/seat/ref_privacy.py --self-test`. Each mutant below was applied to this head, measured, then restored.

- Lookbehind removed (`return re.escape(home) + r"(?![\w-]|\.[\w-])"`): `FAIL a cloud seat's home inside a longer path segment passes`, tally `97 checks, 1 failed`. The cited line is caught by the lookahead (`-` follows `/root`), and `x/root/y` is caught by the lookbehind.
- Lookahead removed (`r"(?<![\w.-])" + re.escape(home)`): `FAIL a sibling extending the home's last segment is not that home: ['home-directory', 'host-path']`, tally `97 checks, 1 failed`.
- Failing test first: the new checks were added before the fix, against the merge base's `_leaks` and `scrub`. The run printed `FAIL a cloud seat's home inside a longer path segment passes: ['home-directory']` and `FAIL a sibling extending the home's last segment is not that home`, tally `97 checks, 2 failed`. The first fix draft also excluded a trailing `.`, and the check `... at a start or after a quote` turned that red on `cd /root.`. The lookahead now excludes only a `.` followed by a path character.

## Null control

- `a macOS home is unchanged: case-folded, after file://, refused (the null control)` is ok both at the merge base and at this head. The fixture identity `Identity.made({/Users/exampleuser}, ...)` gives `['home-directory', 'account-name']` for an upper-cased `/users/EXAMPLEUSER/x` and `home-directory` for `file:///Users/exampleuser/x` at both refs.
- The existing `scrub` checks (`scrub's placeholders, in order ...` and `scrub leaves another account's home and a public one alone`) and every other ref and body check are ok at this head, unchanged.

## Figures

- `python3 -I tools/audit/seat/ref_privacy.py --self-test` at this head: tally `ref_privacy self-test: 97 checks, 0 failed` (one `ok` call per printed line; 5 new, 92 at the merge base). With the new checks only, at the merge base: `97 checks, 2 failed`.
- Finder's harness, the measured instance. `dev/audit/rca/R10-RCA-COP-PARTLOAD.md` was read from #2872's head (`git fetch origin pull/2872/head`) and passed to `ref_privacy.content_refusals` under `Identity.made({"/root"}, {"root"}, 0)`. Before (merge base): one refusal, `dev/audit/rca/R10-RCA-COP-PARTLOAD.md:3: home-directory in an added line of a tracked file`. After (this head): `[]`. Under the same identity, `leaks("/root/.cache/x")` returns `['home-directory']` at both refs.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. Its scope.run names `tests/entities.py`.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` (PYTHON set to the seat venv): mode line `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, `ALL 2470 ENTITY CHECKS PASSED`, `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN`, exit 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Sibling search, for another check matching `$HOME` as a substring: `grep -rnE "HOME.*\) in |home.*casefold\(\) in |homes? in (text|body|line|folded)" tools tests --include='*.py'` prints nothing. `account-name` already excludes `root` as a public account.

## Red checks

none

## Forward-carry

none

## Friction

none
