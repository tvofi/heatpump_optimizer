Fix review: merge cabf2d9f0a34d7fa6a0b16c003899cdac9c9fe38

bus-nonce: 015c44fe6bbc967f69f6876ffbdb4b8d
This is round 4 for the PR. The fixer's change this round repairs the body; it is not a re-cut. It adds the missing ## Red checks row and updates ## Head. Under that repair I judge only the body delta and the main-merge delta on top of aef46436e, which my previous verdict (review/2351 5bd30e631) measured in full.

## My previous block: resolved
The body (ref 7c538e829) now carries: "`pr-contract` -- red at `0adc19241` (run 117608332257, 06:40Z): `## Head` still named `f4df860` ...; cheaper detector `tools/pr/prepr.sh` step 7".
That matches the check-run exactly: run id 117608332257, 06:40:06Z, failed on "PR-BODY: 1 error(s)" while the body named f4df860.
With this row, all 15 failures on the first-parent heads through aef46436e are named and answered. The head adds none: cabf2d9f0 has 0 failure check-runs.
The body diff against what I read last round has three parts. It adds this row. It repoints ## Head to cabf2d9f0 and its code head to aef46436e. It adds a carry sentence, which I re-derived:
RESULT `git diff --quiet 0adc19241 aef46436e -- custom_components 'tests/*.py'` rc=0
RESULT that merge moves 31 tests/mutation_ledger/killed_by rows and nothing else under tests/, none of them on this PR's sites.

## The main-merge delta
cabf2d9f0 = aef46436e + main 994695e06. `git merge-tree --write-tree aef46436e 994695e06` gives tree 62a52fcf3, which is the head's own tree, so the merge resolved nothing.
The merge changes 8 files, all records: 7 under dev/programme/delivery and 1 roster. It changes nothing under custom_components/, tests/*.py, log_flood/, tools/ or .github/.
The production and test trees are therefore identical to 0adc19241 and aef46436e, so my previous figures carry:
- the probe's recur_* arms all recur>=1;
- my own harness's arms recur at 2, 1 and 1 (its reload arm reads 0 only because my harness never calls async_shutdown; the probe's recur_reload, which does, reads 2);
- the two survivors are killed by features.py;
- the census reads sites=71 seams=65, all on the barrier list.
merge-tree against current origin/main: rc=0, and the head is 0 commits behind.

## CI at cabf2d9f0a34d7fa6a0b16c003899cdac9c9fe38, latest run per name (evidence/r4.check-runs.head.tsv)
27 success, 15 skipped, 0 red, and every workflow has concluded. That includes fast (3.14), mutation, closures, arch-score and pr-contract (08:06Z, green on the repaired body). Not re-run: the gate and the mutation table.
Carried notes, not blocking:
- Deleting the forget_held call in async_shutdown survives features.py; only the probe kills it.
- The flow-unit clearing call in _space_target is redundant with the options-change reload.
Evidence: /Users/timmalmstrom/hpo-seats/r10s3/review-n-log-flood/evidence
