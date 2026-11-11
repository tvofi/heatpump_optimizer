# R10-RELAY-REPLAY: a restarted relay loop replayed 93 probes onto review refs

Root-cause seat, `root-cause.md`. Figures are the ones measured when the defect was
found; they are not re-derived here.

## Defect

`cloud_relay.sh`'s `relay()` pushed a `probe/rev-*` verdict to `review/<pr>` whenever
the probe was missing from its ledger. A loop restarted without `HPO_STATE_DIR` read the
stale default ledger (`$HOME/.local/state/hpo/cloud-relayed`), found no entry for any
probe, and replayed 93 probes as 92 commits on 56 `review/<pr>` refs, 53 of them on
closed PRs.

## Cause

The ledger was the only record of delivery, and the loop's state directory came from an
environment variable nothing printed. A wrong or empty ledger therefore read as "nothing
delivered", and relay's only reaction to "not in the ledger" was to push.

## Process state

(c): the process was followed and did not produce the intended result. The restart
followed the documented loop command; the ledger rule ("push once, then record") held
only while the ledger was the right one.

## Countermeasure

- Delivered guard in `relay()`: if `review/<pr>` already has a commit with the probe's
  tree, record the probe as relayed and push nothing.
- Each pass prints `cloud_relay: state dir <dir>, ledger <path>, log <path>` once, so
  a wrong state directory is visible in the first log line.
- Self-tests: `cloud_relay.sh --self-test` (new tree pushed, delivered tree skipped,
  oldest of many review commits found, one state-dir line per pass).

## Cost test

    cost(countermeasure) < cost(defect) x P(recurrence)

cost(defect): 92 spurious commits on 56 refs, 53 on closed PRs, each a notification
and a ref a reader must tell from a real verdict; cleanup is by hand, per ref.
P(recurrence): every restart of the loop without `HPO_STATE_DIR` repeats it.
cost(countermeasure): one `ls-tree`/tree comparison per relayed probe and one printed
line per pass. Passes.

## Dropped condition

An earlier design also required that the review commit be "committed after the
probe". That condition had no historical case behind it and the self-test shows the
guard works without it (a review commit dated after the probe is skipped too), so it
was dropped.

## Class

No entry in `dev/audit/config/bugclasses.json` matches (the nearest, `N-log-flood`, is
a log-volume class, not a replay); no `rca` field is cited or edited.
