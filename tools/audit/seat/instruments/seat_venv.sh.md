# `seat_venv.sh`

- `seat_venv.sh` — builds the seat interpreter venvs reproducibly and installs
  the `shims/`. When: a new workstation or cloud seat; CI features are
  container-only on the Mac (no local venv for the Accelerate wheels).
  Builds `venv-ci` (CI's `fast` pins) and `venv-ha` (the typing lock,
  hash-pinned, `--no-deps`, cloud-setup.sh's pins call). `--check` reports
  both. `--self-test` drives the recipe and the shim export.
