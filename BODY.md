Read the replay job's `timeout-minutes` in `tests/replay.py` (`replay_timeout_minutes`) line by line, with no regex loop over the lines. The old pattern `\n  replay:\n(?:    .*\n|[ \t]*\n)*?    timeout-minutes: (\d+)\n` had two arms that both took a blank line indented four spaces, so a run of such lines before a missing cap backtracked exponentially (code-scanning alert 69, `py/redos`).

The read now works like this:
- It finds each `\n  replay:\n` header in turn.
- From each header it walks the newline-terminated lines. The first line that `_REPLAY_CAP_LINE` (`    timeout-minutes: (\d+)`) matches whole is the result.
- A line that is neither indented four spaces nor blank (spaces and tabs only) ends that header's job.

These are the old pattern's rules: the same header search order, line arms, lazy first cap and trailing newline. The only regex left matches one line with no repetition over lines.

A new control, `control:headroom:cap_read_is_linear`, times the read of 23 blank four-space lines with no cap. The existing `control:headroom:reads_the_replay_job` now also requires two things:
- blank lines spelled with a tab, with mixed spaces and tabs, or with four spaces are skipped;
- a first `replay:` header with no cap falls through to a later one.

No production code changes (`custom_components/` untouched).

Alternatives:
- The first cut kept the regex and made its line arms disjoint (` {0,3}\n| {0,3}\t[ \t]*\n`). That is linear when measured, but CodeQL still reported `py/redos` at the same line on #3941 (head a1fa3889), because its analysis flags the repeated group itself.
- A negative lookahead would be flagged the same way.
- The line-wise read removes the repeated group, which is what the analysis reads.

## Head

5411fd2bb052a6486d6bae69efa3d987df690c1f (the code head; parent 25a003739d, the first cut). Merge base 98541868add741cd1967a82614d3b3b81b9178ef.

## Mutation proof

Each mutant was applied to `tests/replay.py` at the code head and run through `replay.controls()` and the equivalence corpus, then restored. Driver: a scratch script, sha1 ae2b96d03a955965e52ac20be761a0998721fb67, which runs `PYTHONPATH=tests/hastub:tests python3 -c 'import replay; ...replay.controls()...'` per mutant and prints `RESTORED` after `cmp`:

