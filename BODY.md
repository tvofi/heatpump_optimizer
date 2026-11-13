R10-REVIEW-DISPATCH-RESIDUE part 5: Carry 17 (the carry-fold memo recognises an unchanged refused body by its BODY.md blob), Carry 20 (`landed()` reads an empty net diff as landed), Carry 11 (a mechanical-only block is exempt from the three-round rule), Carry 28 (`dispatch-handoff` re-keys a known PR).

Repair round 3: the review of 8382e2aa25cb blocked red-unanswered on `tests / briefs`. The branch is merged with origin/main (e23124ff6e45, 2026-11-13 18:0xZ), the one case where a main merge is the repair. All measurements below are at the head given below, 2026-11-13.

## Head

440ae4033125a7c10560104231f49f8989734821

## Policy

`dev/governance/roles/fixer.md`, "Past three rounds" section, one paragraph appended (Carry 11, owner directive tvofi 2026-11-09 18:35Z, "the split should never apply when the gap is mechanical only"). It names every class `bus.sh` `MECHANICAL_CLASSES` exempts, so the text and the code list the same set: `red-unanswered`, `body`, `contract`, `conflict`, `head-moved`, `carry`, `carry-missing`, `ungated`, and the CI-only classes (`ci-red`, `ci-wait`, `ci-pending`, `ci-cancelled`). These are mechanical and do not count toward the three-round rule. A judgement class, an unknown class or an unreadable log refuses as before. This needs approval at the merge under the owner's mandate. `standing-dispatch.md` is unchanged.

Budget payment, no raise. The paragraph is paid for by deleting resolved-incident citations from steps 1, 3, 8, 9, 10, 15 and 17, as in the first round. In this round, the step-8 gate-lease sentence is also shortened to a pointer to `gate-scoping.md`, which owns the queue, the wait bound and holding the lease by hand (writing-for-agents.md uniqueness). No rule sentence was removed. `node tools/policy/policy_lint.mjs` printed `TOTAL: 0 error(s) across 51 policy file(s)` (rc 0), and `--budgets` exited rc 0.

## Approval

Pending. Two approvals are needed: the owner's approving review at this head, which `main-protect-checks` requires for a code-owned path, and the merge-time approval of the `fixer.md` edit named under `## Policy`. No budget leaf is raised.

## What changed, and which seam it extends

- Carry 17, `tools/audit/seat/cloud_relay.sh` `carry_fold_arm`/`fold_judge`. The memo line now records the BODY.md blob and the handoff/<topic> tip. A fold-failed or push-failed record stands for a later kept body with the same stop, blob and tip. It keeps its first epoch, so the 3600 s retry bound runs from the first failure, and it sets its OWED level line again. A record in the old shape is judged again. P546 is dismissed per P580 and not built.
- Carry 20, `tools/audit/seat/ledger.py`: `empty_net()` and a named reason `empty` in `landed()`. A failing merge-base or diff read (rc != 0) stays not-landed.
- Carry 11, `tools/audit/seat/bus.sh`: `mechanical_block()` reads the class of the latest blocked verdict against `MECHANICAL_CLASSES`, and `three_rounds()` dispatches past round three when that class is mechanical.
- Carry 28, `tools/audit/seat/bus.sh` `dispatch_handoff`: re-keys through the existing `rekey` when `--pr N` was given or `<bus>/rekeyed` holds a numeric `<topic> <sha> <pr>` line. The last such line wins.

### Answer to the block

