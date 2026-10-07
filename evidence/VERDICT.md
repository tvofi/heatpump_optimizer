Fix review: merge 0a68a28687921983ea47eb006ec7c75401e396cc
bus-nonce: 8e10584601ff1dda8e0b5a4787cbbbef

Delta review e4c51f12..0a68a286 of PR #2007. Head read live before posting: 0a68a28687921983ea47eb006ec7c75401e396cc.

RESULT code-delta: the PR's own diff (custom_components, tests/features.py, tests/guard_pins.py, tests/mutation_ledger) is line-identical between e4c51f12 and 0a68a286; only main moved (09ba95d0/c327da7f merged, carrying 60c00052). The PR touches the same 28 files; tests/closures.json, both claim files and VERSION are untouched; git merge-tree --write-tree origin/main exits 0. The earlier merge verdict at 29751f36 and the _service refactor review (behaviour-equivalent; note only: _option_for and int(value) evaluate before the try, neither can raise) stand.
RESULT ci (CI's check-runs at 0a68a286, not local runs): closures success on the rerun (job 112977624580, run 37662110687), closures-autofix skipped, pr-contract success (both runs), mutation, typing, env-matrix, coverage, coverage-ratchet, fast (3.14), closure-scope, hassfest, policy-docs, CodeQL success. Non-green: delivery-status and nightly-status (grade main, not this diff's); budget-raise-gate has a cancelled run with a success twin.
RESULT red-checks: the body's Red checks section now names closures and closures-autofix (job ids 112866129364 and 112886615096, cause: main's inert-read record for eg_b7_seam_hubs.py, answered by merging 60c00052) and its Head section names 0a68a286. The step-11 block at e4c51f12 is cleared.
