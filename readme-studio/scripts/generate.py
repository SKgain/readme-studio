#!/usr/bin/env python3
# readme-studio/scripts/generate.py
"""
Generate a designed GitHub README from one profile.json.

Usage:
    python3 generate.py profile.json OUT_DIR [--theme NAME]
    python3 generate.py --themes                 list available themes

Writes:
    OUT_DIR/README.md
    OUT_DIR/assets/hero-{dark,light}.svg         animated hero (pipeline + optional "now" card)
    OUT_DIR/assets/stack-{dark,light}.svg        layered stack panel   (if "stack")
    OUT_DIR/assets/graph-{dark,light}.svg        Neo4j-style graph     (if "graph")
    OUT_DIR/assets/btn-<slug>-{dark,light}.svg   link buttons          (if "links")
    OUT_DIR/assets/timeline-{dark,light}.svg     career timeline       (if "timeline")
    OUT_DIR/assets/focus-{dark,light}.svg        focus board           (if "focus")
    OUT_DIR/assets/card-<slug>-{dark,light}.svg  project cards         (if "projects_style": "cards")

The theme comes from --theme, else profile.json "theme", else "studio".
Every SVG is self-contained (no external fonts, scripts or images), animates with
CSS only, and respects prefers-reduced-motion. GitHub renders all of it.
"""
import json, math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from themes import FONTS, THEMES  # noqa: E402


# ---------------------------------------------------------------- helpers
def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def sans_w(s, px):
    narrow = sum(1 for ch in s if ch in "ilIjtf.:,;' |!()[]")
    wide = sum(1 for ch in s if ch in "MWmw@")
    return (len(s) - narrow - wide) * px * 0.56 + narrow * px * 0.3 + wide * px * 0.82


def text_w(s, px, kind="sans"):
    """Rough rendered width of text in a font kind (sans, serif or mono)."""
    if kind == "mono":
        return len(s) * px * 0.602
    if kind == "serif":
        return sans_w(s, px) * 1.04
    return sans_w(s, px)


