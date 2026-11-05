import sys,re
p=sys.argv[1]; s=open(p).read()
anchor="        const m = await page.evaluate((co) => window.__p9.measure(co), false);\n"
assert s.count(anchor)==1
add=anchor+'''        if (process.env.HPO_SHOTDIR && st.name.startsWith("score_open") && cell.vp[0] === 375 && !cell.os) {
          const fs = await import("node:fs");
          const base = `${process.env.HPO_SHOTDIR}/${st.name}-375-${cell.theme}-${cell.lang}`;
          const txt = await page.evaluate(() => { const r = document.querySelector("heatpump-optimizer-card"); const root = r.shadowRoot || r; return [...root.children].filter((e) => e.tagName !== "STYLE").map((e) => e.innerText || "").join("\\n"); });
          fs.writeFileSync(base + ".txt", txt);
          await page.screenshot({ path: base + ".png", fullPage: true });
        }
'''
s=s.replace(anchor,add); open(p,"w").write(s)
