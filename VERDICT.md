Fix review: blocked 410d3988fd2ae01ea6ec281174e470b4f5540bcb root-cause-detectable: gate and instrument-self-tests are red at the head because the new review_packet.py is unwired and its render in dispatch breaks cloud_dispatch; ## Red checks names neither
bus-nonce: 8de7caec70872d504eb7cac82264126e

# Fix review — PR #2870 (R10-ORCH-REVIEW-PACKET), head 410d3988fd2ae01ea6ec281174e470b4f5540bcb

Reviewed in a detached worktree at the head (`/tmp/rev-2870`), merge base
`484d9902222031f8e081df9f53b52ffd50fcc0af`, three-dot diffs throughout.
The head was confirmed the PR head before starting and did not move.

The dispatch brief said this PR's only changed path is
`dev/governance/roles/fix-review.md`. That premise is false: the three-dot diff
touches seven paths, ~530 new lines (`review_packet.py` 409, `r10_review_gather_share.py`
71, `bus.sh` +49/-8, `INSTRUMENTS.md` +14/-1, `closures.json` +2, the policy file +3/-3,
and the delivery row). The policy diff is one file of the seven; the rest is the
machinery the policy now points reviewers at, so it was reviewed as code.

## What a reviewer seat must now do differently (plain words)

Before: the reviewer opened the frozen worktree and gathered the facts itself;
the contract named no starting point. Now: `bus.sh dispatch` renders a
`review-packet:` at the frozen head — the three-dot diff, the head's check runs
with each run id, `carry_audit` and `figure_lint` at the head, the finder's
harness output at base and head, and the mutation-ledger diff — and writes its
path into the dispatch output. The reviewer **starts from that packet**, and
because the packet's check digest is only as fresh as its render, the reviewer
**re-reads the live check state before returning a verdict**. Everything else is
unchanged: the fresh-context rule, preparing against the merge base only before
the handoff, steps 1–12, publishing through `bus.sh push-verdict` as
`hpo-approver`, and never treating the verdict as the owner's approving review.

Policy judgement: **no loosening found.** The change adds two obligations
(start from the packet; re-read live checks) and no sentence lets a reviewer
skip a check, accept weaker evidence, or return `merge` earlier. The cuts pay for
the added sentence inside the same paragraph: `in a fresh context` → `fresh`;
`That worktree holds this contract ... frozen by design, so your copy can be
arbitrarily old` → `Its copy of this contract is frozen with the tree, so can be
old`; `Before the fixer's handoff message (fixer.md: "the handoff freezes the
branch")` → `Before the handoff freezes the branch (fixer.md)`; `never ...
never ...` → `never ... or ...`. The dropped phrase `no head measurement` is
subsumed by the retained operative clause `prepare against the merge base only`.
Step 2's "Measure with the finder's harness ... printing your own RESULT lines"
is untouched, so the packet does not substitute for the reviewer's own
measurement. No contradiction with `CLAUDE.md`, `COMMON.md`, or
`dev/governance/rules/*`: `rules_sync --check` passes, `policy_lint --report`
prints 0 errors across 50 policy files, `policy_lint --budgets` exits 0, and the
canon-path cap for this file did not move (2448 → 2446 tokens against a 2451 cap,
140/140 lines).

The verdict is blocked anyway: the policy sentence cannot be delivered to most
reviewers, and the head is red on the required check because of the diff.

## Findings

### F1 (blocking, code) — the new instrument's self-test is not wired into any workflow

`tools/audit/seat/review_packet.py` gains a `--self-test` (21 checks) but the
diff touches no workflow, so nothing names that self-test in a run line. The
repository's own wiring ratchet rejects it at this head and at the merge base it
passes:

- head: `python3 -I tools/audit/seat/selftest_wiring.py --check` →
  `UNWIRED tools/audit/seat/review_packet.py: no workflow run line names its self-test`;
  `selftest_wiring: 98 self-testing, 97 wired, 1 unwired`; rc 1.
