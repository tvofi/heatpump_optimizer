Fix review: blocked d0d35231c633ca447acf04770f9034281417b72d class-open: program spellings outside PROGRAM remain unread and undispositioned, an interpolated program in one string literal (Python f"{GH} pr merge {n} --subject x", "%s pr merge" % GH, "{} pr merge".format(GH), JS `${cfg.gh} pr merge`)

bus-nonce: 1eefc0553e18f66d3a0ba6b90e5fd480

## Block

This is review round 5. `fixer.md` owes a re-cut from round 4 on, and the body was re-cut.

The body claims that `MERGE_CALL` "reads every spelling of one call that gh's argv and the Python, JS and shell call forms accept". It pins `os.system(f"gh pr merge {n} ...")` and the JS template `${GH} pr merge` as such spellings. The same call with its program interpolated into the one string literal is not read. With the head's `subjectWriters` extracted by the argv-seam harness's own method (`ev/probe.mjs`, `ev/probes.json`, output in `ev/own_probes_head.txt`), each of these returns `[]`:
- `os.system(f"{GH} pr merge {n} --subject x")`
- `os.system(f"{gh_bin} pr merge {n} --subject x")`
- `subprocess.run(f"{self.gh} pr merge {n} -t x", shell=True)`
- `os.system("%s pr merge %s --subject x" % (GH, n))`
- `os.system("{} pr merge {} -t x".format(GH, n))`
- `` execSync(`${cfg.gh} pr merge ${n} --subject x`) ``

The control `` execSync(`${GH} pr merge ${n} --subject x`) `` is refused.

This is the round-4 block's class (2), program spellings outside PROGRAM, not a new class. `PROGRAM`'s `$` arm takes only an identifier inside `${...}`, and nothing takes a Python `{...}`, `%s` or `{}` placeholder. The f-string and `${cfg.gh}` shapes are one literal in one expression, so the Unpinned sites disposition "argv built across expressions" does not cover them. The `%`/`.format` shapes are arguable under it, but the body does not name them.

The census rule finds no live site of these shapes. Every such line holds both words and falls among its 60 read-and-cleared lines. So this is the same synthetic-shape standard the round-4 block applied to `${GH:-gh}`.

Either remedy settles it:
- **Code.** Give `PROGRAM` an interpolation-slot arm: `\{[^{}\n]*\}`, `%s`, and a `${...}` arm that is not limited to an identifier. Add one probe per arm in `SPELLINGS`, a null control (`f"{GH} pr view {n} -t x"`), and a mutant per arm.
- **Body.** Narrow the "every spelling" claim, and disposition interpolated programs under Unpinned sites with their reason.

## Findings

- Interpolated-program spellings of a merge call are unread by `MERGE_CALL` and absent from the body's dispositions (Block). Carry: R10-MERGE-SUBJECT-HARDEN
- `gh pr -R $(cat r) merge 9 -t x` is unread: `VALUE` takes no unquoted command substitution that holds whitespace. The miss is in the same family (an option value in a gap), and the body does not disposition it. Fold it into the same re-cut, by code (a `\$\([^()\n]*\)` VALUE arm) or by disposition. Carry: R10-MERGE-SUBJECT-HARDEN
- The brief asked for a body with no round history, and the body still carries some: "The kills this pass adds", "the three writer misses the review showed under RV3", "the Block's shapes", "this pass's parts". Restate these as what the code does at its head. Carry: R10-MERGE-SUBJECT-HARDEN

## Evidence

The three round-4 block items, each confirmed fixed by code and probe at this head:
- **(1) Option values holding whitespace, and the argv form.** `VALUE` gained a quoted run that holds whitespace. Five new `SPELLINGS` probes cover it: `gh pr --subject "x y" merge`, `-t 'x y'`, `-R "o/r x"` before `pr`, the argv `"--subject", "x y"`, and `--subject="x y"`. RV4 kills at 99 of 101 and RV5 at 95 of 101. R11, R11a, R11b and R11c kill at 95, 100, 96 and 96 of 101. The plants `gh pr --subject "x y" merge` and `gh pr -t "x y" merge` give refused=0 at the before end and refused=1 at the head. My own probe of `run([GH, "pr", "--subject", "x y", "merge", n])` is refused at the head and missed at the before end.
- **(2) `${GH:-gh}` and `$(command -v gh)`.** Each is read by code, pinned by a probe, and killed by its mutant: R13a and R13b, each 100 of 101. Each plant gives refused=0 at the before end and refused=1 at the head. My own probes of `` `command -v gh` ``, `"$(command -v gh)"`, `${GH:-/usr/bin/gh}` and `env gh` are all refused at the head.
- **(3) RV3.** It is killed at 98 of 101 by three variable-program probes, each with a gap other than `, `: whitespace before a comma, a split over lines, and a run of spaces in a JS argv. RV1, RV2 and RV6 kill at 99, 98 and 100 of 101.

