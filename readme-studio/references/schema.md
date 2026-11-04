# profile.json schema

Every field except `name` is optional. Leave a field out and its section is not rendered. A complete, real example lives in `assets/example-profile.json`.

| Field | Type | What it drives |
|---|---|---|
| `name` | string | Hero title. Long names shrink to fit. |
| `tagline` | string | One sentence under the name. About 60 characters reads best. |
| `code_line` | string | A single line of code in the accent colour, with a blinking cursor. Make it something this person would actually write. |
| `accent` | `{ "dark": "#hex", "light": "#hex" }` | The one accent colour. The light value must be darker so it keeps contrast on white. |
| `now` | `{ "heading"?, "title", "subtitle", "link" }` | Small card on the right of the hero. `heading` defaults to "Now". |
| `pipeline` | `[{ "label", "note"? }]`, 2 to 5 items | Boxes along the bottom of the hero. An event travels left to right and each box lights up as it arrives. Labels of 10 characters or fewer fit best. |
| `links` | `[{ "label", "url", "primary"?, "alt"? }]` | Buttons under the hero. Exactly one should be `primary`. |
| `intro` | markdown string | Paragraph under the buttons. |
| `stack` | `[{ "layer", "items": [..] }]` | Layered stack panel. Rows wrap automatically. |
| `core` | `[string]` | Items in `stack` to highlight as daily core tools. Two to five. |
| `core_label` / `stack_title` | string | Override "daily core tools" / "Stack". |
| `projects` | `[{ "name", "url"?, "summary", "tech"?, "mermaid"?, "mermaid_title"? }]` | "Selected work". `mermaid` is a diagram source string, shown in a collapsible block. |
| `publications` | `[{ "title", "venue" }]` | A two-column table. Put the strongest venue first. |
| `graph` | object, see below | Neo4j Browser-style animated graph. |
| `footer` | string | Small closing line. |

## graph

```json
{
  "title": "Everything, connected",
  "center": { "label": "Saikat", "kind": "Engineer" },
  "nodes": [ { "id": "Q", "label": "Quickart", "kind": "Project" } ],
  "edges": [ ["center", "Q", "BUILT"] ],
  "query": "optional custom Cypher shown in the top bar",
  "height": 610
}
```

- `kind` becomes the node colour and the legend entry. The centre always takes the accent colour.
- Relationship types are UPPER_SNAKE_CASE, as in Cypher: `BUILT`, `USES`, `WORKS_AT`, `PUBLISHED`, `IMPLEMENTS`, `MAINTAINS`, `CONTRIBUTED_TO`, `STUDIED_AT`.
- Labels longer than 11 characters wrap onto two lines. Keep them under about 20 characters.
- Layout is force-directed with the centre pinned. To place a node by hand, give it `"x"` and `"y"` (the frame is 900 wide; y counts from just under the query bar). Pinned nodes do not move.
- Cross-links between non-centre nodes (a project that `USES` the same database as the job, an API that `IMPLEMENTS` a paper) are what make it read as a real graph. Aim for 8 to 14 nodes and at least two cross-links.
