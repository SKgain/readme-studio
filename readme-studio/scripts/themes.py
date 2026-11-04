# readme-studio/scripts/themes.py
"""
Theme definitions for README Studio.

Each theme has a "dark" and a "light" token set plus shared "style" tokens.
generate.py reads only these tokens, so adding a theme means adding one entry here.

Token reference
  bg, edge, node, ink, muted   panel background, borders, box fill, main text, secondary text
  wire, gedge                  hero wire colour, graph edge colour
  accent                       default accent (profile.json "accent" overrides it)
  grid                         colour of a background grid, or None
  kinds                        graph node palette: list of (fill, stroke, caption ink)

Style tokens
  head, body, label, code      font roles: "sans", "serif" or "mono"
  name_weight                  weight of the hero name
  rx_panel, rx_box, rx_chip    corner radii
  stroke                       border width
  dash                         stroke-dasharray for wires and graph edges ("" for solid)
  graph                        "fill" (solid nodes) or "outline" (ring nodes)
  glow                         soft glow on accent elements
  shadow                       hard offset shadow under boxes (px), 0 for none
  prompt                       text before the code line, e.g. "$ "
  soft                         soft blurred shadows under boxes (optional, default off)
  blobs                        per-mode list of colours that drift slowly behind the panel (optional)
"""

FONTS = {
    "sans": '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif',
    "serif": 'Georgia, "Iowan Old Style", "Palatino Linotype", "Noto Serif", "Times New Roman", serif',
    "mono": 'ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace',
}

NEO4J_KINDS = [
    ("#4C8EDA", "#2870C2", "#FFFFFF"),
    ("#FFC454", "#D7A013", "#0D1117"),
    ("#ECB5C9", "#DA7298", "#0D1117"),
    ("#569480", "#447666", "#FFFFFF"),
    ("#F79767", "#E36A2E", "#0D1117"),
    ("#57C7E3", "#23B3D7", "#0D1117"),
    ("#D9C8AE", "#C0A378", "#0D1117"),
]

