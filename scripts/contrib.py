#!/usr/bin/env python3
"""Render a contribution heatmap as self-hosted SVG (light + dark).

No third-party badge service: fetches the calendar from GitHub's GraphQL API and
draws it locally, so the README cannot break because someone else's Vercel app is
over quota. Text is converted to vector paths, matching the other assets.

  env GH_TOKEN   token with read access (Actions GITHUB_TOKEN or a classic PAT)
  env GH_LOGIN   github username (default KumarPriyam123)
"""
import os, sys, json, datetime, urllib.request
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOGIN = os.environ.get('GH_LOGIN', 'KumarPriyam123')

# ----------------------------------------------------------------- typography
_F = {}
def font(w):
    if w not in _F:
        f = TTFont(os.path.join(HERE, 'fonts', f'jbm-{w}.ttf'))
        _F[w] = dict(cmap=f.getBestCmap(), gs=f.getGlyphSet(),
                     upem=f['head'].unitsPerEm, hmtx=f['hmtx'])
    return _F[w]

def measure(w, text, size, tr=0.0):
    F = font(w); s = size / F['upem']
    return sum(F['hmtx'][F['cmap'].get(ord(c)) or F['cmap'][32]][0] * s + tr
               for c in text) - (tr if text else 0)

def path(w, text, size, x, y, fill, tr=0.0, op=None, cls=None):
    F = font(w); s = size / F['upem']; out = []; cx = x
    for ch in text:
        gn = F['cmap'].get(ord(ch))
        if gn is None:
            cx += F['hmtx'][F['cmap'][32]][0] * s + tr; continue
        sp = SVGPathPen(F['gs'], ntos=lambda v: f'{v:.1f}'.rstrip('0').rstrip('.'))
        F['gs'][gn].draw(TransformPen(sp, Transform(s, 0, 0, -s, cx, y)))
        d = sp.getCommands()
        if d.strip(): out.append(d)
        cx += F['hmtx'][gn][0] * s + tr
    if not out: return ''
    c = f' class="{cls}"' if cls else ''
    o = f' opacity="{op}"' if op is not None else ''
    return f'  <path{c} d="{" ".join(out)}" fill="{fill}"{o}/>\n'

# ---------------------------------------------------------------------- data
QUERY = """query($login:String!){ user(login:$login){ contributionsCollection{
  contributionCalendar{ totalContributions
    weeks{ contributionDays{ date contributionCount weekday } } } } } }"""

def fetch():
    tok = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not tok:
        sys.exit("GH_TOKEN not set. Locally:  $env:GH_TOKEN='<classic PAT, read:user>'")
    req = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': QUERY, 'variables': {'login': LOGIN}}).encode(),
        headers={'Authorization': f'bearer {tok}', 'Content-Type': 'application/json',
                 'User-Agent': f'{LOGIN}-profile'})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if 'errors' in body:
        sys.exit("GitHub API: " + json.dumps(body['errors'])[:300] +
                 "\nIf this is a permissions error, add a classic PAT with read:user "
                 "as the repo secret GH_PAT.")
    cal = body['data']['user']['contributionsCollection']['contributionCalendar']
    weeks = [[(d['date'], d['contributionCount']) for d in w['contributionDays']]
             for w in cal['weeks']]
    return cal['totalContributions'], weeks

def streaks(weeks):
    days = sorted((d for w in weeks for d in w), key=lambda t: t[0])
    best = cur = 0
    for _, c in days:
        cur = cur + 1 if c > 0 else 0
        best = max(best, cur)
    run = 0
    for _, c in reversed(days):
        if c > 0: run += 1
        elif run == 0: continue          # today may legitimately be empty
        else: break
    busiest = max((c for _, c in days), default=0)
    return run, best, busiest

# -------------------------------------------------------------------- render
TH = {'light': dict(fg='#000000', muted='#57606a', hair='#d0d7de', faint='#8c959f'),
      'dark':  dict(fg='#ffffff', muted='#8b949e', hair='#30363d', faint='#6e7681')}

