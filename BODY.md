Replacement for Dependabot #3483 (pip group, 8 updates), red on tests / typing because it moved homeassistant-stubs 2026.9.3 to 2026.10.0 past the pin `tests/typing_ruler.py` enforces. Third compat replacement of this group (#3323, #3414, #3483), so it adds the class barrier: `.github/dependabot.yml` ignores homeassistant-stubs and mypy for `/tests`. Re-locked `tests/requirements-typing.txt` through its header compile with the stubs held.

Resolution deviates from the brief's "7 other bumps": only 2 compile. The header's own rule holds a bump to a package homeassistant 2026.11.0 pins exactly. The compile refused httpx2 2.16.0 (homeassistant pins 2.14.0), zeroconf 0.154.0 (pins 0.152.0) and truststore 0.10.5 (pins 0.10.4); httpcore2 and cronsim were held with them (the same exact-pin class, header hold list updated). Landed: bleak 3.0.2 to 3.1.0, regex 2026.11.7 to 2026.11.9. Closing #3483 as superseded after merge is the orchestrator's.

## Head

b86aed6c3428b21871e698002298b12f4c7cace3

## Mutation proof

Mutant: the lock as #3483 carried it (homeassistant-stubs==2026.10.0) restored over `tests/requirements-typing.txt`; `python3 tests/typing_ruler.py` printed `FAIL the typing job's hashed lock installs the recorded pins [homeassistant-stubs==2026.10.0 in the lock, ==2026.9.3 in the budget...]`. Restored: no FAIL, `ok homeassistant-stubs is pinned at 2026.9.3`.

## Null control

Same compile without the hold (stubs bumped) reproduces the FAIL line above; with `uv pip compile` and zeroconf/truststore/httpx2 bumped without holds it is unsatisfiable ("homeassistant==2026.11.0 depends on zeroconf==0.152.0").

## Figures

- `python3 tests/typing_ruler.py` at the head: `ok mypy is pinned at 2.4.1`, `ok homeassistant-stubs is pinned at 2026.9.3`.
- `git diff -U0 b5057b052558163c499f74426ba26e541475db8f HEAD -- tests/requirements-typing.txt | grep -E '^[-+][a-zA-Z0-9_.-]+=='`: only bleak and regex pins move.

## Red checks

none

## Forward-carry

none

## Friction

none
