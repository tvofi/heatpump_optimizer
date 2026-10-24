Closed by the orchestrator (session s4) after PR #2561 merged at 3976515a08228598ea3863f4f36dc4c7c4846865.

The root-cause record R10-RCA-HARNESS-FRICTION, delivered by #2561, disposes this friction key (`class-open`). One cause covers it: a contract step that defines a block class did not teach the word `VERDICT_CLASSES` uses for it, so one obligation was keyed under several words. The fix teaches both words in `fix-review.md`, and the detector now lives in `check-wave-script.mjs`. #2561's body names this issue as one for the orchestrator to close by hand after the merge. Part of #201.
