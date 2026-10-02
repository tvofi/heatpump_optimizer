"""Reviewer's probes of shapes the design's rule (3) names but the controls do not plant."""
import pathlib, sys, types
sys.path[:0] = ["tests/hastub", "tests", "custom_components"]
import doc_claims as d
PAGE = d.SITE_PAGE.read_text()
def once(s, a, b): assert a in s; return s.replace(a, b, 1)
for name, page in [
 ("icon from a third party (an image)", once(PAGE, "</head>", '<link rel="icon" href="https://x.example/f.ico"></head>')),
 ("preload font from a third party", once(PAGE, "</head>", '<link rel="preload" as="font" href="https://x.example/f.woff2"></head>')),
 ("@import of a third-party sheet", once(PAGE, "<style>", "<style>@import 'https://x.example/a.css';")),
 ("inline style url() third party", once(PAGE, "<section", '<section style="background:url(https://x.example/b.png)"')),
 ("picture source third-party srcset", once(PAGE, 'srcset="img/card/advisor-dark.png"', 'srcset="https://x.example/a.png"')),
 ("iframe from a third party", once(PAGE, "</footer>", '<iframe src="https://x.example/e"></iframe></footer>')),
 ("number in data-copy", once(PAGE, "</footer>", "<p data-copy>Saves 40 % a year</p></footer>")),
 ("number in the meta description", once(PAGE, 'content="Model-predictive', 'content="Saves 40 %. Model-predictive')),
]:
    e, _ = d.site_findings(page)
    print(f"{'RED ' if e else 'GREEN'} {name}: {e[:1]}")
