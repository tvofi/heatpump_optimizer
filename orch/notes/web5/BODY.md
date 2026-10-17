_Requested by **tvofi**_

The README linked the product page repo-relative (`docs/index.html`, README lines 16 and 1012), so on github.com the link opens the raw file, not the published page. Both links now point at the Pages URL the deploy actually serves, and the W1 pin (`tests/doc_claims.py` arm 1b, the R9-WEB-1 product-page arm) refuses a repo-relative README product-page link so the regression cannot return. The published form was determined before it was written, from the deploy's own staging and the live site: `.github/workflows/pages.yml` stages `docs/index.html` at the artifact root (`cp docs/index.html _site/`, the step `tests/entities.py` runs by name), so the served URL is `https://tvofi.github.io/heatpump_optimizer/` (a project Pages site), and `.../docs/index.html` answers 404. The absolute Pages URL also works on the published site itself: `tools/site/build_docs.mjs` `resolveHref` keeps every absolute README link verbatim when it renders the README into `readme.html`. No other repo-relative product-page link exists in the tree; `RELEASE_NOTES.md` and `docs/delivery/1846.md` mention the path as records of what was built, not links, and stay as written.

## Head

`26b8d16c505ba9183edf46bdf8d95b2982661ab3` adds one commit to the authored head, containing only this seat's resume note, `handoff/round9/fix/resume/WEB-5.md`. The authored code head, where every figure below was taken, is `5dbd37263519e3359a7c07348a3601154e4a3f7a`; the note commit changes no code, test or document.

## Mutation proof

Base `1913f0dd736cb66b800b5eabfa6973a917459d83` (origin/main at the branch cut). The pin landed first (e28d23e7) with the README still at base and ran red; then the README fix (d4c76799). Proof the pin carries the property: at the fix commit's content, line 16's link was reverted in place to the repo-relative form and the arm re-run from the repository root:

    /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/doc_claims.py

      FAIL every README link to the product page is the published Pages URL, never a repo-relative path
    1 of 160 checks FAILED

README was then restored and the arm re-run green before the handoff. A disclosed self-correction in the process, not in any figure: the restore was `git checkout -- README.md` while the fix was still uncommitted, which wiped it; the fix was re-applied (the diff above is the re-applied form), committed, and every measurement below was taken at or after the committed head. The diff touches no production line —

    /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/mutation_table.py --scope changed

    MUTATION TABLE -- scope changed: no production code line added or modified against the base
      no production file in scope; nothing to mutate

so there are no mutation survivors to triage; CI's mutation check runs production closures this diff does not reach.

## Null control

The unmodified tree with only the pin added (e28d23e7, README at base) is red, naming both links — the same command as the mutation proof, `1 of 160 checks FAILED`. That is the base red of the pin pair; at the fixed head the same arm runs green (`ALL 160 checks PASSED`), with the README Documentation two-way comparison still intact: the pin learned the published URL as the `docs/index.html` identity (a README link in published form satisfies the table both ways), so the check does not pass by finding nothing.

## Figures

Each figure: the command, then what it printed. Commands run from a repository root.