THEMES = {
    # The original look: GitHub-native panels, Neo4j Browser colours.
    "studio": {
        "description": "GitHub-native dark panels, rounded boxes, Neo4j Browser colours. The safe default.",
        "style": dict(head="sans", body="sans", label="mono", code="mono", name_weight=700,
                      rx_panel=16, rx_box=10, rx_chip=8, stroke=1.5, dash="", graph="fill",
                      glow=False, shadow=0, prompt=""),
        "dark": dict(bg="#0D1117", edge="#30363D", node="#161B22", ink="#E6EDF3", muted="#8B949E",
                     wire="#30363D", gedge="#484F58", accent="#6DB33F", grid=None, kinds=NEO4J_KINDS),
        "light": dict(bg="#FFFFFF", edge="#D0D7DE", node="#F6F8FA", ink="#1F2328", muted="#59636E",
                      wire="#D0D7DE", gedge="#8C959F", accent="#2F7D1F", grid=None, kinds=NEO4J_KINDS),
    },

    # A shell session: monospace everywhere, dashed wiring, ring nodes.
    "terminal": {
        "description": "Monospace everywhere, a shell prompt, dashed wiring and ring nodes. For people who live in a terminal.",
        "style": dict(head="mono", body="mono", label="mono", code="mono", name_weight=700,
                      rx_panel=6, rx_box=3, rx_chip=2, stroke=1.2, dash="4 4", graph="outline",
                      glow=False, shadow=0, prompt="$ "),
        "dark": dict(bg="#0A0A0A", edge="#2A2A2A", node="#121212", ink="#D6D6D6", muted="#7C7C7C",
                     wire="#3A3A3A", gedge="#4A4A4A", accent="#4ADE80", grid=None,
                     kinds=[("#60A5FA", "#60A5FA", "#D6D6D6"), ("#FBBF24", "#FBBF24", "#D6D6D6"),
                            ("#F472B6", "#F472B6", "#D6D6D6"), ("#2DD4BF", "#2DD4BF", "#D6D6D6"),
                            ("#FB923C", "#FB923C", "#D6D6D6"), ("#A3A3A3", "#A3A3A3", "#D6D6D6")]),
        "light": dict(bg="#FAFAF7", edge="#D4D4CF", node="#F1F1EC", ink="#1C1C1C", muted="#6B6B66",
                      wire="#BDBDB7", gedge="#9C9C96", accent="#15803D", grid=None,
                      kinds=[("#1D4ED8", "#1D4ED8", "#1C1C1C"), ("#B45309", "#B45309", "#1C1C1C"),
                             ("#BE185D", "#BE185D", "#1C1C1C"), ("#0F766E", "#0F766E", "#1C1C1C"),
                             ("#C2410C", "#C2410C", "#1C1C1C"), ("#525252", "#525252", "#1C1C1C")]),
    },

    # A printed page: serif headings, warm paper, hairlines.
    "editorial": {
        "description": "Serif headings on warm paper, hairline rules, quiet ring nodes. Suits researchers and writers.",
        "style": dict(head="serif", body="sans", label="serif", code="mono", name_weight=400,
                      rx_panel=2, rx_box=2, rx_chip=14, stroke=1, dash="", graph="outline",
                      glow=False, shadow=0, prompt=""),
        "dark": dict(bg="#141311", edge="#3A3631", node="#1C1A17", ink="#F2EDE4", muted="#A39E93",
                     wire="#4A453E", gedge="#5E5850", accent="#E8A33D", grid=None,
                     kinds=[("#9CB4D8", "#9CB4D8", "#F2EDE4"), ("#D8B37A", "#D8B37A", "#F2EDE4"),
                            ("#D99A9A", "#D99A9A", "#F2EDE4"), ("#93BFA4", "#93BFA4", "#F2EDE4"),
                            ("#C9A9D9", "#C9A9D9", "#F2EDE4"), ("#B5AFA4", "#B5AFA4", "#F2EDE4")]),
        "light": dict(bg="#FBF8F1", edge="#D9D2C3", node="#F3EEE3", ink="#1A1814", muted="#6B6458",
                      wire="#C9C1B0", gedge="#A39A88", accent="#A3561B", grid=None,
                      kinds=[("#2F5A8F", "#2F5A8F", "#1A1814"), ("#8A6420", "#8A6420", "#1A1814"),
                             ("#9A3B3B", "#9A3B3B", "#1A1814"), ("#2F6B4A", "#2F6B4A", "#1A1814"),
                             ("#6B4A8A", "#6B4A8A", "#1A1814"), ("#6B6458", "#6B6458", "#1A1814")]),
    },

    # An engineering drawing: blue paper, grid, dashed construction lines.
    "blueprint": {
        "description": "Blue drafting paper with a grid, dashed construction lines and outlined parts. Suits system designers.",
        "style": dict(head="sans", body="sans", label="mono", code="mono", name_weight=700,
                      rx_panel=4, rx_box=2, rx_chip=2, stroke=1.2, dash="6 4", graph="outline",
                      glow=False, shadow=0, prompt=""),
        "dark": dict(bg="#0B2A5B", edge="#3A64A8", node="#0E3270", ink="#EAF2FF", muted="#A3BCE3",
                     wire="#5B84C6", gedge="#6F95D2", accent="#FFD166", grid="#14397A",
                     kinds=[("#EAF2FF", "#EAF2FF", "#EAF2FF"), ("#7FD3FF", "#7FD3FF", "#EAF2FF"),
                            ("#FFB4A2", "#FFB4A2", "#EAF2FF"), ("#B5E48C", "#B5E48C", "#EAF2FF"),
                            ("#C8B6FF", "#C8B6FF", "#EAF2FF"), ("#A3BCE3", "#A3BCE3", "#EAF2FF")]),
        "light": dict(bg="#F2F7FF", edge="#9DBBE6", node="#E8F0FD", ink="#0B2A5B", muted="#47679A",
                      wire="#7FA2D6", gedge="#6A8FC8", accent="#1D4ED8", grid="#DCE8FA",
                      kinds=[("#0B2A5B", "#0B2A5B", "#0B2A5B"), ("#0369A1", "#0369A1", "#0B2A5B"),
                             ("#B4442E", "#B4442E", "#0B2A5B"), ("#3F7D20", "#3F7D20", "#0B2A5B"),
                             ("#5B3FA8", "#5B3FA8", "#0B2A5B"), ("#47679A", "#47679A", "#0B2A5B")]),
    },

    # Night city: deep navy, glowing accent, saturated nodes.
    "neon": {
        "description": "Deep navy with a glowing accent and saturated nodes. Suits game devs and creative coders.",
        "style": dict(head="sans", body="sans", label="mono", code="mono", name_weight=800,
                      rx_panel=18, rx_box=12, rx_chip=10, stroke=1.5, dash="", graph="fill",
                      glow=True, shadow=0, prompt=""),
        "dark": dict(bg="#070B1A", edge="#1E2A4A", node="#0C1430", ink="#E8ECFF", muted="#8A96C2",
                     wire="#22305A", gedge="#33457A", accent="#FF4FD8", grid=None,
                     kinds=[("#22D3EE", "#06B6D4", "#070B1A"), ("#A3E635", "#84CC16", "#070B1A"),
                            ("#FBBF24", "#F59E0B", "#070B1A"), ("#FB7185", "#F43F5E", "#070B1A"),
                            ("#60A5FA", "#3B82F6", "#070B1A"), ("#F0ABFC", "#E879F9", "#070B1A")]),
        "light": dict(bg="#FFFFFF", edge="#D6DAEB", node="#F5F6FC", ink="#141A33", muted="#5A6385",
                      wire="#C9CEE3", gedge="#9AA3C4", accent="#C0129B", grid=None,
                      kinds=[("#0891B2", "#0E7490", "#FFFFFF"), ("#4D7C0F", "#3F6212", "#FFFFFF"),
                             ("#B45309", "#92400E", "#FFFFFF"), ("#BE123C", "#9F1239", "#FFFFFF"),
                             ("#1D4ED8", "#1E40AF", "#FFFFFF"), ("#A21CAF", "#86198F", "#FFFFFF")]),
    },

    # Soft and friendly: pastel surfaces, big radii, gentle shadows.
    "pastel": {
        "description": "Soft pastel surfaces, generous rounded corners and gentle shadows. Friendly and calm; suits designers, frontend and QA.",
        "style": dict(head="sans", body="sans", label="sans", code="mono", name_weight=700,
                      rx_panel=24, rx_box=16, rx_chip=16, stroke=1, dash="", graph="fill",
                      glow=False, shadow=0, prompt="", soft=True),
        "dark": dict(bg="#1B1D2A", edge="#2E3247", node="#24273A", ink="#ECEDF5", muted="#A3A7C2",
                     wire="#3A3F5A", gedge="#4B5173", accent="#8BD3C7", grid=None,
                     kinds=[("#A5C8F5", "#86B2EC", "#1B1D2A"), ("#F6C9A8", "#EFB083", "#1B1D2A"),
                            ("#F4B6C2", "#EC98A9", "#1B1D2A"), ("#C3E6A8", "#A8D888", "#1B1D2A"),
                            ("#F7E3A1", "#EFD27A", "#1B1D2A"), ("#D6C4F0", "#C2A9E8", "#1B1D2A")]),
        "light": dict(bg="#FCFBFF", edge="#E7E4F2", node="#F4F2FA", ink="#2A2840", muted="#6E6A88",
                      wire="#DAD6EA", gedge="#B7B2CE", accent="#2E9C8A", grid=None,
                      kinds=[("#A5C8F5", "#86B2EC", "#2A2840"), ("#F6C9A8", "#EFB083", "#2A2840"),
                             ("#F4B6C2", "#EC98A9", "#2A2840"), ("#C3E6A8", "#A8D888", "#2A2840"),
                             ("#F7E3A1", "#EFD27A", "#2A2840"), ("#D6C4F0", "#C2A9E8", "#2A2840")]),
    },

    # Living light: soft colour fields drift slowly behind frosted panels.
    "aurora": {
        "description": "Soft colour light drifting slowly behind frosted panels. The most dynamic theme; suits full stack, ML and product people.",
        "style": dict(head="sans", body="sans", label="sans", code="mono", name_weight=700,
                      rx_panel=22, rx_box=14, rx_chip=14, stroke=1, dash="", graph="fill",
                      glow=False, shadow=0, prompt="", soft=True),
        "dark": dict(bg="#0B1416", edge="#22383B", node="#11201F", ink="#E9F5F2", muted="#93B0AB",
                     wire="#2A4744", gedge="#3D605B", accent="#5EEAD4", grid=None,
                     blobs=["#0F766E", "#15803D", "#B45309"],
                     kinds=[("#7DD3FC", "#38BDF8", "#0B1416"), ("#FCD34D", "#F59E0B", "#0B1416"),
                            ("#FDA4AF", "#FB7185", "#0B1416"), ("#86EFAC", "#4ADE80", "#0B1416"),
                            ("#FDBA74", "#FB923C", "#0B1416"), ("#C4B5FD", "#A78BFA", "#0B1416")]),
        "light": dict(bg="#F7FBFA", edge="#D5E6E2", node="#EEF6F4", ink="#12302B", muted="#4E6E68",
                      wire="#C4DAD5", gedge="#93B3AC", accent="#0F766E", grid=None,
                      blobs=["#99F6E4", "#BBF7D0", "#FDE68A"],
                      kinds=[("#0369A1", "#075985", "#FFFFFF"), ("#B45309", "#92400E", "#FFFFFF"),
                             ("#BE123C", "#9F1239", "#FFFFFF"), ("#15803D", "#166534", "#FFFFFF"),
                             ("#C2410C", "#9A3412", "#FFFFFF"), ("#6D28D9", "#5B21B6", "#FFFFFF")]),
    },

    # Warm evening: peach and coral light, soft shadows.
    "sunset": {
        "description": "Warm peach and coral light with soft shadows and a slow glow. Welcoming; suits mobile, game dev, community and PM profiles.",
        "style": dict(head="sans", body="sans", label="sans", code="mono", name_weight=700,
                      rx_panel=22, rx_box=14, rx_chip=14, stroke=1, dash="", graph="fill",
                      glow=False, shadow=0, prompt="", soft=True),
        "dark": dict(bg="#1A1210", edge="#3A2822", node="#231915", ink="#FBEDE6", muted="#C2A296",
                     wire="#4A332B", gedge="#664538", accent="#FF8A65", grid=None,
                     blobs=["#9A3412", "#B45309", "#9F1239"],
                     kinds=[("#FCD34D", "#F59E0B", "#1A1210"), ("#93C5FD", "#60A5FA", "#1A1210"),
                            ("#FDA4AF", "#FB7185", "#1A1210"), ("#A7F3D0", "#6EE7B7", "#1A1210"),
                            ("#FDBA74", "#FB923C", "#1A1210"), ("#E9D5FF", "#D8B4FE", "#1A1210")]),
        "light": dict(bg="#FFFAF6", edge="#F2DDD2", node="#FFF1EA", ink="#3A1F17", muted="#8A5E4F",
                      wire="#EBCFC2", gedge="#CFA594", accent="#D9480F", grid=None,
                      blobs=["#FED7AA", "#FECACA", "#FDE68A"],
                      kinds=[("#B45309", "#92400E", "#FFFFFF"), ("#1D4ED8", "#1E40AF", "#FFFFFF"),
                             ("#BE123C", "#9F1239", "#FFFFFF"), ("#047857", "#065F46", "#FFFFFF"),
                             ("#C2410C", "#9A3412", "#FFFFFF"), ("#7E22CE", "#6B21A8", "#FFFFFF")]),
    },

    # Bold and blunt: thick borders, square corners, hard offset shadows.
    "brutalist": {
        "description": "Thick borders, square corners, hard offset shadows and one loud accent. Confident and impossible to miss.",
        "style": dict(head="sans", body="sans", label="mono", code="mono", name_weight=800,
                      rx_panel=0, rx_box=0, rx_chip=0, stroke=2.5, dash="", graph="fill",
                      glow=False, shadow=5, prompt=""),
        "dark": dict(bg="#111111", edge="#F5F5F5", node="#1C1C1C", ink="#FFFFFF", muted="#C4C4C4",
                     wire="#F5F5F5", gedge="#F5F5F5", accent="#FFE500", grid=None,
                     kinds=[("#FFFFFF", "#F5F5F5", "#111111"), ("#4DA3FF", "#F5F5F5", "#111111"),
                            ("#FF6B6B", "#F5F5F5", "#111111"), ("#5EEAD4", "#F5F5F5", "#111111"),
                            ("#FDBA74", "#F5F5F5", "#111111"), ("#C4B5FD", "#F5F5F5", "#111111")]),
        "light": dict(bg="#FFFFFF", edge="#000000", node="#FFFFFF", ink="#000000", muted="#3A3A3A",
                      wire="#000000", gedge="#000000", accent="#FF3B00", grid=None,
                      kinds=[("#000000", "#000000", "#FFFFFF"), ("#2563EB", "#000000", "#FFFFFF"),
                             ("#FACC15", "#000000", "#000000"), ("#10B981", "#000000", "#000000"),
                             ("#F472B6", "#000000", "#000000"), ("#A3A3A3", "#000000", "#000000")]),
    },
}
