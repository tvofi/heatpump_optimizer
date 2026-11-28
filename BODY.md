Bound the replay-job regex in `tests/replay.py` (`replay_timeout_minutes`) so each line of the job has one parse. The old pattern's two line arms, `    .*\n` and `[ \t]*\n`, both matched a blank line indented four spaces, so a run of such lines before a missing `timeout-minutes` backtracked exponentially (code-scanning alert 69, `py/redos`). The blank arm is now split into ` {0,3}\n` and ` {0,3}\t[ \t]*\n`: blank lines the four-space arm cannot take. The union of line shapes is unchanged, and so is the lazy quantifier's priority, so the leftmost-shortest match and its group are the same.

A new control, `control:headroom:cap_read_is_linear`, times the read of 23 blank four-space lines with no cap, and `control:headroom:reads_the_replay_job` now also requires blank lines spelled with a tab, mixed spaces and tabs, and four spaces to be skipped. No production code changes (`custom_components/` untouched).

Alternatives: a line-by-line Python parse would also be linear, but it would replace one expression with a loop and need a second equivalence argument. A negative lookahead (`(?! {4})[ \t]*\n`) is shorter, but CodeQL's ReDoS analysis approximates lookarounds, so the alert might stay open. The disjoint character-class arms need neither.

## Head

25a003739d6f67cde8437daf60a8e816f8125889 (merge base 98541868add741cd1967a82614d3b3b81b9178ef; `git merge-tree --write-tree origin/main HEAD` clean against origin/main ac9045c223, 2026-11-28).

## Mutation proof

Each mutant was applied to `tests/replay.py` at the head and run through `replay.controls()` (driver: `PYTHONPATH=tests/hastub:tests python3 -c 'import replay; [print(n, ok, d) for n, ok, d in replay.controls() if "headroom" in n]'`), then restored:

- The base regex put back (`(?:    .*\n|[ \t]*\n)*?`): `FAIL control:headroom:cap_read_is_linear read None in 2.544 s`.
- A different overlap added (a third arm ` *\n`, which also takes a blank four-space line): `FAIL control:headroom:cap_read_is_linear read None in 3.359 s`.
- Over-narrowing (the tab arm ` {0,3}\t[ \t]*\n` deleted): `FAIL control:headroom:reads_the_replay_job read 45`, so a fix that drops blank lines spelled with a tab is caught.

No added `.py` lines outside `tests/` or `dev/`, so prepr's mutant draw has nothing to draw.

## Null control

On the unmodified tree, the base pattern searched over `"\n  replay:\n" + "    \n" * n + "x"` with `re.search` took 0.021 s at n=16, 0.059 s at 18, 0.372 s at 20, 1.661 s at 22 and 5.488 s at 24 on this host, about 2.1x per added line. The head pattern returns `None` on the same input in under 1 ms at n=23 (the control prints `0.000 s`). The control's 0.25 s bound sits more than 10x under the base pattern's 2.5 s at n=23 and more than 250x over the head's time.

## Figures

- Equivalence corpus: a scratch driver, sha1 25e3d70d42453803b9cb4b8aad723755cae79c06, quoted in full below. Every sequence of 0 to 3 lines drawn from 19 line shapes (blank lines in each space/tab spelling, four-, six- and three-space content, `timeout-minutes` at the right, deeper and tab indents, a second `replay:` header), between 4 prefixes and 4 suffixes: 115840 strings. Base and head agree on `(span, group(1))` for all of them, and the base matched 23265. Null control: the same corpus with the tab arm dropped disagrees on 8400, so the corpus does reach the arm this diff adds.
- Real input: on every `.github/workflows/*.yml` that contains `  replay:`, which is `tests.yml` alone, base and head both return span (78958, 79176) and group `60`.
- `tests/replay.py`, `tests/debug_collect.py`, `tests/dst_checks.py` and `tests/entities.py` (each module that imports `replay` and runs as a script), run at the merge base and at the head with `PYTHONPATH=tests/hastub python3 tests/<s>.py`:
  - `debug_collect`: rc 0 at both.
  - `dst_checks`: rc 1 at both, with the same 8 FAIL lines (`diff` of the sorted FAIL lines is empty). These are host time-zone checks this diff does not reach.
  - `entities`: `1 of 2793` failed at the base and `1 of 2794` at the head. The added check is the new replay control. The one failure is the same check at both ends (`a measured script's late-writing descendant is waited for`, a host-timing check).
  - `replay`: `1 of 203` failed at the base, the lane wall-time headroom check at 3949.1 s on a loaded host. At the head that check passed (2597 s), so the head failed none. That check reads host wall time, not the regex: both ends read the same cap (60).
- Scope (`python3 tests/closure.py select --diff 98541868ad`): `MODE: SCOPED -- 4 script(s) run`, namely debug_collect, doc_claims, entities and features. At the head, `features` and `doc_claims` returned rc 0, and `debug_collect` and `entities` are as above.
- At the head, the run_always scripts `tests/structure.py` (`STRUCTURE RATCHET PASSED`), `tests/layout.py`, `tests/harness_headers.py` and `tests/closure.py selftest` returned rc 0.

```python
"""Equivalence of the base and head replay-job regexes over a generated corpus."""
import itertools, re, sys
BASE = r"\n  replay:\n(?:    .*\n|[ \t]*\n)*?    timeout-minutes: (\d+)\n"
HEAD = (r"\n  replay:\n(?:    .*\n| {0,3}\n| {0,3}\t[ \t]*\n)*?"
        r"    timeout-minutes: (\d+)\n")
NOTAB = r"\n  replay:\n(?:    .*\n| {0,3}\n)*?    timeout-minutes: (\d+)\n"
LINES = ["\n", " \n", "   \n", "    \n", "     \n", "\t\n", "  \t \n", "   \t\n",
         "\t    \n", "    \t\n", "    needs: [x]\n", "      run: y\n", "   x\n",
         "  next:\n", "    timeout-minutes: 45\n", "      timeout-minutes: 7\n",
         "    timeout-minutes: x\n", "  \n  replay:\n", "\t timeout-minutes: 3\n"]
HEADS = ["\n  replay:\n", "jobs:\n  replay:\n", "\n  replay:\n\n  replay:\n", "x"]
TAILS = ["", "  next:\n", "    timeout-minutes: 9\n", "\n"]
def key(pat, s):
    m = re.search(pat, s)
    return (m.span(), m.group(1)) if m else None
n = dh = dn = matched = 0
for k in range(4):
    for body in itertools.product(LINES, repeat=k):
        for h in HEADS:
            for t in TAILS:
                s = h + "".join(body) + t; n += 1
                b = key(BASE, s); matched += b is not None
                dh += b != key(HEAD, s); dn += b != key(NOTAB, s)
print(f"corpus {n} strings, base matched {matched}; head disagrees on {dh}; null control disagrees on {dn}")
sys.exit(0 if dh == 0 and dn > 0 else 1)
```

## Red checks

`code-scanning alert 69 (py/redos)`: open on main at `tests/replay.py`'s `replay_timeout_minutes`. This diff removes the overlapping arm it reports. A cheaper detector already exists, the CodeQL scan that raised the alert; a local one would add a regex-ambiguity pass to every edit of `tests/`. The recorded finding: no cheaper detector is built here, because the alert is the detector and this one was caught on a test tool, not a release.

## Forward-carry

none

## Friction

none
