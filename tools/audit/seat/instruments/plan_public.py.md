# `plan_public.py`

- `plan_public.py` — stages the ongoing round's plan page for the public site
  (R10-OUTSIDE-INTAKE). `stage --out DIR` takes `PLAN.html` from the newest
  `origin/handoff/audit-r<N>-plan` state ref (the layout `state_docs.state_of`
  owns) and writes it as `DIR/plan/index.html`; `.github/workflows/pages.yml`
  runs it from the dispatched ref's tree, then checks out the newest `v*` tag
  for the docs, so the page is served at `plan/` beside the product page.
  `url` prints `PLAN_URL`, the one spelling of the public address. When: inside
  the Pages workflow, which the beat's `plan-beat` row dispatches after each
  state push that landed; by hand, to see what would be published. Refusals:
  rc 2 and nothing written when there is no state ref or no page at the newest
  one (the workflow deploys without a plan and warns); rc 1 and nothing written
  for a page that is not an HTML document or that `ref_privacy` reads a host
  path, account name, uid, session scratch root or a tool's attribution in --
  the deploy goes red rather than publish it. `--self-test` drives every arm
  offline over a faked git.
