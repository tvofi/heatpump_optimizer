Fix review: blocked a11db7fea14bc34633eb65e8111a207142eb45ab class-open: a row push that lands on origin and then fails (body PATCH or read-back) closes a PR that has its row

bus-nonce: eabc7b4c50769f21225dba2bbdcc5729

Round 1 for this reviewer seat. Head measured: `a11db7fea14bc34633eb65e8111a207142eb45ab`. It was still the PR head when this verdict was written (`ev/heads-at-verdict.txt`).

## Block

`op_close_unrowed` (`tools/audit/seat/open_pr.sh`) treats any non-zero exit of the `--row-only` push as "the row was not pushed". It closes the PR and comments `open_pr: CLOSED: #N ... before its row was pushed`. But `tools/pr/app_push.sh`'s `push_and_open` can exit 1 **after** `git push` has succeeded:

- `die "the body PATCH on #$num was refused; the branch IS pushed as the App ..."`
- `confirm_readback`'s `body`, `bad state=` and exhausted-budget refusals.

In each of those cases the row is on origin, so the PR is not rowless. The diff now closes a correct PR and posts a false reason. Before this diff the same seam only printed a false `ROWLESS` line and left the PR open with its row. So the diff turns a cosmetic error into closing a valid PR.

The body's class description ("a refused second (row) push, a step errexit stops between the two pushes, a stop signal") neither names nor dispositions this seam, and no enumeration rule is given. A stop signal that arrives after the push's `git push` has completed falls in the same seam.

Reproduced, not only read. I ran a reviewer-built probe: the self-test's stub `app_push.sh` call 2 was changed to push the row and then exit 1 with the PATCH refusal text (`ev/probe-postpush-close.diff`). The `rowless -` arm then printed:
`PROBE closed=1 ... rco=1`, `open_pr: CLOSED: #5 at 334fbb5..., before its row was pushed`, and origin's `fix/r` at `2a8f66e record: the delivery row for #5` with `dev/programme/delivery/5.md` present (`ev/probe-postpush-close.txt`, lines 135-138). The probe's own trailing rc=1 comes from a syntax error in my instrumentation line, not from the code under review.

A cheap repair would compare origin's branch tip with `$H` (`git ls-remote`) before closing, and close only when the row commit is absent. A regression arm would plant the post-push failure.

## Findings

- The post-push failure seam of the `--row-only` push closes a PR whose row is on origin, and comments that the row was never pushed (see Block). Carry: R10-FLY-OPENPR-ATOMIC
- The body's `## Figures` misstates the head self-test count. It says `pr_args self-test: 154 checks` and 160 `ok` lines at the head, three more than the base. Re-run at this head: `156 checks, 0 failed` with 162 `ok` lines, five more than the base (`ev/selftest-head.txt`). The base figures (151 / 157) re-derive exactly (`ev/selftest-base-1afdef8.txt`). The two uncounted checks are the `mut:trapclose` and errexit-after-PR (title edit) arms, and `## Mutation proof` does not list `mut:trapclose` either. Carry: R10-FLY-OPENPR-ATOMIC

## Evidence

- RESULT head self-test: `bash tools/audit/seat/open_pr.sh --self-test` at a11db7f exits 0, `pr_args self-test: 156 checks, 0 failed`, `delivery_row self-test: 6 checks, 0 failed`.
- RESULT base self-test at merge base 1afdef8: exits 0, `151 checks, 0 failed`, 157 `ok` lines.
- RESULT mutation proof: the in-tree arms for `mut:rowclose`, `mut:trapclose`, `mut:rowreset` and `mut:mergeabort` all print `ok` at the head, so each named mutant is killed. The failing-test-first claim against main's `open_pr.sh` was not re-run by me.
- RESULT merge: `git merge-tree --write-tree` exits 0 against base 1afdef8 and again against the newer origin/main eec56f2 (`ev/merge-tree.txt`, `ev/merge-tree-eec56f2.txt`). No conflicts and no claim-file involvement.
- RESULT version: VERSION, the manifest and `RELEASE_NOTES.md` are untouched. No golden or claim file is in the diff. `env_drift` is not applicable.
- RESULT finder's harness: none was named, and the review packet reports none. The self-test arms are the fixer's. The post-push probe above is my own instrument, disclosed as such.
- RESULT checks: read from the check-runs API at this head. No check concluded red. Still in progress when read: `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `tests / browser`, `governance / env-matrix`, `governance / instrument-self-tests`, `codeql / Analyze (python)`. The body's `## Red checks: none` matches what has concluded. This verdict does not rest on them.
- RESULT governance: `dev/governance/roles/` is unchanged between the merge base and origin/main.
- RESULT forward-carry: the body says none. Carries 4, 6 and 7 are stated as staying on the roster, which I did not open.
- A cost-guard hook in this session refused further inline commands. The probe was run by a delegated worker under my exact spec. I did not bypass the hook.
