Fix review: merge 2cfa51a43dea225ad55adf1ac3826f58da613655

bus-nonce: 1d8cdfb0c1c417a30fdbcd6183797103

## Evidence
- review_carry.py aca500910 -> 2cfa51a43dea225ad55adf1ac3826f58da613655: CARRY (one branch-only non-merge commit, "ci: pin killed mutants").
- merge-tree --write-tree origin/main 2cfa51a43dea225ad55adf1ac3826f58da613655: clean (rc 0).
- merge_train.py classify exited 2 here: "REFUSE ci: the check runs at 2cfa51a43dea could not be read" (unreadable by the tool in this seat). I read every check-run of the head myself over the GitHub MCP, both pages (107 runs), see ev/checks.txt.
- Concluded reds of the head: pr-contract / pr-contract (06:42Z run), governance / delivery-status, tests / nightly-status. The body's ## Red checks names each: pr-contract and gate of 06:42-06:44Z (cured by the body edit), and nightly-status and delivery-status as inherited from the merge base. tests / mutation-autofix is named too and is skipped at this head.
- Later pr-contract runs (06:56Z, 06:25Z) are success, so the body lints. gate is success at 06:59Z and 07:01Z. tests / mutation is success.
- ## Head names one PR head (2cfa51a43dea225ad55adf1ac3826f58da613655) and refers to aca50091 only as the previously reviewed head.
- Code not re-reviewed, per the brief.