- Failing pin at the base README (commit e28d23e7, pin only):

      /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/doc_claims.py

      FAIL every README link to the product page is the published Pages URL, never a repo-relative path  [README links the product page as 'docs/index.html', ... it must be the published Pages URL https://tvofi.github.io/heatpump_optimizer/; ...]
    1 of 160 checks FAILED

- Green at the head (5dbd3726), the scoped arm:

      /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/doc_claims.py

    ALL 160 checks PASSED

- The served URL, the one the README now names, against the path the old link form would produce:

      curl -sI https://tvofi.github.io/heatpump_optimizer/ | head -3

    HTTP/2 200
    server: GitHub.com
    content-type: text/html; charset=utf-8

      curl -sI https://tvofi.github.io/heatpump_optimizer/docs/index.html | head -2

    HTTP/2 404
    server: GitHub.com

      curl -s https://tvofi.github.io/heatpump_optimizer/ | grep -o '<title>[^<]*</title>'

    <title>Heat Pump Cost Optimizer</title>

- The gate's scope at the head, derived not assumed (the mode line, never the count):

      D=$(mktemp -d); /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.run"

    MODE: SCOPED -- 6 script(s) run, 24 scoped out.
    tests/doc_claims.py / tests/entities.py / tests/harness_headers.py / tests/md_tables.mjs / tests/plan_view.py / tests/card_drift.mjs

- The six scoped scripts green at the head (PYTHONPATH=tests/hastub):

      /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/doc_claims.py            # ALL 160 checks PASSED
      /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/entities.py              # ALL 2137 ENTITY CHECKS PASSED
      /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/harness_headers.py       # ALL 105 HARNESS HEADER CHECKS PASSED
      node tests/md_tables.mjs                                                               # RESULT doc_orphaned_table_rows=0 / doc_misrendered_lines=0
      /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/plan_view.py             # plan reason codes, price provenance and slot energy OK
      node tests/card_drift.mjs                                                              # card_drift: identical in all 40 states

- The ratchet, which runs before every push regardless of scope:

      /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/structure.py

    STRUCTURE RATCHET PASSED

- The D6 link census `harness_headers` executes re-measured over the new links (its committed output moved with the tree, and the re-measured output is what this PR commits): relative links 93 -> 91 (README lines 16 and 1012 were both relative), external links 16 -> 17 (both lines now cite the same published URL, deduplicated to one); verdicts unchanged (`broken=[]`, relative still true; the `--links` HEAD run stays CI's). The moved figures, as the harness wrote them:

      git diff 1913f0dd736cb66b800b5eabfa6973a917459d83 HEAD -- tools/audit/round4/D6/claims.json | grep '^[+-].*links'

    - "claim": "every relative link resolves (93 links)",
    - "claim": "every relative link resolves (91 links)",
    - "claim": "every external link answers 200 to a HEAD request (16 links)",
    + "claim": "every external link answers 200 to a HEAD request (17 links)",

## Red checks

None on this branch: every script the scoped gate names is green at the head, and `tests/structure.py` passes. The selection skips `tests/features.py` and `tests/optimality.py` (no changed file is in their measured closures); they are left to CI, where the known Mac-local reds (R9-F2.1 P3, `features/optimality`; card_browser P9) are judged on CI per the standing disclosure — nightly-status expected-red, not chased here. One local check did go red on this branch and is answered: `tools/audit/prepr.sh`'s `closures` step refused twice with `failed while being recorded: tests/entities.py (exit 1) tests/harness_headers.py (exit 1)`. The cause is the recorder's default interpreter, `PYTHON="${PYTHON:-python3}"` (`tests/derive_closures.sh` line 35) — pyenv 3.11 here, the interpreter this seat is told never to use — not the tree: under the seat venv the identical step records `scoped recordings are covered; left to CI: tests/md_tables.mjs tests/card_drift.mjs`, and both scripts pass directly at the head (figures above). The standing cost of a cheaper detector: none built; a per-seat venv default in the recorder would remove the trip, which is a change to `tests/derive_closures.sh`, not this PR's. A second local refusal, standing and disclosed: at the head (`26b8d16c5`) `tools/audit/prepr.sh`'s `transport` step refuses — `26b8d16c5 handoff/round9/fix/resume/WEB-5.md -- transport is in the code head's ancestry; the body goes on the orphan ref handoff-body/<topic> (fixer.md step 6), and the code head is re-cut without these commits`. The file it names is this seat's resume note, `handoff/round9/fix/resume/WEB-5.md`, which the roster's own `resume.note_file` field places on this branch and the orchestrator's instruction orders as a note commit on top of the code; the transport rule exists so a PR *body* never rides in the code head, and the body here does not — it travels on the orphan ref `handoff-body/r9-web-5` as `fixer.md` step 6 requires. Three round-9 PRs shipped the same note in their code heads and main dropped them in a record commit (`541e4611d`), so the disposition is the roster's convention over the local rule; `pr-contract` does not re-execute the transport step, so the pull request does not go red on it, and every other prepr step at this head is green (the digest's single set bit is this step).

## Forward-carry

none

## Friction

none
