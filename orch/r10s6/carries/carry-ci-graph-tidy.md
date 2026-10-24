Owner request (tvofi 2026-10-24): the ci.yml pull_request graph on GitHub renders as a tangle. It works correctly, but it is hard to read: about 15 edges cross into `gate`, and fan-in lines run between every column. If it is cheap, the same P2 fixer also tidies it. Cheap means a `needs:`/naming change only:
(a) Make `gate` and `pr-contract` need a few stage fan-in points rather than every job. Where a job already aggregates, use that job's `needs`. Add no new runner jobs unless one costs under 10 s and does not lengthen the critical path (measure it with `ci_critpath.py --charge`).
(b) Order jobs so each column feeds the next.
(c) Shorten the long reusable-workflow prefixes that GitHub truncates ("governan... /", "g.../").
Hard constraints:
- The required-context set in ruleset main-protect-checks and gate's verdict semantics stay byte-identical: no context is renamed, dropped or added unless the ruleset changes with it, and a ruleset toggle needs tvofi's word.
- Critical-path wall time must not grow; prove it with `ci_critpath.py` median over the last 10 runs, before and after.
Evidence: a screenshot or text listing of the before and after graph edge counts. If no cheap version exists, record "dismissed: <binding cost>" in the body rather than doing a large rework.
