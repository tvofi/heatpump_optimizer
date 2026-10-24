Main pins the patched aiohttp, pillow, uv and certifi, yet 27 Dependabot alerts stay open because the SBOM still reports the old versions and the dependency-graph workflow last ran on 2026-10-03. Find why manifest-touching pushes stopped triggering it and restore the update, so the alerts close on their own.

Roster group: `R10-FLY-DEPGRAPH-STALE`. Part of #201.