- base: `97 self-testing, 97 wired, 0 unwired`; rc 0.
- CI, `governance / instrument-self-tests` id 121985023161:
  `UNWIRED tools/audit/seat/review_packet.py: no workflow run line names its self-test`
  and `##[error]Process completed with exit code 1`.

The delta is exactly the file this PR adds. Fix: add the self-test to the
instrument-self-tests job's run line in `.github/workflows/governance.yml`
(the shape at lines 480–482) with its `grep -Eq '^review_packet self-test:
[1-9][0-9]* checks, 0 failed$'`.
Carry: R10-ORCH-REVIEW-PACKET — fix here before merge.

### F2 (blocking, regression) — the packet render makes `bus.sh dispatch` hard-fail in a caller that used to pass

`dispatch` now runs `review_packet.py render` unconditionally, and
`review_packet.gather` raises `SystemExit` on any failed `git merge-base
origin/main <head>`. `cloud_dispatch.py` calls `bash bus.sh dispatch` inside a
synthetic repo whose `origin/main` cannot resolve the synthetic head, so the
whole dispatch refuses. This is a regression of an existing tool's self-test:

- head: `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` → rc 1,
  `Refusal: bus.sh dispatch refused: review_packet: REFUSED git merge-base
  origin/main <sha>: fatal: Not a valid commit name <sha>`.
- base (null control): `cloud_dispatch self-test: 73 checks, 0 failed`, rc 0.
- CI, `governance / instrument-self-tests` id 121985023161, second failing step,
  same traceback through `cloud_dispatch._bus_dispatch`.

The same shape bites any real caller whose checkout cannot resolve
`origin/main` to the dispatched head (a partial clone, a cloud seat's repo dir, a
stale base). Fix: resolve the base once with a caller-supplied or recorded base
and degrade to an advisory (or a named refusal the caller can pass) rather than
`SystemExit`, and update the cloud-dispatch fixture.
Carry: R10-ORCH-REVIEW-PACKET — fix here before merge.

### F3 (blocking, body) — `## Red checks` names none of the head's concluded reds

The head has three concluded red contexts (`gate` id 121997429064,
`governance / instrument-self-tests` id 121985023161, `pr-contract / pr-contract`
id 121997241906). The body's `## Red checks` answers four *local* `tests/entities.py`
sub-checks from a Darwin scoped-gate run and names none of the three. Reproduced
with the exact invocation the new packet uses:

- `node tools/policy/policy_lint.mjs --pr-body <body> --head <head> --red "governance / instrument-self-tests" --red "pr-contract / pr-contract"`
  → two `ERROR [pr-body] ... check \`X\` is red and \`## Red checks\` does not name it`
  (`evidence/policy-lint-red.txt`).
- `pr-contract / pr-contract` is red for exactly that body omission
  (its log: `ERROR [pr-body] ... check \`governance /
  instrument-self-tests\` is red and \`## Red checks\` does not name it`;
  `evidence/instrument-self-tests-excerpt.txt` and `evidence/gate-log.txt`).
- `gate` is red because `gate.py` reads that `pr-contract` failure:
  `FAIL pr-contract / pr-contract: failure` (`evidence/gate-log.txt`).

This is contract step 11 silence over every head. A cheaper detector existed and
is named: `python3 -I tools/audit/seat/selftest_wiring.py --check` and
`python3 -I tools/audit/seat/cloud_dispatch.py --self-test` show F1 and F2 in
under a minute; `policy_lint --pr-body ... --red ...` shows the omission itself.
Carry: R10-ORCH-REVIEW-PACKET — answer each red in `## Red checks` (the cheaper
detector and its standing cost) before merge.

### F4 (blocking, self-refutation) — the PR's own instrument refuses this PR

Live at the dispatched head:

