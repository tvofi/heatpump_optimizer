Fix review: merge 06201ef470b91af9d36a11591e95f4e1f40b331a

bus-nonce: aa77a9cb45cb97d0c485ea7b23572170

Round 1 (first-round review), record PR 3332, head 06201ef470b91af9d36a11591e95f4e1f40b331a.

## Evidence
- RESULT 3321 row byte-identical to record_row.open_row_line(3321, API title): True
- RESULT 3322 row byte-identical to open_row_line(3322, API title): True
- RESULT 3323 row byte-identical to open_row_line(3323, API title): True
- RESULT 3332 row byte-identical to open_row_line(3332, OPEN_ROW_TITLE): True (the API title names #3321.. and open_row_line refuses it, so the generated self row is the OPEN_ROW_TITLE form, as the checker expects)
- Three-dot diff holds exactly the four dev/programme/delivery/{3321,3322,3323,3332}.md files, one line each; VERSION, manifest and RELEASE_NOTES.md untouched.
- git merge-tree --write-tree origin/main head: exit 0, no conflict.
- merge_train.py classify: GREEN, pending none, red none (ev/classify.txt).
- Mutation, null-control and both-ends checks do not apply: the diff writes no production code.
- Automerge guard refusal for open rows is expected, not a finding.
