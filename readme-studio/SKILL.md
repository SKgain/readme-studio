---
name: readme-studio
description: Designs a polished, animated GitHub README (profile or project) for any profession - engineers, QA, designers, data, PMs, researchers - as self-hosted SVGs in nine modern themes, in light and dark, with sections chosen to fit each person. Use when someone asks for an attractive, unique or animated GitHub README or profile.
---

# README Studio

Produces a GitHub README that looks designed rather than templated: custom SVG panels in one visual system, animated with CSS that GitHub actually renders, in dark and light versions, built only from facts the person gave. It fits any role, from backend and QA to product design and research, and comes in nine themes. Every README is assembled from only the sections that person has material for, so no two need look the same.

## What it makes

| Asset | What it shows |
|---|---|
| Hero (always) | Name, tagline, an optional line of code with a blinking cursor, an optional "now" card, and an event travelling through the person's real pipeline, lighting each stage as it arrives |
| Buttons | Link buttons, one primary in the accent colour |
| Stack panel | Tools grouped by layer, with the daily core tools highlighted |
| Project list or cards | Projects as text, or as clickable cards two per row |
| Timeline | Career and education milestones on a line that draws itself |
| Focus board | What they are building, learning and exploring right now |
| Graph | A Neo4j Browser-style graph of how their work connects |
| README.md | Wires everything together with `<picture>` dark/light switching and full alt text |

Everything is static files committed to the person's repo. No Actions, no third-party image services, nothing that can break later.

## Workflow

### 1. Gather the facts

Use anything already available first: an existing README, a CV, a portfolio URL, their GitHub. Work out their role, then read that role's preset in `references/professions.md`. A preset is a first draft: replace every stage and tool with what this person actually uses.

Then ask once, in a single message, for what is still missing:

- **Theme**: offer two or three that fit their role (see the themes table in `references/design-rules.md`), one line each.
- **Links**, and which one is primary (usually the portfolio).
- **Pipeline**: the path work or data takes through their world, 2 to 5 stages. Offer the preset adapted to their stack and let them correct it.
- **Projects**: name, URL, one-sentence summary, tech.
- **Stack**, and which 2 to 5 items are their daily core tools.
- **Sections**: propose a set from what they have (see "Choosing sections" in `references/design-rules.md`), for example "stack, project cards and a timeline", and let them add or drop any.
- **Material for those sections**: jobs and studies for a timeline; what they are building, learning and exploring for a focus board; employer, papers, talks or open-source work and the real links between them for a graph.

Never invent a metric, a quote, an employer or a link. If something is missing, leave the section out. Roles that do not code can leave out the code line.

### 2. Write profile.json

Follow `references/schema.md`. `assets/example-profile.json` is a complete real example.

### 3. Generate

```bash
python3 <skill-dir>/scripts/generate.py profile.json out/
```

This writes `out/README.md` and `out/assets/*.svg`. Add `--theme NAME` to try another theme without editing the file, and `--themes` lists them all. When the person cannot decide, generate two themes into separate folders and show both previews.

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
