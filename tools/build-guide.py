#!/usr/bin/env python3
"""Build guide.html from the app repo's GUIDE.md.  Usage: tools/build-guide.py path/to/GUIDE.md
Screenshots live in img/ (see SHOTS below); a missing image hides its slot."""
import sys, re, markdown
src = open(sys.argv[1]).read()

# user-facing part only: drop the maintenance note, the feature index and repo references
src = src.split('## Feature index')[0]
src = re.sub(r'> \*\*Keep this guide current\.\*\*.*?\n\n', '', src, flags=re.S)
src = src.replace('# PaiYo user guide\n', '')
src = re.sub(r'\*\*PaiYo: Track, Budget & Save\*\* · by AdRaw App Studio · app\.paiyo@thevoltdesk\.in\n\n', '', src)
src = re.sub(r'\d+\. \[Feature index\]\(#feature-index\)\n', '', src)
src = re.sub(r'\d+\. \[Keeping this guide current\]\(#keeping-this-guide-current\)\n', '', src)
src = src.replace('(Building it yourself from source is covered in `README.md`.)', '')
src = src.replace('(steps in `README.md`)', 'for anyone already on it')
src = re.sub(r' \(F\d+\)', '', src)
src = src.replace('Public privacy policy: https://paiyo.thevoltdesk.in/privacy.html', 'Full details: the [privacy policy](privacy.html).')

body = markdown.markdown(src, extensions=['tables', 'toc', 'sane_lists'])

def fig(src, cap, cls=''):
    c = f' class="{cls}"' if cls else ''
    return (f'<figure{c}><img src="img/{src}.png" alt="{cap}" loading="lazy" '
            f'onerror="this.parentNode.classList.add(\'missing\')"><figcaption>{cap}</figcaption></figure>')
def strip(items):
    return '<div class="shots">' + ''.join(fig(s, c) for s, c in items) + '</div>'
def floats(items):
    return '<div class="shotpair">' + ''.join(fig(s, c, 'shot') for s, c in items) + '</div>'

# (heading id, where, images)
SHOTS = [
    ('first-run', 'after-heading', strip([('welcome', 'Welcome'), ('privacy', 'Your data stays with you'), ('sms-access', 'Allow SMS access')])),
    ('home', 'after-heading', floats([('home', 'Home')])),
    ('home', 'after-table', strip([('home-charts-1', 'Where it went · how you paid'), ('home-charts-2', 'Monthly average · this month vs last')])),
    ('transactions', 'after-heading', floats([('transactions', 'Transactions'), ('money-in', 'Filtered to money in')])),
    ('accounts', 'after-heading', floats([('accounts', 'Accounts'), ('card', "A card's statement, by bill")])),
    ('budget', 'after-heading', floats([('budget', 'Budget'), ('budgets-editor', 'Edit budgets')])),
    ('bills', 'after-heading', floats([('bills', 'Bills'), ('add-bill', 'Add a bill')])),
    ('summary', 'after-heading', floats([('summary', 'Summary')])),
    ('settings', 'after-heading', strip([('settings-1', 'Budget month · categories'), ('settings-2', 'Appearance · app lock · SMS'),
                                         ('settings-3', 'Drive backup · live Sheet · Excel'), ('settings-4', 'SMS or email? · troubleshooting · About')])),
]
for hid, where, html in SHOTS:
    m = re.search(rf'<h3 id="{hid}">[^<]*</h3>', body)
    if not m: continue
    if where == 'after-heading':
        body = body[:m.end()] + '\n' + html + body[m.end():]
    else:
        j = body.index('</table>', m.end()) + len('</table>')
        body = body[:j] + '\n' + html + body[j:]

nav = '<nav class="dock"><a href="#home">Home</a><a href="#transactions">Transactions</a><a href="#accounts">Accounts</a><a href="#budget">Budget</a><a href="#bills">Bills</a><a href="#summary">Summary</a><a href="#settings">Settings</a><a href="#7-faqs">FAQs</a></nav>'
page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PaiYo user guide</title>
<meta name="description" content="How to use PaiYo: every screen, how bank alerts are read, budgets, bills, accounts, backups, privacy and FAQs.">
<meta name="theme-color" content="#3629B7">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
<link rel="icon" href="img/icon-32.png"><link rel="apple-touch-icon" href="img/icon-192.png"><link rel="stylesheet" href="style.css"></head>
<body>
<header class="band"><nav class="top"><a class="brand" href="index.html"><img class="coin" src="img/icon-192.png" alt="">PaiYo</a><a href="index.html">Home</a><a href="guide.html" class="on">Guide</a><a href="privacy.html">Privacy</a></nav>
<h1>User guide</h1><p>Every screen, every control, and the answers to the questions testers ask.</p></header>
<main class="sheet guide">
{body}
{nav}
</main>
<footer>© 2026 AdRaw App Studio · <a href="mailto:app.paiyo@thevoltdesk.in">app.paiyo@thevoltdesk.in</a> · <a href="privacy.html">Privacy policy</a></footer>
</body></html>'''
open('guide.html', 'w').write(page)
print('guide.html written,', len(page), 'bytes')
