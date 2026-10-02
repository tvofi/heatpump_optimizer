Fix review: merge 66cc8ccdabd40de9dcfff0f6628d20a45344dc33

Round 2 of R9-F10.9 (#1815). Judged the delta 74988886..66cc8ccd: tests/entities.py, +48 lines. Round 1 (e4eda221 + 74988886) found everything else sound; see 1815-review-74988886/VERDICT.md.

- The new check runs closure.main() with `select --files tests/closures.json --diff <ancestor>` and a spy on select. It passes only if all of these hold:
  - the ancestor is the first parent of a commit that changed the table, and its table differs from HEAD's;
  - base_closures(ancestor) equals that ancestor's table;
  - select received exactly that table;
  - an unresolvable ref returns None.
- I ran it in isolation (pin_mutants.py) at 66cc8ccd. Unmutated it passes, with ancestor e4eda221^. With base_closures reading HEAD's table it fails, and with main passing None it fails. Both round-1 mutants are killed.
- A shallow clone yields no ancestor, so the check fails closed, as entities.py's other history checks already do.
- This adds no production code, raises no budget, and leaves VERSION, the manifest and the notes untouched.
- I did not re-run entities.py in full. The fixer reports 2014/2014; cite the head's CI.
