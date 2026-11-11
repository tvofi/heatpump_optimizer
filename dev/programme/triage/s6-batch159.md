# Proposal triage, session s14, batch 159 (P571)

This batch rules `s7/triage-queue-s7.txt` line 254. The bar and the denominators are batch 141's.

Sources:
- origin/main `dbd1ab5b07`. `failure_logs.sh`, `merge_train.py`, `tools/ci/gate.py` and `ci.yml`
  are unchanged from `444cf62fab`.
- The merge seat's own output, `s14/seat/merge/fl3355/` (`HEAD.txt` 03:56:43Z, `failing.tsv`).
- The GitHub API, read at about 04:05Z (about 30 calls):
  - the check-runs at `dee7a1fa45`, both pages;
  - check-runs 130305517989 and 130305543232 by id, with their annotations;
  - workflow runs 42818706376 and 42945740958;
  - commits 98a544dba9 and 6f1e3cfd16;
  - `total_count` at 15 heads `failure_logs.sh` has read since 2026-11-10.

## P571: S14-FAILURE-LOGS-HIDES-OLDER-GATE

Verdict: ACCEPT, at a corrected cause and fix site. It repairs an observed wrong behaviour, and it
is its own carry on R10-TRAIN-RESIDUE, not a fold into carry 18. The ruling also corrects carry
18's deferral test, which the evidence shows never matches as written.

Source: queue line 254 (2026-11-11T03:58:10Z, the merge seat, PR 3355 at dee7a1fa).

Instances:
- **The reds were real, and the tool did not list them.**
  - Check-runs 130305517989 and 130305543232 are `gate`, `failure`, at head `dee7a1fa`, started
    03:41:05Z and 03:43:02Z, in run 42818706376 (`CI edit`, attempt 3).
  - The seat's `fl3355/failing.tsv` (03:56:43Z, before the 03:57Z re-runs) lists only
    `governance / delivery-status` and `pr-contract / pr-contract`.
- **The cause is not grouping.** `failure_logs.sh` lines 125-130 keep only completed failures
  first, and then take the newest per name. A newer green therefore cannot hide an older red.
  - I ran the script's own jq over the 3355 shape: two red `gate` entries, then a newer green one.
    It prints `gate failure 2`, the newer red.
  - A false premise would have looked like that jq printing nothing for `gate`.
- **The cause is that it reads only the first page.**
  - Line 125 calls `check-runs?per_page=100` with no `--paginate` and no page loop.
  - The head holds 144 check-runs (`total_count`), and GitHub lists them by id, descending:
    - page 1 is ids 130311468189 down to 130305614669, 100 entries, sorted descending;
    - page 2 is 130305614454 down to 129809007326, 44 entries.
  - Both reds' ids (130305517989 and 130305543232) are below page 1's last id. Even now one
    green `gate` check-run, 130305563880, is on page 2.
  - At 03:56Z the 36 check-runs the re-runs later created did not exist yet. About 90 surviving
    entries sat above the reds, plus the failed jobs the re-runs replaced. That puts the reds at
    or past the boundary. Today's reading shows the mechanism directly.
  - A false premise would have looked like a head under 100 check-runs, or a red id above page
    1's last id.
- **How often it happens.** Of 15 heads that `failure_logs.sh` read since 2026-11-10 (the newest
  out-dirs), 2 now hold more than 100 check-runs: `dee7a1fa45` (144, PR 3355) and `60a26fee42`
  (121, PR 3341). The queue line's second instance, PR 3405 at `068074f0`, holds 179.
  - These are today's totals. The totals at read time were at most these.
- **"Newest red per name" also drops reds, as a second effect.** A head with two red `gate`
  entries lists one. GitHub blocks on any red entry of a required context (batch 155, P567), and
  `gate` is that context. So for `gate`, every red is the answer to "why is this PR blocked".
