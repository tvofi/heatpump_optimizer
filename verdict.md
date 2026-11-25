Fix review: blocked b15a9f2cadb869915afbd317c08d1acd900259d2 class-open: axis dispatch paths that write the seat key unenumerated (e.g. publish_seat stub)

bus-nonce: aec2337b7b02b00abd51dfa9089150c0

Round: 1 (first review of #3898, full diff against merge base 0e1eba2b4a).

## Block

- class-open: axis dispatch paths that write the seat key unenumerated (e.g. publish_seat stub). The body claims a seat is "keyed by the `Seat key:` line that `cloud_dispatch.render` now ends every prompt's first line with", and `token_ledger.read_transcript` reads the key only from a transcript's first user message. But every real cloud dispatch goes through `publish_seat`: `dispatch_group` calls it at `tools/audit/seat/cloud_dispatch.py:743`, and `main --publish` at `:1691`. The seat's first user message is then the `_pointer` stub (`cloud_dispatch.py:220-228`), and that stub deliberately carries no key: `if not publish_ref:` at `:420`, asserted by the self-test arm "its stub carries no key". The key sits only in PROMPT.md, which the seat reads through a tool call, so the ledger never sees it. Measured at this head: the PROMPT.md first line parses as `{'role': 'reviewer', 'seat': 'reviewer-rev-3898', ...}`, while `parse_header(stub)` is `None` (`ev/stub_key.txt`). `collect --seat-class cloud` over this seat's own transcript, whose first user message is exactly such a stub, writes `group=- role=- dimension=- seat=-` (`ev/own_cloud_keys.txt`). Local spawns are the other member of the set. The key is written there only by the convention in `instruments/token_ledger.py.md:7-10`, which no rule reads and no check enforces; an unkeyed subagent gets `seat=-`.
  Consequence on the refusal this PR adds: `ledger_gaps` drops `-` seats, and `round_ledger_gaps` prints `LEDGER unread` only when the ledger or the window is absent. An evaluator or reviewer run as a published cloud seat, or as an unkeyed local spawn, therefore reads `ok start evaluation` with no gap and no unread line. That is a silent pass, not the "unread, never a partial" the body states for `token_line`. Owed: either put the key where the reader looks (the stub's first line; the key is about 80 bytes against the stub's 1 KB bound), or have the reader take it from the pinned PROMPT.md. Disposition the local-spawn member by a rule or a stated residue category. Make `round_ledger_gaps` print unread while a seat class, or the seat column, the refusal depends on is unledgered.
- Surviving mutants in `token_ledger.read_transcript`, my own targeted runs at this head (`ev/mutants.txt`); the fix round pins them:
  - M4 `if first and o.get("type") == "user":` changed to `if o.get("type") == "user":` survives. Every later user line, which in a real transcript includes each tool_result, would then overwrite the key, usually with `None`, and no self-test transcript holds a second user message.
  - M5 `d["t"] = max(d["t"], stamp)` changed to `d["t"] = stamp` survives, because the fixtures' stamps only ascend.

## Findings

none

## Evidence

- RESULT: head reviewed b15a9f2cadb869915afbd317c08d1acd900259d2 (`ev/HEAD.txt`). The body's `## Head` names 8bafe16f10 and merge base e3cb5c01. The head adds main's merge 99e805acaf and the delivery row b15a9f2cad, and the code is unchanged.
- RESULT: `git merge-tree --write-tree origin/main b15a9f2cadb869915afbd317c08d1acd900259d2` rc=0, no conflict (`ev/merge_tree.txt`). `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- RESULT: VERSION, the manifest and RELEASE_NOTES are untouched, and no golden or claim file is in the diff (`ev/changed_files.txt`), so step 4 has nothing to compare.
- RESULT: self-tests at the head (`ev/selftests.txt`): token_ledger 16 passed, 0 failed; cloud_dispatch 186 checks, 0 failed; beat_jobs 313 checks, 0 failed; check_scopes `SELF-TEST passed`; `tests/structure.py` `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
- RESULT: the body's mutation proof re-run (`ev/mutants.txt`). These are killed: M1 the seen guard; M2 the class rule; M3 keeping a pruned transcript's rows; M6 round_metrics `if missing or not prod`; M7 the key insertion; M8 inherit_part; M9 `group=group_id`; M10 `gaps += round_ledger_gaps`; M11 the window lower bound `a <`; M12 dropping `reviewer` from ledger_gaps. M4 and M5 survive (see the Block section). I ran no diff-mutant table; that is CI's to run.
- RESULT: usage is the same on every content-block line of one response (12 multi-line responses, 0 differing) in this seat's own transcript, so the once-per-(id, requestId) count is sound on real data.
- RESULT: no finder's harness is named; the packet reads "none named". This group is instrument-building (card P4), not an audit finding.
- CI: `merge_train.py classify b15a9f2cadb869915afbd317c08d1acd900259d2 --pr 3898` still WAIT at the last poll (`ev/classify.txt`), with no red. I did not wait for GREEN because the verdict blocks on code.
