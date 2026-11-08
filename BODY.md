Repairs the blocked verdict `own-row-not-generated` on #3332: its own row `dev/programme/delivery/3332.md` carried a hand-written title and is now the line `record_row.py` generates, `open_row_line(3332, OPEN_ROW_TITLE)`. The rows for #3321, #3322 and #3323 are unchanged.

## Head

a254cd764e49e39691d635246dc5c5b840dbb5e5

## Mutation proof

n/a: the diff is one data row, no production line changed; the generator is untouched.

## Null control

At the previous head e9a128cd283417d9f141780ff6b461678535a0f9 the row read "record: delivery rows for dependabot #3321 #3322 #3323 (R10-RECORD)", and `record_row.py --automerge-check --pr 3332` refused with "this pull request's own row is not the generated open row".

## Figures

- own row equals the generated line: `python3 -c "import sys;sys.path.insert(0,'tools/audit/seat');import record_row as r;print(open('dev/programme/delivery/3332.md').read().strip()==r.open_row_line(3332,r.OPEN_ROW_TITLE))"` printed True at this head (row produced by `python3 tools/audit/seat/record_row.py --write-self-row --pr 3332 --root .` after deleting the old file, since write_rows skips existing files).
- `python3 tools/audit/seat/record_row.py --automerge-check --pr 3332` run at this head's parent still refuses #3321, #3322, #3323 (the API reports them open, not merged into main) and "not record/autofix -> main"; those two refusals concern state and branch name, not row bytes, and are outside this repair. Run with --head at the new SHA it refuses "head moved" because the live PR head is the old one.
- `tools/pr/prepr.sh` ran clean (rc=0) at a254cd764e49e39691d635246dc5c5b840dbb5e5 against origin/main bb7dfb9bd6c6; main had not moved since.

## Red checks

none

## Forward-carry

none

## Friction

none