def mix(hex_a, hex_b, t):
    a = [int(hex_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(hex_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def ink_for(fill):
    """Black or white text, whichever contrasts more with the fill (WCAG luminance)."""
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(fill[i:i + 2], 16) for i in (1, 3, 5))
    L = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    return "#0D1117" if (L + 0.05) / 0.05 >= 1.05 / (L + 0.05) else "#FFFFFF"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "link"


def theme(cfg, mode):
    name = cfg.get("theme", "studio")
    if name not in THEMES:
        sys.exit(f'unknown theme "{name}". Available: {", ".join(THEMES)}')
    T = THEMES[name]
    c = dict(T[mode])
    c.update(T["style"])
    c["mode"] = mode
    c["accent"] = cfg.get("accent", {}).get(mode, c["accent"])
    c["accent_soft"] = mix(c["bg"], c["accent"], 0.16 if mode == "dark" else 0.12)
    c["glow"] = c["glow"] and mode == "dark"
    c.setdefault("soft", False)
    c.setdefault("blobs", None)
    for role in ("head", "body", "label", "code"):
        c["f_" + role] = FONTS[c[role]]
    return c


def defs(c, W, H):
    """Shared <defs>: background grid, glow, soft shadow and colour fields, when the theme uses them."""
    d = []
    if c["soft"]:
        col, op = ("#000000", 0.45) if c["mode"] == "dark" else (c["ink"], 0.10)
        d.append(f'    <filter id="soft" x="-20%" y="-30%" width="140%" height="190%">'
                 f'<feDropShadow dx="0" dy="4" stdDeviation="7" flood-color="{col}" flood-opacity="{op}"/></filter>')
    if c["blobs"]:
        for i, col in enumerate(c["blobs"]):
            d.append(f'    <radialGradient id="haze{i}"><stop offset="0" stop-color="{col}" stop-opacity="1"/>'
                     f'<stop offset=".45" stop-color="{col}" stop-opacity=".55"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>')
        d.append(f'    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="{c["rx_panel"]}"/></clipPath>')
    if c["grid"]:
        d.append(f'    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">'
                 f'<path d="M24 0 H0 V24" fill="none" stroke="{c["grid"]}" stroke-width="1"/></pattern>')
    if c["glow"]:
        d.append('    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
                 '<feGaussianBlur stdDeviation="3.5" result="b"/>'
                 '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return d


def glow_attr(c):
    return ' filter="url(#glow)"' if c["glow"] else ""


def panel(c, W, H):
    s = c["stroke"]
    out = [f'  <rect x="{s/2:.2f}" y="{s/2:.2f}" width="{W-s:.2f}" height="{H-s:.2f}" rx="{c["rx_panel"]}" fill="{c["bg"]}"/>']
    if c["blobs"]:
        spots = [(0.10, 0.15, 0.55), (0.88, 0.95, 0.60), (0.55, -0.05, 0.42)]
        moves = [(70, 35), (-80, -30), (40, 45)]
        op = 0.42 if c["mode"] == "dark" else 0.7
        out.append('  <style>')
        for i, (dx, dy) in enumerate(moves):
            out.append(f'    .blob{i} {{ animation: drift{i} {16 + i*4}s ease-in-out infinite alternate; }}')
            out.append(f'    @keyframes drift{i} {{ to {{ transform: translate({dx}px, {dy}px); }} }}')
        out += ['    @media (prefers-reduced-motion: reduce) { .blob0, .blob1, .blob2 { animation: none; } }', '  </style>',
                f'  <g clip-path="url(#frame)" opacity="{op}">']
        for i, ((fx, fy, fr), col) in enumerate(zip(spots, c["blobs"])):
            r = fr * min(W, H) + 160
            out.append(f'    <circle class="blob{i}" cx="{fx*W:.0f}" cy="{fy*H:.0f}" r="{r:.0f}" fill="url(#haze{i})"/>')
        out.append('  </g>')
    if c["grid"]:
        out.append(f'  <rect x="{s/2:.2f}" y="{s/2:.2f}" width="{W-s:.2f}" height="{H-s:.2f}" rx="{c["rx_panel"]}" fill="url(#grid)"/>')
    out.append(f'  <rect x="{s/2:.2f}" y="{s/2:.2f}" width="{W-s:.2f}" height="{H-s:.2f}" rx="{c["rx_panel"]}" fill="none" stroke="{c["edge"]}" stroke-width="{s}"/>')
    return out


def box(c, x, y, w, h, cls, rx, extra=""):
    """A box, with the theme's hard shadow under it when it has one."""
    out = []
    if c["shadow"]:
        sh = min(c["shadow"], 4) if h < 40 else c["shadow"]
        out.append(f'  <rect x="{x+sh:.0f}" y="{y+sh:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{c["edge"]}"{extra}/>')
    soft = ' filter="url(#soft)"' if c["soft"] else ""
    out.append(f'  <rect class="{cls}" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}"{extra}{soft}/>')
    return out


def picture(name, alt):
    return (f'<picture>\n'
            f'  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n'
            f'  <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">\n'
            f'  <img alt="{esc(alt)}" src="assets/{name}-dark.svg" width="100%">\n'
            f'</picture>')


def svg_open(W, H, title, desc, tid):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="{tid}t {tid}d">',
            f'  <title id="{tid}t">{esc(title)}</title>', f'  <desc id="{tid}d">{esc(desc)}</desc>']


# ---------------------------------------------------------------- hero
def hero(cfg, c):
    W, H = 900, 300
    name, tagline = cfg["name"], cfg.get("tagline", "")
    code = c["prompt"] + cfg.get("code_line", "") if cfg.get("code_line") else ""
    now = cfg.get("now")
    pipe = cfg.get("pipeline") or []
    text_max = 540 if now else 804
    hk, bk, ck, lk = c["head"], c["body"], c["code"], c["label"]

    name_px = 40
    while text_w(name, name_px, hk) > text_max and name_px > 24:
        name_px -= 1
    tag_px = 18
    while text_w(tagline, tag_px, bk) > text_max and tag_px > 12:
        tag_px -= 0.5
    code_px = 15
    while text_w(code, code_px, ck) > text_max - 20 and code_px > 11:
        code_px -= 0.5

    desc = f"{name}. {tagline}."
    if pipe:
        desc += " An event travels through " + ", ".join(p["label"] for p in pipe) + "."
    if now:
        desc += " " + now.get("heading", "Now") + ": " + ", ".join(v for v in (now.get("title"), now.get("subtitle")) if v) + "."

    dash = f' stroke-dasharray="{c["dash"]}"' if c["dash"] else ""
    o = svg_open(W, H, name, desc, "h")
    d = defs(c, W, H)
    if d:
        o += ["  <defs>"] + d + ["  </defs>"]
    o += ['  <style>',
          f'    .name {{ font: {c["name_weight"]} {name_px}px {c["f_head"]}; fill: {c["ink"]}; }}',
          f'    .role {{ font: 400 {tag_px}px {c["f_body"]}; fill: {c["muted"]}; }}',
          f'    .code {{ font: 500 {code_px}px {c["f_code"]}; fill: {c["accent"]}; }}',
          f'    .card {{ fill: {c["node"]}; stroke: {c["edge"]}; stroke-width: {c["stroke"]}; }}',
          f'    .k {{ font: 400 13px {c["f_body"]}; fill: {c["muted"]}; }}',
          f'    .v {{ font: 600 15px {c["f_head"] if hk == "serif" else c["f_body"]}; fill: {c["ink"]}; }}',
          f'    .lnk {{ font: 500 13px {c["f_code"]}; fill: {c["accent"]}; }}',
          f'    .wire {{ stroke: {c["wire"]}; stroke-width: {max(c["stroke"], 1.5)}; }}',
          f'    .node {{ fill: {c["node"]}; stroke: {c["edge"]}; stroke-width: {c["stroke"]}; }}',
          f'    .glow {{ fill: {c["accent_soft"]}; stroke: {c["accent"]}; stroke-width: {c["stroke"]}; opacity: 0; }}',
          f'    .label {{ font: 500 14px {c["f_label"]}; fill: {c["ink"]}; }}',
          f'    .sub {{ font: 400 12px {c["f_body"]}; fill: {c["muted"]}; }}',
          f'    .event {{ fill: {c["accent"]}; }}',
          f'    .cursor {{ fill: {c["accent"]}; animation: blink 1.1s steps(1) infinite; }}',
          '    @keyframes blink { 50% { opacity: 0; } }']

    n = len(pipe)
    if n >= 2:
        P = 1.6 * (n - 1) + 2.0
        gap = 76 if n == 4 else (60 if n == 5 else 96)
        w = (804 - gap * (n - 1)) / n
        xs = [48 + i * (w + gap) for i in range(n)]
        cx = [x + w / 2 for x in xs]
        travel_end = 0.84
        dist = cx[-1] - cx[0]
        o += [f'    .ev {{ animation: travel {P:.1f}s linear infinite both; }}',
              '    .trail { animation-delay: .07s; opacity: .45; }',
              f'    @keyframes travel {{ 0% {{ transform: translateX(0); }} {travel_end*100:.0f}%, 100% {{ transform: translateX({dist:.0f}px); }} }}']
        for i in range(n):
            p = travel_end * i / (n - 1) * 100
            lo, hi = max(p - 1, 0), min(p + 9, 100)
            o.append(f'    .g{i} {{ animation: glow{i} {P:.1f}s ease-out infinite both; }}')
            o.append(f'    @keyframes glow{i} {{ 0%, {lo:.1f}% {{ opacity: {1 if i == 0 else 0}; }} {p:.1f}% {{ opacity: 1; }} {hi:.1f}%, 100% {{ opacity: 0; }} }}')
        mid = (cx[1] - cx[0]) / 2 if n == 2 else (cx[1] - cx[0]) + (cx[2] - cx[1]) / 2
        o += ['    @media (prefers-reduced-motion: reduce) {',
              '      .cursor, .ev, ' + ", ".join(f".g{i}" for i in range(n)) + ' { animation: none; }',
              f'      .ev {{ transform: translateX({mid:.0f}px); }}', '    }']
    else:
        o.append('    @media (prefers-reduced-motion: reduce) { .cursor { animation: none; } }')
    o.append('  </style>')
    o += panel(c, W, H)

    top = 78 if n >= 2 else 120
    o.append(f'  <text class="name" x="48" y="{top}">{esc(name)}</text>')
    if tagline:
        o.append(f'  <text class="role" x="48" y="{top+32}">{esc(tagline)}</text>')
    if code:
        o.append(f'  <text class="code" x="48" y="{top+68}">{esc(code)}</text>')
        o.append(f'  <rect class="cursor" x="{48 + text_w(code, code_px, ck) + 10:.0f}" y="{top+68-code_px+2:.0f}" width="9" height="{code_px+2:.0f}"{glow_attr(c)}/>')
    if now:
        o += box(c, 620, top - 42, 232, 124, "card", c["rx_box"] + 2)
        o.append(f'  <text class="k" x="640" y="{top-16}">{esc(now.get("heading", "Now"))}</text>')
        if now.get("title"):
            o.append(f'  <text class="v" x="640" y="{top+8}">{esc(now["title"])}</text>')
        if now.get("subtitle"):
            o.append(f'  <text class="k" x="640" y="{top+28}">{esc(now["subtitle"])}</text>')
        if now.get("link"):
            o.append(f'  <text class="lnk" x="640" y="{top+62}">{esc(now["link"])}</text>')

    if n >= 2:
        y, h = 200, 48
        o += [f'  <line class="wire" x1="{cx[0]:.0f}" y1="{y+h/2}" x2="{cx[-1]:.0f}" y2="{y+h/2}"{dash}/>',
              f'  <circle class="event ev trail" cx="{cx[0]:.0f}" cy="{y+h/2}" r="4"/>',
              f'  <circle class="event ev" cx="{cx[0]:.0f}" cy="{y+h/2}" r="5.5"{glow_attr(c)}/>']
        for i, (x, p) in enumerate(zip(xs, pipe)):
            o += box(c, x, y, w, h, "node", c["rx_box"])
            o.append(f'  <rect class="glow g{i}" x="{x:.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="{c["rx_box"]}"{glow_attr(c)}/>')
            o.append(f'  <text class="label" x="{cx[i]:.0f}" y="{y+29}" text-anchor="middle">{esc(p["label"])}</text>')
            if p.get("note"):
                o.append(f'  <text class="sub" x="{cx[i]:.0f}" y="{y+h+22}" text-anchor="middle">{esc(p["note"])}</text>')
    o.append('</svg>')
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- stack
def stack(cfg, c):
    layers = cfg["stack"]
    core = set(cfg.get("core", []))
    bk = c["body"]
    W, x0, x_max, chip_h, line_gap = 900, 220, 868, 32, 10
    rows, y = [], 64
    for layer in layers:
        chips, x, ly = [], x0, 0
        for it in layer["items"]:
            tw = text_w(it, 14, bk) + (40 if it in core else 28)
            if x + tw > x_max and x > x0:
                x, ly = x0, ly + chip_h + line_gap
            chips.append((it, x, ly, tw))
            x += tw + 10 + (2 if c["shadow"] else 0)
        height = ly + chip_h + 24
        rows.append((layer["layer"], y, chips, height))
        y += height
    H = y + 12
    desc = ". ".join(f"{l['layer']}: {', '.join(l['items'])}" for l in layers)
    if core:
        desc += ". Core: " + ", ".join(cfg["core"])
    title = cfg.get("stack_title", "Stack")
    o = svg_open(W, H, title, desc + ".", "s")
    d = defs(c, W, H)
    if d:
        o += ["  <defs>"] + d + ["  </defs>"]
    o += ['  <style>',
          f'    .rule {{ stroke: {c["edge"]}; stroke-width: {min(c["stroke"], 1.5)}; }}',
          f'    .layer {{ font: 600 15px {c["f_head"]}; fill: {c["ink"]}; }}',
          f'    .key {{ font: 400 13px {c["f_body"]}; fill: {c["muted"]}; }}',
          f'    .chip {{ fill: {c["node"]}; stroke: {c["edge"]}; stroke-width: {c["stroke"] if c["shadow"] else 1}; }}',
          f'    .chip-core {{ fill: {c["accent_soft"] if not c["shadow"] else c["accent"]}; stroke: {c["accent"] if not c["shadow"] else c["edge"]}; stroke-width: {c["stroke"] if c["shadow"] else 1}; }}',
          f'    .t {{ font: 500 14px {c["f_body"]}; fill: {c["ink"]}; }}',
          f'    .t-core {{ font: 600 14px {c["f_body"]}; fill: {ink_for(c["accent"]) if c["shadow"] else c["ink"]}; }}',
          f'    .dot {{ fill: {c["accent"] if not c["shadow"] else ink_for(c["accent"])}; }}',
          f'    .keydot {{ fill: {c["accent"]}; }}',
          '    .row { animation: rise .5s cubic-bezier(.2,.8,.3,1) both; }',
          '    @keyframes rise { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }',
          '    @media (prefers-reduced-motion: reduce) { .row { animation: none; } }', '  </style>']
    o += panel(c, W, H)
    o.append(f'  <text class="layer" x="32" y="38">{esc(title)}</text>')
    if core:
        key = cfg.get("core_label", "daily core tools")
        kx = W - 32 - text_w(key, 13, bk) - 12
        o += [f'  <circle class="keydot" cx="{kx:.0f}" cy="33" r="5"{glow_attr(c)}/>', f'  <text class="key" x="{kx+12:.0f}" y="38">{esc(key)}</text>']
    for i, (label, y, chips, _) in enumerate(rows):
        o += [f'  <line class="rule" x1="32" y1="{y}" x2="{W-32}" y2="{y}"/>', f'  <g class="row" style="animation-delay:{0.1 + i*0.12:.2f}s">',
              f'    <text class="key" x="32" y="{y+33}">{esc(label)}</text>']
        for it, x, ly, tw in chips:
            cy = y + 12 + ly
            if it in core:
                o += ["  " + s for s in box(c, x, cy, tw, chip_h, "chip-core", c["rx_chip"])]
                o += [f'    <circle class="dot" cx="{x+15:.0f}" cy="{cy+16}" r="4"/>',
                      f'    <text class="t-core" x="{x+26:.0f}" y="{cy+21}">{esc(it)}</text>']
            else:
                o += ["  " + s for s in box(c, x, cy, tw, chip_h, "chip", c["rx_chip"])]
                o.append(f'    <text class="t" x="{x+14:.0f}" y="{cy+21}">{esc(it)}</text>')
        o.append('  </g>')
    o.append('</svg>')
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- graph
def wrap2(label, limit=11):
    words = label.split()
    if len(label) <= limit or len(words) == 1:
        return [label]
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        score = max(len(a), len(b))
        if best is None or score < best[0]:
            best = (score, [a, b])
    return best[1]


def graph_layout(g, W, H, OY, fk):
    nodes = {n["id"]: dict(n) for n in g["nodes"]}
    center = g["center"]
    nodes["center"] = dict(id="center", label=center["label"], kind=center.get("kind", "Person"))
    cx, cy = W / 2, OY + (H - OY - 50) / 2
    first = [b for a, b, _ in g["edges"] if a == "center"] + [a for a, b, _ in g["edges"] if b == "center"]
    first = list(dict.fromkeys(first))
    seen = list(first)
    first.sort(key=lambda i: (nodes[i]["kind"], seen.index(i)))
    ang = {}
    for k, nid in enumerate(first):
        ang[nid] = -math.pi / 2 + 2 * math.pi * k / max(len(first), 1)
    rx1, ry1 = 0.29 * W, 0.30 * (H - OY)
    pos = {"center": (cx, cy)}
    for nid, a in ang.items():
        pos[nid] = (cx + rx1 * math.cos(a), cy + ry1 * math.sin(a))
    rest = [nid for nid in nodes if nid not in pos]
    used = []
    for _ in range(3):
        for nid in list(rest):
            nb = [b if a == nid else a for a, b, _ in g["edges"] if nid in (a, b)]
            nb = [x for x in nb if x in pos and x != "center"]
            if not nb:
                continue
            mx = sum(pos[x][0] for x in nb) / len(nb) - cx
            my = sum(pos[x][1] for x in nb) / len(nb) - cy
            a = math.atan2(my / ry1, mx / rx1)
            clash = sum(1 for u in used if abs(math.remainder(u - a, 2 * math.pi)) < 0.3)
            a += (0.32 * ((clash + 1) // 2)) * (1 if clash % 2 else -1)
            used.append(a)
            pos[nid] = (cx + 0.44 * W * math.cos(a), cy + 0.40 * (H - OY) * math.sin(a))
            rest.remove(nid)
    for k, nid in enumerate(rest):
        pos[nid] = (60 + k * 90, H - 90)
    for nid, n in nodes.items():
        if "x" in n and "y" in n:
            pos[nid] = (n["x"], n["y"] + OY)
    for nid, n in nodes.items():
        lines = wrap2(n["label"])
        px = 14 if nid == "center" else 11.5
        need = max(text_w(l, px, fk) for l in lines) / 2 + 9
        n["lines"], n["r"] = lines, max(30 if nid != "center" else 42, min(need, 48))

    # force-directed refinement (Fruchterman-Reingold), centre and manual nodes pinned
    ids = list(nodes)
    pinned = {"center"} | {nid for nid, n in nodes.items() if "x" in n and "y" in n}
    x0, x1, y0, y1 = 24, W - 24, OY + 16, H - 46
    sy = (x1 - x0) / (y1 - y0)
    P = {nid: [pos[nid][0], (pos[nid][1] - cy) * sy] for nid in ids}
    k = 0.62 * math.sqrt((x1 - x0) * (y1 - y0) * sy / len(ids))
    iters = 260
    for it in range(iters):
        temp = 40 * (1 - it / iters) + 1
        disp = {nid: [0.0, 0.0] for nid in ids}
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = ids[i], ids[j]
                dx, dy = P[a][0] - P[b][0], P[a][1] - P[b][1]
                d = math.hypot(dx, dy) or 0.01
                f = k * k / d
                if d < nodes[a]["r"] + nodes[b]["r"] + 40:
                    f *= 3
                disp[a][0] += dx / d * f; disp[a][1] += dy / d * f
                disp[b][0] -= dx / d * f; disp[b][1] -= dy / d * f
        for a, b, _ in g["edges"]:
            dx, dy = P[a][0] - P[b][0], P[a][1] - P[b][1]
            d = math.hypot(dx, dy) or 0.01
            f = d * d / k
            disp[a][0] -= dx / d * f; disp[a][1] -= dy / d * f
            disp[b][0] += dx / d * f; disp[b][1] += dy / d * f
        for nid in ids:
            if nid in pinned:
                continue
            dx, dy = disp[nid]
            d = math.hypot(dx, dy) or 0.01
            P[nid][0] += dx / d * min(d, temp)
            P[nid][1] += dy / d * min(d, temp)
            r = nodes[nid]["r"]
            P[nid][0] = min(max(P[nid][0], x0 + r), x1 - r)
            P[nid][1] = min(max(P[nid][1], (y0 + r - cy) * sy), (y1 - r - cy) * sy)
    pos = {nid: (P[nid][0], P[nid][1] / sy + cy) for nid in ids}

    # reduce edge crossings: swap pairs of free nodes while that removes crossings
    def crosses(p1, p2, p3, p4):
        def ccw(a, b, c_):
            return (c_[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c_[0] - a[0])
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

    def crossings():
        E = [(a, b) for a, b, _ in g["edges"]]
        n = 0
        for i in range(len(E)):
            for j in range(i + 1, len(E)):
                if len({*E[i], *E[j]}) == 4 and crosses(pos[E[i][0]], pos[E[i][1]], pos[E[j][0]], pos[E[j][1]]):
                    n += 1
        return n

    free = [nid for nid in ids if nid not in pinned]
    best = crossings()
    improved = True
    while improved and best:
        improved = False
        for i in range(len(free)):
            for j in range(i + 1, len(free)):
                a, b = free[i], free[j]
                pos[a], pos[b] = pos[b], pos[a]
                n = crossings()
                if n < best:
                    best, improved = n, True
                else:
                    pos[a], pos[b] = pos[b], pos[a]

    label_room = {frozenset((a, b)): len(rel) * 5.9 + 30 for a, b, rel in g["edges"]}
    for _ in range(120):
        moved = False
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = ids[i], ids[j]
                (ax, ay), (bx, by) = pos[a], pos[b]
                dx, dy = bx - ax, by - ay
                d = math.hypot(dx, dy) or 0.01
                need = nodes[a]["r"] + nodes[b]["r"] + max(34, label_room.get(frozenset((a, b)), 0))
                if d < need:
                    push = (need - d) / 2
                    ux, uy = dx / d, dy / d
                    if a not in pinned:
                        pos[a] = (ax - ux * push, ay - uy * push)
                    if b not in pinned:
                        pos[b] = (bx + ux * push, by + uy * push)
                    moved = True
        for nid in ids:
            r = nodes[nid]["r"]
            x, y = pos[nid]
            pos[nid] = (min(max(x, 24 + r), W - 24 - r), min(max(y, OY + 16 + r), H - 46 - r))
        if not moved:
            break
    return nodes, pos


def graph(cfg, c):
    g = cfg["graph"]
    W, H, OY = 900, int(g.get("height", 610)), 48
    fk = c["body"]
    nodes, pos = graph_layout(g, W, H, OY, fk)
    kinds = list(dict.fromkeys([nodes["center"]["kind"]] + [n["kind"] for k, n in nodes.items() if k != "center"]))
    outline = c["graph"] == "outline"
    pal = {}
    for i, k in enumerate(kinds):
        if i == 0:
            pal[k] = (c["accent"], c["edge"] if c["shadow"] else mix(c["accent"], "#000000", 0.25), ink_for(c["accent"]))
        else:
            pal[k] = c["kinds"][(i - 1) % len(c["kinds"])]
    center_label = nodes["center"]["label"]
    query = g.get("query") or f'MATCH (me:{nodes["center"]["kind"]} {{name: "{center_label}"}})-[r]->(n) RETURN me, r, n'

    order = ["center"] + [b for a, b, _ in g["edges"] if a == "center"]
    order += [n for n in nodes if n not in order]
    order = list(dict.fromkeys(order))
    delay = {n: 0.15 + i * 0.12 for i, n in enumerate(order)}
    edge_w = 2.5 if c["shadow"] else 1.5
    dashed = bool(c["dash"])

    desc = "; ".join(f'{nodes[a]["label"]} {rel.lower().replace("_", " ")} {nodes[b]["label"]}' for a, b, rel in g["edges"])
    o = svg_open(W, H, f"{center_label} as a graph", desc + ".", "g")
    o += ['  <defs>', f'    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c["gedge"]}"/></marker>']
    o += defs(c, W, H) + ['  </defs>']
    o += ['  <style>',
          f'    .bar {{ fill: {c["node"]}; }}', f'    .rule {{ stroke: {c["edge"]}; stroke-width: {min(c["stroke"], 1.5)}; }}',
          f'    .q {{ font: 500 14px {FONTS["mono"]}; fill: {c["ink"]}; }}', f'    .kw {{ fill: {c["accent"]}; }}',
          f'    .edge {{ stroke: {c["gedge"]}; stroke-width: {edge_w}; fill: none; }}',
          f'    .rel {{ font: 500 9.5px {FONTS["mono"]}; fill: {c["muted"]}; }}', f'    .relbg {{ fill: {c["bg"]}; }}',
          f'    .cap {{ font: 600 11.5px {c["f_body"]}; }}', f'    .cap-big {{ font: {max(c["name_weight"], 600)} 14px {c["f_head"]}; }}',
          f'    .legend {{ font: 400 12px {c["f_body"]}; fill: {c["muted"]}; }}',
          f'    .ring {{ fill: none; stroke: {c["accent"]}; stroke-width: 2; }}',
          '    .node { transform-box: fill-box; transform-origin: center; animation: pop .5s cubic-bezier(.2,.8,.3,1.2) both; }',
          '    .link { animation: fade .5s ease-out both; }',
          '    .edge.draw { stroke-dasharray: 1; animation: draw .6s ease-out both; }',
          '    .ring { transform-box: fill-box; transform-origin: center; animation: pulse 2.8s ease-out 2.4s infinite both; }',
          '    @keyframes pop { from { opacity: 0; transform: scale(.6); } to { opacity: 1; transform: scale(1); } }',
          '    @keyframes fade { from { opacity: 0; } to { opacity: 1; } }',
          '    @keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }',
          '    @keyframes pulse { 0% { opacity: .7; transform: scale(1); } 80%, 100% { opacity: 0; transform: scale(1.45); } }',
          '    @media (prefers-reduced-motion: reduce) { .node, .link, .edge.draw, .ring { animation: none; } .ring { opacity: 0; } }',
          '  </style>']
    o += panel(c, W, H)
    s = c["stroke"]
    rp = c["rx_panel"]
    if rp:
        o.append(f'  <path class="bar" d="M{s} {rp} a{rp-s/2} {rp-s/2} 0 0 1 {rp-s/2} -{rp-s/2} H{W-rp} a{rp-s/2} {rp-s/2} 0 0 1 {rp-s/2} {rp-s/2} V48 H{s} z"/>')
    else:
        o.append(f'  <rect class="bar" x="{s}" y="{s}" width="{W-2*s}" height="{48-s}"/>')
    o.append(f'  <line class="rule" x1="{s}" y1="48" x2="{W-s}" y2="48"/>')
    q = esc(query)
    for kw in ("MATCH", "RETURN", "WHERE", "OPTIONAL"):
        q = re.sub(rf"\b{kw}\b", f'<tspan class="kw">{kw}</tspan>', q)
    o.append(f'  <text class="q" x="28" y="30">{q}</text>')

    # place each relationship label where it does not collide with labels already placed
    def seg_cross(p1, p2, p3, p4):
        d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
        if abs(d) < 1e-9:
            return None
        t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
        u = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
        return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])) if 0 < t < 1 and 0 < u < 1 else None

    E = [(pos[a], pos[b]) for a, b, _ in g["edges"]]
    placed, label_at = [], {}
    for i in range(len(E)):            # crossing points are obstacles too
        for j in range(i + 1, len(E)):
            pt = seg_cross(*E[i], *E[j])
            if pt:
                placed.append(pt)
    for idx, (a, b, rel) in enumerate(g["edges"]):
        (ax, ay), (bx, by) = pos[a], pos[b]
        L = math.hypot(bx - ax, by - ay) or 1
        ux, uy = (bx - ax) / L, (by - ay) / L
        x1, y1 = ax + ux * nodes[a]["r"], ay + uy * nodes[a]["r"]
        x2, y2 = bx - ux * (nodes[b]["r"] + 2), by - uy * (nodes[b]["r"] + 2)
        best = None
        for t in (0.5, 0.36, 0.64, 0.28, 0.72):
            px_, py_ = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            clear = min((math.hypot(px_ - qx, py_ - qy) for qx, qy in placed), default=1e9)
            if best is None or clear > best[0] + 0.5:
                best = (clear, px_, py_)
            if clear > 40:
                break
        placed.append((best[1], best[2]))
        label_at[idx] = (best[1], best[2])

    o.append('  <g>')
    for idx, (a, b, rel) in enumerate(g["edges"]):
        (ax, ay), (bx, by) = pos[a], pos[b]
        ar, br = nodes[a]["r"], nodes[b]["r"]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        x1, y1, x2, y2 = ax + ux * ar, ay + uy * ar, bx - ux * (br + 2), by - uy * (br + 2)
        d = max(delay[a], delay[b]) + 0.25
        mx, my = label_at[idx]
        ang = math.degrees(math.atan2(dy, dx))
        ang = ang - 180 if ang > 90 else (ang + 180 if ang < -90 else ang)
        tw = len(rel) * 5.9 + 8
        line = (f'<line class="edge" stroke-dasharray="{c["dash"]}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" marker-end="url(#arrow)"/>' if dashed else
                f'<line class="edge draw" pathLength="1" style="animation-delay:{d:.2f}s" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" marker-end="url(#arrow)"/>')
        o += [f'    <g class="link" style="animation-delay:{d:.2f}s">', '      ' + line,
              f'      <g transform="translate({mx:.1f} {my:.1f}) rotate({ang:.1f})"><rect class="relbg" x="{-tw/2:.1f}" y="-7" width="{tw:.1f}" height="13" rx="3"/><text class="rel" text-anchor="middle" y="3.5">{esc(rel)}</text></g>',
              '    </g>']
    o.append('  </g>')
    for nid in order:
        n = nodes[nid]
        x, y = pos[nid]
        fill, stroke, ink = pal[n["kind"]]
        r = n["r"]
        o.append(f'  <g class="node" style="animation-delay:{delay[nid]:.2f}s">')
        if nid == "center":
            o.append(f'    <circle class="ring" cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}"/>')
        if c["shadow"]:
            o.append(f'    <circle cx="{x+4:.0f}" cy="{y+4:.0f}" r="{r:.0f}" fill="{c["edge"]}"/>')
        if outline and nid != "center":
            o.append(f'    <circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{c["node"]}" stroke="{fill}" stroke-width="2.2"/>')
            ink = c["ink"]
        else:
            sw = c["stroke"] if c["shadow"] else 2
            o.append(f'    <circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{glow_attr(c) if nid == "center" else ""}/>')
        cls = "cap-big" if nid == "center" else "cap"
        ls = n["lines"]
        ys = [y + 4] if len(ls) == 1 else [y - 3, y + 11]
        for line, ty in zip(ls, ys):
            o.append(f'    <text class="{cls}" x="{x:.0f}" y="{ty:.0f}" text-anchor="middle" fill="{ink}">{esc(line)}</text>')
        o.append('  </g>')
    lx, ly = 28, H - 22
    for i, k in enumerate(kinds):
        fill, stroke, _ = pal[k]
        if outline and i:
            o.append(f'  <circle cx="{lx+6}" cy="{ly-4}" r="5.5" fill="{c["node"]}" stroke="{fill}" stroke-width="2"/>')
        else:
            o.append(f'  <circle cx="{lx+6}" cy="{ly-4}" r="6" fill="{fill}" stroke="{stroke}"/>')
        o.append(f'  <text class="legend" x="{lx+18}" y="{ly}">{esc(k)}</text>')
        lx += 18 + text_w(k, 12, fk) + 26
    o.append('</svg>')
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- text wrapping
def wrap(text, px, kind, max_w, max_lines=99):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if cur and text_w(trial, px, kind) > max_w:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines[-1] and text_w(lines[-1] + "...", px, kind) > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-1]
        lines[-1] += "..."
    return lines


def base_style(c):
    """CSS shared by the timeline, card and focus panels."""
    return [f'    .h {{ font: 600 15px {c["f_head"]}; fill: {c["ink"]}; }}',
            f'    .t {{ font: 600 16px {c["f_head"]}; fill: {c["ink"]}; }}',
            f'    .p {{ font: 400 14px {c["f_body"]}; fill: {c["muted"]}; }}',
            f'    .m {{ font: 500 13px {c["f_code"]}; fill: {c["muted"]}; }}',
            f'    .acc {{ fill: {c["accent"]}; }}',
            f'    .chip {{ fill: {c["node"]}; stroke: {c["edge"]}; stroke-width: {c["stroke"] if c["shadow"] else 1}; }}',
            f'    .ct {{ font: 500 12px {c["f_body"]}; fill: {c["ink"]}; }}',
            f'    .card {{ fill: {c["node"]}; stroke: {c["edge"]}; stroke-width: {c["stroke"]}; }}',
            f'    .rule {{ stroke: {c["edge"]}; stroke-width: {min(c["stroke"], 1.5)}; }}',
            '    .in { animation: rise .55s cubic-bezier(.2,.8,.3,1) both; }',
            '    @keyframes rise { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }']


# ---------------------------------------------------------------- timeline
def timeline(cfg, c):
    items = cfg["timeline"]
    W, x_line, x_text = 900, 190, 222
    rows, y = [], 78
    for it in items:
        lines = wrap(it.get("note", ""), 14, c["body"], W - x_text - 40, 2) if it.get("note") else []
        h = 30 + (20 if it.get("place") else 0) + 20 * len(lines) + 26
        rows.append((it, y, lines, h))
        y += h
    H = y - 6
    title = cfg.get("timeline_title", "Journey")
    desc = "; ".join(f'{it.get("when", "")}: {it["title"]}' + (f', {it["place"]}' if it.get("place") else "") for it in items)
    o = svg_open(W, H, title, desc + ".", "t")
    d = defs(c, W, H)
    if d:
        o += ["  <defs>"] + d + ["  </defs>"]
    line_len = rows[-1][1] - rows[0][1] + 8
    o += ['  <style>'] + base_style(c) + [
        f'    .spine {{ stroke: {c["edge"]}; stroke-width: 2; stroke-dasharray: {line_len:.0f}; animation: grow 1.4s ease-out .2s both; }}',
        f'    @keyframes grow {{ from {{ stroke-dashoffset: {line_len:.0f}; }} to {{ stroke-dashoffset: 0; }} }}',
        f'    .dot {{ fill: {c["bg"]}; stroke: {c["accent"]}; stroke-width: 2.5; }}',
        '    .dot.now { fill: ' + c["accent"] + '; }',
        '    .halo { fill: none; stroke: ' + c["accent"] + '; stroke-width: 2; transform-box: fill-box; transform-origin: center; animation: pulse 2.6s ease-out 1.6s infinite both; }',
        '    @keyframes pulse { 0% { opacity: .7; transform: scale(1); } 80%, 100% { opacity: 0; transform: scale(2.4); } }',
        '    @media (prefers-reduced-motion: reduce) { .in, .spine, .halo { animation: none; } .halo { opacity: 0; } }',
        '  </style>']
    o += panel(c, W, H)
    o.append(f'  <text class="h" x="32" y="40">{esc(title)}</text>')
    o.append(f'  <line class="spine" x1="{x_line}" y1="{rows[0][1]}" x2="{x_line}" y2="{rows[-1][1] + 8}"/>')
    for i, (it, y, lines, h) in enumerate(rows):
        now = bool(it.get("current"))
        o.append(f'  <g class="in" style="animation-delay:{0.25 + i*0.18:.2f}s">')
        o.append(f'    <text class="m" x="{x_line - 24}" y="{y + 5}" text-anchor="end">{esc(it.get("when", ""))}</text>')
        if now:
            o.append(f'    <circle class="halo" cx="{x_line}" cy="{y}" r="7"/>')
        o.append(f'    <circle class="dot{" now" if now else ""}" cx="{x_line}" cy="{y}" r="7"{glow_attr(c) if now else ""}/>')
        o.append(f'    <text class="t" x="{x_text}" y="{y + 6}">{esc(it["title"])}</text>')
        ty = y + 6
        if it.get("place"):
            ty += 22
            o.append(f'    <text class="p" x="{x_text}" y="{ty}" style="fill:{c["accent"]}">{esc(it["place"])}</text>')
        for ln in lines:
            ty += 20
            o.append(f'    <text class="p" x="{x_text}" y="{ty}">{esc(ln)}</text>')
        o.append('  </g>')
    o.append('</svg>')
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- project cards (one SVG per project)
def card(p, c, i):
    W, H = 440, 200
    pad = 26
    title_lines = wrap(p["name"], 18, c["head"], W - 2 * pad - 20, 1)
    sum_lines = wrap(p.get("summary", ""), 14, c["body"], W - 2 * pad, 3)
    sh = c["shadow"]
    o = svg_open(W + sh, H + sh, p["name"], p.get("summary", ""), f"c{i}")
    d = defs(c, W, H)
    if d:
        o += ["  <defs>"] + d + ["  </defs>"]
    o += ['  <style>'] + base_style(c) + [
        f'    .name {{ font: {max(c["name_weight"], 600) if c["head"] != "serif" else 500} 18px {c["f_head"]}; fill: {c["ink"]}; }}',
        f'    .bar {{ fill: {c["accent"]}; transform-box: fill-box; transform-origin: left; animation: bar .9s cubic-bezier(.2,.8,.3,1) {0.2 + i*0.15:.2f}s both; }}',
        '    @keyframes bar { from { transform: scaleX(0); } to { transform: scaleX(1); } }',
        '    @media (prefers-reduced-motion: reduce) { .in, .bar { animation: none; } }',
        '  </style>']
    if sh:
        o.append(f'  <rect x="{sh}" y="{sh}" width="{W}" height="{H}" rx="{c["rx_panel"]}" fill="{c["edge"]}"/>')
    o += panel(c, W, H)
    o.append(f'  <rect class="bar" x="{pad}" y="{pad}" width="36" height="4" rx="2"{glow_attr(c)}/>')
    o.append(f'  <g class="in" style="animation-delay:{0.1 + i*0.15:.2f}s">')
    o.append(f'    <text class="name" x="{pad}" y="{pad + 34}">{esc(title_lines[0])}</text>')
    for k, ln in enumerate(sum_lines):
        o.append(f'    <text class="p" x="{pad}" y="{pad + 62 + k*20}">{esc(ln)}</text>')
    x, cy = pad, H - pad - 26
    for t in p.get("tech", []):
        tw = text_w(t, 12, c["body"]) + 20
        if x + tw > W - pad:
            break
        o += ["  " + s for s in box(c, x, cy, tw, 26, "chip", c["rx_chip"])]
        o.append(f'    <text class="ct" x="{x + 10:.0f}" y="{cy + 17}">{esc(t)}</text>')
        x += tw + 8
    o.append('  </g>')
    o.append('</svg>')
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- focus board
def focus(cfg, c):
    cols = cfg["focus"]
    W, pad, gap = 900, 32, 18
    n = len(cols)
    cw = (W - 2 * pad - gap * (n - 1)) / n
    body = []
    for col in cols:
        lines = []
        for it in col["items"]:
            lines.append(wrap(it, 14, c["body"], cw - 52, 2))
        body.append(lines)
    col_h = max(58 + sum(22 * len(l) + 12 for l in lines) for lines in body) + 6
    H = 70 + col_h + 28
    title = cfg.get("focus_title", "Right now")
    desc = ". ".join(f'{col["label"]}: {", ".join(col["items"])}' for col in cols)
    o = svg_open(W, H, title, desc + ".", "f")
    d = defs(c, W, H)
    if d:
        o += ["  <defs>"] + d + ["  </defs>"]
    o += ['  <style>'] + base_style(c) + [
        '    .blink { animation: blink 2.4s ease-in-out infinite; }',
        '    @keyframes blink { 50% { opacity: .35; } }',
        '    @media (prefers-reduced-motion: reduce) { .in, .blink { animation: none; } }',
        '  </style>']
    o += panel(c, W, H)
    o.append(f'  <text class="h" x="32" y="40">{esc(title)}</text>')
    y0 = 64
    for i, (col, lines) in enumerate(zip(cols, body)):
        x = pad + i * (cw + gap)
        o += box(c, x, y0, cw, col_h, "card", c["rx_box"])
        o.append(f'  <g class="in" style="animation-delay:{0.15 + i*0.18:.2f}s">')
        o.append(f'    <circle class="acc{" blink" if i == 0 else ""}" cx="{x + 24:.0f}" cy="{y0 + 31}" r="5"{glow_attr(c)}/>')
        o.append(f'    <text class="t" x="{x + 38:.0f}" y="{y0 + 36}">{esc(col["label"])}</text>')
        ty = y0 + 70
        for item in lines:
            o.append(f'    <rect class="acc" x="{x + 22:.0f}" y="{ty - 6}" width="8" height="2" rx="1"/>')
            for k, ln in enumerate(item):
                o.append(f'    <text class="p" x="{x + 38:.0f}" y="{ty + k*22}" style="fill:{c["ink"]}">{esc(ln)}</text>')
            ty += 22 * len(item) + 12
        o.append('  </g>')
    o.append('</svg>')
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- buttons
def button(label, primary, c):
    tw = text_w(label, 15, c["body"])
    sh = min(c["shadow"], 4)
    w, h = int(tw + 40), 40
    W, H = w + sh, h + sh
    s = c["stroke"] if c["shadow"] else 1
    if primary:
        fill, stroke, ink = c["accent"], (c["edge"] if c["shadow"] else mix(c["accent"], "#000000", 0.25)), ink_for(c["accent"])
    else:
        fill, stroke, ink = c["node"], c["edge"], c["ink"]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}">',
         f'  <title>{esc(label)}</title>',
         f'  <style>.b {{ font: {600 if primary else 500} 15px {c["f_body"]}; fill: {ink}; }}</style>']
    if sh:
        o.append(f'  <rect x="{sh}" y="{sh}" width="{w}" height="{h}" rx="{c["rx_box"]}" fill="{c["edge"]}"/>')
    o += [f'  <rect x="{s/2}" y="{s/2}" width="{w-s}" height="{h-s}" rx="{c["rx_box"]}" fill="{fill}" stroke="{stroke}" stroke-width="{s}"/>',
          f'  <text class="b" x="{w/2:.1f}" y="25.5" text-anchor="middle">{esc(label)}</text>', '</svg>']
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- README
def readme(cfg):
    out = ["<!-- README.md -->", ""]
    alt = f'{cfg["name"]}. {cfg.get("tagline", "")}'
    if cfg.get("pipeline"):
        alt += " An event travels through " + ", ".join(p["label"] for p in cfg["pipeline"]) + "."
    out += [picture("hero", alt), ""]
    if cfg.get("links"):
        out.append("<p>")
        for l in cfg["links"]:
            sl = slug(l["label"])
            out.append(f'  <a href="{esc(l["url"])}"><picture>'
                       f'<source media="(prefers-color-scheme: dark)" srcset="assets/btn-{sl}-dark.svg">'
                       f'<source media="(prefers-color-scheme: light)" srcset="assets/btn-{sl}-light.svg">'
                       f'<img alt="{esc(l.get("alt", l["label"]))}" src="assets/btn-{sl}-dark.svg" height="40"></picture></a>')
        out += ["</p>", ""]
    if cfg.get("intro"):
        out += [cfg["intro"], ""]
    if cfg.get("stack"):
        alt = "Tech stack. " + " ".join(f"{l['layer']}: {', '.join(l['items'])}." for l in cfg["stack"])
        out += [picture("stack", alt), ""]
    if cfg.get("projects") and cfg.get("projects_style") == "cards":
        out += [f'## {cfg.get("projects_title", "Selected work")}', "", "<p>"]
        for i, p in enumerate(cfg["projects"]):
            sl = slug(p["name"])
            img = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/card-{sl}-dark.svg">'
                   f'<source media="(prefers-color-scheme: light)" srcset="assets/card-{sl}-light.svg">'
                   f'<img alt="{esc(p["name"])}: {esc(p.get("summary", ""))}" src="assets/card-{sl}-dark.svg" width="49%"></picture>')
            out.append(f'  <a href="{esc(p["url"])}">{img}</a>' if p.get("url") else f"  {img}")
        out += ["</p>", ""]
        for p in cfg["projects"]:
            if p.get("mermaid"):
                out += ["<details>", f'<summary>{p["name"]}: {p.get("mermaid_title", "architecture")}</summary>', "", "```mermaid", p["mermaid"].rstrip(), "```", "", "</details>", ""]
    elif cfg.get("projects"):
        out += [f'## {cfg.get("projects_title", "Selected work")}', ""]
        for p in cfg["projects"]:
            out.append(f'### [{p["name"]}]({p["url"]})' if p.get("url") else f'### {p["name"]}')
            out.append(p.get("summary", ""))
            if p.get("tech"):
                out.append(f'<br><sub>{", ".join(p["tech"])}</sub>')
            if p.get("mermaid"):
                out += ["", "<details>", f'<summary>{p.get("mermaid_title", "Architecture")}</summary>', "", "```mermaid", p["mermaid"].rstrip(), "```", "", "</details>"]
            out.append("")
    if cfg.get("timeline"):
        alt = "Timeline. " + " ".join(f'{t.get("when", "")}: {t["title"]}' + (f', {t["place"]}' if t.get("place") else "") + "." for t in cfg["timeline"])
        out += [picture("timeline", alt), ""]
    if cfg.get("publications"):
        out += [f'## {cfg.get("publications_title", "Publications")}', "", "| Paper | Venue |", "|---|---|"]
        out += [f'| {p["title"]} | {p.get("venue", "")} |' for p in cfg["publications"]]
        out.append("")
    if cfg.get("focus"):
        alt = " ".join(f'{col["label"]}: {", ".join(col["items"])}.' for col in cfg["focus"])
        out += [picture("focus", alt), ""]
    if cfg.get("graph"):
        g = cfg["graph"]
        alt = g.get("alt") or f'Graph of {cfg["name"]}\'s work: ' + "; ".join(
            f'{g["center"]["label"]} {r.lower().replace("_", " ")} {next((n["label"] for n in g["nodes"] if n["id"] == b), b)}'
            for a, b, r in g["edges"] if a == "center")
        out += [f'## {g.get("title", "Everything, connected")}', "", picture("graph", alt), ""]
    if cfg.get("footer"):
        out += [f'<sub>{cfg["footer"]}</sub>', ""]
    return "\n".join(out)