1. **Mutation-vacuous.** The reviewer's specs were rebuilt at this head by the reviewer's own `ev/spec/build.py`, with `ML` read from the file. Each spec then ran through `mutant_run.py` against its file's `--self-test`. Bus runs `--in-place`, because in the copy-tree mode the packet-renderer arm fails on an unedited tree (the NULL is killed there). Results:
   - Bus, 20 mutants: every `B-drop-<class>` member is KILLED. A table-driven arm drives one case per class beside its null, and a drop of any single class fails it. `B-add-harness`, `B-exempt-off`, `B-rekeyed-lookup-off`, `B-rekeyed-numeric-guard`, `B-rekeyed-first-not-last`, `B-pr-numeric-off` and `B-pr-ignored` are KILLED. NULL SURVIVED.
   - Relay, 12 mutants: `R-foldfailed-off`, `R-tip-unrecorded-foldfailed` and `R-first-epoch` are KILLED. The other eight reviewer mutants that still apply (`R-oldformat-guard-off`, `R-oldformat-dash-off`, `R-tip-cmp-off`, `R-blob-cmp-off`, `R-pushfailed-off`, `R-blob-unrecorded`, `R-tip-unrecorded-pushfailed`, `R-owed-line-dropped`) are KILLED. `R-ttl-off`, re-cut to the current line (`fold_memo_stands "$fo" "$fe" "$now" \` → `true \`), is KILLED. NULL SURVIVED.
   - `B-rekey-call-off` / `B-rekey-fail-ignored`: the `|| die "...could not re-key"` tail was unreachable and is removed. `rekey` dies on every failure it can meet, and its only other non-zero exit (rc 3, no `topic:` record) cannot follow the append just above it. So `B-rekey-fail-ignored` has no site left. `B-rekey-call-off`, re-cut to the current call (`rekey "$t" "$pr" >&2` → `true >&2`), is KILLED.
   - `R-fb-len-off`: the `[ "${#fb}" = 40 ]` test is removed, because the blob comparison subsumes it: a malformed `fb` never equals a 40-hex `blob`. So no site is left.
   - `ledger.py` sites 387, 388, 471, 1202, 1204 and 1206-1209: KILLED. `mutant_run.py --diff 0723540391a1c431b6f91629485bc2f00d90a4e7...HEAD --path tools/audit/seat/ledger.py --cmd 'python3 tools/audit/seat/ledger.py --self-test'` prints no survivor from those sites. The new oracle drives a merge-base read with rc != 0 and asserts that `landed()`'s reasons are exactly `ANCESTRY_WHY + CONTENT_WHY` (with `empty`). That run's one survivor, `ledger.py:1248 STMT_DEL`, is triaged under `## Mutation proof`.
2. **Required reds.**
   - `governance / policy-docs` and `governance / env-matrix`: fixer.md is now within its `files_tokens` cap. `policy_lint` printed TOTAL 0 with rc 0, and `--budgets` exited rc 0. No cap is raised.
   - `tests / fast (3.14)`: the job log (job 131786078626) reads `1 of 2709 ENTITY CHECKS FAILED` / `>>> FAILED: python3 tests/entities.py`. The failing check is "the template arm turns the acceptance red on a template that fails its own contract (and the real template keeps it green)" with `the real template -> rc=1 (must be 0)`. That check's live arm runs the whole `policy_lint.mjs`, so it goes red on any policy-lint error, and at 676d726d the only one was the fixer.md budget error. It is this branch's red, with the same cause as the two above, and it is fixed by the same payment: the live policy_lint run at this head exits 0. `tests/entities.py` cannot run end to end in this container (venv-ha lacks `paho`/`scipy`, and its Home Assistant `FakeConfig` lacks `path`), so this head's proof is the check's own input (policy_lint rc 0), not a full run.
3. **Exempt set.** The code side moved. Carry 11 (roster, verbatim) lists the mechanical classes as "ci-red, red-unanswered, body/contract, conflict or head-moved, carry, ungated step", plus the carried ruling "a CI-only block (ci-red, ci-wait, ci-pending, a cancelled run) is mechanical". It names neither `root-cause-unanswered` nor `preflight-mismatch`, so those two are dropped from `MECHANICAL_CLASSES` and refuse as judgement or unknown classes do. fixer.md now names each member, and a bus self-test arm reads the class list out of fixer.md's paragraph and compares it with `MECHANICAL_CLASSES`. That arm is what kills `B-add-harness` and every `B-drop-*` mutant.

The B1-B7 and R1-R5 behaviour the review re-confirmed is unchanged, and its mutants are all in the KILLED lists above.

## Mutation proof

The instrument is `tools/audit/seat/mutant_run.py`. The specs are the reviewer's, rebuilt at this head; the commands are as under `### Answer to the block` item 1. Totals:
- `bus.sh`: 20 of 20 KILLED.
- `cloud_relay.sh`: 12 of 12 KILLED.
- `ledger.py` diff mode: every site KILLED except one.

The one survivor, as its survivor_triage record:

```json
{
  "anchor": "tools/audit/seat/ledger.py:1248 STMT_DEL",
  "old": "        check(\"carry 20: an empty net diff lands as empty; one real line, an unreadable merge-base or diff does not; ...\",",
  "reason": "Unkillable by construction: the mutant deletes the self-test's own carry-20 assertion (the check() call at 1248-1253), not a production line. No oracle can kill the deletion of itself. The production sites that assertion pins (ledger.py 387, 388, 471, 1202-1209) are each KILLED by it in the same diff-mode run.",
  "verdict": "equivalent"
}
```

The record is kept in this body and not under `tests/mutation_ledger/survivor_triage/`, because no record there anchors a `tools/` file and the site is test code.

## Null control

Each spec run's NULL mutant (the unedited tree) SURVIVED, for both bus and relay. At this head, `bash tools/audit/seat/bus.sh --self-test` printed `bus self-test: 202 checks, 0 failed`, `bash tools/audit/seat/cloud_relay.sh --self-test` printed `cloud_relay self-test: 501 checks, 0 failed`, and `python3 tools/audit/seat/ledger.py --self-test` printed `ledger self-test: 103 checks, 0 failed`. The cloud_relay figure was 465 at the earlier head 8382e2aa25 and is 501 at the merged head a60a65d873 (main's bdf1dc827e and 7d09eae1ba add 36 checks); it is corrected here. Every other figure was re-read at a60a65d873 and holds: bus 202 and ledger 103 by the commands above, and `node tools/policy/policy_lint.mjs` TOTAL 0 over 51 files, `--budgets` rc 0, `node tools/policy/brief_lint.mjs` rc 0. Each production mutant above turns its self-test red. The per-carry nulls are unchanged from the first round:
- Carry 17: a stop with no record runs body_push.sh.
- Carry 20: a tip with one real line stays None.
- Carry 11: a fourth round after a proof-class or unknown-class block refuses.
- Carry 28: a topic with no PR stays `topic:`-only.

