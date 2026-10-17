"""Minimal Jinja filter registration helper kept separate for readability."""
import re
from markupsafe import Markup, escape

def markdown_to_html(value: str) -> Markup:
    """Render a small safe subset of Markdown without an extra dependency."""
    text = escape(value or "")
    # bold, then basic headings and bullets; escape occurs before replacements.
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", str(text))
    lines = text.splitlines()
    out = []
    in_list = False
    for line in lines:
        s = line.strip()
        if s.startswith("### "):
            if in_list: out.append("</ul>"); in_list = False
            out.append(f"<h3>{s[4:]}</h3>")
        elif s.startswith("- ") or s.startswith("* "):
            if not in_list: out.append("<ul>"); in_list = True
            out.append(f"<li>{s[2:]}</li>")
        elif not s:
            if in_list: out.append("</ul>"); in_list = False
        else:
            if in_list: out.append("</ul>"); in_list = False
            out.append(f"<p>{s}</p>")
    if in_list: out.append("</ul>")
    return Markup("\n".join(out))
