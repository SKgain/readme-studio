#!/usr/bin/env python3
# readme-studio/scripts/generate.py
"""
Generate a designed GitHub README from one profile.json.

Usage:
    python3 generate.py profile.json OUT_DIR

Writes:
    OUT_DIR/README.md
    OUT_DIR/assets/hero-{dark,light}.svg      animated hero (pipeline + optional "now" card)
    OUT_DIR/assets/stack-{dark,light}.svg     layered stack panel   (if "stack")
    OUT_DIR/assets/graph-{dark,light}.svg     Neo4j-style graph     (if "graph")
    OUT_DIR/assets/btn-<slug>.svg             link buttons          (if "links")

Every SVG is self-contained (no external fonts, scripts or images), animates with
CSS only, and respects prefers-reduced-motion. GitHub renders all of it.
"""
import json, math, os, re, sys

MONO = 'ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace'
SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif'

BASE = {
    "dark":  dict(bg="#0D1117", edge="#30363D", node="#161B22", ink="#E6EDF3", muted="#8B949E", wire="#30363D", gedge="#484F58"),
    "light": dict(bg="#FFFFFF", edge="#D0D7DE", node="#F6F8FA", ink="#1F2328", muted="#59636E", wire="#D0D7DE", gedge="#8C959F"),
}
# Neo4j Browser-like label palette: (fill, stroke, caption ink)
KIND_PALETTE = [
    ("#4C8EDA", "#2870C2", "#FFFFFF"),
    ("#FFC454", "#D7A013", "#0D1117"),
    ("#ECB5C9", "#DA7298", "#0D1117"),
    ("#569480", "#447666", "#FFFFFF"),
    ("#F79767", "#E36A2E", "#0D1117"),
    ("#57C7E3", "#23B3D7", "#0D1117"),
    ("#D9C8AE", "#C0A378", "#0D1117"),
]


# ---------------------------------------------------------------- helpers
def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def text_w(s, px):
    """Rough rendered width of sans text."""
    narrow = sum(1 for ch in s if ch in "ilIjtf.:,;' |!()[]")
    wide = sum(1 for ch in s if ch in "MWmw@")
    return (len(s) - narrow - wide) * px * 0.56 + narrow * px * 0.3 + wide * px * 0.82


def mono_w(s, px):
    return len(s) * px * 0.602


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


def theme(cfg, t):
    c = dict(BASE[t])
    acc = cfg.get("accent", {})
    c["accent"] = acc.get(t, "#6DB33F" if t == "dark" else "#2F7D1F")
    c["accent_soft"] = mix(c["bg"], c["accent"], 0.14 if t == "dark" else 0.12)
    return c


def picture(name, alt):
    return (f'<picture>\n'
            f'  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n'
            f'  <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">\n'
            f'  <img alt="{esc(alt)}" src="assets/{name}-dark.svg" width="100%">\n'
            f'</picture>')


