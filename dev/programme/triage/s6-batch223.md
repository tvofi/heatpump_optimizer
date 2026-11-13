# Proposal triage, session s14, batch 223

Sources: triage queue line 353 (orchestrator, 2026-11-12T00:01:47Z), ruled as P676. Line numbers
are at origin/main 6d16af36c2. Roster read at handoff/audit-r10-roster dc65b69234.

## P676: prepr.sh's self-test compares padded wc output as a string and fails on Darwin

Verdict: ACCEPT (a) the site fix, as a new hotfix group R10-HOTFIX-PREPR-WC-PAD on the
orchestrator's go; DEFER (b) the raw-`wc` string-compare lint until a third instance of the shape.

Source: triage queue line 353. Since #3455 (commit 003f89cf9c), main's prepr.sh self-test fails
on macOS: one arm compares `wc -l` output as a string, and BSD wc pads it with blanks. Every
full-prepr open or update from the orchestrator's macOS host is refused, including the
r10-hotfix-opener-unblock handoff at 00:00Z. CI runs on Linux and never sees it. Local stopgap:
a wc shim on the instruments' PATH strips leading blanks.

Instances:
- tools/pr/prepr.sh :2403 `st "$(mg status --porcelain | wc -l)" 0 "and the in-place run leaves
  the work tree clean"`. `st` compares strings, so BSD's `       0` is not `0`.
  `git log -L2403,2403:tools/pr/prepr.sh` names 003f89cf9c as the commit that added the line.
- pr/r10-hotfix-opener-unblock/p1.log :22-23: `REFUSE self-test 536 passed, 1 failed` and
  `FAIL and the in-place run leaves the work tree clean (got        0, wanted 0)`.
- Sweep of the proposed scope, at 6d16af36c2: `git grep -nE 'wc -[lc]' -- '*.sh'`, minus lines
  that pipe through `tr -d` or wrap the count in `$(( ))`, keeping string compares (`=`, `!=`, or
  an `st`/`chk`/`ans` argument), and excluding numeric `-lt/-ge/-eq` tests (padding-safe). It
  returns 2 lines. prepr.sh:2403 is the defect. app_push.sh:1095 pipes `wc -c` into awk `$1`,
  which is padding-safe. No `var=$(... | wc -l)` assignment without `tr -d` exists under tools/
  or .claude/. About 20 other sites (cloud_relay.sh, handoff_push.sh, tick_loop.sh,
  session-start.sh) already follow the `| tr -d ' '` convention. The sweep therefore owes no
  second site. The fixer re-runs it at its base.
- Class: this is the second Darwin-only prepr self-test red to block local opens. The first was
  R10-HOTFIX-PREPR-SELFTEST-DARWIN (done; the shim's HOME). The two causes differ. The raw-wc
  string-compare shape has 1 instance.

Duplicate check: R10-HOTFIX-PREPR-SELFTEST-DARWIN is done and fixed a different arm (planted HOME
under the python3 shim). R10-PREPR-RESIDUE (in progress, 25 carries) and R10-HOTFIX-OPENER-UNBLOCK
(not started) name no wc padding (roster dc65b69234).

Accepted change (a): a new group, size XS, class hotfix, severity high (it refuses every local
full-prepr open and update, and the hotfix lane opens through that path). The bar is exempt by
severity. Edit prepr.sh:2403 to compare `$(( $(... | wc -l) ))` or pipe through `tr -d ' '`,
as its siblings do. Add a test that the arm passes under a padding wc on PATH (a null control:
it fails before the edit). Then retire the local wc shim from the instruments' PATH, so the
macOS host again runs what main ships. Sonnet fixer and reviewer. File: tools/pr/prepr.sh.

Deferred (b): a bare_array.py-style lint for raw `wc` in a string compare. 1 instance of the
shape against about 20 compliant sites. A new check file and its self-test cost more than a
one-site recurrence. It becomes due at the third instance (audit-class barrier). The cheaper
class barrier, a Darwin run of prepr's self-test, is the stage that would also have caught the
first instance. It belongs to whichever group next owns prepr's self-test host coverage, and is
not built here.

Cost: XS. One line in tools/pr/prepr.sh plus one self-test arm; no new file. prepr.sh is not
on a capped list in tests/structure_budgets.json.

Binding: the orchestrator's go for the new group. Until it lands, the local wc shim stays in
place.