## Figures

- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 51 policy file(s)` (rc 0). `--budgets`: rc 0. Scope: the policy corpus.
- The self-test check counts and mutant totals are as printed above. Instrument: the three `--self-test` commands and `mutant_run.py`. Scope: the three files named.
- `git merge-tree --write-tree origin/main 8382e2aa25` printed one tree, no conflict; `git merge origin/main` then merged cleanly into 440ae4033125.
- `node tools/policy/brief_lint.mjs` at 440ae4033125 exited 0; its last lines were `LEGACY-CONTROL ok: ... the legacy set is within its cap and each member still needs the exemption`, `LEGACY-LISTED-CLEAN ok ...` and `PLAYBOOK ok ...`. `grep -n LEGACY_CONTROL_FILES tools/policy/brief_lint.mjs` shows `const LEGACY_CONTROL_FILES = readLegacyControlFiles()`, main's file-based list (`tools/policy/legacy_control_files.json`).
- `bash tools/pr/prepr.sh` on the committed merged head: rc 0, no REFUSE, FAIL or SURVIVED line (brief_lint step ran: ok).

## Red checks

- `tests / briefs` (run 43461406948, job 132009362217, on the PR merge ref): `LEGACY-CONTROL VACUOUS: carry-1412.json: its controls lint clean without the exemption: remove it from LEGACY_CONTROL_FILES`. INTRODUCED by a stale base, not by this diff's files: the head 8382e2aa25 kept the inline LEGACY_CONTROL_FILES set in tools/policy/brief_lint.mjs listing carry-1412.json, while main delisted it in d65839f2e2 (PR 3552) and moved the list to tools/policy/legacy_control_files.json in b4a663ebe5; neither is an ancestor of 8382e2aa25. Fixed by merging origin/main; brief_lint exits 0 (see `## Figures`). Cheaper-detector answer: prepr step 3f runs brief_lint only when a pinned path changed; this branch changed none of them, so it did not run there at 8382e2aa25, and the detector is a stale base the fixer contract does not re-check (fixer.md step 6 merges only on conflict). Process state: detector exists, did not fire. Countermeasure: none built; brief_lint ran here after the merge. Null control: I could not reproduce the refusal. `git merge-tree --write-tree origin/main 8382e2aa25` at today's main, built into a commit and linted in a worktree, exits 0, because main's two commits now both merge in; the CI merge ref was formed against a main without b4a663ebe5.
- `governance / policy-docs`: INTRODUCED at 676d726d by the fixer.md `files_tokens` overrun (5229 > 5216). Fixed by the payment under `## Policy`, and policy_lint TOTAL 0 at this head.
- `governance / env-matrix`: INTRODUCED, with the same cause as policy-docs, and fixed by the same payment.
- `tests / fast (3.14)`: INTRODUCED. The failing check is `tests/entities.py`'s template-arm check, whose live arm runs the whole policy_lint and so failed on the same budget error. It is fixed by the same payment (see `### Answer to the block` item 2).
- `governance / instrument-self-tests`: red in `selftest_scope`, which this diff does not touch. The reviewer could not classify it (base run in progress, classify rc 2). Not introduced by this branch's files. It is left to the train's re-proof on current main.

Root cause, for the red-check trigger: the budget overrun reached CI because the first round's lint ran at f71c5e69, before the 676d726d delivery-row commit and main merge. That merge brought main's newer fixer.md text under the same cap. The cheaper detector already exists, in `prepr.sh`'s policy_lint step, if it is re-run after the merge. Its process state is that the detector exists but was not re-run. Countermeasure: none built. The fixer contract already re-executes steps 2-8 after any merge (fixer.md), and this round does.

## Unpinned sites

- `tools/audit/seat/ledger.py:1248 STMT_DEL` (the carry-20 `check()` call in the self-test): triaged equivalent, record under `## Mutation proof` — the mutant deletes the oracle itself; every production site it pins is KILLED.

## Forward-carry

none

## Friction

none
