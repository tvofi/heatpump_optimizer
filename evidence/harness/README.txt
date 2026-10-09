# Reviewer-built instruments (fix-review.md step 9: disclosed as this reviewer's own, NOT the finder's and NOT the fixer's)
#
# build_fixtures.sh  builds a throwaway origin+clone and the ten attack heads listed in matrix.txt
# run_matrix.sh      runs one app_approve.sh copy over every attack head; rc>1 is reported HARNESS-ERROR, never REFUSE
# make_mutants.py    builds no_literal / no_narrow (the body's two named mutants) and vbase (this reviewer's sound variant)
# norm2010.sh        re-derives the body's #2010 norm() line counts with carry's own pipeline
# mut_vbase.sh       the one-line closure of the DELREADD seam, as measured
#
# The finding this review found (DELREADD) has NO committed harness in the tree: the PR's own arms cover the
# single-commit rewrite (H_PINMOD), the single-commit delete (H_PINDEL), the glob-named addition (H_PINGLOB)
# and the bad subject (H_PIN_BADMSG). Nothing in tools/pr/app_approve.sh's --self-test builds a TWO-commit
# delete-then-readd. That absence is itself the class-open ground.
