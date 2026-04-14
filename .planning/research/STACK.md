# Technology Stack — Documentation Milestone v1.3

**Project:** MindGuard v2
**Researched:** 2026-04-14
**Scope:** Tools and conventions for SOP reports & technical documentation only

---

## Recommended Stack

This is a docs-only milestone. The "stack" is deliberately minimal — Markdown files in the repo, rendered by GitHub and VS Code. No static site generators, no build steps, no new dependencies.

### Core Authoring

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Markdown (CommonMark + GFM) | — | All documentation format | Already in use. GitHub renders natively. Zero tooling overhead. |
| Mermaid | 11.x | Diagrams (architecture, flows, ER) | GitHub renders mermaid fenced blocks natively since 2022. No install needed for readers. |
| VS Code + extensions | — | Authoring environment | Team already uses VS Code. Extensions provide live preview. |

### VS Code Extensions (Authoring Aids)

| Extension | ID | Purpose |
|-----------|----|---------|
| Markdown All in One | yzhang.markdown-all-in-one | TOC generation, formatting shortcuts, auto-preview |
| Mermaid Preview | bierner.markdown-mermaid | Live Mermaid diagram preview inside VS Code Markdown preview |
| Markdown Lint | davidanson.vscode-markdownlint | Catches inconsistent heading levels, trailing spaces, broken links |
| Code Spell Checker | streetsidesoftware.code-spell-checker | Catches English typos in code/variable references |

**Not recommended:** Vietnamese spell-checker extensions — none are mature enough to be useful. Manual review is more reliable for Vietnamese content.

### Diagram Tool: Mermaid (Primary)

**Why Mermaid over alternatives:**

| Criterion | Mermaid | PlantUML | draw.io |
|-----------|---------|----------|---------|
| GitHub native rendering | Yes | No (needs image export) | No (binary files) |
| Install required to read | None | Java runtime | Browser/app |
| Text-based (git-diffable) | Yes | Yes | No (.drawio is XML) |
| VS Code preview | Extension | Extension | Extension |
| Learning curve | Low | Medium | Low (but not diffable) |
| Vietnamese text in diagrams | Unicode support | Unicode support | Yes |

**Mermaid diagram types needed for this milestone:**

| Diagram Type | Use Case |
|--------------|----------|
| flowchart TD | SOP quy trinh (workflow steps) |
| erDiagram | DATABASE.md (entity relationships) |
| sequenceDiagram | API.md (request/response flows) |
| graph LR | ARCHITECTURE.md (component relationships) |

**Example — SOP workflow in Mermaid:**

    ```mermaid
    flowchart TD
        A[Mo hang doi xu ly] --> B{Co bao cao cho duyet?}
        B -- Co --> C[Kiem tra bang chung]
        B -- Khong --> D[Ket thuc]
        C --> E{Du dieu kien?}
        E -- Du --> F[Phe duyet]
        E -- Khong du --> G[Tu choi]
    ```

### Documentation Structure

No new folders needed. Use existing structure:

    documents/
      SOP/
        SOP_BAO_CAO.md          <- Update (exists)
        SOP_VAN_HANH.md         <- New: operations SOP
        SOP_QUAN_TRI.md         <- New: admin SOP
        HUONG_DAN_BAO_CAO_NGUOI_DUNG.md  <- Existing
        README.md               <- Update index
    docs/
      technical/
        ARCHITECTURE.md         <- Update (exists, needs NeonDB/Vercel content)
        API.md                  <- Update (exists, template only)
        DATABASE.md             <- Update (exists, needs actual schema)
        DECISIONS.md            <- Update (add ADRs for NeonDB, Vercel, AI safety)
      user/
        USER_GUIDE.md           <- Update if needed

## Markdown Conventions

### Document Header Standard

Every document should start with:

    # Tieu de tai lieu

    > Cap nhat lan cuoi: YYYY-MM-DD
    > Phien ban: X.Y
    > Nguoi phu trach: [role/name]

    ---

### Heading Hierarchy

    # H1 — Document title (one per file)
    ## H2 — Major sections (Muc dich, Pham vi, Quy trinh...)
    ### H3 — Subsections (Buoc 1, Buoc 2...)
    #### H4 — Detail items (rarely needed)

