# BLOCKED: r11-owner-cooling-autoreturn-fix

Seat: fixer-r11-owner-cooling-autoreturn-fix. Base given: origin/main fd93aa3e9b161e92ead26e04ba8311b3fc0fc7e5.

Question: may this group be built on a main that does not carry R11-OWNER-FAULT-HOLD (#3872), or does it wait for #3872 to merge?

Why it stops: the approved design (design/R11-OWNER-COOLING-AUTORETURN 726e84d230, approved by design-verdict 95ac7c753a) says, under "Hot files, serial position, carries": "The fixer branches from main after #3864 and FAULT-HOLD's #3872 have merged, never before." The roster group's `after` lists R11-OWNER-FAULT-HOLD. At fd93aa3e9b #3864 is merged (d3d66c4040) but #3872 is open (state open, merged false, head 2f7a3aa54b): `custom_components/heatpump_optimizer/fault_hold.py` does not exist on main. The return's last guard, `fault_hold.consult(entry, inp)` (the design's R1), its E4 fault case and null control, and the `_write_supply` composition all read that module, so building now would be a departure from the approved note, which fixer.md step 17 says is raised, not made.

What resumes it: #3872 merging into main (then re-dispatch at the new main), or an orchestrator ruling that narrows the design to build without the fault consult (which would need a design revision, since R1 was the revise-round's blocking finding).

No code was written.
