Fix review: merge 652929f336d6b8fe2bcaae9cf237a20e61bb8620

bus-nonce: 1c833ecb7cec3a8cb692239c6a516ec1

## Evidence
- The PR was already merged by tvofi (merge e4c9e2016) when reviewed, so the three-dot diff against current main is empty. I reviewed the diff against the PR's own base c3b7c96 (8 files, +8/-7).
- Only dev/programme/delivery/<N>.md files change: 3048, 3059, 3061, 3068, 3075, 3079, 3086 (open -> merged) and 3093 (new). No production code, claim file, VERSION, manifest or RELEASE_NOTES change.
- Each row is one line in the row_line shape. Merge SHAs match the merge commits on origin/main: 3048=92588d5, 3059=42b23e4, 3061=fb0a6d5, 3068=f4a5082, 3075=6421fe1, 3079=bc56483, 3086=1a80513.
- Titles and group phrasing are true. Rows whose subject no roster group claimed (3048, 3061, 3068, 3075, 3079, 3086) carry neutral phrasing.
- All seven PRs had open rows at the base, so the PR flips them to merged and adds none duplicated.
- tests/delivery_status.py at the head exits 0. It lists #3080 and #3082 as pending rows, the ordinary batch state, and says it is not a required check.
- merge_train classify at the head: GREEN, pending none, red none. The packet's whole check-run set has no red check. ## Head names the head and ## Red checks answers the three checks that could stand red on main.
- No commit message in the range carries a Claude footer or trailer.
- Minor: 3059 and 3075 and 3086 repeat the group name in parentheses and 3048 does not. This is cosmetic, not a defect.
