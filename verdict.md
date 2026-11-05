Fix review: blocked 0a13dd1a9c053948311df30953557ddb6b341120 class-open: for-target and nested-tuple packing still read IMPROVES (rt_50 +0.0089, rt_49 +0.0017)

bus-nonce: 0ef049209fb1e842afce53c2ea37d9e3

Round 1. I measured head 0a13dd1a9c053948311df30953557ddb6b341120 from a detached worktree. Base is a45cf7f509477596e8024ad2293073f83f04d3e3.

## Block

The brief asks for the sibling packing shapes to be closed. Two shapes I planted myself still lower coord_footprint with nothing improved, and calibrate reads both as admissible IMPROVES at this head (ev/rv_siblings_calibrate.txt):

- rt_50_rv_for_literal: each run of plain assignments becomes one `for a, b, c in [(e1, e2, e3,)]: "_"`. It reads IMPROVES, dS +0.0089, almost the whole +0.0092 that rt_48 reads with C25 ablated. This is the "tuple-unpack in a for target" the brief names. The body says `for a, b in x` is one operation on one value, but a loop over a one-element literal is the generator unpack respelled. `_units` returns 1 for every `For`, and its docstring-shaped body is not counted.
- rt_49_rv_nested_tuple: each run becomes `a, (b, c) = e1, (e2, e3)`. It reads IMPROVES, dS +0.0017. `_pairs` zips only the top level, and `_plumbing` is then asked about a pair whose target is a tuple, so the nested pair counts 1.

## Findings

- Open sibling: a for loop over a one-element literal packs N assignments into one statement (`_units` returns 1 for `For`). On the coordinator, rt_50 reads dS +0.0089 IMPROVES. Carry: R10-FLY-ARCHSCORE-STMT-PACKING
- Open sibling: nested tuple pairs (`(a, b), c = (f(), g()), h()` reads 2 against plain 3, and `(f(), (g(), h()))` reads 2 against 3). On the coordinator, rt_49 reads dS +0.0017 IMPROVES. Carry: R10-FLY-ARCHSCORE-STMT-PACKING
- Over-count in the fix: a single target bound to a tuple or list display is charged once per element (`rhs = len(s.value.elts)`). So `x = [1, 2, 3]` reads 3 and `cur = (self.a, self.b, self.c, self.d)` reads 4, where base read 1 each; `return f(a+1), g(b+1)` stays 1 while `r = f(a+1), g(b+1)` reads 2 (ev/rv_tuple_value_overcount.txt). Because of this, the finder's #3185 case still reads packed and plain differently at this head. I scored #3185 (cc67aa45df1ca9931130c6bdca543d9acc97a748) against its merge base d7582ed404a87603bd02fefda610d7ebbe4181e1 with each archscore swapped in (ev/finder_3185.txt). Base instrument: packed +0.0042, my plain +0.0030. Head instrument: packed +0.0006, plain +0.0029. The packed spelling keeps `cur = (4 attrs)`, which is now charged 4. The control "packed and plain read the same" does not hold. Carry: R10-FLY-ARCHSCORE-STMT-PACKING
- Shapes neither closed nor dispositioned in the body (ev/sib.py, the packed/plain RESULT lines in this verdict's Evidence): a walrus inside a call or a value (`h(a := f(x+1), b := g(y+1))` reads 1 against 2; `c = (a := ...) + (b := ...)` reads 1 against 3), a set or dict display as a statement (1 against 2), and conditional-expression chains (`a = f() if p else g() if q else h()` reads 1 against an if/elif/else of 5). The brief names starred, walrus and conditional chains. Starred is closed (3 = 3). The other two need either a rule or a written disposition. Carry: R10-FLY-ARCHSCORE-STMT-PACKING
- The body's mutation proof names `footprint.PACKING_UNITS = False` as the mutant. Set as a source edit, `vector.measure` resets it to True (`footprint.PACKING_UNITS = "C25" not in off`), and tests/arch_score.py then reads ALL 272 PASSED (ev/mutant_arch_score.txt). The mutant that actually reaches the code is `ARCHSCORE_ABLATE=C25`, or deleting `_units` (below). The body should name it that way. Carry: R10-FLY-ARCHSCORE-STMT-PACKING

## Evidence

- Mutation, step 1: I forced `_units` to `return 1` and ran `PYTHONPATH=tests/hastub python3 tests/arch_score.py`. Result: 5 of 272 ARCHITECTURE SCORE CHECKS FAILED, rc=1. The failures are the packed_plain table, the control, a1_G2_dedupe, rt_48, and "no red-team attempt reads IMPROVES" (ev/mutant2_arch_score.txt). The test is not vacuous.
- Null control: at the head, rt_00_null_rename reads NULL and rt_48 reads NULL. With ARCHSCORE_ABLATE=C25, rt_48 reads IMPROVES +0.0092, as the body says.
- Packed/plain RESULT lines at the head (ev/sib.py; same order at the base): for-target literal 2/3 DIFF; set display 1/2 DIFF; dict display 1/2 DIFF; walrus tuple 2/2 SAME (base 1/2); walrus in call 1/2 DIFF; walrus in assign 1/3 DIFF; ifexp chain 1/5 DIFF; starred value 3/3 SAME (base 1/2); nested tuple expr 2/3 DIFF; tuple-of-tuples target 2/3 DIFF.
- Finder's harness: none is committed, and the packet says "Finder's harness: none named". I built the #3185 reproduction myself (ev/finder_3185.txt, script logic in this verdict). My plain spelling is four explicit assignments with `n[i]`; the finder's plain spelling (+0.0006) is not in the tree. Under the base instrument I re-derived the packed +0.0042 exactly. I could not re-derive the finder's plain +0.0006 and read +0.0030.
- The body's figure "Footprint 2483 and 2381": my archscore runs read coord_footprint 2483 (head instrument) and 2381 (base instrument) on #3185's base tree. The body's figure is on the PR's own tree, which I did not re-derive separately.
- Merge: `git merge-tree --write-tree origin/main 0a13dd1a9c053948311df30953557ddb6b341120` gives eb63c2023b892b53f29e3b131511fec474aebe2c, rc=0, no conflicts (ev/merge-tree.txt).
- VERSION, the manifest version and RELEASE_NOTES.md: untouched (none in the diff). Golden and claim files: untouched. tests/structure.py: untouched.
- Role drift: `git diff merge-base...origin/main -- dev/governance/roles/` touches only nudge.md, not fix-review.md.
- CI: `merge_train.py classify` printed `RED 0a13dd1a9c053948311df30953557ddb6b341120 pending: none red: gate`, rc=1 (ev/classify.txt). The red `gate` is the cancelled gate of superseded run 41937490359. The live run 41937192628 was still queued for tests/fast, mutation, closures, coverage, typing, browser, briefs and arch-instrument when I read it. In that run, arch-score/arch-score is success and governance/delivery-status is failure. I return the block before CI concluded, because the block does not depend on CI. I did not judge the red-check answer (step 11), since the head's workflows have not all concluded.
- Head in body: the body names 0a13dd1a9c053948311df30953557ddb6b341120 as the head.
