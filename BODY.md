Group: R10-FLOW-YIELD-PROBE

Pinned pack file: `dev/programme/flow-study/roster/groups/R10-FLOW-YIELD-PROBE.json` at pack commit 78117030 on branch `claude/dazzling-gauss-7l3u2b`.

R10-FLOW-YIELD-PROBE (owner ruling R13) asks two things: why real-catch blocks per reviewed PR fell from 0.52 to 0.15, and what threshold to recommend for the review-strength guardrail. The answer is the study record, `dev/audit/rounds/round10/D13/yield-probe.md`. Every figure in it comes from `tools/audit/seat/review_strength.py`, which reads the verdict bus over git only and is self-tested in `governance.yml` `instrument-self-tests`. No production code, budget, `VERSION`, manifest or claim file is touched.

This is round 5, so it is a re-cut. Rounds 2 to 4 each blocked on one-line mutants of `review_strength.py` that passed the self-test and moved figures the body quoted. This round replaces pinning mutants one at a time with a sweep under a stated class rule:

- **The rule.** `dev/audit/harnesses/r10_review_strength_mutants.py` parses the tool with `ast`. Its header lists the operator classes and their bounds. This round adds these classes:
  - literal edits: end characters dropped, prefix and suffix cuts at each separator, and numerals moved by one, across every string, f-string part and format spec;
  - statement moves into and out of blocks, and swaps of adjacent statements that depend on each other;
  - bool flips, positional-argument drops, and method swaps (`startswith`/`endswith`, `match`/`search`, and `split`/`rsplit` where a maxsplit is given).
- **The sweep's result.** Every survivor is killed by a check that asserts a pinned value, or is listed in `DISPOSED` as equivalent, with the reason it changes nothing. None is disposed as merely "unpinned".
- **The tool changes the sweep forced.** None moves a figure on the real bus (see Null control).
  - `VERDICT_RE`, `PREFIX_RE` and `MERGE_RE` drop a `^` that `.match` already anchors. Their `.match` is pinned instead.
  - `bus-confirmed:` ids are read with one `finditer` per verdict ref.
  - `main` refuses bad arguments before it fetches.
  - The argument parser is its own function, so its defaults are asserted.
- **The self-test** grows from 76 to 96 checks. New fixture PRs 16 to 18 pin these seams:
  - the delivery and product prefixes at their trailing `/`;
  - the nonce and confirmation regexes: line start, the hex class and the probe-ref name shape;
  - the scope of the review, verdict, probe and archive-tag refs;
  - first-parent merge walking, a tab inside a merge subject, and a prefixed merge subject;
  - the group regex's digit classes;
  - first-pass for a PR first reviewed before the window;
  - the guardrail's time guard on catches;
  - `--fetch` against a bare remote with no configured refspec, so the tool's own forced refspecs and `--tags` are what get measured.

The round-4 verdict's items:

- F2, the delivery-path prefix widened to `dev/programme/`. PR 16's `dev/programme/delivery.md` kills it, together with every other cut of that literal. Carry: dismissed: fixed in this pull request
- F7, the first-pass seen-set scoped to the window. The check "first-pass: a PR whose first verdict precedes the window is no first pass in it" kills it. The sweep's statement-move class generates F7 and its siblings. Carry: dismissed: fixed in this pull request
- F4, the cloud id prefix cut to `clou`. It is now killed rather than called equivalent: PR 17's confirmed id `clou9-xcloud` reads local, and the same id kills the `-cloud` → `cloud` cut. Carry: dismissed: fixed in this pull request
- The sweep skipped `print` arguments. They are now inside it. Only the docstrings, `help=`/`metavar=`/`description=`, and `.error`/`SystemExit` message arguments are skipped. Carry: dismissed: fixed in this pull request

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01PkFrJiaXS2wi271zKNmzm6

## Head

The code head is `384a0e8cd600d6034d0c44c478ed1360b1f0ff71`. It sits on the reviewed head `e53fee3670d81481bd25d255f3f27365e287c12e` and has eight commits:

- `26b7792d4`: the sweep's new classes, the tool changes and the self-test cases.
- `4d57931e6` and `0ae4967e2`: merges of `origin/main` (at `b787c7d45951` and `01cf1398a9cf`).
- `dc422d6f2`: the fetch test's bare remote is built by `throwaway_git_init` (prepr's throwaway-git guard).
- `c2215974c`: a merge of `origin/main` at `0b162da1adb73367eddcae1623cf5688422ad9a7` (committed 2026-10-22T09:03:46Z). The one conflict was in `.github/workflows/governance.yml`, where #2578's body-PATCH step and this PR's review-strength step were added at the same place. Both are kept. Against `0b162da1a`, `git diff 0b162da1a c2215974c -- .github/workflows/governance.yml` shows only this PR's 7-line step.
- `8174c1503`: a merge of `origin/main` at `babd88e7b134`. It brings only `dev/programme/delivery/` rows: `git diff --name-only c2215974c 8174c1503 | grep -v '^dev/programme/delivery/'` prints nothing.
- `294a4cbbe`: a merge of `origin/main` at `c1e1967bcb75`. It brings only `dev/programme/delivery/2601.md` and roster carry lines in `dev/programme/rosters/wave-r10-groups.json` (`git diff --name-only 8174c1503 294a4cbbe`).
- `384a0e8cd`: a merge of `origin/main` at `c409c9b18a9f`, which brings only `dev/programme/delivery/` rows (`git diff --name-only 294a4cbbe 384a0e8cd`). `prepr.sh` passed at `294a4cbbe` (`PRE-PR: 294a4cbbec83d1965bc52a643b0bbbae889d021f 000000000000000000000000`).

