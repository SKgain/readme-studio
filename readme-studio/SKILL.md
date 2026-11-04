---
name: readme-studio
description: Designs a polished, animated GitHub README (profile or project) as self-hosted SVGs - an animated architecture hero, a layered stack panel, a Neo4j-style graph of the person's work and link buttons, in light and dark. Use when someone asks for an attractive, unique or animated GitHub README or profile.
---

# README Studio

Produces a GitHub README that looks designed rather than templated: custom SVG panels in one visual system, animated with CSS that GitHub actually renders, in dark and light versions, built only from facts the person gave.

## What it makes

| Asset | What it shows |
|---|---|
| Hero | Name, tagline, one line of code with a blinking cursor, an optional "now" card, and an event travelling through the person's real pipeline, lighting each stage as it arrives |
| Buttons | Link buttons, one primary in the accent colour |
| Stack panel | Tools grouped by layer, with the daily core tools highlighted |
| Graph | A Neo4j Browser-style graph that builds outward from the person: what they built, where they work, what they published, and how those connect |
| README.md | Wires everything together with `<picture>` dark/light switching and full alt text |

Everything is static files committed to the person's repo. No Actions, no third-party image services, nothing that can break later.

## Workflow

### 1. Gather the facts

Use anything already available first: an existing README, a CV, a portfolio URL, their GitHub. Then ask once, in a single message, for what is still missing:

- **Links**, and which one is primary (usually the portfolio).
- **Pipeline**: the path data takes through their typical system, 2 to 5 stages. Offer a guess from their stack (see `references/design-rules.md`) and let them correct it.
- **Projects**: name, URL, one-sentence summary, tech.
- **Stack**, and which 2 to 5 items are their daily core tools.
- **Anything for the graph**: employer, papers, talks, open-source work, and real links between them (a project that uses the same database as their job, an API that implements a paper).
- **Accent colour**, or let them pick from their brand or stack (Spring green, React cyan, Rust orange).

Never invent a metric, a quote, an employer or a link. If something is missing, leave the section out.

### 2. Write profile.json

Follow `references/schema.md`. `assets/example-profile.json` is a complete real example.

### 3. Generate

```bash
python3 <skill-dir>/scripts/generate.py profile.json out/
```

This writes `out/README.md` and `out/assets/*.svg`.

### 4. Look at it

```bash
python3 <skill-dir>/scripts/preview.py out/
```

This screenshots both themes mid-animation (Playwright and Chrome or Chromium needed; it skips cleanly otherwise). Open both PNGs and check:

- No text overflows a box or collides with another label.
- The graph has no node sitting on an edge label. If it does, pin one or two nodes with `x` and `y` and regenerate.
- The light version keeps contrast.
- Every claim on the page is something the person said.

Fix and regenerate until it is clean. Only then hand it over.

### 5. Hand it over

Zip `README.md` and `assets/` together, and tell the person:

1. In the repo (`<username>/<username>` for a profile), choose **Add file → Upload files**.
2. Drag in the `assets` folder and `README.md` together, then commit.
3. Hard-refresh the page, since GitHub caches images.
4. If an image shows as alt text, the file is not at `assets/<name>.svg`. Paths are case-sensitive.

## Editing later

Small changes go into `profile.json` and a re-run regenerates everything consistently. Do not hand-edit generated SVGs. When the person wants something the schema cannot express, extend `generate.py` rather than patching output.

## Rules

Read `references/design-rules.md` before the first build. In short: one accent colour, one idea per panel, one shared frame, no emoji icons, no invented facts, calm motion with a reduced-motion fallback, alt text everywhere, and files committed to the repo rather than third-party services.
