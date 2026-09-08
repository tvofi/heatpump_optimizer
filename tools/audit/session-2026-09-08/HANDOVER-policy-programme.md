# Handover — governance/policy programme, cloud session to local session

Written 2026-09-08T18:00Z. **Every number here is a reading at that moment.**
Re-measure before acting on any of it; three figures in the predecessor of this
document were later measured false, which is the standing reason to distrust the
rest. Prefer BRANCH NAMES over SHAs: the chain is rebased after every merge, so
each SHA below goes stale within the hour.

## The one thing that does not carry over

**The policy-merge grant in `docs/decisions/0001-session-policy-merge-grant.md`
is scoped to the cloud session that received it, and to that session only.** Its
own text says so, and its Consequences say policy merges revert to owner
approval afterwards. A new session does **not** inherit it.

So before merging any `policy:` pull request, the local session must either get
the owner to re-grant it explicitly, or fall back to per-pull-request owner
approval. Merging under 0001 without that is the precise failure this audit was
called in to examine: an authority claimed rather than held.

Everything else below is state and mechanics.

## State at handover

- `main` = `03af74b` (#623). **Sixteen** merges: #607 #608 #610 #611 #612 #613
  #614 #615 #616 #617 #618 #619 #620 #621 #622 #623.
- **No completed gate run on `main` has failed** across all sixteen.
- Nothing is open. The queue below is the whole remainder.
- Live governance jobs on `main`: `policy-docs`, `wave-script`, `pr-contract`.
  `env-matrix` and `record` do **not** exist there yet; they land with `08` and
  `07` respectively.

## The queue, in merge order — the order is load-bearing

Local branch names are IDENTICAL to their remote refs, so there is no mapping to
get wrong. All are mirrored; `git ls-remote` is the check, never a push's own
output (a `git push --delete` once printed success while failing).

| branch | lands |
|---|---|
| `audit/queue-06-hooks` | `.claude/settings.json` + three hooks (SessionStart, PreToolUse, Stop), `policy_lint --hooks`, five rot fixtures |
| **`audit/queue-06b-record3`** | **DOES NOT EXIST YET — build it before `07`. See the trap below.** |
| `audit/queue-07-loop` | `--record`/`--stats`/`--sunset` and the `record` CI job |
| `audit/queue-08-envmatrix` | `policy_lint_envmatrix.mjs`, the `env-matrix` job, ADR 0004, the prepr gate widening |
| `audit/queue-09-verdicts` | `fix-review.md` verdict spellings, `D7.md`, ADR 0005 |
| `audit/queue-10-adr-corpus` | ADRs excluded from the corpus; ADR 0005 records O1 declined |
| `audit/session-evidence-2026-09-08` | the 416-line execution plan plus four seat reports, on no other ref. **Cut from an older main — do not merge it, it is an archive.** |

`audit/queue-01`..`04` are merged; their refs linger only because deletes were
proxy-refused from the cloud container.

## Invariant at the chain tip

At `audit/queue-10-adr-corpus`: `policy_lint` reports **76 pins across 10 check
classes**; `--record` is rc=0; `policy_lint_envmatrix` is 13/13 over 5 shapes.
Fewer means the chain is mispointed — check that before anything else. This
number is the only thing that has ever caught a mis-rebase.

## The trap that turns `main` red

The `record` CI job lands with `07-loop`. It runs on push to `main` only
(`if: github.event_name != 'pull_request'`), and its window is
`git describe --tags --abbrev=0 --match 'v*'` = `v6.3.18`. `checkRecord` is one
line — `new RegExp("#"+pr+"(?![0-9])").test(text)` — so a row is satisfied by the
bare token `#650` appearing anywhere in `docs/plan-2026-09-open-issues.md` **or**
`docs/HANDOVER.md`. Not a paragraph, not a format.

Measured at handover: **29 merged pull requests in the window, two missing** —
#622 and #623. Re-derive rather than trust that; the appendix has drafted rows
for #621 and #622, and #623's is yours to write.

**Before pushing `07-loop`:** create `audit/queue-06b-record3` between `06-hooks`
and `07-loop` carrying rows for every pull request merged since #620, and rebase
`07/08/09/10` onto it. Do not sprinkle rows into `05`/`06` — that is scope creep
into unrelated changes.

**The sharp edge, disclosed and undecided.** The job cannot run on a pull
request, because the pull request is not in `git log main` until merged. So a
pull request that forgets its row turns `main` red *after* merging. The owner was
offered a template reminder or a warning-only step and did not choose; absent an
answer it ships as a hard refusal, which is what the plan specified.

## What the local box unlocks

These were all proxy-refused from the cloud container and are the reason for the
move. Each is now doable:

1. **Tag creation.** Refused on both routes (`git push` of a tag, `POST
   /git/refs`). A release tag resets the `record` window, and #618's archive had
   to cite a bare commit rather than a tag name because of this.
2. **Branch deletion.** `git push --delete` returns rc=1 with a sideband
   disconnect. `audit/queue-01`..`04` are merged and can go; leave `05`..`10`
   and `session-evidence` alone until each merges.
3. **Ruleset creation.** `POST /repos/.../rulesets` refused. The paste-ready
   payload is on #609. **Do this LAST** — a required check that does not exist on
   `main` blocks every merge permanently, and `env-matrix` and `record` do not
   exist there until `08` and `07` land.
4. **A real machine.** The full unscoped gate is ~26 minutes in CI; `tests/stress.py`
   measures the box while it solves, so respect `gate_lock.py` and never run a
   full `derive_closures.sh` off Linux — that path once replaced the Linux
   recordings and cost one lane most of its closure.

## Owner decisions already taken — do not relitigate

- **`docs/decisions/` classification: EXCLUDE (option B).** The owner first chose
  measurement with a corpus raise to 63,000, then reversed after the alternative
  was measured at **fourteen** errors: corpus over by 1,457 tokens, five missing
  caps, five `checkIndex` entries that would push the always-loaded set past its
  cap to carry documents no seat is ever sent to read, and three citations in ADR
  0003 that are correct *because* it describes an experiment over files and
  symbols that do not exist. Built as `queue-10`. The five ADRs are named **one
  by one**, not by prefix: `CORPUS_EXCLUDED_PREFIX` refuses to excuse a `.md` by
  design, so a sixth ADR costs a line, which is the same bar as raising a cap.
- **O1, a second GitHub identity: DECLINED.** Recorded in ADR 0005 with the
  measurement that settles it — one collaborator, seats authenticate as that same
  identity, GitHub refuses self-approval, so a required-approval rule today is a
  **lock** rather than weak enforcement. The safe ordering, if ever revisited, is
  in that ADR: create, switch, **verify the authenticated login**, then add
  CODEOWNERS and the rule.
- **O3 is still open** and is the closing question: after the programme, do policy
  merges revert to owner approval per pull request, or stand on the ruleset plus
  `pr-contract`?

## Per-merge ritual

verdict + checks green → un-draft (`draft:false`; merging a draft returns 405) →
squash-merge with the full 40-char `expectedHeadSha`, citing the approval basis
and the verdict → `git fetch --prune` → update local `main` (**it goes stale and
the env matrix silently falls back to it**) → rebase the chain → **re-point by
commit SUBJECT, never by position** → `git -C <wt> reset --hard -q HEAD` per
worktree → verify the tip invariant → mirror → check `main`'s CI.

Re-pointing by index once shifted eight branches by one and dropped a commit;
the only thing that noticed was the tip's pin count reading 57 where it owed 76.

## Traps this session paid for

- **A count taken the easy way is this queue's recurring defect.** #621's body
  said five disposition rows; the diff added nine. #622's count of stale
  *"the five `web-*.js`"* prose sites was stated four times — five, six, four,
  seven — and seven is right. Every wrong count came from a line-anchored
  `git grep`, which cannot see a phrase that wraps a line, nor a site that states
  the claim without the searched token: `tools/audit/prepr.sh:111` says *"the five
  copies of the shared prompt block"* with no glob, one line above output printing
  `4 script(s)`. **Sweep prose wrap-aware**: strip comment leaders, join each
  file's lines, then match. **Derive a body's counts by mutating the artefact and
  reading the detector.**
- **A false claim in a code comment is worse than in a pull-request body.** The
  body is read once; the comment by everyone who opens the file. #622 shipped one
  such sentence wrong twice before it was right.
- **Body/push order (steward S10) relocates rather than removes.** Writing the
  body naming the new commit before pushing does not prevent the `pr-contract`
  failure — the `edited` event fires against whatever the remote head is at that
  moment. What it buys is that the *incoming* head is green from its first run.
- **Nothing measures a numbered list's numbering.** `05-handover` shipped two 8s,
  two 9s and two 10s green through `policy-docs`, `prepr` and a review.
- **`git checkout -q <file>` after a mutation reverts your own uncommitted work
  in that file too.** Commit first, or re-apply.
- **Assert the occurrence count before any string replacement** — and beware a
  count unique only in the multi-line form: `grep -c 'if proc.returncode != 0:'`
  is 4 in `env_drift.py` while the five-line block is 1.
- **A number a reviewer gives you is not measured either.** Re-deriving caught a
  review's own miscount twice in this queue.
- **Subagent mortality is the bottleneck, not CI.** Six review seats were lost.
  One died because the owner interrupted the parent turn. Always read
  `tasks/<agentId>.output` — last assistant text via a python json loop, never
  `tail` — before re-dispatching, and clean up its worktree. Briefs that survive:
  numbered drives in priority order, ending *"reach a verdict over being
  exhaustive"*, plus an explicit note that a shallow verdict beats forty minutes
  and none.

## Measurement discipline

Exit status from the **command**, never from a pipe and never from an `echo` that
runs regardless. `node --check` before trusting a zero-finding run. **Drive the
script, not the helper.** Never carry a number from a neighbouring branch into a
null control. A tool that does not support a flag is not a finding.

Checks before any push: `policy_lint`, `policy_lint_mutants`,
`policy_lint_envmatrix`, `fragments_sync --check`, `policy_lint --hooks`,
`rules_sync --check`, `brief_lint`, `check-wave-script`, `prepr.sh`, and
`PYTHONPATH="$PWD/tests/hastub" python3 tests/entities.py`. There is no venv and
`homeassistant` is **not** pip-installable. Entities is 1112 on `main` through
`03-record2` and 1114 from `04-claims-fiction` on.

## Standing constraints

Never raise a cap to fit — pay by cutting. Take no release stamp without the
owner saying so. Stale pre-archive branches are renamed `superseded/*` locally;
merging one re-adds roughly 71k lines that #618 deleted.

## Still owed

- The policy-document format contract (large, unbuilt).
- ADRs 0006–0007.
- The `worktree:` key in eleven briefs — every per-file cap is at zero headroom,
  so it needs eleven cuts.
- `orchestrator.md` 370 → 120; `fixer.md` 257 → 120.
- The **seven** prose sites saying five `web-*.js` when four remain, enumerated
  with line numbers in #622's `## Forward-carry`.
- O3, above.

## Appendix — the two disposition rows drafted but not landed

Reproduced here because the cloud container's `/tmp` does not exist on your box.
Either paste them into `docs/plan-2026-09-open-issues.md` in `06b-record3`, or
write your own; the check only needs the token `#621` and `#622` to appear.

- `#621` merged `07ae2d8` — the lane table truthed after #612 cut the copy that
  contradicted it; three statements corrected; nine disposition rows, established
  by mutation after the body claimed five.
- `#622` merged `d8dccd1` — `env_drift.three_dot_files` read `stdout` without
  ever reading `returncode`, so an unanswerable comparison and a clean tree gave
  the same all-clear; `release.yml`'s dispatch tag no longer interpolated into a
  shell line; three further reported defects refuted with the command that
  refutes each. Three review rounds, two blocks, both on claims rather than code.
- `#623` merged `03af74b` — the handover eleven merges stale, a machine section
  describing a box no reader is on, and three traps numbered onto three existing
  ones. Two review rounds. The first blocked on a carry naming a **branch**
  rather than a file, and on the body reporting the distance from a value the
  branch had written itself.
