<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: the `browser` job installs playwright 1.49.0 from `tests/pwlane/package-lock.json`, inside GHSA-7mvr-c777-76hp (fixed in 1.55.1): its browser installer downloaded Chromium without verifying the TLS certificate.

After: the lane pins playwright 1.56.1, and the job's Chromium cache key moves with the pin so the old revision is not restored beside the new one.

1.56.1 rather than the newest release because its Chromium revision, 1194, is the one this change could be measured against: `tests/card_browser.mjs` passes every check under it. The exposure was the CI runner's download of Chromium, never a user install.

Touches `.github/workflows/tests.yml`, owned by @tvofi in `.github/CODEOWNERS`, so this needs tvofi's approving review.

## Head

ba8b9f59

## Mutation proof

n/a: a pin bump with no code path to break. The advisory check is the null control below, run against both pins.

## Null control

`npm audit --prefix tests/pwlane` on `origin/main` reports playwright `<1.55.1` (GHSA-7mvr-c777-76hp); at the head it prints `found 0 vulnerabilities`. `tests/card_browser.mjs` at the head, with `NODE_PATH` at an `npm ci` of this lock and Chromium 1194, ends `ALL BROWSER CHECKS PASSED`.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
