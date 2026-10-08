Fix review: merge c983b9778924a0eefca57e7bb8fbb221462a7570

Round 3, measured at c983b977 (live head at posting; merge-tree clean against today's fb11a0172). Round 3 vs 7162a2d8: the stubbed `--anchor` check, the two closures.json lines removed, main merges, and both round-2 body debts (hand-applied closure disclosure; the time figure).

The stub is honest. Clean: `ALL 2137 ENTITY CHECKS PASSED`, rc=0, 142.7 s. Mutants re-run at this head, post-merge: MC rc=1 killed by `--anchor re-drives one site...`; MB rc=1 killed by `a pinned site's killer is driven first...` (both were fixer-only before). The check fails rather than passes when the anchor pin is absent, and the body names exactly what is deferred. Planted always-green `run_script`: the stub check stays green as disclosed, but four other entity checks go red — the class is not orphaned. The deferred real surface re-measured: real `--anchor` CLI here (real worktree, real subprocess drivers): `PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced, 0 not re-verified`, null control survived, 17.3 s. Note: this head's `mutation` lane printed `MUTATION TABLE PASSED (empty scope)` — the named lane exercises nothing at this PR; the body's own real-run null control carries it, verified above. MA/MD remain the fixer's pre-merge measurement.

Closures: `git diff origin/main...HEAD -- tests/closures.json` is empty. Linux closures lane at head: `SCOPE_CASE: full`, entities recording exit 0, `closure: committed closures cover every file this run touched`, no UNDER-SCOPED; `tests/entities.py lists 1 file(s) this run did not touch (safe: over-scoped)`.

CI: every completed lane green; `nightly-status` red, named in Red checks, main-wide. pr-contract green, preflight clean, no closing keyword.

Evidence: /Users/timmalmstrom/hpo-seats/review-1885/evidence (SUMMARY-c983b977.txt).
