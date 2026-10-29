# `cloud-setup.sh`

- `cloud-setup.sh` — the cloud seat environment's setup script (interpreter,
  CI-run pinning): it builds `venv-ci` and `venv-ha` under `/opt/hpo` and
  writes the toolchain profile. When: tvofi pastes it into Project settings; a
  seat cannot apply its own environment. A seat's Bash call inherits the
  agent's environment and reads neither the profile nor `BASH_ENV`, so the
  toolchain reaches it only through the environment's variables, which
  `--variables` prints and the setup run's last line names; `--check`, in a
  seat: `OK` (exit 0) only when all three hold, or `REFUSE` naming them (exit
  1). The profile prepends `venv-ci/bin` only
  when absent, so a PATH a caller narrowed is left alone; `--self-test`: the
  profile, variables and check arms. Refusal: a missing checkout warns and
  exits 0, so a session still starts, without pins.
