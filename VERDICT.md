Fix review: blocked b8fba2c8d5ab03067539c7e8d06e369f85162c31 countermeasure-unsound: the built detector measures the shell's cwd tree, not the checkout it is given; the RCA's own Reproduce recipe returns rc 1 for the fix tree, and a defective v7.1.5 reads rc 0 from a fixed cwd

bus-nonce: 02fea4f6344a76b34285b6cbdbd280ad

Round 1 of the fix review for PR #3316 (R10-RCA-COP-UNMEASURED). Measured at head `b8fba2c8d5ab03067539c7e8d06e369f85162c31`, merge base `2a3c05644d85b7ee5c2c314fde5aca950e4aba91`. `refs/pull/3316/head` was re-read at 11:00Z and has not moved.

## Block

- The RCA's only built countermeasure, `dev/audit/harnesses/r10_rca_cop_unmeasured.py --check <checkout>`, does not measure `<checkout>`. It prepends `<root>/tests/hastub`, `<root>/custom_components` and `<root>/tests` to `sys.path`, then imports `harness`. `tests/harness.py:22-23` (at this head and at every tree measured) then runs `sys.path.insert(0, "tests")` and `sys.path.insert(0, "custom_components")`. Those cwd-relative entries go ahead of the root's, so `heatpump_optimizer` loads from whatever checkout the shell is in. Shown in `ev/cwd_dependence.txt`:
  - The RCA's `## Reproduce` recipe, run verbatim from a repository checkout at this head (`python3 -I dev/audit/harnesses/r10_rca_cop_unmeasured.py --check <fix tree 2d010b091>`), prints `RESULT null=graded tuya=graded metered=graded` with rc 1. The document says `# rc 0`.
  - Run from inside the fix tree with the root set to v7.1.5 (`516ad1b6b`), it prints `null=withheld tuya=withheld metered=graded` with rc 0. That is a defective release certified as fixed: a false clean from the detector.
  - My first measurement pass, run from the repository root, printed rc 1 for every tree including the fix head (`ev/harness_runs.txt`). That is how I found this.
  - The module docstring says it "builds the real coordinator ... from the checkout named on the command line". That is not true unless the cwd is neutral.
  - The fix is small and has to go in the PR: `os.chdir(root)` before the imports (or importing `harness` before the inserts and then re-putting the root first), plus a control that runs the detector from a cwd holding a different tree and shows the verdict follows `<checkout>`. The documented recipe and every rc in section 5 should then be re-taken under it.
  Carry: R10-RCA-COP-UNMEASURED

## Findings

- Follow-up: the same cwd capture reaches every harness that takes a root and imports `tests/harness.py`. Eleven files under `dev/audit/harnesses/` pair `from harness import` with a root-relative `sys.path` insert (`ev/class_sites.txt`, a pattern grep, not a per-file trace). Each one silently measures the cwd's tree when run from a checkout. The single sound repair is in `tests/harness.py`: anchor its two inserts to `os.path.dirname(__file__)` rather than the cwd. This seat's PR may land that repair with its own control, or record why not. Either way, the RCA's process section should name it, because a detector that reads the wrong tree is the same "never traced its inputs" unit this RCA indicts.
  Carry: R10-RCA-COP-UNMEASURED
- Follow-up: CI is not green at this head, independent of the block. The required `gate` is `failure` on every entry. The only code run (`CI code pr=3316`, run 42463804677, attempt 44) concluded `cancelled`, with `tests / fast (3.14)`, `tests / closures`, `coverage`, `coverage-ratchet`, `ci-ratchet`, `graders-head-copy`, `lane-proofs`, `claims-autofix`, `closures-autofix` and `governance / instrument-self-tests` cancelled. The code gate printed `FAIL tests / fast (3.14): cancelled (this run)`. The latest edit gate (128707623015) exited 3 on `RATE-LIMITED reset_epoch=1794135167`. So no run has shown this head's suite green. The body's `## Red checks` names the cancellations truthfully, but it was written before the 10:25Z, 10:45Z and 10:47Z gate entries and does not mention the RATE-LIMITED one. The next head needs a code run that concludes.
  Carry: R10-RCA-COP-UNMEASURED

## Evidence

- Harness, neutral cwd (`/tmp`), the PR head's copy of the detector: v7.1.5 rc 1, merge base `2a3c05644` rc 1, origin/main `4fe7d5934` rc 1, PR head rc 1, fix head `2d010b091` rc 0 (`null=withheld tuya=withheld metered=graded`). The null band `{(2, True): [2.5533587538536424, 1]}` with `equal = True`, and the tuya band `[3.1833333333333336, 3]`, reproduce the RCA's table exactly. `ev/cwd_dependence.txt`.
- Controls, neutral cwd, on the fix tree `2d010b091` (`ev/controls.txt`): skip (`if measured:` changed to `if False:`) gives all withheld, rc 2. Door N (the no-heat arm of `cop_sample` returns `True`) gives `null=graded tuya=withheld`, rc 1. Door T (`_estimated` returns `False` first) gives `null=withheld tuya=graded`, rc 1. All three match the body.
- Hand mutants of the detector that I re-ran myself: M-a (the verdict changed to `return 0`) gives rc 0 on v7.1.5, killed. M-e (`null` dropped from the verdict) gives rc 0 on door N, killed. I did not re-run M-b, M-c, M-d or M-f.
- Figures re-derived at the merge base (`ev/figures.txt`): the name census gives 23. `git tag --contains a63b576cd -l 'v*'` gives 135 today, which is 134 without the later `v7.1.6`, so it matches the RCA as of v7.1.5. `a63b576cd` is dated 2026-08-26 (PR #50, v4.0.0). `sweep-P5.md:37` and `D1.md:10-11` quote verbatim. `DEFAULT_CAPACITY_CURVE_ENABLED: Final = False`. `df7db8215` is dated 2026-08-22.
- Not verified: the cost-test inputs (#3297's 12.0 h, 12 commits, 39 files, +700/-146, the 0.1-per-round estimate). The RCA itself labels the 2 to 3 min per name and the 1 to 3 h seat cost as estimates.
- Process state (c): checked against the tree. D1 names "fabricated data as measured" with no method step that reaches it. The P5 sweep cleared `_cop_health_cusum` by its container. On the history, `a63b576cd` added the watch onto the inferred sample. I did not open the claim about #2262's study text.
- Closure classification: the new harness is added under `inert_reads` / `tests/harness_headers.py` in `tests/closures.json`. No `*_budgets.json`, no claim file, no `VERSION`, no manifest and no notes heading appear in the three-dot diff. Nothing is under `custom_components/`.
- `git merge-tree --write-tree origin/main b8fba2c8d` exits 0, so there is no conflict.
- `merge_train.py classify b8fba2c8d... --pr 3316` was run at about 10:55Z and 11:00Z. Both runs gave `REFUSE ci: the check runs at b8fba2c8d5ab could not be read` with rc 2, so the classifier's verdict is unreadable. I read the check runs directly through the commit's `check-runs` API across all 107 entries (`ev/ci.txt`, and the gate logs quoted above).
- I measured with the PR's own harness, because the finder named none: the packet says `Finder's harness: none named`. This is an RCA seat, and the harness is the product under review.
