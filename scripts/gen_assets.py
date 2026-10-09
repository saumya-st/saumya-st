"""Generate the README banner (assets/banner-light.svg and assets/banner-dark.svg).

Run from anywhere:  python scripts/gen_assets.py
Edit NODES, NAME or TAGLINE below and re-run. No external fonts or scripts are used,
so the SVG animates inside GitHub's <img> sandbox.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
SANS = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"

NAME = "Saumya Tiwari"
TAGLINE = "Full-stack developer. Third-year B.Tech CS, KIET Delhi."
STATUS = "Open to software, full-stack and backend internships"

# Whimsical-style pastel nodes: (label, light fill, light text, dark fill, dark text)
NODES = [
    ("idea",  "#fff1b8", "#7a5a00", "#4a3f12", "#ffe28a"),
    ("build", "#d6e8ff", "#174a8c", "#1d3557", "#a9ccff"),
    ("test",  "#d9f5e3", "#0f6b3a", "#143d2a", "#9fe0b8"),
    ("ship",  "#ffdcec", "#8c1d55", "#4a1d35", "#ffb3d3"),
]

THEMES = {
    "light": dict(bg="#fcfcfa", text="#1f2328", muted="#636c76", line="#1f2328", status="#1a7f37", edge="#d0d7de"),
    "dark":  dict(bg="#0d1117", text="#e6edf3", muted="#8d96a0", line="#c9d1d9", status="#3fb950", edge="#30363d"),
}


def fmt(v):
    return ("%.3f" % v).rstrip("0").rstrip(".")


def banner(theme):
    t = THEMES[theme]
    W, H = 1200, 260
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="{NAME}. {TAGLINE} {STATUS}.">',
         f'<rect width="{W}" height="{H}" rx="16" fill="{t["bg"]}"/>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{t["edge"]}"/>']

    # ---- left: words ----
    x = 56
    o.append(f'<text x="{x}" y="112" font-family="{SANS}" font-size="52" font-weight="700" letter-spacing="-1" fill="{t["text"]}">{NAME}</text>')
    o.append(f'<text x="{x}" y="152" font-family="{SANS}" font-size="19" fill="{t["muted"]}">{TAGLINE}</text>')
    o.append(f'<circle cx="{x + 6}" cy="190" r="5" fill="{t["status"]}">'
             f'<animate attributeName="r" values="5;6.5;5" dur="2.4s" repeatCount="indefinite"/></circle>')
    o.append(f'<text x="{x + 20}" y="196" font-family="{SANS}" font-size="17" font-weight="600" fill="{t["text"]}">{STATUS}</text>')

    # ---- right: hand-laid flowchart that draws itself ----
    nw, nh, gap = 112, 52, 46
    start_x, cy = 570, 136
    centers = []
    for i, (label, lf, lt, df, dt) in enumerate(NODES):
        nx = start_x + i * (nw + gap)
        fill, col = (lf, lt) if theme == "light" else (df, dt)
        delay = 0.25 + i * 0.75
        cx = nx + nw / 2
        centers.append(cx)
        # tiny offset per node so the row feels placed by hand, not snapped
        dy = [0, -8, 6, -4][i]
        o.append(f'<g transform="translate({cx} {cy + dy})">'
                 f'<g opacity="0" transform="scale(0.6)">'
                 f'<animate attributeName="opacity" values="0;1" dur="0.35s" begin="{fmt(delay)}s" fill="freeze"/>'
                 f'<animateTransform attributeName="transform" type="scale" values="0.6;1.06;1" keyTimes="0;0.7;1" dur="0.45s" begin="{fmt(delay)}s" fill="freeze" calcMode="spline" keySplines="0.2 0 0.3 1;0.4 0 0.6 1"/>'
                 f'<rect x="{-nw / 2}" y="{-nh / 2}" width="{nw}" height="{nh}" rx="14" fill="{fill}"/>'
                 f'<text y="7" font-family="{SANS}" font-size="20" font-weight="600" fill="{col}" text-anchor="middle">{label}</text>'
                 f'</g></g>')
        if i > 0:
            # connector from previous node to this one, drawn in just before the node pops
            x1 = centers[i - 1] + nw / 2 + 4
            x2 = nx - 4
            y1 = cy + [0, -8, 6, -4][i - 1]
            y2 = cy + dy
            mid = (x1 + x2) / 2
            path = f"M{fmt(x1)} {y1} C{fmt(mid)} {y1} {fmt(mid)} {y2} {fmt(x2)} {y2}"
            o.append(f'<path d="{path}" fill="none" stroke="{t["line"]}" stroke-width="2.5" stroke-linecap="round" '
                     f'stroke-dasharray="60" stroke-dashoffset="60">'
                     f'<animate attributeName="stroke-dashoffset" values="60;0" dur="0.4s" begin="{fmt(delay - 0.35)}s" fill="freeze"/></path>')
            o.append(f'<path d="M{fmt(x2 - 9)} {y2 - 6} L{fmt(x2)} {y2} L{fmt(x2 - 9)} {y2 + 6}" fill="none" stroke="{t["line"]}" stroke-width="2.5" '
                     f'stroke-linecap="round" stroke-linejoin="round" opacity="0">'
                     f'<animate attributeName="opacity" values="0;1" dur="0.15s" begin="{fmt(delay - 0.05)}s" fill="freeze"/></path>')
    # after everything is drawn, a loop arrow from ship back to idea (iterate)
    lx1, lx2 = centers[-1], centers[0]
    top = cy - nh / 2 - 36
    loop = f"M{fmt(lx1)} {cy - nh / 2 - 4 - 4} C{fmt(lx1)} {top} {fmt(lx2)} {top} {fmt(lx2)} {cy - nh / 2 - 8 - 4}"
    o.append(f'<path d="{loop}" fill="none" stroke="{t["line"]}" stroke-width="2" stroke-linecap="round" stroke-dasharray="6 7" opacity="0">'
             f'<animate attributeName="opacity" values="0;0.75" dur="0.5s" begin="3.4s" fill="freeze"/>'
             f'<animate attributeName="stroke-dashoffset" values="0;-26" dur="1.2s" begin="3.4s" repeatCount="indefinite"/></path>')
    o.append(f'<path d="M{fmt(lx2 - 6)} {cy - nh / 2 - 22} L{fmt(lx2)} {cy - nh / 2 - 12} L{fmt(lx2 + 6)} {cy - nh / 2 - 22}" fill="none" stroke="{t["line"]}" '
             f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0">'
             f'<animate attributeName="opacity" values="0;0.75" dur="0.3s" begin="3.6s" fill="freeze"/></path>')
    o.append(f'<text x="{fmt((lx1 + lx2) / 2)}" y="{top - 2}" font-family="{SANS}" font-size="13" fill="{t["muted"]}" text-anchor="middle" opacity="0">repeat'
             f'<animate attributeName="opacity" values="0;1" dur="0.4s" begin="3.7s" fill="freeze"/></text>')
    o.append('</svg>')
    return "\n".join(o)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for th in THEMES:
        path = os.path.join(OUT, f"banner-{th}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(banner(th))
        print(os.path.basename(path), os.path.getsize(path), "bytes")
