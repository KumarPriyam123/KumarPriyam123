#!/usr/bin/env python3
"""Render the stack panel and the project cards as self-hosted SVG (light + dark).

Same approach as contrib.py: no badge service, text converted to vector paths
(JetBrains Mono), logos from Simple Icons (CC0) stored in scripts/icons.json.
Edit STACK or PROJECTS below, then run:  python scripts/cards.py
"""
import os, json
from contrib import font, measure, path, TH, ROOT, HERE

ICONS = json.load(open(os.path.join(HERE, 'icons.json')))
BG = {'dark': '#0d1117', 'light': '#ffffff'}
CHIP = {'dark': '#161b22', 'light': '#f6f8fa'}
BODY = {'dark': '#c9d1d9', 'light': '#24292f'}
ACCENT = {'dark': '#34d36b', 'light': '#1a7f37'}     # same green as the contribution graph

CSS = """  <style>
    .f{opacity:0;animation:f .7s ease forwards}@keyframes f{to{opacity:1}}
    .rise{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) forwards}
    @keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
    .d1{animation-delay:.05s}.d2{animation-delay:.15s}.d3{animation-delay:.25s}
    .d4{animation-delay:.35s}.d5{animation-delay:.45s}.d6{animation-delay:.55s}
    .d7{animation-delay:.65s}
    @media (prefers-reduced-motion:reduce){.f,.rise{animation:none;opacity:1;transform:none}}
  </style>
"""

# ------------------------------------------------------------------ helpers
def _lum(hexc):
    h = hexc.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def _contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

def icon_colour(key, theme):
    """Brand colour, unless it would vanish on this theme's background."""
    hexc = '#' + ICONS[key]['hex']
    return hexc if _contrast(hexc, BG[theme]) >= 2.2 else TH[theme]['fg']

def icon(key, x, y, size, theme):
    s = size / 24
    return (f'  <path transform="translate({x:.1f} {y:.1f}) scale({s:.4f})" '
            f'd="{ICONS[key]["path"]}" fill="{icon_colour(key, theme)}"/>\n')

def chip(theme, x, y, label, key=None, h=26, size=11, pad=10, isz=14):
    """A rounded chip with an optional logo. Returns (svg, width)."""
    c = TH[theme]
    tw = measure('500', label, size, .2)
    w = pad + (isz + 7 if key else 0) + tw + pad
    out = (f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="5" '
           f'fill="{CHIP[theme]}" stroke="{c["hair"]}"/>\n')
    tx = x + pad
    if key:
        out += icon(key, x + pad, y + (h - isz) / 2, isz, theme)
        tx += isz + 7
    out += path('500', label, size, tx, y + h / 2 + size * 0.36, BODY[theme], .2)
    return out, w

def wrap(text, size, width, w='400'):
    lines, cur = [], ''
    for word in text.split():
        cand = (cur + ' ' + word).strip()
        if measure(w, cand, size) <= width:
            cur = cand
        else:
            lines.append(cur); cur = word
    if cur:
        lines.append(cur)
    return lines

def svg(W, H, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" fill="none" role="img" aria-label="{label}">\n'
            f'{CSS}{body}</svg>\n')

# -------------------------------------------------------------------- stack
STACK = [
    ('LANGUAGES', [('Python', 'python'), ('TypeScript', 'typescript'),
                   ('JavaScript', 'javascript'), ('C++', 'cplusplus'), ('SQL', 'postgresql')]),
    ('FRONTEND',  [('React', 'react'), ('Next.js', 'nextdotjs'), ('Tailwind', 'tailwindcss')]),
    ('BACKEND',   [('Node.js', 'nodedotjs'), ('Express', 'express'), ('FastAPI', 'fastapi'),
                   ('Socket.IO', 'socketdotio'), ('WebRTC', 'webrtc')]),
    ('AI / ML',   [('PyTorch', 'pytorch'), ('LangChain', 'langchain'), ('pgvector', 'postgresql'),
                   ('Gemini', 'googlegemini')]),
    ('DATA',      [('PostgreSQL', 'postgresql'), ('MongoDB', 'mongodb'), ('Redis', 'redis'),
                   ('Supabase', 'supabase'), ('Kafka', 'apachekafka'), ('Airflow', 'apacheairflow')]),
    ('INFRA',     [('Docker', 'docker'), ('GitHub Actions', 'githubactions'), ('n8n', 'n8n'),
                   ('Cloudflare', 'cloudflare'), ('Linux', 'linux')]),
]

def render_stack(theme):
    c = TH[theme]; W = 880; top = 62; row = 40
    H = top + row * len(STACK) + 14
    b = f'  <rect class="f" x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="6" fill="none" stroke="{c["hair"]}"/>\n'
    b += '  <g class="f d1">\n'
    b += path('700', 'DAILY DRIVERS', 11, 22, 30, c['muted'], 3.0)
    rt = 'grouped by layer'
    b += path('400', rt, 11, W - measure('400', rt, 11, .3) - 22, 30, c['faint'], .3)
    b += '  </g>\n'
    b += f'  <line class="f d1" x1="22" y1="44" x2="{W-22}" y2="44" stroke="{c["hair"]}"/>\n'
    for i, (label, items) in enumerate(STACK):
        y = top + i * row
        b += f'  <g class="rise d{min(7, i + 2)}">\n'
        b += path('500', label, 8.5, 22, y + 17, c['muted'], 1.3)
        x = 132
        for name, key in items:
            s, w = chip(theme, x, y, name, key)
            b += s; x += w + 8
        b += '  </g>\n'
    return svg(W, H, b, 'Tech stack')

