"""Generate the README SVG assets (banner, project cards, tech stack) in light and dark variants.

Run from anywhere:  python scripts/gen_assets.py
Output goes to assets/. Edit the data at the top of each section (PROJECTS, STACK, phrases) and re-run.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
SANS = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'Cascadia Code','JetBrains Mono','Fira Code',SFMono-Regular,Consolas,Menlo,monospace"

THEMES = {
    "dark": dict(
        bg="#0c0e12", surface="#14171d", panel="#0a0c10",
        border="#ffffff", border_op="0.11",
        text="#f4f5f7", muted="#aab2bd", dim="#737b86",
        accent="#ffb224", accent_fill_op="0.14", accent_line_op="0.55",
        green="#4ade80", dot="#ffffff", dot_op="0.08", glow_op="0.16",
        chip_fill="#ffffff", chip_fill_op="0.05",
    ),
    "light": dict(
        bg="#f8f5ee", surface="#ffffff", panel="#1b1d22",
        border="#15171c", border_op="0.13",
        text="#15171c", muted="#4f5763", dim="#8a919c",
        accent="#b35a00", accent_fill_op="0.10", accent_line_op="0.55",
        green="#15803d", dot="#15171c", dot_op="0.09", glow_op="0.10",
        chip_fill="#15171c", chip_fill_op="0.035",
    ),
}
# text colours used INSIDE the terminal panel (panel is always dark)
TERM = dict(text="#e9ecf1", muted="#9aa3ae", dim="#5d6672", accent="#ffb224", green="#4ade80")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(v):
    return ("%.4f" % v).rstrip("0").rstrip(".")


# ---------- typing helpers ----------
def typing_cycle(phrases, cps=16, hold=2.2, erase_cps=40, gap=0.45):
    """Return (total, events[(t, nchars, idx)]) for a looping type/erase cycle."""
    ev, t = [], 0.0
    for i, p in enumerate(phrases):
        n = len(p)
        for k in range(n + 1):
            ev.append((t, k, i)); t += 1.0 / cps
        t += hold
        for k in range(n - 1, -1, -1):
            ev.append((t, k, i)); t += 1.0 / erase_cps
        t += gap
    return t, ev


def discrete_anim(attr, pairs, total, begin="0s", repeat="indefinite", extra=""):
    """pairs: [(t, value)] -> <animate calcMode=discrete>"""
    vals = ";".join(fmt(v) if isinstance(v, (int, float)) else v for _, v in pairs)
    keys = ";".join(fmt(t / total) for t, _ in pairs)
    return (f'<animate attributeName="{attr}" calcMode="discrete" values="{vals}" keyTimes="{keys}" '
            f'dur="{fmt(total)}s" begin="{begin}" repeatCount="{repeat}" {extra}/>')


def typed_tagline(x, y, phrases, size, cw, color, cursor_color, prefix_id):
    total, ev = typing_cycle(phrases)
    ev_closed = ev + [(total, ev[-1][1], ev[-1][2])]
    width_pairs = [(t, k * cw) for t, k, _ in ev_closed]
    cur_pairs = [(t, x + k * cw + 2) for t, k, _ in ev_closed]
    # which phrase visible
    vis = {i: [] for i in range(len(phrases))}
    last = None
    for t, k, i in ev_closed:
        if i != last:
            for j in vis:
                vis[j].append((t, 1 if j == i else 0))
            last = i
    for j in vis:
        vis[j].append((total, vis[j][-1][1]))
    out = [f'<clipPath id="{prefix_id}clip"><rect x="{x}" y="{y - size}" width="0" height="{size * 1.4}">'
           + discrete_anim("width", width_pairs, total) + '</rect></clipPath>']
    out.append(f'<g clip-path="url(#{prefix_id}clip)" font-family="{MONO}" font-size="{size}" fill="{color}">')
    for i, p in enumerate(phrases):
        out.append(f'<text x="{x}" y="{y}" textLength="{fmt(len(p) * cw)}" lengthAdjust="spacingAndGlyphs" opacity="0">{esc(p)}'
                   + discrete_anim("opacity", vis[i], total) + '</text>')
    out.append('</g>')
    out.append(f'<rect x="{x + 2}" y="{y - size * 0.82}" width="{size * 0.5}" height="{size * 1.0}" rx="1.5" fill="{cursor_color}">'
               + discrete_anim("x", cur_pairs, total)
               + '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" calcMode="discrete" dur="1.1s" repeatCount="indefinite"/>'
               + '</rect>')
    return "\n".join(out)


# ---------- common chrome ----------
def dots_pattern(t, pid="dots"):
    return (f'<pattern id="{pid}" width="26" height="26" patternUnits="userSpaceOnUse">'
            f'<circle cx="1.5" cy="1.5" r="1.3" fill="{t["dot"]}" fill-opacity="{t["dot_op"]}"/></pattern>')


def chip(x, y, label, t, h=30, size=15, pad=16, mono=False, accent=False):
    cwid = size * (0.62 if mono else 0.56)
    w = int(len(label) * cwid + pad * 2)
    fam = MONO if mono else SANS
    fill = t["accent"] if accent else t["chip_fill"]
    fop = t["accent_fill_op"] if accent else t["chip_fill_op"]
    stroke = t["accent"] if accent else t["border"]
    sop = t["accent_line_op"] if accent else t["border_op"]
    txt = t["accent"] if accent else t["text"]
    svg = (f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{fill}" fill-opacity="{fop}" '
           f'stroke="{stroke}" stroke-opacity="{sop}"/>'
           f'<text x="{x + w / 2}" y="{y + h / 2 + size * 0.36}" font-family="{fam}" font-size="{size}" font-weight="600" '
           f'fill="{txt}" text-anchor="middle">{esc(label)}</text></g>')
    return svg, w


# ---------- BANNER ----------
def banner(theme):
    t = THEMES[theme]
    W, H = 1200, 300
    phrases = ["full-stack developer", "backend & API builder", "AI-powered web apps", "open to internships"]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Saumya Tiwari, full-stack developer and third-year B.Tech CS student at KIET Delhi, open to software, full-stack and backend internships">',
         '<defs>', dots_pattern(t),
         f'<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow_op"]}"/>'
         f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>',
         f'<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/>'
         f'<stop offset="0.5" stop-color="{t["accent"]}" stop-opacity="0.9"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></linearGradient>',
         f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>',
         '</defs>',
         '<g clip-path="url(#frame)">',
         f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>',
         f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
         # soft moving light, top-left
         f'<circle cx="120" cy="40" r="420" fill="url(#glow)"><animate attributeName="cx" values="120;260;120" dur="14s" repeatCount="indefinite"/>'
         f'<animate attributeName="cy" values="40;120;40" dur="18s" repeatCount="indefinite"/></circle>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{t["border"]}" stroke-opacity="{t["border_op"]}"/>',
         # bottom accent rule with a sweeping highlight
         f'<rect x="0" y="{H - 3}" width="{W}" height="3" fill="{t["accent"]}" fill-opacity="0.25"/>',
         f'<rect x="-400" y="{H - 3}" width="400" height="3" fill="url(#sweep)"><animate attributeName="x" values="-400;{W}" dur="5s" repeatCount="indefinite"/></rect>',
         ]
    # ---- left column ----
    x = 64
    o.append(f'<text x="{x}" y="88" font-family="{MONO}" font-size="14" letter-spacing="3" fill="{t["accent"]}" font-weight="700">HELLO, I AM</text>')
    o.append(f'<text x="{x}" y="146" font-family="{SANS}" font-size="58" font-weight="800" letter-spacing="-1.5" fill="{t["text"]}">Saumya Tiwari</text>')
    # prompt + typed tagline
    o.append(f'<text x="{x}" y="196" font-family="{MONO}" font-size="24" font-weight="700" fill="{t["accent"]}">&gt;</text>')
    o.append(typed_tagline(x + 26, 196, phrases, 24, 14.4, t["text"], t["accent"], "tl"))
    # meta line
    o.append(f'<text x="{x}" y="243" font-family="{SANS}" font-size="17" fill="{t["muted"]}">3rd-year B.Tech CS · KIET, Delhi · AWS Certified Cloud Practitioner</text>')
    # ---- right: terminal panel ----
    px, py, pw, ph = 690, 40, 446, 220
    o.append(f'<g transform="translate({px} {py})">')
    o.append(f'<rect width="{pw}" height="{ph}" rx="14" fill="{t["panel"]}" stroke="{"#ffffff" if theme == "dark" else "#15171c"}" stroke-opacity="{"0.14" if theme == "dark" else "0.35"}"/>')
    o.append(f'<rect width="{pw}" height="36" rx="14" fill="#ffffff" fill-opacity="0.04"/><rect y="24" width="{pw}" height="12" fill="#ffffff" fill-opacity="0.04"/>')
    o.append('<circle cx="20" cy="18" r="5.5" fill="#ff5f57"/><circle cx="38" cy="18" r="5.5" fill="#febc2e"/><circle cx="56" cy="18" r="5.5" fill="#28c840"/>')
    o.append(f'<text x="{pw / 2}" y="22" font-family="{MONO}" font-size="12" fill="{TERM["dim"]}" text-anchor="middle">saumya@dev — zsh</text>')
    lines = [
        ("cmd", "whoami", 0.3),
        ("out", "saumya-st · builds web apps end to end", None),
        ("cmd", "cat focus.txt", 2.4),
        ("out", "React · Next.js · Node · PostgreSQL · Python", None),
        ("cmd", "status --now", 4.6),
        ("ok", "open to software & backend internships", None),
        ("prompt", "", 6.6),
    ]
    ly, lh, fs, cw = 62, 27, 15.5, 9.3
    tx = 22
    for kind, text, begin in lines:
        if kind == "cmd":
            dur = max(0.25, len(text) / 22)
            cid = f"c{int(begin * 10)}"
            o.append(f'<text x="{tx}" y="{ly}" font-family="{MONO}" font-size="{fs}" fill="{TERM["accent"]}" font-weight="700" opacity="0">$'
                     f'<animate attributeName="opacity" values="0;1" dur="0.01s" begin="{begin}s" fill="freeze"/></text>')
            o.append(f'<clipPath id="{cid}"><rect x="{tx + 16}" y="{ly - fs}" width="0" height="{fs * 1.4}">'
                     f'<animate attributeName="width" values="0;{fmt(len(text) * cw + 4)}" dur="{fmt(dur)}s" begin="{begin}s" calcMode="linear" fill="freeze"/></rect></clipPath>')
            o.append(f'<text clip-path="url(#{cid})" x="{tx + 16}" y="{ly}" font-family="{MONO}" font-size="{fs}" fill="{TERM["text"]}" '
                     f'textLength="{fmt(len(text) * cw)}" lengthAdjust="spacingAndGlyphs">{esc(text)}</text>')
            last_end = begin + dur
        elif kind in ("out", "ok"):
            col = TERM["green"] if kind == "ok" else TERM["muted"]
            b = last_end + 0.25
            prefix = ""
            if kind == "ok":
                o.append(f'<circle cx="{tx + 6}" cy="{ly - 5}" r="4" fill="{TERM["green"]}" opacity="0">'
                         f'<animate attributeName="opacity" values="0;1" dur="0.01s" begin="{fmt(b)}s" fill="freeze"/>'
                         f'<animate attributeName="r" values="4;5.5;4" dur="1.8s" begin="{fmt(b)}s" repeatCount="indefinite"/></circle>')
                prefix_x = tx + 18
            else:
                prefix_x = tx
            o.append(f'<text x="{prefix_x}" y="{ly}" font-family="{MONO}" font-size="{fs}" fill="{col}" opacity="0">{esc(text)}'
                     f'<animate attributeName="opacity" values="0;1" dur="0.35s" begin="{fmt(b)}s" fill="freeze"/></text>')
        else:  # prompt + blinking cursor
            o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.01s" begin="{begin}s" fill="freeze"/>'
                     f'<text x="{tx}" y="{ly}" font-family="{MONO}" font-size="{fs}" fill="{TERM["accent"]}" font-weight="700">$</text>'
                     f'<rect x="{tx + 16}" y="{ly - fs * 0.85}" width="9" height="{fs * 1.05}" fill="{TERM["text"]}">'
                     f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" calcMode="discrete" dur="1.1s" repeatCount="indefinite"/></rect></g>')
        ly += lh
    o.append('</g>')
    o.append('</g></svg>')
    return "\n".join(o)


# ---------- CARD MOTIFS (each ~110x70, origin top-left) ----------
def motif_kanban(t):
    a = t["accent"]; bar = t["dim"]
    cols = [0, 38, 76]
    o = []
    for cx in cols:
        o.append(f'<rect x="{cx}" y="0" width="32" height="70" rx="6" fill="{t["chip_fill"]}" fill-opacity="{t["chip_fill_op"]}" stroke="{t["border"]}" stroke-opacity="{t["border_op"]}"/>')
    # static bars
    for (cx, y) in [(0, 10), (0, 24), (38, 10), (76, 10), (76, 24), (76, 38)]:
        o.append(f'<rect x="{cx + 6}" y="{y}" width="20" height="8" rx="3" fill="{bar}" fill-opacity="0.55"/>')
    # moving card: col0 slot3 -> col1 slot2 -> col2 slot4 -> back
    o.append(f'<rect x="6" y="38" width="20" height="8" rx="3" fill="{a}">'
             '<animate attributeName="x" values="6;6;44;44;82;82;6" keyTimes="0;0.2;0.3;0.55;0.65;0.9;1" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;0.4 0 0.2 1;0 0 1 1;0.4 0 0.2 1;0 0 1 1;0.4 0 0.2 1"/>'
             '<animate attributeName="y" values="38;38;24;24;52;52;38" keyTimes="0;0.2;0.3;0.55;0.65;0.9;1" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;0.4 0 0.2 1;0 0 1 1;0.4 0 0.2 1;0 0 1 1;0.4 0 0.2 1"/>'
             '</rect>')
    return "\n".join(o)


def motif_sync(t):
    a = t["accent"]; ln = t["dim"]
    o = [
        # phone
        f'<rect x="2" y="14" width="26" height="44" rx="6" fill="none" stroke="{ln}" stroke-width="2"/>',
        f'<rect x="10" y="20" width="10" height="2" rx="1" fill="{ln}"/>',
        # cloud
        f'<path d="M80 50h18a9 9 0 0 0 1-18 13 13 0 0 0-25-3 8 8 0 0 0 6 21z" fill="none" stroke="{ln}" stroke-width="2" stroke-linejoin="round"/>',
        # dashed link
        f'<line x1="32" y1="36" x2="70" y2="36" stroke="{ln}" stroke-opacity="0.5" stroke-width="2" stroke-dasharray="3 5"/>',
    ]
    for i in range(3):
        o.append(f'<circle cx="32" cy="36" r="3.2" fill="{a}" opacity="0">'
                 f'<animate attributeName="cx" values="32;70" dur="2.4s" begin="{i * 0.8}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" dur="2.4s" begin="{i * 0.8}s" repeatCount="indefinite"/></circle>')
    # cloud "received" pulse
    o.append(f'<circle cx="88" cy="42" r="3" fill="{a}"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.4s" repeatCount="indefinite"/></circle>')
    return "\n".join(o)


def motif_timer(t):
    a = t["accent"]; ln = t["dim"]
    C = 2 * 3.14159 * 26
    o = [
        f'<circle cx="34" cy="35" r="26" fill="none" stroke="{ln}" stroke-opacity="0.35" stroke-width="5"/>',
        f'<circle cx="34" cy="35" r="26" fill="none" stroke="{a}" stroke-width="5" stroke-linecap="round" '
        f'stroke-dasharray="{fmt(C)}" stroke-dashoffset="{fmt(C)}" transform="rotate(-90 34 35)">'
        f'<animate attributeName="stroke-dashoffset" values="{fmt(C)};0;0;{fmt(C)}" keyTimes="0;0.8;0.92;1" dur="8s" repeatCount="indefinite"/></circle>',
        f'<text x="34" y="40" font-family="{MONO}" font-size="13" font-weight="700" fill="{t["text"]}" text-anchor="middle">25:00</text>',
    ]
    # streak bars
    for i, h in enumerate([14, 22, 18, 30, 26]):
        x = 72 + i * 8
        o.append(f'<rect x="{x}" y="{62 - h}" width="5" height="{h}" rx="2" fill="{a if i == 4 else ln}" fill-opacity="{1 if i == 4 else 0.55}">'
                 f'<animate attributeName="height" values="0;{h}" dur="0.6s" begin="{0.15 * i}s" fill="freeze"/>'
                 f'<animate attributeName="y" values="62;{62 - h}" dur="0.6s" begin="{0.15 * i}s" fill="freeze"/></rect>')
    return "\n".join(o)


ICONS = {
    "kanban": '<rect x="0" y="0" width="7" height="22" rx="2"/><rect x="9.5" y="0" width="7" height="14" rx="2"/><rect x="19" y="0" width="5" height="18" rx="2"/>',
    "pin": '<path d="M12 23s9-8.4 9-14A9 9 0 0 0 3 9c0 5.6 9 14 9 14z"/><circle cx="12" cy="9" r="3"/>',
    "book": '<path d="M2 2h8a4 4 0 0 1 4 4v16a3 3 0 0 0-3-3H2z"/><path d="M24 2h-8a4 4 0 0 0-4 4v16a3 3 0 0 1 3-3h9z"/>',
}

PROJECTS = [
    dict(slug="karyaa", name="Karya", label="TASK MANAGEMENT", icon="kanban", live=True, motif=motif_kanban,
         desc=["Team projects, kanban boards, invites", "and Google Calendar sync. JWT sessions", "and server-side role checks."],
         chips=["Next.js", "Prisma", "Postgres", "JWT"],
         alt="Karya: team task management with JWT auth, role checks, kanban and Google Calendar sync"),
    dict(slug="jansewa-project", name="Jansewa", label="CIVIC TECH", icon="pin", live=False, motif=motif_sync,
         desc=["Offline-first civic issue reporting.", "Reports queue in IndexedDB and sync to", "Firestore. Gemini predicts priority."],
         chips=["React", "Firebase", "Supabase", "Gemini"],
         alt="Jansewa: offline-first civic issue reporting with Firestore sync and Gemini priority prediction"),
    dict(slug="study-assis", name="AI Study Coach", label="AI PLANNER", icon="book", live=True, motif=motif_timer,
         desc=["Time-blocked study schedules from Groq,", "focus sessions logged in SQLite,", "streaks, trends and CSV export."],
         chips=["Python", "Streamlit", "SQLite", "Groq"],
         alt="AI Study Coach: time-blocked study schedules from Groq with SQLite streak tracking and CSV export"),
]


def card(p, theme):
    t = THEMES[theme]
    W, H = 380, 262
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(p["alt"])}">',
         f'<defs><clipPath id="f"><rect width="{W}" height="{H}" rx="18"/></clipPath>{dots_pattern(t)}</defs>',
         '<g clip-path="url(#f)">',
         f'<rect width="{W}" height="{H}" fill="{t["surface"]}"/>',
         f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{t["border"]}" stroke-opacity="{t["border_op"]}"/>',
         # left accent bar that grows in
         f'<rect x="0" y="24" width="4" height="0" rx="2" fill="{t["accent"]}"><animate attributeName="height" values="0;54" dur="0.7s" begin="0.2s" fill="freeze" calcMode="spline" keySplines="0.2 0 0.2 1"/></rect>',
         # icon tile
         f'<rect x="24" y="26" width="46" height="46" rx="12" fill="{t["accent"]}" fill-opacity="{t["accent_fill_op"]}" stroke="{t["accent"]}" stroke-opacity="{t["accent_line_op"]}"/>',
         f'<g transform="translate(35 37)" stroke="{t["accent"]}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">{ICONS[p["icon"]]}</g>',
         f'<text x="84" y="48" font-family="{SANS}" font-size="23" font-weight="800" letter-spacing="-0.3" fill="{t["text"]}">{esc(p["name"])}</text>',
         f'<text x="84" y="68" font-family="{MONO}" font-size="11.5" letter-spacing="2" font-weight="700" fill="{t["accent"]}">{esc(p["label"])}</text>',
         f'<g transform="translate(252 16)">{p["motif"](t)}</g>',
         ]
    y = 118
    for line in p["desc"]:
        o.append(f'<text x="24" y="{y}" font-family="{SANS}" font-size="16.5" fill="{t["muted"]}">{esc(line)}</text>')
        y += 24
    cx = 24
    for i, c in enumerate(p["chips"]):
        s, w = chip(cx, 200, c, t, h=28, size=13.5, pad=12, mono=True)
        o.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.4s" begin="{fmt(0.3 + i * 0.12)}s" fill="freeze"/>{s}</g>')
        cx += w + 7
    if p["live"]:
        o.append(f'<g transform="translate({W - 24 - 62} {H - 34})"><rect width="62" height="24" rx="12" fill="{t["green"]}" fill-opacity="0.14" stroke="{t["green"]}" stroke-opacity="0.6"/>'
                 f'<circle cx="13" cy="12" r="3.5" fill="{t["green"]}"><animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></circle>'
                 f'<text x="39" y="16" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{t["green"]}" text-anchor="middle">LIVE</text></g>')
    o.append(f'<text x="24" y="{H - 18}" font-family="{MONO}" font-size="11.5" fill="{t["dim"]}">github.com/saumya-st/{esc(p["slug"].upper() if p["slug"] != "karyaa" else "Karyaa")}</text>')
    o.append('</g></svg>')
    return "\n".join(o)


# ---------- STACK ----------
STACK = [
    ("FRONTEND", ["React", "Next.js", "TypeScript", "Tailwind CSS", "Vite", "Streamlit"]),
    ("BACKEND", ["Node.js", "Server Actions", "NextAuth · JWT", "Zod", "Python", "Java"]),
    ("DATABASES", ["PostgreSQL", "Prisma", "Firestore", "SQLite", "Supabase Storage", "IndexedDB"]),
    ("CLOUD & AI", ["AWS · Certified", "Vercel", "Streamlit Cloud", "GitHub Actions", "Docker", "Gemini API", "Groq API"]),
]


def stack(theme):
    t = THEMES[theme]
    W, rows = 1200, len(STACK)
    top, rh = 30, 58
    H = top * 2 + rows * rh - 16
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack">',
         f'<defs><clipPath id="f"><rect width="{W}" height="{H}" rx="18"/></clipPath>{dots_pattern(t)}</defs>',
         '<g clip-path="url(#f)">',
         f'<rect width="{W}" height="{H}" fill="{t["surface"]}"/>',
         f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{t["border"]}" stroke-opacity="{t["border_op"]}"/>',
         ]
    n = 0
    for r, (label, items) in enumerate(STACK):
        y = top + r * rh
        o.append(f'<text x="36" y="{y + 21}" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="2.5" fill="{t["accent"]}">{esc(label)}</text>')
        if r < rows - 1:
            o.append(f'<line x1="36" y1="{y + rh - 10}" x2="{W - 36}" y2="{y + rh - 10}" stroke="{t["border"]}" stroke-opacity="{float(t["border_op"]) * 0.6}"/>')
        x = 210
        for it in items:
            s, w = chip(x, y, it, t, h=34, size=16, pad=17)
            d = 0.15 + n * 0.06
            o.append(f'<g opacity="0" transform="translate(0 8)"><animate attributeName="opacity" values="0;1" dur="0.45s" begin="{fmt(d)}s" fill="freeze"/>'
                     f'<animateTransform attributeName="transform" type="translate" values="0 8;0 0" dur="0.45s" begin="{fmt(d)}s" fill="freeze" calcMode="spline" keySplines="0.2 0 0.2 1"/>{s}</g>')
            x += w + 10
            n += 1
    o.append('</g></svg>')
    return "\n".join(o)


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(name, len(content.encode()), "bytes")


if __name__ == "__main__":
    for th in THEMES:
        write(f"banner-{th}.svg", banner(th))
        write(f"stack-{th}.svg", stack(th))
        for p in PROJECTS:
            write(f"card-{p['slug']}-{th}.svg", card(p, th))