# Cell colours per theme: [empty, level 1, level 2, level 3, level 4].
# Level 1 is already a clear colour, so every active day stands out on the page.
PALETTES = {
    'green':  {'dark':  ['#161b22', '#0f6d36', '#16a34a', '#34d36b', '#8df5a9'],
               'light': ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']},
    'ocean':  {'dark':  ['#161b22', '#0b4f8a', '#1478d4', '#3aa8ff', '#a6dcff'],
               'light': ['#ebedf0', '#a5d8ff', '#4dabf7', '#1c7ed6', '#0b4a8f']},
    'ember':  {'dark':  ['#161b22', '#7a2e0e', '#c2501a', '#f5842a', '#ffd27a'],
               'light': ['#ebedf0', '#ffd8a8', '#ffa94d', '#f76707', '#a33a00']},
    'aurora': {'dark':  ['#161b22', '#4c2a99', '#7b4ddb', '#a97bff', '#e0ccff'],
               'light': ['#ebedf0', '#d0bfff', '#9775fa', '#7048e8', '#432c9e']},
}
PALETTE = os.environ.get('CONTRIB_PALETTE', 'green')

def thresholds(weeks):
    """Quartiles of the active days, close to how GitHub's own graph buckets them.

    Scaling by the busiest day put almost every ordinary day in level 1 (one
    21-commit day meant a day needed 8+ to reach level 2). Quartiles spread the
    active days across all four levels; empty days stay empty.
    """
    xs = sorted(n for w in weeks for _, n in w if n > 0)
    if not xs:
        return [1, 1, 1]
    q = lambda p: xs[min(len(xs) - 1, int(p * len(xs)))]
    return [q(.25), q(.5), q(.75)]

def level(n, t):
    return 0 if n == 0 else 1 + sum(n > x for x in t)

CSS = """  <style>
    .f{opacity:0;animation:f .8s ease forwards}@keyframes f{to{opacity:1}}
    .cell{opacity:0;animation:pop .5s ease forwards}
    @keyframes pop{to{opacity:1}}
    .rise{opacity:0;animation:rise .9s cubic-bezier(.2,.7,.2,1) forwards}
    @keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
    .d1{animation-delay:.05s}.d2{animation-delay:.25s}.d3{animation-delay:.5s}
    @media (prefers-reduced-motion:reduce){
      .f,.cell,.rise{animation:none;opacity:1;transform:none}}
  </style>
"""
W, CELL, GAP = 880, 11, 2.6
MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def render(theme, total, weeks, cur, best, busiest):
    c = TH[theme]
    ramp = PALETTES[PALETTE][theme]
    t = thresholds(weeks)
    gx, gy = 44, 98
    h = int(gy + 7 * (CELL + GAP) + 56)
    b = f'  <rect class="f" x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="6" fill="none" stroke="{c["hair"]}"/>\n'
    b += '  <g class="f d1">\n'
    b += path('700', 'CONTRIBUTIONS', 11, 22, 30, c['muted'], 3.0)
    rt = 'rolling 12 months'
    b += path('400', rt, 11, W - measure('400', rt, 11, .3) - 22, 30, c['faint'], .3)
    b += '  </g>\n'
    b += f'  <line class="f d1" x1="22" y1="44" x2="{W-22}" y2="44" stroke="{c["hair"]}" stroke-width="1"/>\n'
    # summary row
    cells = [(f'{total:,}', 'TOTAL'), (str(cur), 'CURRENT STREAK'),
             (str(best), 'LONGEST STREAK'), (str(busiest), 'BUSIEST DAY')]
    x = 22
    b += '  <g class="rise d2">\n'
    for val, lab in cells:
        b += path('800', val, 16, x, 66, c['fg'], .3)
        b += path('500', lab, 8.5, x + measure('800', val, 16, .3) + 8, 66, c['muted'], 1.3)
        x += measure('800', val, 16, .3) + measure('500', lab, 8.5, 1.3) + 34
    b += '  </g>\n'
    # month labels
    seen = set(); step = CELL + GAP
    for wi, wk in enumerate(weeks):
        if not wk: continue
        d = datetime.date.fromisoformat(wk[0][0])
        if d.day <= 7 and d.month not in seen:
            seen.add(d.month)
            b += path('400', MON[d.month-1], 8.5, gx + wi*step, gy - 8, c['faint'], .6, cls='f d2')
    # day labels
    for di, lab in ((1,'Mon'), (3,'Wed'), (5,'Fri')):
        b += path('400', lab, 8, 12, gy + di*step + CELL - 2, c['faint'], .3, cls='f d2')
    # grid
    for wi, wk in enumerate(weeks):
        for (date, n) in wk:
            di = datetime.date.fromisoformat(date).weekday()
            di = (di + 1) % 7                      # calendar starts Sunday
            lvl = level(n, t)
            delay = .35 + wi * 0.007
            b += (f'  <rect class="cell" x="{gx+wi*step:.1f}" y="{gy+di*step:.1f}" '
                  f'width="{CELL}" height="{CELL}" rx="2.5" fill="{ramp[lvl]}" '
                  f'style="animation-delay:{delay:.2f}s"/>\n')
    # legend
    ly = gy + 7*step + 22
    lx = W - 22 - (5*(CELL+3) + measure('400','less',8.5,.3) + measure('400','more',8.5,.3) + 20)
    b += '  <g class="f d3">\n'
    b += path('400', 'less', 8.5, lx, ly + 8, c['faint'], .3)
    bx = lx + measure('400','less',8.5,.3) + 8
    for i, col in enumerate(ramp):
        b += (f'    <rect x="{bx+i*(CELL+3):.1f}" y="{ly}" width="{CELL}" height="{CELL}" '
              f'rx="2.5" fill="{col}"/>\n')
    b += path('400', 'more', 8.5, bx + 5*(CELL+3) + 5, ly + 8, c['faint'], .3)
    b += '  </g>\n'
    b += path('400', f'@{LOGIN}', 9, 22, ly + 8, c['faint'], .8, cls='f d3')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
            f'viewBox="0 0 {W} {h}" fill="none" role="img" '
            f'aria-label="{total} contributions in the last 12 months">\n{CSS}{b}</svg>\n')

if __name__ == '__main__':
    total, weeks = fetch()
    cur, best, busiest = streaks(weeks)
    for theme, sub in (('light', ''), ('dark', 'dark')):
        d = os.path.join(ROOT, 'assets', sub); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'contrib.svg'), 'w').write(
            render(theme, total, weeks, cur, best, busiest))
    print(f"contrib.svg written — {total:,} contributions, "
          f"current streak {cur}, longest {best}, busiest {busiest}")
