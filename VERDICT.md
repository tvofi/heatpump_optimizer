Fix review: blocked fc75984b2e961563bed4e952272024f14fb3d764 preflight-mismatch: closures is red (UNDER-SCOPED tests/entities.py misses dev/audit/rounds/round4/D12/cells.py and d12lib.py; tests/harness_headers.py misses corpus_churn.py), closures-autofix reports skip-classifier-disagrees so no bot commit comes, and the body says "Red checks: none" and that prepr's ci predict predicted no closures red

bus-nonce: 0061fa1682d55f19d2824702539cb161

Round 1. Reviewed at head fc75984b2e961563bed4e952272024f14fb3d764 (= 0461329ce + the delivery row only; merge base 694120d5a). Detached worktrees, seat venv python 3.14. Every code figure below was taken at 0461329ce and re-taken at fc75984b2 for the arm and the enumerator, since the delta is the row only.

RESULT ci_closures=failure (check-run 116584227429): UNDER-SCOPED tests/entities.py reads dev/audit/rounds/round4/D12/cells.py, dev/audit/rounds/round4/D12/d12lib.py; UNDER-SCOPED tests/harness_headers.py reads dev/audit/rounds/round5/D11/seat-b/corpus_churn.py
RESULT ci_closures_autofix=failure (check-run 116595179899): skip-classifier-disagrees, "THE REPAIR DID NOT HAPPEN"
RESULT ci_other_required=success (fast 3.14 MODE: FULL, ALL 2320 ENTITY CHECKS PASSED; mutation, pr-contract, briefs, coverage, composed-proof, lane-proofs and the rest green)
RESULT finder_dora_keys_loads base=0 head=1 (bare); FIX_IMPORT=1 base=0 head=1; FIX_IMPORT=1+DORA_EXCL base=1 head=1
RESULT corpus_churn base_rc=1 (FileNotFoundError .claude/workflows/policy_budgets.json) head_rc=0
RESULT mutants M1..M5 killed=5/5 (M1, M4, M5 fail the cited-program check; M2, M3 fail both checks)
RESULT failing_first 8d5b657e1=FAIL (dora_keys: d11lib, :103 cfr_exclusions) aaaac99d1=PASS cccf2f932=FAIL (corpus_churn :68/:100/:133) a86998d3e=PASS
RESULT null_control codeowners_gap: 4 held stale literals, 0 opened faults; arm passes on it
RESULT carry_plant python3 -I dev/audit/rounds/round4/D11/merge_census.py in a staged carry: REFUSED (does not load, d11lib); same with the pre-move spelling tools/audit/round4/...: REFUSED; unstaged plant: not seen (index read, by design)
RESULT open_shape_plants refused=5 escaped=8 (see findings)
RESULT enumerator base=seams 2872 broken 369; head=seams 2878 broken 368 (body says 2877)
RESULT merge_tree vs origin/main rc=0; VERSION/manifest/RELEASE_NOTES untouched; claim files untouched; structure ratchet PASSED

What blocks:
1. closures is red on this head and closures-autofix will not repair it. The committed tests/closures.json was re-recorded with a Darwin --single, whose sys.addaudithook trace does not follow the arm's subprocess probe: units.py's child imports cells.py and d12lib.py, which only the Linux strace lane sees. And moving corpus_churn.py into INERT_EXCEPT makes tests/harness_headers.py's read of it a recorded dependency that its committed closure does not list. ci-autofix.md: on skip-classifier-disagrees the --single prohibition lapses; re-derive both named scripts (entities.py's child reads need the Linux recording, or add them by hand only if the rule allows; harness_headers.py --single) and commit tests/closures.json.
2. The body owes that red an answer (defect-root-cause.md second trigger): it states "Red checks: none" and that prepr.sh's ci predict predicted no closures red. Name closures and say why the local predict missed it (the Darwin recorder does not see the probe's child; the predict did not reach harness_headers.py).
3. Body figures stale at the stated head, to fix in the same re-take: the enumerator reads seams=2878 at 0461329ce/fc75984b2 (2877 was 4e28c97f7, before the INERT_EXCEPT literal added one seam), and the "whole delta" omits two broken seam lines that shifted in tests/closure.py (3844/3845 -> 3850/3851, same literals, sweep's tests/ "not applicable" bucket). Re-take the whole body at the new head.

What holds (no action owed for the block):
- The dora_keys.py and corpus_churn.py repairs resolve through tests/layout.py's locate/canon; finder's harness moves 0 -> 1, corpus_churn runs end to end.
- INERT_EXCEPT by name and the index reads are sound under #357: no INERT-and-recorded pair is introduced, the route is the documented one (dora_cfr.py precedent), and reading INERT policy/carry text from the index mirrors tests/layout.py.
- Forward-carry confirmed: wave-r10-groups.json R10-BRIEFS-FOLD's brief carries "confirm under D2 that the 35 evidence-only stale-path seams are by design".

Findings (not blocks; beyond the finder's demonstrated shape, which the arm catches: a sibling import, a one-hop named literal, a direct open):
F1. Open-shape escapes in _sp_literals, each planted into units.py's source: two-hop alias (_A = lit; _B = _A; open(_B)), the same via os.path.join, a pathlib / whose result is read by .read_text() (direct or through a name), an f-string with an interpolated prefix (f"{root}/lit"), a dict value read by subscript, a tuple-unpack assignment, an annotated assignment. Refused: one-hop name, open(Path('.') / lit), bare f"lit", './' + lit, Path(lit).read_text(). None of the 5 cited programs uses an escaping shape on a repository path today (checked).
F2. The citation side is main-only: policy files and carries are INERT and read from the index, so a PR that only adds a broken citation is SCOPED with tests/entities.py skipped (closure.py select --files carry-201.json: 0 scripts); main's forced full run catches it one merge later. The program side (d11lib.py, dora_keys.py, cfr_exclusions.json) is in the closure and selects the script.
F3. carry-201's remeasure commands still spell pre-move paths (tools/audit/round5/D11/seat-b/corpus_churn.py, tools/audit/round4/D11/dora_keys.py, tools/audit/round5/D13/seat-a/dora_cfr.py) that do not exist; the arm follows them through locate and prints "runs", and tests/layout.py's reference arm skips them by design (a retired path that the move map puts under a historical prefix). A seat that pastes the command gets ENOENT: the citation half of the same class, left open.

Evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/revstale-ev (arm.py is the reviewer's own driver of the arm block; plants.py, d13_both_ends.txt, churn_*.out, mutants.txt, failing_first.txt, carry_plant.txt, plants.txt, enum_*.out, job_*.log).
