// Reviewer's own probe: extract slotHitExtents from the card at <worktree> and lay out a boxed-in lane.
import { readFileSync } from "node:fs";
const src = readFileSync(`${process.argv[2]}/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`, "utf8");
const a = src.indexOf("function slotHitExtents("), b = src.indexOf("const _coarsePointer");
const f = new Function(src.slice(a, b) + "\nreturn slotHitExtents;")();
const cases = {
  boxed_in: [[100, 103], [113, 116], [126, 129]],     // 3 px inks, 10 px gaps, floor 24
  pair_close: [[100, 103], [108, 111]],
  shared_steps_like: [[50, 54], [60, 64], [70, 74], [80, 84], [90, 94]],
};
for (const [name, ink] of Object.entries(cases)) {
  const drawn = ink.map(([x1, x2]) => ({ x1, x2, shown: true }));
  const h = f(drawn, 0, 400, 24, () => true);
  let overlap = 0;
  for (let i = 0; i + 1 < h.length; i++) overlap = Math.max(overlap, h[i].right - h[i + 1].left);
  console.log(`RESULT ${name} max_overlap_px=${overlap.toFixed(2)} targets=${h.map((t) => `${t.left.toFixed(1)}-${t.right.toFixed(1)}`).join(",")}`);
}