### Vietnamese Language Conventions

| Rule | Example | Reason |
|------|---------|--------|
| Use Vietnamese for all visible content | `## Muc dich` not `## Purpose` | Project constraint: all docs in Vietnamese |
| Keep code/technical terms in English | `Flask`, `SQLAlchemy`, `session`, `endpoint` | Vietnamese translations of tech terms cause confusion |
| Use backticks for code references | `session.get('is_admin')` | Distinguishes code from prose |
| Use Vietnamese punctuation consistently | Dau phay, dau cham theo tieng Viet | Consistency across documents |
| Avoid mixed-language sentences where possible | "Su dung endpoint `/api/reports`" (OK) | Brief English insertions for technical terms are fine |

### Table Format

Use GFM tables. Align columns for readability in source:

    | Cot 1      | Cot 2        | Cot 3     |
    |------------|--------------|-----------|
    | Gia tri 1  | Gia tri 2    | Gia tri 3 |

### SOP-Specific Conventions

Based on existing SOP_BAO_CAO.md patterns (maintain consistency):

1. **Numbered sections** — `## 1. Muc dich`, `## 2. Pham vi ap dung`, etc.
2. **Checklists per step** — Use `- [ ]` or bullet checklists after each procedure step
3. **Screenshot placeholders** — `[PLACEHOLDER_HINH_XX: Mo ta]` for future screenshot insertion
4. **Route references** — Include exact URL paths: `GET /admin/scammer-reports`
5. **Role identification** — Each SOP names who performs each action

### ADR (Architecture Decision Record) Format

For `docs/technical/DECISIONS.md`, use this structure per decision:

    ### ADR-XXX: [Tieu de quyet dinh]

    - **Ngay:** YYYY-MM-DD
    - **Trang thai:** Accepted / Superseded / Deprecated
    - **Boi canh:** [Van de can giai quyet]
    - **Quyet dinh:** [Phuong an duoc chon]
    - **Ly do:** [Tai sao chon phuong an nay]
    - **He qua:** [Tac dong, trade-offs]

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Diagrams | Mermaid | PlantUML | Requires Java. GitHub does not render natively. More setup friction. |
| Diagrams | Mermaid | draw.io / Excalidraw | Binary/XML files not git-diffable. Cannot review in PRs. |
| Doc site | None (raw Markdown in repo) | MkDocs / Sphinx | Over-engineering for a team reading docs on GitHub. Adds build step. |
| Doc site | None | Notion / Confluence | Docs drift from code. Not version-controlled. Not free for teams. |
| Linting | markdownlint (VS Code) | remark-lint (CI) | CI linting is overkill for a docs milestone. VS Code extension is sufficient. |
| API docs | Hand-written Markdown | Swagger/OpenAPI auto-gen | Flask app uses session auth + server-rendered pages, not a REST API. Auto-gen adds complexity for minimal benefit. |

## No Installation Required

This milestone adds no new Python packages, no build tools, no CI changes. Everything is:

- **Markdown** — already supported
- **Mermaid** — rendered by GitHub natively, previewed by VS Code extension
- **VS Code extensions** — optional authoring aids, not required to read docs

    # Nothing to install. Extensions are optional:
    # VS Code: Ctrl+Shift+X -> search "Markdown All in One" -> Install
    # VS Code: Ctrl+Shift+X -> search "Markdown Mermaid" -> Install

## Sources

- GitHub Mermaid support: native since Feb 2022, supports flowchart/sequence/ER/class diagrams in fenced code blocks
- Mermaid documentation: https://mermaid.js.org — current version 11.x
- GitHub Flavored Markdown spec: tables, task lists, fenced code blocks — all used in existing project docs
- CommonMark spec: heading hierarchy, link references, emphasis — baseline Markdown standard
- Existing project conventions: derived from documents/SOP/SOP_BAO_CAO.md and docs/technical/ARCHITECTURE.md in this repo

---

*Confidence: HIGH — all recommendations based on tools already working in the project ecosystem (GitHub + VS Code + Markdown). No unverified claims.*