# ---------------------------------------------------------------- hero
def hero(cfg, c):
    W, H = 900, 300
    name, tagline = cfg["name"], cfg.get("tagline", "")
    code = cfg.get("code_line", "")
    now = cfg.get("now")
    pipe = cfg.get("pipeline") or []
    text_max = 540 if now else 804

    name_px = 40
    while text_w(name, name_px) > text_max and name_px > 26:
        name_px -= 1
    tag_px = 18
    while text_w(tagline, tag_px) > text_max and tag_px > 13:
        tag_px -= 0.5
    code_px = 15
    while mono_w(code, code_px) > text_max - 20 and code_px > 11:
        code_px -= 0.5

    desc = f"{name}. {tagline}."
    if pipe:
        desc += " An event travels through " + ", ".join(p["label"] for p in pipe) + "."
    if now:
        desc += " Now: " + ", ".join(v for v in (now.get("title"), now.get("subtitle")) if v) + "."

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
         f'  <title id="t">{esc(name)}</title>', f'  <desc id="d">{esc(desc)}</desc>', '  <style>',
         f'    .panel {{ fill: {c["bg"]}; stroke: {c["edge"]}; }}',
         f'    .name {{ font: 700 {name_px}px {SANS}; fill: {c["ink"]}; }}',
         f'    .role {{ font: 400 {tag_px}px {SANS}; fill: {c["muted"]}; }}',
         f'    .code {{ font: 500 {code_px}px {MONO}; fill: {c["accent"]}; }}',
         f'    .card {{ fill: {c["node"]}; stroke: {c["edge"]}; }}',
         f'    .k {{ font: 400 13px {SANS}; fill: {c["muted"]}; }}',
         f'    .v {{ font: 600 15px {SANS}; fill: {c["ink"]}; }}',
         f'    .lnk {{ font: 500 13px {MONO}; fill: {c["accent"]}; }}',
         f'    .wire {{ stroke: {c["wire"]}; stroke-width: 2; }}',
         f'    .node {{ fill: {c["node"]}; stroke: {c["edge"]}; stroke-width: 1.5; }}',
         f'    .glow {{ fill: {c["accent_soft"]}; stroke: {c["accent"]}; stroke-width: 1.5; opacity: 0; }}',
         f'    .label {{ font: 500 14px {MONO}; fill: {c["ink"]}; }}',
         f'    .sub {{ font: 400 12px {SANS}; fill: {c["muted"]}; }}',
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

    top = 78 if n >= 2 else 120
    o += [f'  <rect class="panel" x="1" y="1" width="{W-2}" height="{H-2}" rx="16"/>',
          f'  <text class="name" x="48" y="{top}">{esc(name)}</text>']
    if tagline:
        o.append(f'  <text class="role" x="48" y="{top+32}">{esc(tagline)}</text>')
    if code:
        o.append(f'  <text class="code" x="48" y="{top+68}">{esc(code)}</text>')
        o.append(f'  <rect class="cursor" x="{48 + mono_w(code, code_px) + 10:.0f}" y="{top+68-code_px+2:.0f}" width="9" height="{code_px+2:.0f}"/>')
    if now:
        lines = [("v", now.get("title")), ("k", now.get("subtitle"))]
        o.append(f'  <rect class="card" x="620" y="{top-42}" width="232" height="124" rx="12"/>')
        o.append(f'  <text class="k" x="640" y="{top-16}">{esc(now.get("heading", "Now"))}</text>')
        if now.get("title"):
            o.append(f'  <text class="v" x="640" y="{top+8}">{esc(now["title"])}</text>')
        if now.get("subtitle"):
            o.append(f'  <text class="k" x="640" y="{top+28}">{esc(now["subtitle"])}</text>')
        if now.get("link"):
            o.append(f'  <text class="lnk" x="640" y="{top+62}">{esc(now["link"])}</text>')

    if n >= 2:
        y, h = 200, 48
        o += [f'  <line class="wire" x1="{cx[0]:.0f}" y1="{y+h/2}" x2="{cx[-1]:.0f}" y2="{y+h/2}"/>',
              f'  <circle class="event ev trail" cx="{cx[0]:.0f}" cy="{y+h/2}" r="4"/>',
              f'  <circle class="event ev" cx="{cx[0]:.0f}" cy="{y+h/2}" r="5.5"/>']
        for i, (x, p) in enumerate(zip(xs, pipe)):
            o.append(f'  <rect class="node" x="{x:.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="10"/>')
            o.append(f'  <rect class="glow g{i}" x="{x:.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="10"/>')
            o.append(f'  <text class="label" x="{cx[i]:.0f}" y="{y+29}" text-anchor="middle">{esc(p["label"])}</text>')
            if p.get("note"):
                o.append(f'  <text class="sub" x="{cx[i]:.0f}" y="{y+h+22}" text-anchor="middle">{esc(p["note"])}</text>')
    o.append('</svg>')
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- stack
def stack(cfg, c):
    layers = cfg["stack"]
    core = set(cfg.get("core", []))
    W, x0, x_max, chip_h, line_gap = 900, 220, 868, 32, 10
    # lay out chips, wrapping inside a layer when needed
    rows, y = [], 64
    for layer in layers:
        chips, x, ly = [], x0, 0
        for it in layer["items"]:
            tw = text_w(it, 14) + (40 if it in core else 28)
            if x + tw > x_max and x > x0:
                x, ly = x0, ly + chip_h + line_gap
            chips.append((it, x, ly, tw))
            x += tw + 10
        height = ly + chip_h + 24
        rows.append((layer["layer"], y, chips, height))
        y += height
    H = y + 12
    desc = ". ".join(f"{l['layer']}: {', '.join(l['items'])}" for l in layers)
    if core:
        desc += ". Core: " + ", ".join(cfg["core"])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="st sd">',
         f'  <title id="st">{esc(cfg.get("stack_title", "Stack"))}</title>', f'  <desc id="sd">{esc(desc)}.</desc>', '  <style>',
         f'    .panel {{ fill: {c["bg"]}; stroke: {c["edge"]}; }}', f'    .rule {{ stroke: {c["edge"]}; }}',
         f'    .layer {{ font: 600 14px {SANS}; fill: {c["ink"]}; }}', f'    .key {{ font: 400 13px {SANS}; fill: {c["muted"]}; }}',
         f'    .chip {{ fill: {c["node"]}; stroke: {c["edge"]}; }}', f'    .chip-core {{ fill: {c["accent_soft"]}; stroke: {c["accent"]}; }}',
         f'    .t {{ font: 500 14px {SANS}; fill: {c["ink"]}; }}', f'    .dot {{ fill: {c["accent"]}; }}',
         '    .row { animation: rise .5s cubic-bezier(.2,.8,.3,1) both; }',
         '    @keyframes rise { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }',
         '    @media (prefers-reduced-motion: reduce) { .row { animation: none; } }', '  </style>',
         f'  <rect class="panel" x="1" y="1" width="{W-2}" height="{H-2}" rx="16"/>',
         f'  <text class="layer" x="32" y="38">{esc(cfg.get("stack_title", "Stack"))}</text>']
    if core:
        key = cfg.get("core_label", "daily core tools")
        kx = W - 32 - text_w(key, 13) - 12
        o += [f'  <circle class="dot" cx="{kx:.0f}" cy="33" r="5"/>', f'  <text class="key" x="{kx+12:.0f}" y="38">{esc(key)}</text>']
    for i, (label, y, chips, _) in enumerate(rows):
        o += [f'  <line class="rule" x1="32" y1="{y}" x2="{W-32}" y2="{y}"/>', f'  <g class="row" style="animation-delay:{0.1 + i*0.12:.2f}s">',
              f'    <text class="key" x="32" y="{y+33}">{esc(label)}</text>']
        for it, x, ly, tw in chips:
            cy = y + 12 + ly
            if it in core:
                o += [f'    <rect class="chip-core" x="{x:.0f}" y="{cy}" width="{tw:.0f}" height="{chip_h}" rx="8"/>',
                      f'    <circle class="dot" cx="{x+15:.0f}" cy="{cy+16}" r="4"/>',
                      f'    <text class="t" x="{x+26:.0f}" y="{cy+21}">{esc(it)}</text>']
            else:
                o += [f'    <rect class="chip" x="{x:.0f}" y="{cy}" width="{tw:.0f}" height="{chip_h}" rx="8"/>',
                      f'    <text class="t" x="{x+14:.0f}" y="{cy+21}">{esc(it)}</text>']
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