Every merge is a merge, never a rebase. `tests/closures.json` was resolved as a set by the ledger merge driver.

The sweep was run at `dc422d6f2`. `git diff --quiet dc422d6f2 384a0e8cd -- tools/audit/seat/review_strength.py dev/audit/harnesses/r10_review_strength_mutants.py tests/throwaway_git.py dev/audit/rounds/round10/D13/yield-probe.md && echo SWEEP-INPUTS-IDENTICAL` prints `SWEEP-INPUTS-IDENTICAL`, so the sweep's inputs are the head's. The bus figures and the bundle null were re-taken with the same tool file at 2026-10-22T08:31Z, after `--fetch`. `git diff --quiet 4d57931e6 384a0e8cd -- dev/governance/roles/ CLAUDE.md && echo ROLES-UNCHANGED` prints `ROLES-UNCHANGED`.

## Mutation proof

**The class rule is the command:** `python3 dev/audit/harnesses/r10_review_strength_mutants.py --jobs 4`. Its header states the operator classes, what it skips (docstrings and the human-text arguments named above) and its BOUNDS. The rule does not rename variables, swap two different names, insert statements, move a statement more than one block or two positions, or replace a literal with an unrelated one. A mutant of those shapes is outside the rule.

At `dc422d6f2`, whose sweep inputs are the head's (see Head), the sweep (3.11) prints `M0 (unmutated emission): passed -- review_strength self-test: 96 checks, 0 failed` and then `RESULT mutants=2333 killed=2286 survived=47 disposed=47 undisposed=0 stale=0`, rc=0.

The 47 survivors are equivalent mutants, each keyed and reasoned in `DISPOSED`. They fall into these groups:

| group | n | why it changes nothing |
|---|---|---|
| `parser`: two `add_argument` calls swapped | 11 | argparse registration order of optionals orders only the `--help` listing |
| window spec `split('=', 1)` and `split('..', 1)`: rsplit, maxsplit dropped, or maxsplit 1 → 2 | 6 | a spec holds one `=` and a span one `..` |
| numstat `split('\t', 2)`: rsplit, maxsplit dropped, or 2 → 3 | 3 | numstat quotes any path holding a tab |
| numstat `git diff`: `check=` dropped, `False` → `True`, or `if mb` forced True | 3 | the diff runs only with a merge base |
| `stratum`: its four early returns swapped | 4 | their tests are disjoint |
| ref patterns with the trailing `/` dropped (`/review`, `/verdict`, `/probe`, `refs/tags/archive/probe`) | 4 | `for-each-ref` matches a pattern only at a whole path component (checked with `git for-each-ref` in a scratch repo: `archive/probex/...` and `reviewx/...` are not listed) |
| `tally`: two counter updates swapped, and the catch moved out of the blocked test | 3 | different keys of `o`; real implies blocked |
| `files.append` moved or swapped beside the delivery test | 2 | `files` feeds only product, which no delivery row matches |
| `'+00:00'` → `'+00'` | 1 | `fromisoformat` reads both alike (3.11+) |
| nonce `{32}` → `{31}` | 1 | only `nonce[:8]` is read |
| `^1` → `^` | 1 | git reads `X^` as `X^1` |
| `--tags` → `--tag` | 1 | git accepts an unambiguous long-option prefix (`git fetch --tag .` rc=0) |
| fetch `-q` dropped | 1 | `git()` captures output |
| `if not m: continue` swapped with the `git show` read after it | 1 | the read's result is used only after the `continue` |
| `if a.fetch:` swapped with `extra = ...` | 1 | `extra` only reads `a.real_extra` |
| `--window` `default=` dropped | 1 | `not a.window` refuses `None` and `[]` alike |
| `cls`'s `or ''` arm dropped | 1 | `None` and `''` read alike |
| `g[1]` → `g[0]` | 1 | GROUP_RE's one group is its whole match |
| `cdf < ALPHA` → `<=` | 1 | no binomial CDF lands exactly on 0.05 in floating point |

**The verdict's own mutants.** F2, F7 and F4 are generated by the rule and killed in the run above. Applied by hand in a scratch root at the head, they fail these checks:

