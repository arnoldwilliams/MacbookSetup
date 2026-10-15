#!/usr/bin/env python3
"""Convert the UK autism aggression guide (Markdown) to a print-ready HTML file."""

import markdown

SRC = "autism-aggression-parent-support-guide.md"
OUT_HTML = "autism-aggression-parent-support-guide.html"

with open(SRC, encoding="utf-8") as f:
    text = f.read()

body = markdown.markdown(
    text,
    extensions=["tables", "toc", "sane_lists", "attr_list"],
)

CSS = """
@page {
  size: A4;
  margin: 18mm 16mm 20mm 16mm;
}
* { box-sizing: border-box; }
body {
  font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.5;
  color: #1f2328;
  margin: 0;
}
h1 {
  font-size: 22pt;
  line-height: 1.25;
  color: #0f4c81;
  border-bottom: 3px solid #0f4c81;
  padding-bottom: 8px;
  margin: 0 0 6px 0;
}
h2 {
  font-size: 15pt;
  color: #0f4c81;
  border-bottom: 1px solid #c9d6e3;
  padding-bottom: 4px;
  margin: 22px 0 8px 0;
  page-break-after: avoid;
}
h3 {
  font-size: 12pt;
  color: #14415f;
  margin: 14px 0 5px 0;
  page-break-after: avoid;
}
p { margin: 0 0 8px 0; }
ul, ol { margin: 0 0 10px 0; padding-left: 22px; }
li { margin: 2px 0; }
strong { color: #10233a; }
hr {
  border: none;
  border-top: 1px solid #d7dee6;
  margin: 18px 0;
}
blockquote {
  margin: 8px 0 12px 0;
  padding: 8px 12px;
  background: #f4f7fa;
  border-left: 4px solid #0f4c81;
  font-size: 10pt;
  page-break-inside: avoid;
}
blockquote p { margin: 0 0 6px 0; }
code {
  font-family: "DejaVu Sans Mono", monospace;
  background: #eef2f6;
  padding: 1px 3px;
  border-radius: 3px;
  font-size: 9.5pt;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0 14px 0;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid #c9d6e3;
  padding: 5px 7px;
  text-align: left;
  vertical-align: top;
}
th {
  background: #0f4c81;
  color: #ffffff;
  font-weight: bold;
}
tr:nth-child(even) td { background: #f6f9fc; }
h1 + p, h1 + hr { margin-top: 4px; }
/* Keep the table of contents links plain in print */
a { color: #0f4c81; text-decoration: none; }
"""

html = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<title>Supporting a 4-Year-Old Autistic Child Who Is Aggressive Toward Adults and Peers</title>
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Wrote {OUT_HTML} ({len(html)} bytes)")
