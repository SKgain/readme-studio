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

The pipeline should be the path data takes through this person's typical system, in their words.

| Role | Pipeline | Code line |
|---|---|---|
| Reactive backend | Gateway, Kafka, WebFlux, Neo4j | `Flux.from(events).flatMap(service::handle)` |
| Frontend | Figma, React, Vercel | `const ui = compose(tokens, components, motion);` |
| ML engineer | Data, Features, Model, Serving | `model.fit(X_train, y_train).predict(X_live)` |
| Data engineer | Sources, Airflow, dbt, Warehouse | `SELECT * FROM raw JOIN clean USING (id)` |
| Mobile | Design, Flutter, Firebase, Store | `runApp(const MyApp());` |
| DevOps | Commit, CI, Registry, Kubernetes | `kubectl rollout status deploy/api` |

Ask before guessing when the role is unclear.

## Project READMEs

The same generator works for a repository README:
- `name` is the project name, `tagline` its one-line pitch, `pipeline` its real architecture.
- Use `links` for Docs, Demo and Releases.
- Put a quick start, configuration and license in `intro` and the markdown that follows. A clear quick start matters more than any animation.
- Use the graph only when the project genuinely has entities that relate (services, modules, plugins).