- **Correction to carry 18 (P567), read from the same runs.**
  - Carry 18 re-runs a red `gate` when "its output title is gate.py's deferral line, or [it]
    comes from a run whose `sha=` names another head".
    - **The title arm never matches.** Check-run 130305517989 has `output.title`, `summary` and
      `text` all null. Its one failure annotation is "Process completed with exit code 1". The
      deferral text (`gate.py` line 130: `run(s) [...] at this head are still being judged;
      their gate decides`) is printed only into the job log.
    - **The `sha=` arm matches every run.** `ci.yml`'s run-name (lines 21-32) puts `github.sha`
      in `sha=`, and for a `pull_request` run that is the merge commit:
      - 98a544dba9 (run 42818706376) has parents `cd36e79737` and `dee7a1fa45`;
      - 6f1e3cfd16 (PR 3404's run 42945740958) has parents `63bcdcaad8` and `561edf4c8f`.
  - So the arm fires on every `pull_request` run, and carry 18's real filter is only its second
    condition (a green `gate` at the same head from a completed run).
  - That condition is the sound one. Every gate at a head computes the same verdict from the same
    sources (`gate.py`'s module doc, lines 30-36), so a red beside a completed green at one head
    is a stale or deferred red.
  - A false premise would have looked like a non-null deferral title, or a `sha=` equal to the
    head.

Cost:
- **(1) `failure_logs.sh` reads every check-run at the head through the one paginated reader.** It
  stops making its own single-page call.
  - A `merge_train.py check-runs <sha> <owner/repo>` shell entry prints `Train._check_runs(sha)`
    (line 1843, `--paginate`) as JSON lines. It sits beside the existing `job-log` entry
    (`merge_train.py` line 653, "every Actions job-log read in the tree goes through here").
  - `failure_logs.sh` slurps those lines into its existing jq.
  - The paged read then follows whatever page fix carry P549 lands in the same file, in a cloud
    seat too.
- **(2) Every completed red of a required context is listed, not only the newest.** Today that
  context is `gate`; the set is the one `merge_train.py` reads (`REQUIRED_CONTEXTS`, line 397: `tools/policy/fixtures/required-contexts.json`), not a new list. Other names
  keep "newest red per name".
  - A red whose log holds `gate.py`'s deferral text prints `deferral` beside its job id.
- **Self-test, in `failure_logs.sh`:**
  - the fake `gh` serves 101 check-runs over two pages, with a red `gate` on page 2, and it is
    listed;
  - two red `gate` entries and a newer green are all listed, the reds each with their log;
  - a deferral log is tagged and a plain failure is not;
  - the null control: a one-page head with one red per name prints today's lines;
  - a mutant that reads one page fails the page-2 case.
  - The existing "red-then-green grouped to the newest" check stays for a non-required name.
- **(3) The amendment to carry 18.** Its deferral test becomes: the red `gate` check-run's job log
  holds `gate.py`'s deferral text (read through `merge_train.py job_log`), or a green `gate`
  check-run from a completed run is at the same head.
  - The title and `sha=` arms are dropped.
  - Carry 18's self-test fixtures follow suit: titles null and `sha=` set to a merge commit, as
    GitHub serves them.
- Size: about 15 lines in `failure_logs.sh`, about 8 in `merge_train.py`, and the self-test cases.
  Neither file has a row in `tests/structure_budgets.json`.

Binding:
- `failure_logs.sh` is the instrument that answers "why is this PR red". It silently answers from
  the newest 100 check-runs, and the heads that sit longest in the train, the ones re-run most,
  are the ones past 100.
- Each miss cost the merge seat a hand read by job id: 3355, and 3405 before it.
- Folding this into carry 18 would merge two different repairs, a diagnostic reader and the
  train's re-run decision. They share one rule, so they are kept separate.
- Correcting carry 18 now costs one sentence. Building it as written would ship a filter whose
  first condition is always true and whose other arm is never true.

Routing:
- Two carries go to R10-TRAIN-RESIDUE, which owns `merge_train.py` and `failure_logs.sh`. It is in
  progress as PR 3424 (handoff moved to `5e91c2cfe5`), so both carry the PART 2 prefix.
- Carry files:
  - `b159-P571.txt`: items (1) and (2);
  - `b159-P571-c18.txt`: item (3), which names itself carry 18's amendment.