```
review_packet.py render --pr 2870 --head 410d3988… --out /tmp/pk-2870.md
  REFUSE red-unanswered: concluded red check `governance / instrument-self-tests` is not named in ## Red checks
  REFUSE red-unanswered: concluded red check `pr-contract / pr-contract` is not named in ## Red checks
  REFUSE required-red: required context `gate` concluded failure at 410d3988…
  rc=1 ; packet written: no
```

`bus.sh dispatch` would therefore refuse to record a reviewer dispatch for this
PR at this head, and the policy now tells every reviewer to start from a packet
that cannot be produced here. Fix by F3 (answer the reds); the instrument then
renders.
Carry: R10-ORCH-REVIEW-PACKET — fix here before merge.

### F5 (blocking, policy deliverability) — the packet path never reaches a cloud or relayed reviewer

The contract now binds every reviewer to `start from the dispatch's
review-packet:`, but the only in-tree path that fires a *cloud* reviewer never
receives it:

- `cloud_dispatch.py` contains 0 references to `review-packet`; `_bus_dispatch`
  parses `^bus-nonce: ([0-9a-f]{32})$` out of the dispatch stdout and discards
  the rest, so the `review-packet:` line is dropped.
- `bus.sh` prints the packet path only to stdout; the persistent dispatch record
  is `pr head reviewer nonce timestamp model` — no packet field
  (`$S/dispatched`). `cloud_relay.sh` and `standing-dispatch.md` also contain 0
  references to the packet.
- The printed path is `home_rel` of the dispatcher's state dir
  (`~/state/packets/<pr>-<head>.md`), a host-local path a seat on another machine
  cannot read.
- No dispatch path supplies `--harness`, and the roster group has
  `"harness": null`, so the packet's independence arm renders
  `## Finder's harness: none named / not run / not run` by default — verified on
  #2864 at 30c940e5b (`evidence/packet-2864-bytes.txt`).

So the added obligation is unsatisfiable for the cloud seats that carry most
reviews, and the packet's advertised independence evidence is absent unless a
human passes `--harness` by hand. Fix: record the packet path in the dispatch
record (or payload) and forward it in `cloud_dispatch.render`, put the packet on
a path the remote seat can read, and derive `--harness` from the roster/topic
instead of a manual flag; or scope the policy sentence to a dispatch that
actually carries a packet.
Carry: R10-ORCH-REVIEW-PACKET — fix here before merge.

### F6 (non-blocking, coverage) — the new file is inert and no closure names it

Both new files are in `tests/closures.json`'s `inert_reads` for
`tests/entities.py` and `tests/harness_headers.py`, and no closure lists
`review_packet.py` or `bus.sh`. `ci_predict.py --base origin/main` therefore
printed `no closures, fast, wave-script or instrument red predicted` (rc 0) while
CI's instrument job went red on the new file. The full `governance /
instrument-self-tests` job (not closure-scoped) is what caught it. Once F1 wires
the self-test, a change to `review_packet.py` should also select a script that
runs it.
Carry: R10-ORCH-REVIEW-PACKET — fold into F1.

### F7 (low, robustness) — the check-run read is not paginated

`review_packet.gather` reads
`commits/{head}/check-runs?per_page=100` without pagination. At this head there
are 55 runs, so the digest is correct today; a commit exceeding 100 runs would
silently truncate the digest and could miss a pending or red required run, which
is what `required-red` and the `pending` state exist to catch. The dispatch's own
check-run read paginates. Carry: #2717.

### F8 (low, claim) — the packet's harness section is conditional, the prose is not

Body and `INSTRUMENTS.md` say the packet holds "the finder's harness output at
the base and at the head". Without `--harness` it holds `none named` / `not run`
/ `not run` (verified on #2864). State the condition in both places.
Carry: R10-ORCH-REVIEW-PACKET.

## Figures re-taken at this head (all matched)

- `review_packet.py --self-test` → `21 checks, 0 failed`.
- `bus.sh --self-test` (`env -u BASH_ENV`) → `91 checks, 0 failed`.
- `tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED`.
- `tests/structure.py` → `STRUCTURE RATCHET PASSED` (every metric at its budget).
- Byte identity, #2864 at 30c940e5b, two renders + `cmp` → identical,
  `87` lines / `3591` bytes, `## Refusals none`, `## Gate digest: green`.