- F2 fails 2 of 96: "size: delivery rows are excluded at their '/', other dev/programme/ files count" and "merge subject: a two-parent commit naming a PR merge after a prefix is no merge (16 stays M<600)".
- F7 fails 1: "first-pass: a PR whose first verdict precedes the window is no first pass in it".
- F4 and the `-cloud` → `cloud` cut each fail 1: "cloud: no decoy marks 17".

## Null control

- **M0.** The sweep's unmutated emission passes, 96 checks with 0 failed, before any mutant runs. A harness that killed everything would fail M0.
- **The rule's baseline end.** The same harness, run over the reviewed head's tool and 76-check self-test (`e53fee3670d81481bd25d255f3f27365e287c12e` with only the harness file replaced), prints `undisposed=128` (rc=1), with the verdict's F2, F4 and F7 among those survivors (Figures). The rule therefore finds the class at the baseline and reads 0 undisposed at the head.
- **No figure moves.** The study bundle printed by the `e53fee3` tool and by the head's tool over the same fetched bus is byte-identical: `diff old.txt new.txt && echo BUNDLE-IDENTICAL` prints `BUNDLE-IDENTICAL`. Both print `facts as of 2026-10-21T15:15Z: tree e7c664856776 roster 2c76c3128bf6`. The tool changes therefore change no figure in the study record.

## Figures

- `python3 -I tools/audit/seat/review_strength.py --self-test` prints `review_strength self-test: 96 checks, 0 failed` (3.11 and 3.14).
- `python3 dev/audit/harnesses/r10_review_strength_mutants.py --jobs 4` prints `RESULT mutants=2333 killed=2286 survived=47 disposed=47 undisposed=0 stale=0`, measured as stated under Head.
- The finder's harness is the tool on the real bus after `--fetch`, both ends being the brief's quoted rates. The rule is: verdicts whose committer time falls in the window, real when the class is in `REAL_CATCH`, divided by the distinct PRs reviewed in the window.
  - `python3 tools/audit/seat/review_strength.py --window A=2026-10-15T12:37Z..2026-10-21T11:00Z` prints `all A PRs 112 verdicts 257 real 58 (0.52/PR)`.
  - The bundle (the study record's command, windows E, L, P1, P2, L1 and S) prints `all L PRs 47 verdicts 84 real 7 (0.15/PR)`.
  - Every window closes by 2026-10-21T15:15Z, so verdicts landing later move neither figure.
- The null sweep: the same harness over the reviewed head's tool (`e53fee3670d81481bd25d255f3f27365e287c12e`, its 76-check self-test, with only the harness file replaced) prints `RESULT mutants=2342 killed=2183 survived=159 disposed=31 undisposed=128 stale=16`, rc=1. F2 (`'dev/programme/delivery/' -> 'dev/programme/'`), F4 (`'cloud' -> 'clou'`) and F7 (`move 1 statement(s) before into if a <= v['t'] < b:`) are among its 128 undisposed survivors.

Every other figure the study record states is printed by the same bundle. The byte-identical null above shows that the tool changes leave all of them where they were.

## Red checks

- **Local**, with `PYTHONPATH=tests/hastub` and `PREPR_SKIP_CLOSURES=1`:
  - At `8174c1503`: `tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. The two are `tests/entities.py` and `tests/harness_headers.py`.
  - At `c2215974c`, which is the head less main's delivery rows: `tests/entities.py` (3.14) prints `ALL 2388 ENTITY CHECKS PASSED`, and `tests/harness_headers.py` (3.14) prints `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - Everything below is at `8174c1503` (the head less #2601's row and roster lines). `tests/structure.py`, `tmp_paths.py --check` and `ci_predict.py` were re-run at `294a4cbbe`, the head less the last merge's delivery rows, with the same results.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `tests/layout.py`: ok. `tests/closure.py selftest`: `ALL 112 closure shrink pins PASSED`.
  - `tests/env_drift.py --claims-only <merge base>`: ok.
  - `tmp_paths.py --check`: 0 refused.
  - `selftest_wiring.py --check`: `78 self-testing, 78 wired, 0 unwired`.
  - `ci_predict.py --base origin/main`: no closures or fast red predicted, and no unpinned mutation site.
- **CI at the reviewed head `e53fee3`.** Every gate check is success or skipped. The one failure is `nightly-status`.
- **`nightly-status`** grades `main`'s scheduled run, not this diff. Main was red from 2026-10-22T02:52Z to 04:35Z (`orchestrator.md` over its cap), and #2595 fixed it. This diff touches nothing the check reads. Carry: dismissed: grades main, not this diff
- **The eight new commits** carry no check runs yet. The orchestrator's push starts them.

## Forward-carry

- The guardrail threshold, the extended class list, the seat-family arm and the planted-defect calibration are on R10-ORCH-MACHINERY's roster carry, and the reviewer-model-in-dispatch control is routed to the same group. Destination: `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-MACHINERY (item b8b28b28)

## Friction

none
