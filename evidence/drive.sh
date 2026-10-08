set -u
cd /Users/timmalmstrom/hpo-seats/review-2053/wt
PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/entities.py > /Users/timmalmstrom/hpo-seats/review-2053/evidence/ent-head.txt 2>&1; echo "head rc=$?" >> /Users/timmalmstrom/hpo-seats/review-2053/evidence/drive.log
sed -i '' 's/^  cancel-in-progress: false$/  cancel-in-progress: true/' .github/workflows/budget-raise-gate.yml; git diff --stat >> /Users/timmalmstrom/hpo-seats/review-2053/evidence/drive.log
PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/entities.py > /Users/timmalmstrom/hpo-seats/review-2053/evidence/ent-mut-cancel.txt 2>&1; echo "mut-cancel rc=$?" >> /Users/timmalmstrom/hpo-seats/review-2053/evidence/drive.log
git checkout -- .github/workflows/budget-raise-gate.yml
sed -i '' 's/^  group: \${{ github.workflow }}-\${{ github.run_id }}$/  group: \${{ github.workflow }}-\${{ github.event.pull_request.number || github.run_id }}/' .github/workflows/budget-raise-gate.yml; git diff >> /Users/timmalmstrom/hpo-seats/review-2053/evidence/drive.log
PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/entities.py > /Users/timmalmstrom/hpo-seats/review-2053/evidence/ent-mut-group.txt 2>&1; echo "mut-group rc=$?" >> /Users/timmalmstrom/hpo-seats/review-2053/evidence/drive.log
git checkout -- .github/workflows/budget-raise-gate.yml
git show 470bbd6087e5978eae594e616a76e207336b289c:.github/workflows/budget-raise-gate.yml > .github/workflows/budget-raise-gate.yml; git diff --stat >> /Users/timmalmstrom/hpo-seats/review-2053/evidence/drive.log
PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python tests/entities.py > /Users/timmalmstrom/hpo-seats/review-2053/evidence/ent-baseworkflow.txt 2>&1; echo "base-wf rc=$?" >> /Users/timmalmstrom/hpo-seats/review-2053/evidence/drive.log
git checkout -- .github/workflows/budget-raise-gate.yml; git status --short >> /Users/timmalmstrom/hpo-seats/review-2053/evidence/drive.log; echo DONE >> /Users/timmalmstrom/hpo-seats/review-2053/evidence/drive.log