def graph_layout(g, W, H, OY):
    nodes = {n["id"]: dict(n) for n in g["nodes"]}
    center = g["center"]
    nodes["center"] = dict(id="center", label=center["label"], kind=center.get("kind", "Person"))
    cx, cy = W / 2, OY + (H - OY - 50) / 2
    first = [b for a, b, _ in g["edges"] if a == "center"] + [a for a, b, _ in g["edges"] if b == "center"]
    first = list(dict.fromkeys(first))
    # group first ring by kind so sectors stay coherent
    seen = list(first)
    first.sort(key=lambda i: (nodes[i]["kind"], seen.index(i)))
    ang = {}
    for k, nid in enumerate(first):
        ang[nid] = -math.pi / 2 + 2 * math.pi * k / max(len(first), 1)
    rx1, ry1 = 0.29 * W, 0.30 * (H - OY)
    pos = {"center": (cx, cy)}
    for nid, a in ang.items():
        pos[nid] = (cx + rx1 * math.cos(a), cy + ry1 * math.sin(a))
    # second ring: push outward from the mean angle of placed neighbours
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
    for k, nid in enumerate(rest):   # unconnected leftovers
        pos[nid] = (60 + k * 90, H - 90)
    # manual overrides
    for nid, n in nodes.items():
        if "x" in n and "y" in n:
            pos[nid] = (n["x"], n["y"] + OY)
    # radii
    for nid, n in nodes.items():
        lines = wrap2(n["label"])
        px = 14 if nid == "center" else 11.5
        need = max(text_w(l, px) for l in lines) / 2 + 9
        n["lines"], n["r"] = lines, max(30 if nid != "center" else 42, min(need, 46))

    # force-directed refinement (Fruchterman-Reingold), centre and manual nodes pinned
    ids = list(nodes)
    pinned = {"center"} | {nid for nid, n in nodes.items() if "x" in n and "y" in n}
    x0, x1, y0, y1 = 24, W - 24, OY + 16, H - 46
    sy = (x1 - x0) / (y1 - y0)            # run in a space stretched to the frame's aspect
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
                gap = nodes[a]["r"] + nodes[b]["r"] + 40
                if d < gap:
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

    # connected pairs must leave room for their relationship label between the circles
    label_room = {}
    for a, b, rel in g["edges"]:
        label_room[frozenset((a, b))] = len(rel) * 5.9 + 30

    # final pass: remove any remaining overlaps and keep inside the frame
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
                    if a != "center":
                        pos[a] = (ax - ux * push, ay - uy * push)
                    if b != "center":
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
    nodes, pos = graph_layout(g, W, H, OY)
    kinds = list(dict.fromkeys([nodes["center"]["kind"]] + [n["kind"] for k, n in nodes.items() if k != "center"]))
    pal = {}
    for i, k in enumerate(kinds):
        pal[k] = (c["accent"], mix(c["accent"], "#000000", 0.25), ink_for(c["accent"])) if i == 0 else KIND_PALETTE[(i - 1) % len(KIND_PALETTE)]
    query = g.get("query") or f'MATCH (me:{nodes["center"]["kind"]} {{name: "{nodes["center"]["label"]}"}})-[r]->(n) RETURN me, r, n'

    order = ["center"] + [b for a, b, _ in g["edges"] if a == "center"]
    order += [n for n in nodes if n not in order]
    order = list(dict.fromkeys(order))
    delay = {n: 0.15 + i * 0.12 for i, n in enumerate(order)}

    desc = "; ".join(f'{nodes[a]["label"]} {rel.lower().replace("_", " ")} {nodes[b]["label"]}' for a, b, rel in g["edges"])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="gt gd">',
         f'  <title id="gt">{esc(nodes["center"]["label"])} as a graph</title>', f'  <desc id="gd">{esc(desc)}.</desc>',
         f'  <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c["gedge"]}"/></marker></defs>',
         '  <style>',
         f'    .panel {{ fill: {c["bg"]}; stroke: {c["edge"]}; }}', f'    .bar {{ fill: {c["node"]}; }}', f'    .rule {{ stroke: {c["edge"]}; }}',
         f'    .q {{ font: 500 14px {MONO}; fill: {c["ink"]}; }}', f'    .kw {{ fill: {c["accent"]}; }}',
         f'    .edge {{ stroke: {c["gedge"]}; stroke-width: 1.5; fill: none; }}',
         f'    .rel {{ font: 500 9.5px {MONO}; fill: {c["muted"]}; }}', f'    .relbg {{ fill: {c["bg"]}; }}',
         f'    .cap {{ font: 600 11.5px {SANS}; }}', f'    .cap-big {{ font: 700 14px {SANS}; }}',
         f'    .legend {{ font: 400 12px {SANS}; fill: {c["muted"]}; }}',
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
         '  </style>',
         f'  <rect class="panel" x="1" y="1" width="{W-2}" height="{H-2}" rx="16"/>',
         f'  <path class="bar" d="M1 17 a16 16 0 0 1 16 -16 H{W-17} a16 16 0 0 1 16 16 V48 H1 z"/>',
         f'  <line class="rule" x1="1" y1="48" x2="{W-1}" y2="48"/>']
    q = esc(query)
    for kw in ("MATCH", "RETURN", "WHERE", "OPTIONAL"):
        q = re.sub(rf"\b{kw}\b", f'<tspan class="kw">{kw}</tspan>', q)
    o.append(f'  <text class="q" x="28" y="30">{q}</text>')

    o.append('  <g>')
    for a, b, rel in g["edges"]:
        (ax, ay), (bx, by) = pos[a], pos[b]
        ar, br = nodes[a]["r"], nodes[b]["r"]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        x1, y1, x2, y2 = ax + ux * ar, ay + uy * ar, bx - ux * (br + 2), by - uy * (br + 2)
        d = max(delay[a], delay[b]) + 0.25
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ang = math.degrees(math.atan2(dy, dx))
        ang = ang - 180 if ang > 90 else (ang + 180 if ang < -90 else ang)
        tw = len(rel) * 5.9 + 8
        o += [f'    <g class="link" style="animation-delay:{d:.2f}s">',
              f'      <line class="edge draw" pathLength="1" style="animation-delay:{d:.2f}s" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" marker-end="url(#arrow)"/>',
              f'      <g transform="translate({mx:.1f} {my:.1f}) rotate({ang:.1f})"><rect class="relbg" x="{-tw/2:.1f}" y="-7" width="{tw:.1f}" height="13" rx="3"/><text class="rel" text-anchor="middle" y="3.5">{esc(rel)}</text></g>',
              '    </g>']
    o.append('  </g>')
    for nid in order:
        n = nodes[nid]
        x, y = pos[nid]
        fill, stroke, ink = pal[n["kind"]]
        o.append(f'  <g class="node" style="animation-delay:{delay[nid]:.2f}s">')
        if nid == "center":
            o.append(f'    <circle class="ring" cx="{x:.0f}" cy="{y:.0f}" r="{n["r"]:.0f}"/>')
        o.append(f'    <circle cx="{x:.0f}" cy="{y:.0f}" r="{n["r"]:.0f}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        cls = "cap-big" if nid == "center" else "cap"
        ls = n["lines"]
        ys = [y + 4] if len(ls) == 1 else [y - 3, y + 11]
        for line, ty in zip(ls, ys):
            o.append(f'    <text class="{cls}" x="{x:.0f}" y="{ty:.0f}" text-anchor="middle" fill="{ink}">{esc(line)}</text>')
        o.append('  </g>')
    lx, ly = 28, H - 22
    for k in kinds:
        fill, stroke, _ = pal[k]
        o += [f'  <circle cx="{lx+6}" cy="{ly-4}" r="6" fill="{fill}" stroke="{stroke}"/>', f'  <text class="legend" x="{lx+18}" y="{ly}">{esc(k)}</text>']
        lx += 18 + text_w(k, 12) + 26
    o.append('</svg>')
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- buttons (one file works in both themes)
def button(label, primary, cfg):
    acc = cfg.get("accent", {}).get("dark", "#6DB33F")
    tw = text_w(label, 15)
    W, H = int(tw + 40), 40
    fill, stroke, ink = (acc, mix(acc, "#000000", 0.25), ink_for(acc)) if primary else ("#21262D", "#3D444D", "#F0F6FC")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}">\n'
            f'  <title>{esc(label)}</title>\n'
            f'  <style>.b {{ font: {600 if primary else 500} 15px {SANS}; fill: {ink}; }}</style>\n'
            f'  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{fill}" stroke="{stroke}"/>\n'
            f'  <text class="b" x="{W/2:.1f}" y="25.5" text-anchor="middle">{esc(label)}</text>\n'
            '</svg>\n')


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
            out.append(f'  <a href="{esc(l["url"])}"><img alt="{esc(l.get("alt", l["label"]))}" src="assets/btn-{slug(l["label"])}.svg" height="40"></a>')
        out += ["</p>", ""]
    if cfg.get("intro"):
        out += [cfg["intro"], ""]
    if cfg.get("stack"):
        alt = "Tech stack. " + " ".join(f"{l['layer']}: {', '.join(l['items'])}." for l in cfg["stack"])
        out += [picture("stack", alt), ""]
    if cfg.get("projects"):
        out += [f'## {cfg.get("projects_title", "Selected work")}', ""]
        for p in cfg["projects"]:
            out.append(f'### [{p["name"]}]({p["url"]})' if p.get("url") else f'### {p["name"]}')
            out.append(p.get("summary", ""))
            if p.get("tech"):
                out.append(f'<br><sub>{", ".join(p["tech"])}</sub>')
            if p.get("mermaid"):
                out += ["", "<details>", f'<summary>{p.get("mermaid_title", "Architecture")}</summary>', "", "```mermaid", p["mermaid"].rstrip(), "```", "", "</details>"]
            out.append("")
    if cfg.get("publications"):
        out += [f'## {cfg.get("publications_title", "Publications")}', "", "| Paper | Venue |", "|---|---|"]
        out += [f'| {p["title"]} | {p.get("venue", "")} |' for p in cfg["publications"]]
        out.append("")
    if cfg.get("graph"):
        alt = cfg["graph"].get("alt") or f'Graph of {cfg["name"]}\'s work: ' + "; ".join(f"{a} {r.lower().replace('_', ' ')} {b}" for a, b, r in cfg["graph"]["edges"] if a == "center").replace("center", cfg["graph"]["center"]["label"])
        out += [f'## {cfg["graph"].get("title", "Everything, connected")}', "", picture("graph", alt), ""]
    if cfg.get("footer"):
        out += [f'<sub>{cfg["footer"]}</sub>', ""]
    return "\n".join(out)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    cfg = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(f"{out}/assets", exist_ok=True)
    written = []
    for t in ("dark", "light"):
        c = theme(cfg, t)
        parts = [("hero", hero)] + ([("stack", stack)] if cfg.get("stack") else []) + ([("graph", graph)] if cfg.get("graph") else [])
        for name, fn in parts:
            path = f"{out}/assets/{name}-{t}.svg"
            open(path, "w").write(fn(cfg, c))
            written.append(path)
    for l in cfg.get("links", []):
        path = f"{out}/assets/btn-{slug(l['label'])}.svg"
        open(path, "w").write(button(l["label"], l.get("primary", False), cfg))
        written.append(path)
    open(f"{out}/README.md", "w").write(readme(cfg))
    written.append(f"{out}/README.md")
    print("\n".join(written))


if __name__ == "__main__":
    main()