- **Backtracking regex reintroduced** (the old `re.search` put back as the function's first statements): `FAIL control:headroom:cap_read_is_linear read None in 6.117 s`. At the first cut, the same check failed on that regex (2.544 s) and on a third overlapping arm ` *\n` (3.359 s).
- **A blank line ends the job** (`and line.strip(" \t")` deleted): `FAIL control:headroom:reads_the_replay_job read None`; the corpus disagrees on 22547.
- **Only the first header read** (`start = workflow.find(header, start + 1)` changed to `start = -1`): `FAIL control:headroom:reads_the_replay_job`; the corpus disagrees on 21436.

No added `.py` lines outside `tests/` or `dev/`, so prepr's mutant draw has nothing to draw.

## Null control

On the unmodified tree, the base pattern searched over `"\n  replay:\n" + "    \n" * n + "x"` took 0.021 s at n=16, 0.059 s at 18, 0.372 s at 20, 1.661 s at 22 and 5.488 s at 24 on this host, about 2.1x per added line. The line-wise read returns `None` on the same input in under 1 ms at n=23 (the control prints `0.000 s`). The control's 0.25 s bound sits more than 10x under the base pattern's time at n=23 and more than 250x over the head's.

## Figures

- Equivalence corpus: a scratch driver, sha1 054b35856ce7032398c27fef69fa800f5daa3a12, quoted below. Every sequence of 0 to 3 lines drawn from 23 line shapes, between 4 prefixes and 5 suffixes: 254400 strings. The base regex's `int(group(1))` or `None` equals `replay.replay_timeout_minutes` at the head for all of them, and the base matched 55785. The line shapes include:
  - blank lines in each space/tab spelling, and `\r` lines;
  - four-, six- and three-space content;
  - `timeout-minutes` at the right, deeper and tab indents, in Arabic-Indic digits, and with `\r\n`;
  - a second `replay:` header;
  - and, among the suffixes, a cap with no trailing newline.

  Null control: the same corpus run against the base regex with its tab-blank arm dropped disagrees on 14660, and the two function mutants above disagree on 22547 and 21436.
- Real input: `replay_timeout_minutes(REPLAY_WORKFLOW.read_text())` at the head reads 60. The base regex on the same `tests.yml` reads 60 (span 78958..79176).
- Before and after, at the first cut (logs kept in the seat's scratch dir): `tests/replay.py`, `tests/debug_collect.py`, `tests/dst_checks.py` and `tests/entities.py` were run at the merge base and at 25a003739d with `PYTHONPATH=tests/hastub python3 tests/<s>.py`.
  - `debug_collect`: rc 0 at both.
  - `dst_checks`: the same 8 FAIL lines at both (host time-zone checks).
  - `entities`: the same 1 FAIL at both (`a measured script's late-writing descendant is waited for`, host timing).
  - `replay`: the base failed only its lane wall-time headroom check (3949.1 s on a loaded host) and the first cut none.
- At this code head: `replay.controls()` returns 42 checks, 0 failed, and `tests.yml` reads cap 60. `replay_timeout_minutes` has two callers, `controls()` and `main()`'s final headroom check (`grep -rn replay_timeout_minutes tests tools` names no other file), and no fixture replay reaches it. So the full lane and the scoped scripts were not re-run at this head; their first-cut results above stand, and CI runs them.
- Scope (`python3 tests/closure.py select --diff 98541868ad`): `MODE: SCOPED -- 4 script(s) run`, namely debug_collect, doc_claims, entities and features.

```python
import itertools, re, sys
sys.path[:0] = [sys.argv[1] + "/tests/hastub", sys.argv[1] + "/tests"]
import replay
BASE = r"\n  replay:\n(?:    .*\n|[ \t]*\n)*?    timeout-minutes: (\d+)\n"
NOTAB = r"\n  replay:\n(?:    .*\n| {0,3}\n)*?    timeout-minutes: (\d+)\n"
LINES = ["\n", " \n", "   \n", "    \n", "     \n", "\t\n", "  \t \n", "   \t\n",
         "\t    \n", "    \t\n", "    needs: [x]\n", "      run: y\n", "   x\n",
         "  next:\n", "    timeout-minutes: 45\n", "      timeout-minutes: 7\n",
         "    timeout-minutes: x\n", "  \n  replay:\n", "\t timeout-minutes: 3\n",
         "    timeout-minutes: ٤٥\n", "    \r\n", " \r\n", "    timeout-minutes: 4\r\n"]
HEADS = ["\n  replay:\n", "jobs:\n  replay:\n", "\n  replay:\n\n  replay:\n", "x"]
TAILS = ["", "  next:\n", "    timeout-minutes: 9\n", "\n", "    timeout-minutes: 8"]
def key(pat, s):
    if callable(pat):
        return pat(s)
    m = re.search(pat, s)
    return int(m.group(1)) if m else None
n = dh = dn = matched = 0
for k in range(4):
    for body in itertools.product(LINES, repeat=k):
        for h in HEADS:
            for t in TAILS:
                s = h + "".join(body) + t; n += 1
                b = key(BASE, s); matched += b is not None
                dh += b != key(replay.replay_timeout_minutes, s); dn += b != key(NOTAB, s)
print(f"corpus {n} strings, base matched {matched}; head disagrees on {dh}; null control disagrees on {dn}")
sys.exit(0 if dh == 0 and dn > 0 else 1)
```

## Red checks

`code-scanning alert 69 (py/redos)`: open on main at `tests/replay.py`'s `replay_timeout_minutes`. CodeQL also raised it as a new alert on #3941's first cut, the disjoint-arms regex, at a1fa3889. This head removes the repeated group the analysis reports; CodeQL's result on this head is the check that decides it. The cheaper detector is that same CodeQL scan on the pull request. No local one is built: no CodeQL CLI is installed on the seat hosts, and the alert reached no release.

## Forward-carry

none

## Friction

none
