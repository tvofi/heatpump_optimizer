A verdict push refused as non-fast-forward is dropped, and probe_arm writes .refused on every non-zero exit, so a transient failure is never retried and a verdict can sit unposted. #2664 landed the confirm retry; the group's remaining carries own the re-apply on a fresh tip and the transient retry.

Roster group: `R10-FLY-RELAY-REVIEW-FF`. Part of #201.
