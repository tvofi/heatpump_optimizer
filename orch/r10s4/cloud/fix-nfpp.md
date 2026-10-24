# Fixer, R10-FLY-NO-FOOTERS-PUSH-PATHS (lane FLY, size S, instrument), topic r10-fly-no-footers-push-paths. Cut from current origin/main (4c31eb16 or later).

Read the group with jq from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json, roster tip e5fdf08cc or later. Read its brief in full. Files: tools/audit/seat/handoff_push.sh, tools/audit/seat/body_push.sh, tools/audit/seat/ci_probe.py, tools/pr/app_push.sh, tools/audit/seat/ref_privacy.py.

Two holes let commit 767a06f7f, which carries Co-Authored-By and Claude-Session trailers, reach a PR head after the guard a4b27986 landed. Close both:
1. A push path that publishes commits runs no message guard. handoff_push.sh, body_push.sh and ci_probe.py push all publish commits. Each must judge every commit message it publishes using ref_privacy's existing attribution check: share the check, do not copy it. The cloud harness's own `git push` cannot be hooked from the tree, so say in the body what covers it. Item 2 is the backstop.
2. app_push.sh judges only first-published commits (line ~481). A commit first published on a ci-probe/* ref is therefore exempt. Make app_push judge every commit the PR adds over origin/main (`git rev-list origin/main..HEAD`), not only first-published ones.

Commits authored before the guard (a4b27986, 2026-10-22T23:07Z) are already dismissed by the orchestrator's ruling, because we do not rewrite a published branch. If item 2 would refuse an existing open PR because of such a commit, measure which ones and say so in the body. Do not add an allow-list silently: propose one keyed on the commit SHA, with the ruling cited.

Author identity: the owner's rule names footers, trailers and session links, not authors. The orchestrator's ruling under mandate 6329234399 is that author identity is OUT of scope for this group. Record that in the body and do not widen the check.

Each item needs a failing fixture first and null controls: a clean commit passes on every path, and an old dismissed commit is handled as the body states. Mutants: drop the judgement on each path, and restrict app_push back to first-published. Each must go red. Update tools/audit/seat/INSTRUMENTS.md for the behaviour change. Before returning, run `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` until it prints all ok at the final head. That includes the agreement lane and no ADDED UNPINNED mutation sites: pin with `python3 tests/mutation_table.py --pin-killed`, and add a value check for each survivor.
Rules: PREPR_SKIP_CLOSURES=1; spare the GitHub API (stop on a 403); no Claude footers, Co-Authored-By or session links anywhere.
