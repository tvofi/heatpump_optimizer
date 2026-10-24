#!/bin/bash
for p in 14344 14372 14390 14405; do while kill -0 $p 2>/dev/null; do sleep 20; done; done
cd ~/hpo-orch/r10s3/upd; for p in 2404 2390 2368 2406; do echo "== $p"; tail -3 $p.log; done