Self-test and mutation table:
- `node tools/policy/agreement.mjs --self-test` gives `SELF-TEST 101 of 101 probes held` (`ev/selftest.txt`).
- `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` gives 71 rows (`ev/mutants.txt`). Exactly X5, Y9 and Y10 print `101 of 101`, and no row prints `NOT APPLIED`.
- I did not re-run the before-end guard block substitution (`90 of 101`).
- X5, Y9 and Y10 are near-equivalent or widening-only, as the body says. I read each and concur.

Finder's harness, at both ends under plants (`ev/plants_head.txt`, `ev/plants_before.txt`):
- Unperturbed, both ends give `56 merge call(s) in 11 file(s)` and `RESULT divergent=0 unregistered=0 dead=0 refused=0`.
- The five pre-existing plants give refused=1 at both ends.
- The five new plants give refused=0 at the before end and refused=1 at the head.
- The null plant `gh pr view 1 -t ...` gives refused=0 at both ends.
- `python3 -I tools/policy/agreement_py.py --run` at the head gives refused=0 (`ev/finder_head.txt`).
- The first-parent count, 297, describes this SHA only.

Census and argv seam:
- The census against the before end's guard gives `TOTAL old=56 new=56 over 290 file(s)` and `UNCOVERED 60 of 95 line(s)` (`ev/census.txt`). This matches the body.
- The argv-seam harness gives `[]`, `[]`, `["f:1"]` (`ev/argv_seam.txt`). This matches the body.

Figures at this head (`ev/figures.txt`, `ev/policy_lint.txt`, `ev/ci_predict.txt`):
- `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`
- `STRUCTURE RATCHET PASSED`
- `RULES-SYNC ok`
- `claims hygiene: origin/main ok`
- `ALL 117 closure shrink pins PASSED`
- `layout self-test: ok`
- `ALL 112 HARNESS HEADER CHECKS PASSED`
- `Architecture score: dS +0.0000 NULL`
- `TOTAL: 0 error(s) across 50 policy file(s)`
- `CI PREDICT: no ... red predicted against 5c0ee109305f`. The body's figure names `fe5884445452` because it was taken at the code head `4b12f738`, before the main merge.

`tests/entities.py` summary not re-derived:
- My capture truncated the output before its summary line.
- Its FAIL lines are the self-test's planted a3 cases.
- The body's `2 of 2429` figure is not re-derived by me.
- CI's `tests / closures` and `tests / fast (3.14)` are success on this head.

Head, merge, versions and template:
- VERSION, the manifest and RELEASE_NOTES.md are untouched, checked three-dot against the merge base.
- `git merge-tree --write-tree origin/main d0d35231` exits 0 with tree `8f357e2f` and no conflict (`ev/merge_tree.txt`).
- The body names the head `d0d35231c633ca447acf04770f9034281417b72d`, and the head is unchanged at verdict time.
- The body carries every template heading: Head, Mutation proof, Null control, Figures, Red checks, Forward-carry, Friction.

CI at this head (check-runs API, 43 runs):
- No run is red, and every completed run is success or skipped.
- Still running at read time: `tests / lane-proofs` (queued), `tests / coverage-ratchet` (queued), `tests / graders-head-copy` (in progress) and one `prelude` (in progress).
- The body's "No check has run on this head yet" is stale but claims no red. The red-check trigger is not engaged.

Role contract: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract read is current.

Instruments: the probe instrument `ev/probe.mjs` is my own. It extracts `subjectWriters` exactly as `dev/audit/harnesses/r10_merge_subject_argv_seam.mjs` does. Its before-end output is in `ev/own_probes_before.txt`.