- Verdict reads: `verdict/2865` tip 33d6c5a4 first line
  `Fix review: merge 07bc8000cd85b894ae65905eee065f0e15c21a68`; `verdict/2864`
  tip b3d758ec first line `Fix review: merge 30c940e5b5e009ebe95004235cbab8536ea14799`.
- `carry_audit.py check` → `5 finding item(s): 5 routed, 0 unrouted`.
- `figure_lint.mjs` → `FIGURES: 7 resolved, 1 not verified, 0 refused`.
- `rules_sync.mjs --check` → ok; `policy_lint --report` → 0 errors / 50 files;
  `policy_lint --budgets` → rc 0, cap unchanged.
- Mutation proof re-run (body's own method, one line replaced by `pass`/`true`,
  self-test re-run, restored): `red-unanswered` → exactly one FAIL;
  `head-note` → exactly one FAIL; `bus.sh`'s `review_packet.py check` call →
  `bus self-test: 91 checks, 1 failed`, the `stale packet` case. Not vacuous.

## Numbers I did not re-derive (say so, per step 8)

- Reviewer gather share `seats=14 calls=731 gather=361 share=49%`: the transcript
  corpus is out of tree, so the rule cannot be re-run here; the harness's own
  `--self-test` passes but that pins the rule, not the 49%. The harness is the
  fixer's own instrument (new in this diff) and the body does not label it as
  the fixer's, only as `(new)`.
- Packet size `950` lines / `98657` bytes at #2866 eb97437e: not re-taken.
- Structure arm `real 29.97`s: host- and PR-specific; not comparable here (the
  #2870 render took 40.8 s wall on this host).
- The four local `tests/entities.py`/nightly hang-control failures on Darwin:
  not reproduced; they are not the head's CI reds and do not offset them.

## Policy approval (required line)

This PR changes policy: `dev/governance/roles/fix-review.md` under
`dev/governance/`. `.github/CODEOWNERS` routes `/dev/governance/roles/` to
`@tvofi` and `CLAUDE.md` says the owner approves any policy change before
merging. **It needs the owner's policy approval at merge; the orchestrator must
surface it and must not merge it on a seat's approval.** The body's `## Approval`
says "the policy approval is the orchestrator's approving review at the head
under that mandate"; mandate 6329234399 is cited in the tree
(`dev/programme/triage/s6-batch26.md`) as the mandate under which the
orchestrator opens and merges policy edits, but the code-owner rule still names
`@tvofi`, so the owner's approving review is the one that must be on the head.

## Forward-carry checked

The body's `## Forward-carry` routes roster carry [11] and the gather-wiring
control to #2717; the group's carry list in
`dev/programme/rosters/wave-r10-groups.json` states both with their controls as
preconditions, so step 10 holds for those two. F5 is **not** carried anywhere:
nothing in the body or the roster says the packet path must reach a cloud or
relayed seat. That must be fixed here or carried explicitly before merge.

## Evidence

`evidence/HEAD.txt` holds the head sha. Supporting files:
`check-runs-nongreen.txt`, `gate-log.txt`, `instrument-self-tests-excerpt.txt`,
`policy-lint-red.txt`, `selftest-wiring-head.txt`, `selftest-wiring-base.txt`,
`cloud-dispatch-head.txt`, `cloud-dispatch-base.txt`,
`packet-render-2870.txt`, `packet-2864-bytes.txt`,
`cloud-packet-delivery.txt`, `mutation-red-unanswered.txt`,
`mutation-head-note.txt`, `mutation-bus-check.txt`,
`policy-budgets.txt`, `policy-budgets-base.txt`, `policy-report.txt`,
`rules-sync.txt`.