# ----------------------------------------------------------------- projects
PROJECTS = [
    dict(slug='jobmatch', name='JobMatch', status='LIVE',
         kicker='SEMANTIC JOB MATCHING',
         desc='Upload a resume, get jobs ranked by meaning, not keywords: '
              'cosine similarity over 768-d embeddings in pgvector, with each '
              "user's rows isolated by Postgres RLS.",
         signal='idempotent ingest: sha256(url) + ON CONFLICT DO NOTHING',
         stack=[('Next.js', 'nextdotjs'), ('FastAPI', 'fastapi'),
                ('pgvector', 'postgresql'), ('Supabase', 'supabase')]),
    dict(slug='marl-maps', name='MARL-MAPS', status='RESEARCH',
         kicker='MULTI-AGENT RL FOR RAG',
         desc='Agents learn when to retrieve instead of retrieving on every hop. '
              'Query, Judge and Answer agents share one frozen 7B base through '
              'role-scoped LoRA adapters.',
         signal='91% fewer redundant retrievals, 60% less VRAM',
         stack=[('PyTorch', 'pytorch'), ('GRPO', None), ('LoRA', None), ('vLLM', None)]),
    dict(slug='clinicq', name='ClinicQ', status='DEPLOYED',
         kicker='WHATSAPP TOKEN QUEUE FOR CLINICS',
         desc='Patients book and track their turn on WhatsApp; the doctor runs '
              'the queue from a PWA. Exactly-once "next patient" under '
              'concurrency, webhook replays deduped by message id.',
         signal='164 tests, 0 skipped · SELECT ... FOR UPDATE',
         stack=[('FastAPI', 'fastapi'), ('PostgreSQL', 'postgresql'),
                ('Docker', 'docker'), ('Gemini', 'googlegemini')]),
    dict(slug='data-pipeline', name='Multi-Tenant Pipeline', status='OPEN SOURCE',
         kicker='CONFIG-DRIVEN ETL + LLM AGENT',
         desc='Isolated per-tenant ETL pipelines built from config, plus a '
              'hand-rolled LLM agent (no framework) that classifies failures '
              'and picks a recovery path.',
         signal='failures triaged by an agent, not a pager',
         stack=[('Airflow', 'apacheairflow'), ('Python', 'python'), ('Docker', 'docker')]),
    dict(slug='interview-platform', name='AI Interview Platform', status='TEAM',
         kicker='AI INTERVIEWS + PEER MOCKS',
         desc='My part: a sandboxed code runner (Docker, no network, CPU / RAM / '
              'pid caps, 5 s limit) behind a BullMQ queue, and 1:1 WebRTC '
              'interview rooms over Socket.IO signalling.',
         signal='I own code execution and the realtime layer',
         stack=[('Node.js', 'nodedotjs'), ('Redis', 'redis'),
                ('Docker', 'docker'), ('WebRTC', 'webrtc')]),
    dict(slug='memorylane', name='MemoryLane', status='OPEN SOURCE',
         kicker='DIGITAL TIME CAPSULES',
         desc='Letters, photos, video and music, sealed until a date you choose '
              'and opened together when it arrives.',
         signal='full MERN build, schema to UI',
         stack=[('React', 'react'), ('Node.js', 'nodedotjs'),
                ('Express', 'express'), ('MongoDB', 'mongodb')]),
]

def pill(theme, label, right, y):
    c = TH[theme]; live = label in ('LIVE', 'DEPLOYED')
    col = ACCENT[theme] if live else c['muted']
    tw = measure('700', label, 8.5, 1.3)
    w = tw + (30 if live else 20); x = right - w
    out = f'  <rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="20" rx="10" fill="none" stroke="{col}"/>\n'
    tx = x + 10
    if live:
        out += f'  <circle cx="{x + 12:.1f}" cy="{y + 10}" r="3" fill="{col}"/>\n'
        tx += 10
    out += path('700', label, 8.5, tx, y + 13.5, col, 1.3)
    return out

def render_card(theme, p):
    c = TH[theme]; W, H = 440, 214
    b = f'  <rect class="f" x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" fill="none" stroke="{c["hair"]}"/>\n'
    b += '  <g class="rise d1">\n'
    b += path('800', p['name'], 17, 22, 38, c['fg'], .2)
    b += pill(theme, p['status'], W - 20, 22)
    b += path('500', p['kicker'], 8.5, 22, 58, c['muted'], 1.3)
    b += '  </g>\n'
    b += '  <g class="f d3">\n'
    for i, line in enumerate(wrap(p['desc'], 11, W - 44)[:3]):
        b += path('400', line, 11, 22, 84 + i * 17, BODY[theme])
    b += '  </g>\n'
    if p['signal']:
        b += '  <g class="f d4">\n'
        b += path('700', '>', 10.5, 22, 146, ACCENT[theme])
        b += path('500', p['signal'], 10.5, 36, 146, c['muted'])
        b += '  </g>\n'
    b += '  <g class="f d5">\n'
    x = 22
    for name, key in p['stack']:
        s, w = chip(theme, x, 166, name, key, h=24, size=10, pad=9, isz=12)
        b += s; x += w + 6
    b += '  </g>\n'
    return svg(W, H, b, f'{p["name"]}: {p["kicker"].lower()}')

# --------------------------------------------------------------------- main
if __name__ == '__main__':
    for theme, sub in (('light', ''), ('dark', 'dark')):
        d = os.path.join(ROOT, 'assets', sub)
        open(os.path.join(d, 'stack.svg'), 'w').write(render_stack(theme))
        for p in PROJECTS:
            open(os.path.join(d, f'p-{p["slug"]}.svg'), 'w').write(render_card(theme, p))
    print('stack.svg and', len(PROJECTS), 'project cards written (light + dark)')
