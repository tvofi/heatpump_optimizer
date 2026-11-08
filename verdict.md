Fix review: blocked e9a128cd283417d9f141780ff6b461678535a0f9 own-row-not-generated: #3332's own row is not record_row.py's open_row_line(3332, OPEN_ROW_TITLE)

bus-nonce: 0188809d490af29a59d4701d24f27c90

## Block

dev/programme/delivery/3332.md holds the PR's own title, "record: delivery rows for dependabot #3321 #3322 #3323 (R10-RECORD)". The generated self-row (record_row.py self_row / _row_refusal) is `open_row_line(3332, OPEN_ROW_TITLE)` with OPEN_ROW_TITLE = 'record: delivery rows (autofix)', so the row must read "... — **open**, record: delivery rows (autofix)". Byte comparison at this head: 3321, 3322, 3323 match (titles read from the API, rows regenerated); 3332 differs. `record_row.py --automerge-check --pr 3332 --head e9a128cd283417d9f141780ff6b461678535a0f9` reports "#3332: this pull request's own row is not the generated open row" (ev/automerge.txt). The three refusals for #3321-3323 ("not reported merged") are the expected open-row refusals and are not findings. The offending title also names #3321/#3322/#3323, which open_row_line itself refuses because mentions() would read them as rows of those PRs.
Fix: rewrite 3332.md with the generated open row (autofix title).
Carry: built-here

## Evidence

- Three-dot diff: exactly four files, dev/programme/delivery/{3321,3322,3323,3332}.md, one added line each; VERSION, manifest and RELEASE_NOTES.md untouched.
- Rows 3321/3322/3323 byte-equal to open_row_line(N, API title) (ev/gen.txt). API titles: mermaid 12.2.0->12.3.0 site group; actions group 3 updates; pip group in /tests 16 updates.
- merge-tree origin/main vs head: clean (ev/merge-tree.txt).
- CI classify at review time: see ev/classify.txt (WAIT, no gate red; not needed for this block).
