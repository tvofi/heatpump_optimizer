# What is here, and what is not

The six `FINDING_*.png` frames are the ones D4's findings cite by name in their
reproduction steps, so they are kept.

The other 72 screenshots and the two `cells*.json.gz` grid dumps (7.6 MB) are
**not** landed. #859 settled the rule for this repository when it landed round
3's reports: documents and instruments are committed, evidence blobs are not,
because a reader re-runs the harness. Regenerate the full set with

    NODE_PATH=/private/tmp/hpo-pw/node_modules \
    PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
    HPO_PLANDATA=<a private path> node tools/audit/round4/D4/card_grid.mjs

which also rewrites `out/cells.json.gz`. `D4_FREEZE=1` gives the frozen-clock
arm; without it, two states fail to drive because the recorded payload's day is
entirely in the past, which is a property of the fixture and not of the card.
