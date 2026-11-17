# D10 acceptance criteria: platinum, rule by rule

> Adherence to home assistant integration platinum quality requirements.

— the owner, `D10.md`. The tier is the owner's and `manifest.json` already
declares it; the register is `quality_scale.yaml` in the integration.

Drafted by a fixer seat under mandate 6893738184 (scope all);
binding as the owner's words until the owner rewrites them.
A finding names the statement it fails.

- **Q1 the register.** Every rule of bronze, silver, gold and platinum on
  Home Assistant's current checklist (`D10.md` step 1) has a row, and every
  row reads `done` or `exempt`; every `exempt` row carries a `comment`
  stating why the rule cannot apply. Command, printing each row that fails:

      python3 -c "import yaml,sys;r=yaml.safe_load(open(sys.argv[1]))['rules'];\
      [print(k,v) for k,v in r.items() if (v if isinstance(v,str) else v['status']) not in ('done','exempt')\
      or (not isinstance(v,str) and v['status']=='exempt' and not str(v.get('comment','')).strip())\
      or (v=='exempt')]" custom_components/heatpump_optimizer/quality_scale.yaml

  Pass: no line, and no checklist rule missing a row. Fail: either.
- **Q2 every site.** A `done` row holds at every site the rule reaches, not
  at one: every entity, platform, service, flow step, raise and log site the
  rule's page names. Procedure: `D10.md` step 1's check per rule, run over
  the enumeration of those sites. Fail: one site that breaks the rule, which
  makes its row's `done` false.
- **Q3 exemptions stay true.** An `exempt` row's reason is still true of the
  code. Fail: the reason contradicted (an exempt discovery row beside a
  discovery mechanism, for example).
