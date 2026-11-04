# Design rules for GitHub READMEs

## What GitHub allows

GitHub sanitizes README HTML. It strips `<script>`, `<style>`, `<iframe>`, inline `style` attributes and most CSS. What survives:

- Markdown, `<p align>`, `<img>`, `<picture>` with `<source media="(prefers-color-scheme: …)">`, `<details>`/`<summary>`, `<table>`, `<sub>`, `<br>`, `<kbd>`.
- Mermaid diagrams in fenced code blocks, rendered natively and themed automatically.
- SVG files shown through `<img>`. CSS **inside** the SVG works there, including `@keyframes` and `@media (prefers-reduced-motion)`. That is the only way to get motion besides GIFs.

Inside an SVG shown as an image:
- No external fonts, images or scripts load. Use system font stacks.
- Write every attribute value with plain quotes and escape `&`, `<`, `>`. A font stack containing `"Segoe UI"` must live in a `<style>` block, never inside a `style="…"` attribute, or the file breaks.
- `prefers-color-scheme` inside the SVG follows the browser, not GitHub's theme. Ship a dark and a light file and switch with `<picture>`.

## The visual system

1. **One accent colour.** Every highlight, glow, cursor and primary button uses it. A rainbow of brand-coloured badges is the clearest sign of a template.
2. **One idea per panel.** Hero: who and how they build. Stack: what they use. Graph: what they made and how it connects.
3. **Every panel shares one frame:** 900 wide, 16px radius, the same border, background and type. Mixing custom panels with shields.io badges breaks it.
4. **No emoji as icons, no middle-dot meta strings, no tracked all-caps labels.**
5. **Never invent facts.** No made-up metrics, testimonials, star counts or "years of experience". If the person did not say it, it does not go in.
6. **Motion carries meaning.** The hero event flows through the person's real architecture. The graph builds outward from the person. Decoration that moves for its own sake reads as noise.
7. **Motion is calm.** At most one looping element per panel. Every animation has a `prefers-reduced-motion` fallback that shows a sensible still frame.
8. **Alt text on every image** that says what the picture shows, so the README still reads with images off.
9. **Mobile.** GitHub's app shows a narrow column. Full-width SVGs scale down cleanly. Avoid side-by-side tables of images.

## Reliability

- Prefer files committed to the repo over third-party image services. Public stat-card instances are frequently rate-limited and show broken images.
- Nothing here needs a GitHub Action, so nothing can silently stop updating.

## Picking the hero pipeline and code line

The pipeline should be the path work or data takes through this person's world, in their words. `references/professions.md` has starting points for more than fifteen roles, from backend and QA to designers, PMs and researchers. Ask before guessing when the role is unclear.

## Themes

Nine themes, all modern and professional. Run `generate.py --themes` for the live list.

| Theme | Feel | Usually suits |
|---|---|---|
| studio | GitHub-native panels, Neo4j colours | anyone; the safe default |
| pastel | soft pastel surfaces, big radii, gentle shadows | designers, frontend, QA |
| aurora | colour light drifting behind frosted panels | full stack, ML, product |
| sunset | warm peach and coral light | mobile, game dev, community, PM |
| editorial | serif type on warm paper, hairlines | researchers, writers, students |
| blueprint | blue drafting paper, grid, dashed lines | system designers, data, embedded |
| terminal | monospace, shell prompt, ring nodes | DevOps, security, CLI people |
| neon | deep navy with a glowing accent | game dev, creative coders |
| brutalist | thick borders, square corners, hard shadows | confident personal brands, designers who want to stand out |

## Choosing sections

Every section is optional, so build each README from what the person actually has. Never pad a section to fill a slot.

| Section | Use it when the person has |
|---|---|
| Stack panel | tools worth listing (almost everyone) |
| Project list | projects with links and short write-ups |
| Project cards | two to six projects that deserve to be seen at a glance |
| Timeline | a career or study path worth showing: jobs, degrees, bootcamps |
| Focus board | things they are building, learning or exploring now; good for students and people between roles |
| Graph | work that genuinely connects: a job, projects and papers that share tools or ideas |
| Publications | papers, with venues |

A student with two projects might get stack, cards and focus. A senior engineer with papers might get stack, list, timeline and graph. A designer might get cards and a timeline.

Offer two or three themes that fit, with one line on each, and let the person choose. When they have no preference, use the first match for their role in `references/professions.md`.

## Project READMEs

The same generator works for a repository README:
- `name` is the project name, `tagline` its one-line pitch, `pipeline` its real architecture.
- Use `links` for Docs, Demo and Releases.
- Put a quick start, configuration and license in `intro` and the markdown that follows. A clear quick start matters more than any animation.
- Use the graph only when the project genuinely has entities that relate (services, modules, plugins).