def main():
    args = sys.argv[1:]
    if args == ["--themes"]:
        for name, T in THEMES.items():
            print(f"{name:10} {T['description']}")
        return
    theme_arg = None
    if "--theme" in args:
        i = args.index("--theme")
        theme_arg = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        sys.exit(__doc__)
    cfg = json.load(open(args[0]))
    if theme_arg:
        cfg["theme"] = theme_arg
    out = args[1]
    os.makedirs(f"{out}/assets", exist_ok=True)
    written = []
    for mode in ("dark", "light"):
        c = theme(cfg, mode)
        parts = [("hero", hero), ("stack", stack), ("timeline", timeline), ("focus", focus), ("graph", graph)]
        for name, fn in parts:
            if name != "hero" and not cfg.get(name):
                continue
            path = f"{out}/assets/{name}-{mode}.svg"
            open(path, "w").write(fn(cfg, c))
            written.append(path)
        if cfg.get("projects_style") == "cards":
            for i, p in enumerate(cfg.get("projects", [])):
                path = f"{out}/assets/card-{slug(p['name'])}-{mode}.svg"
                open(path, "w").write(card(p, c, i))
                written.append(path)
        for l in cfg.get("links", []):
            path = f"{out}/assets/btn-{slug(l['label'])}-{mode}.svg"
            open(path, "w").write(button(l["label"], l.get("primary", False), c))
            written.append(path)
    open(f"{out}/README.md", "w").write(readme(cfg))
    written.append(f"{out}/README.md")
    print("\n".join(written))


if __name__ == "__main__":
    main()
