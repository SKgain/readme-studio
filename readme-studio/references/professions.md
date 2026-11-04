# Role presets

Starting points for people in different roles. A preset is a first draft, never the answer: replace every stage, tool and relationship with what this person actually uses, and drop anything they did not mention. Two backend engineers on different stacks should end up with different pipelines.

Each preset gives:
- **Pipeline**: the path work or data takes through their world, 3 to 5 stages, left to right.
- **Code line**: one line they might genuinely write. Leave it out for roles that do not code.
- **Stack layers**: row names for the stack panel.
- **Graph**: the node kinds and relationship types that suit the role.
- **Themes**: the two or three that usually fit best. Offer them; the person chooses.

## Engineering

### Backend engineer
- Pipeline: Gateway, Queue, Service, Database (use their real ones: `Kafka`, `RabbitMQ`, `gRPC`, `PostgreSQL`, `Neo4j`, `MongoDB`)
- Code line, by language: Java reactive `Flux.from(events).flatMap(service::handle)`, Go `go worker(ctx, jobs)`, Node `app.use(rateLimit({ windowMs: 60_000 }))`, Python `async def handle(event: Event) -> None:`
- Stack layers: Language and framework, Data, Messaging, Infra
- Graph: Company, Project, Technology. `BUILT`, `USES`, `WORKS_AT`, `MAINTAINS`
- Themes: studio, blueprint, terminal

### Frontend engineer
- Pipeline: Design, Components, State, Deploy (`Figma`, `React`, `Zustand`, `Vercel`)
- Code line: `const ui = compose(tokens, components, motion);` or `<Button variant="primary" onClick={save} />`
- Stack layers: Frameworks, Styling, Testing, Tooling
- Graph: Project, Library, Company. `BUILT`, `USES`, `CONTRIBUTED_TO`
- Themes: pastel, aurora, neon

### Full stack developer
- Pipeline: UI, API, Database, Deploy (`Next.js`, `tRPC`, `Postgres`, `Vercel`)
- Code line: `export default async function Page() { return <App /> }`
- Stack layers: Frontend, Backend, Data, Infra
- Graph: Product, Technology, Client or Company. `BUILT`, `USES`, `SHIPPED_FOR`
- Themes: aurora, studio, sunset

### QA engineer / SDET
- Pipeline: Commit, Unit, API, E2E, Release
- Code line: `await expect(page.getByRole('button')).toBeVisible();` or `given().when().get("/orders").then().statusCode(200);`
- Stack layers: Automation, Languages, Performance, Pipeline
- Graph: Test suite, Tool, Company, Open source. `AUTOMATED`, `USES`, `RUNS`, `MAINTAINS`
- Themes: pastel, studio, blueprint

### Mobile developer
- Pipeline: Design, App, API, Store (`Figma`, `Flutter`, `Firebase`, `Play Store`)
- Code line: Flutter `runApp(const MyApp());`, Swift `NavigationStack { HomeView() }`, Kotlin `setContent { AppTheme { Home() } }`
- Stack layers: Platforms, Languages, Backend, Release
- Graph: App, Technology, Company. `BUILT`, `PUBLISHED_ON`, `USES`
- Themes: sunset, pastel, neon

### DevOps / SRE / platform
- Pipeline: Commit, CI, Registry, Cluster, Observe
- Code line: `kubectl rollout status deploy/api` or `terraform apply -auto-approve=false`
- Stack layers: Cloud, Containers, CI/CD, Observability
- Graph: Platform, Tool, Company. `RUNS_ON`, `AUTOMATED`, `MONITORS`
- Themes: terminal, blueprint, studio

### Security engineer
- Pipeline: Recon, Scan, Exploit, Report (offensive) or Detect, Triage, Respond, Harden (defensive)
- Code line: `nmap -sV --top-ports 1000 target` or `rule: alert on failed_login > 5 per 1m`
- Stack layers: Offensive, Defensive, Cloud, Compliance
- Graph: Finding, Tool, Certification. `REPORTED`, `USES`, `CERTIFIED_IN`
- Themes: terminal, neon, blueprint

### Embedded / IoT engineer
- Pipeline: Sensor, MCU, Firmware, Gateway, Cloud
- Code line: `HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);`
- Stack layers: Hardware, Languages, Protocols, Tooling
- Graph: Device, Protocol, Project. `BUILT`, `SPEAKS`, `RUNS_ON`
- Themes: blueprint, terminal

### Game developer
- Pipeline: Idea, Prototype, Engine, Playtest, Release
- Code line: `transform.Translate(velocity * Time.deltaTime);` or `func _physics_process(delta):`
- Stack layers: Engines, Languages, Art and audio, Platforms
- Graph: Game, Engine, Jam or Studio. `MADE`, `BUILT_WITH`, `RELEASED_ON`
- Themes: neon, sunset

## Data and AI

### Data engineer
- Pipeline: Sources, Ingest, Transform, Warehouse, BI
- Code line: `SELECT * FROM raw.orders JOIN dim.customers USING (customer_id)`
- Stack layers: Orchestration, Processing, Storage, Analytics
- Graph: Pipeline, Tool, Company. `BUILT`, `FEEDS`, `USES`
- Themes: blueprint, studio, aurora

### Data scientist / ML engineer
- Pipeline: Data, Features, Model, Evaluate, Serve
- Code line: `model.fit(X_train, y_train).score(X_test, y_test)` or `trainer.train(); trainer.push_to_hub()`
- Stack layers: Modelling, Data, MLOps, Visualization
- Graph: Model, Dataset, Paper, Project. `TRAINED`, `PUBLISHED`, `USES`, `IMPLEMENTS`
- Themes: aurora, editorial, studio

## Design, product and beyond

### Product / UI / UX designer
- Pipeline: Research, Wireframe, Prototype, Test, Ship
- Code line: optional; a token line suits designers who code: `--radius: 12px; --space: 8px; --motion: 200ms ease-out;`
- Stack layers: Design, Research, Prototyping, Build
- Graph: Case study, Tool, Company. `DESIGNED`, `RESEARCHED`, `USES`
- Themes: sunset, pastel, editorial

### Product manager
- Pipeline: Discover, Define, Build, Launch, Measure
- Code line: usually none
- Stack layers: Discovery, Delivery, Analytics, Collaboration
- Graph: Product, Team, Metric they named. `LAUNCHED`, `LED`, `MEASURED_BY`
- Themes: aurora, sunset, editorial

### Researcher / academic / student
- Pipeline: Question, Data, Method, Results, Paper
- Code line: their actual research language, e.g. `df.groupby("cohort").agg(mean_score=("score", "mean"))`
- Stack layers: Methods, Languages, Tools, Domains
- Graph: Paper, Dataset, Lab or University, Course. `PUBLISHED`, `STUDIED_AT`, `CREATED`
- Themes: editorial, pastel, studio

### Technical writer / developer advocate
- Pipeline: Learn, Build, Write, Teach
- Code line: a snippet from their best tutorial
- Stack layers: Writing, Platforms, Technologies, Community
- Graph: Article, Talk, Community. `WROTE`, `SPOKE_AT`, `ORGANIZES`
- Themes: editorial, sunset, pastel

## When the role is mixed or unusual

Build the pipeline from how they describe their work, in their words. A "backend engineer who also does ML" gets their real path, for example `API, Kafka, Feature store, Model`. Ask when unsure rather than forcing a preset.
