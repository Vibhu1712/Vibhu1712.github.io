"""Build the PaiYo blog.

Write each post as blogs/posts/<slug>.md with a front-matter block
(title, slug, date YYYY-MM-DD, description), then run:

    python3 tools/build-blog.py

It writes blogs/<slug>/index.html for every post, the list page
blogs/index.html (newest first), and sitemap.xml. Needs: pip install markdown
"""
import html
import json
import pathlib
import re
from datetime import date

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS = ROOT / "blogs" / "posts"
SITE = "https://paiyo.thevoltdesk.in"
FOOT = ('<footer>© 2026 AdRaw App Studio · <a href="mailto:app.paiyo@thevoltdesk.in">'
        'app.paiyo@thevoltdesk.in</a> · <a href="{up}privacy.html">Privacy policy</a></footer>')


def nav(up, on):
    links = [("index.html", "Home"), ("guide.html", "Guide"), ("blogs/", "Blog"), ("privacy.html", "Privacy")]
    items = "".join(
        f'<a href="{up}{href}"{" class=\"on\"" if label == on else ""}>{label}</a>' for href, label in links
    )
    return (f'<nav class="top"><a class="brand" href="{up}index.html"><img class="coin" '
            f'src="{up}img/icon-192.png" alt="">PaiYo</a>{items}</nav>')


def head(title, desc, url, up, extra=""):
    t, d = html.escape(title), html.escape(desc)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{t}">
<meta property="og:description" content="{d}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/icon-512.png"><meta name="twitter:card" content="summary">
<meta name="theme-color" content="#3629B7">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
<link rel="icon" href="{up}img/icon-32.png"><link rel="apple-touch-icon" href="{up}img/icon-192.png"><link rel="stylesheet" href="{up}style.css">{extra}</head>"""


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line)
    meta["body"] = markdown.markdown(m.group(2), extensions=["tables"])
    meta["nice"] = date.fromisoformat(meta["date"]).strftime("%-d %B %Y")
    return meta


def build_post(p):
    url = f"{SITE}/blogs/{p['slug']}/"
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
        "description": p["description"], "datePublished": p["date"], "url": url,
        "author": {"@type": "Organization", "name": "AdRaw App Studio"},
        "publisher": {"@type": "Organization", "name": "AdRaw App Studio"},
    }, ensure_ascii=False)
    page = head(p["title"], p["description"], url, "../../",
                f'\n<script type="application/ld+json">{ld}</script>') + f"""
<body>
<header class="band">{nav("../../", "Blog")}
<h1>{html.escape(p["title"])}</h1><p>{p["nice"]} · AdRaw App Studio</p></header>
<main class="sheet guide post">
{p["body"]}
<p class="muted"><a href="../">← All posts</a></p>
</main>
{FOOT.format(up="../../")}
</body></html>
"""
    out = ROOT / "blogs" / p["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


def build_index(posts):
    cards = "\n".join(
        f'<a class="card postcard" href="{p["slug"]}/"><span class="muted">{p["nice"]}</span>'
        f'<b>{html.escape(p["title"])}</b><span>{html.escape(p["description"])}</span></a>'
        for p in posts
    )
    desc = "Money stories, budgeting and getting out of debt, from the makers of PaiYo."
    page = head("PaiYo Blog", desc, f"{SITE}/blogs/", "../") + f"""
<body>
<header class="band">{nav("../", "Blog")}
<h1>Blog</h1><p>{desc}</p></header>
<main class="sheet">
{cards}
</main>
{FOOT.format(up="../")}
</body></html>
"""
    (ROOT / "blogs" / "index.html").write_text(page, encoding="utf-8")


def build_sitemap(posts):
    urls = ["", "guide.html", "privacy.html", "blogs/"] + [f"blogs/{p['slug']}/" for p in posts]
    body = "".join(f"<url><loc>{SITE}/{u}</loc></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n',
        encoding="utf-8")


posts = sorted((parse(f) for f in POSTS.glob("*.md")), key=lambda p: p["date"], reverse=True)
for p in posts:
    build_post(p)
build_index(posts)
build_sitemap(posts)
print(f"Built {len(posts)} post(s)")
