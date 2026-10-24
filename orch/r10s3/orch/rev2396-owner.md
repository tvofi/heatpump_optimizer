Approved as tvofi under mandate #201 comment 6175172275 (scope all, valid to 2026-10-28T18:14Z), for the code-owned paths `.github/CODEOWNERS` and `.github/workflows/**`.

Basis: the fix review posted as comment 6252811411 is `merge` at head 860ca72cb48e90e56f8f50663be7bf63a135daaa. Round 2 resolved both round-1 blockers: the conflict with #2405, checked by reading the merged artifact, and the workflow class, where the harness re-ran over the body's window. CI at this head has 48 check-runs, none failed.
