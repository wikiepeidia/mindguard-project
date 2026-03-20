# Phase 3: Light Mode UX System - Research

**Researched:** 2026-03-20
**Domain:** Flask/Jinja + Bootstrap light-mode migration with token-first theming
**Confidence:** HIGH

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

- Palette: nen trang/xam sang, giu accent cyan de bao toan nhan dien san pham.
- Contrast: uu tien readability dat muc WCAG AA.
- Surface style: card/section nen trang, border mong, shadow nhe (khong glass-heavy).
- Alert semantics: warning dung amber/vang, danger dung do.

### Fast defaults for remaining areas

- Design token scope (default): uu tien token hoa `base.css`/`style.css` truoc, sau do apply vao `quiz`, `report_scammer`, `leaderboard`, `scammer_profile`.
- Rollout order (default): base layout/nav -> report flow -> quiz flow -> leaderboard/profile.
- Mobile-first baseline (default): optimized cho viewport pho bien 360-430px va breakpoint Bootstrap hien co.

### Claude's Discretion

- Naming cu the cho token map (color, spacing, radius, typography).
- Motion/transitions nhe de tang cam giac hien dai nhung khong gay roi.
- Cach gop style duplicate giua `style.css`, `base.css`, va css page-level theo lo trinh an toan.

### Deferred Ideas (OUT OF SCOPE)

- Quiz one-question-per-page chi tiet thuoc Phase 4.
- Leaderboard integrity behavior thuoc Phase 5.
- Advanced animation system ngoai nhu cau UX can ban cua v1.
</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| UI-01 | Nguoi dung thay light mode dong bo tren cac trang chinh (auth, quiz, report, profile, leaderboard). | Tokenized global foundation in `style.css`/`base.css`, dark-utility deprecation map, staged template class migration checklist. |
| UI-02 | He thong su dung design tokens thong nhat (mau, font, spacing) cho cac trang uu tien. | Prescriptive token contract (semantic color/surface/text/border/spacing/radius/shadow/focus), Bootstrap variable alignment strategy. |
| UI-03 | Trang quiz va report dam bao trai nghiem mobile-first o kich thuoc man hinh pho bien. | Mobile-first CSS pattern using Bootstrap breakpoints and explicit 360-430px acceptance checks for quiz/report flows. |
</phase_requirements>

## Summary

Project UI currently runs dark-first globally via `static/css/style.css` + `static/css/base.css`, while some page CSS (notably `quiz.css`) is already light-leaning. This split creates style drift and increases regression risk when touching shared templates. The safest Phase 03 approach is token-first: define a semantic light token layer in global CSS, map legacy dark tokens to aliases, then migrate page-level selectors and template utilities in a strict rollout order.

Bootstrap 5.3 already exposes robust CSS variables and color-mode primitives. For this codebase, do not build a custom theme engine. Instead, align project tokens with Bootstrap root/component variables (`--bs-*`) and keep light as default mode. Given requirements explicitly prioritize light mode in v1, dark behavior should be scoped fallback only (or deferred), not co-equal rollout.

Current templates show many inline dark utilities (`bg-dark`, `text-white`, `btn-close-white`, `data-theme="dark"` in Turnstile widgets) and inline `style=` usage. Migration should replace these with semantic utility classes and tokenized component classes. This allows safe visual convergence without breaking existing Flask routes or JS behavior.

**Primary recommendation:** Implement a semantic token layer in global CSS first, then perform route-priority class migration (base -> report -> quiz -> leaderboard/profile) with mobile and contrast checks at each step.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Bootstrap | 5.3.8 (verified latest; published 2025-08-26) | Responsive system, component variables, light-default theming | Native CSS variable architecture and mobile-first breakpoints reduce custom CSS complexity. |
| CSS Custom Properties | Native (browser standard) | Design token source of truth | Fast runtime theming and safe incremental migration across Jinja templates. |
| Flask + Jinja templates | Existing app stack | Server-rendered UI composition | Zero architecture churn; supports phased template class updates. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| AOS | 2.3.4 latest (project uses 2.3.1) | Motion reveals | Keep only subtle decorative motion; disable/limit on small screens. |
| Font Awesome Free | 7.2.0 latest (project uses 6.4.0) | Iconography | Optional upgrade; no blocker for Phase 03 if icon set is stable. |
| Cloudflare Turnstile | Hosted script | Bot mitigation widgets on auth/report forms | Keep integration; set widget theme to match new light UI. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Bootstrap variable alignment | Tailwind rebuild | High rewrite cost and template churn; not justified for Phase 03 scope. |
| Semantic token classes | Per-page hardcoded hex values | Faster short-term but causes ongoing drift and regression risk. |
| Incremental migration | Big-bang redesign | Big-bang has high risk across auth/report/quiz flows and anti-spam UX messaging. |

**Installation:**

```bash
# No new mandatory package for Phase 03 core work.
# Optional upgrade path if desired:
# Bootstrap CDN: 5.3.0 -> 5.3.8
# AOS CDN: 2.3.1 -> 2.3.4
# Font Awesome CDN: 6.4.0 -> 7.2.0
```

**Version verification:**

```bash
npm view bootstrap version
npm view aos version
npm view @fortawesome/fontawesome-free version
```

## Architecture Patterns

### Recommended Project Structure

```text
static/css/
├── tokens.css              # New semantic design tokens (light default)
├── style.css               # Keep global layout + component-level styles
├── base.css                # Shared shell/chatbot/navbar/footer behaviors
├── report_scammer.css      # Page-specific styles (consume tokens only)
├── quiz.css                # Page-specific styles (consume tokens only)
├── leaderboard.css         # Page-specific styles (consume tokens only)
└── scammer_profile.css     # Page-specific styles (consume tokens only)

templates/
├── base.html               # global classes/utilities, remove dark hardcoding
├── login.html              # auth light utilities + Turnstile theme alignment
├── register.html
├── profile.html
├── report_scammer.html
├── quiz.html
├── leaderboard.html
└── scammer_profile.html
```

### Pattern 1: Token-First Semantic Layer

**What:** Create semantic tokens (`--mg-surface-1`, `--mg-text-primary`, `--mg-border-muted`, etc.) and map them to Bootstrap variables where possible.
**When to use:** Before touching per-page CSS; this is wave 1 foundation.
**Example:**

```css
/* Source pattern: Bootstrap CSS variables docs */
:root,
[data-bs-theme="light"] {
  --mg-bg-canvas: #f5f7fb;
  --mg-surface-1: #ffffff;
  --mg-surface-2: #f8fafc;
  --mg-text-primary: #0f172a;
  --mg-text-secondary: #475569;
  --mg-border-subtle: #dbe3ee;
  --mg-accent: #06b6d4;
  --mg-danger: #dc3545;
  --mg-warning: #f59e0b;

  --bs-body-bg: var(--mg-bg-canvas);
  --bs-body-color: var(--mg-text-primary);
  --bs-border-color: var(--mg-border-subtle);
  --bs-primary: var(--mg-accent);
}
```

### Pattern 2: Dark Utility Decommission Map

**What:** Replace `text-white/bg-dark/bg-black/btn-close-white` usages with semantic classes or Bootstrap light variables.
**When to use:** During each template migration wave.
**Example:**

```html
<!-- before -->
<div class="modal-content bg-dark border border-secondary">

<!-- after -->
<div class="modal-content mg-surface border mg-border-subtle">
```

### Pattern 3: Mobile-First Page Lock for Quiz/Report

**What:** Keep base styles targeting xs first, then layer `min-width` breakpoints (`sm`, `md`, `lg`).
**When to use:** UI-03 verification for 360-430px viewport first.
**Example:**

```css
/* xs default */
.quiz-container { padding: 0.75rem; }

/* >=576px */
@media (min-width: 576px) {
  .quiz-container { padding: 1rem; }
}

/* >=768px */
@media (min-width: 768px) {
  .quiz-container { padding: 1.5rem; }
}
```

### Anti-Patterns to Avoid

- **Token bypassing:** Adding new hex colors directly inside page CSS or inline `style=`.
- **Mixed-mode component styling:** Keeping `bg-dark` while switching text tokens to dark text causes unreadable combos.
- **Template-only fixes:** Changing template utility classes without aligning CSS token values creates hidden regressions.
- **Big-bang CSS rewrite:** Avoid editing all pages in one commit; use wave-based migration.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Responsive grid/breakpoints | Custom breakpoint framework | Bootstrap grid + documented breakpoints | Already integrated; fewer bugs and consistent behavior. |
| Theme variable plumbing | Custom JS theme engine | CSS variables + Bootstrap `--bs-*` root/component variables | Less JS, less flicker, safer server-rendered pages. |
| Form control state visuals | Custom input state system | Bootstrap form + validation classes | Accessibility and browser consistency handled by framework. |
| Contrast rules | Ad-hoc visual judgment only | WCAG AA ratio checks + token constraints | Prevents illegible states across alert/text/inputs. |

**Key insight:** In this phase, complexity is migration control, not feature invention. Hand-rolled theming logic increases failure surface without adding product value.

## Common Pitfalls

### Pitfall 1: Dual Global Style Sources Diverge

**What goes wrong:** `style.css` and `base.css` both define body/navbar/text in conflicting ways.
**Why it happens:** Dark-first overrides were added incrementally.
**How to avoid:** Introduce `tokens.css`, then reduce duplicate declarations and enforce one owner per concern.
**Warning signs:** Same selector appears in both files with different colors.

### Pitfall 2: Hardcoded Dark Utilities in Templates

**What goes wrong:** Light palette is introduced but many components stay dark due to utility classes.
**Why it happens:** Existing templates rely on `bg-dark`, `text-white`, inline styles.
**How to avoid:** Build an explicit replacement list and migrate in rollout order.
**Warning signs:** Modal/input/pagination remains dark after global token switch.

### Pitfall 3: Cloudflare Widget Theme Mismatch

**What goes wrong:** Turnstile stays dark (`data-theme="dark"`) on light forms, breaking visual consistency.
**Why it happens:** Attribute hardcoded in auth/report templates.
**How to avoid:** Move to light theme default, optionally set via config variable.
**Warning signs:** CAPTCHA block is the only dark element on form pages.

### Pitfall 4: Mobile Regressions on Quiz/Report

**What goes wrong:** Desktop fixes break small viewport readability and touch spacing.
**Why it happens:** Editing only `md/lg` styles, ignoring xs defaults.
**How to avoid:** Validate 360px and 430px first, then scale upward.
**Warning signs:** Horizontal overflow, clipped button labels, stacked controls overlap.

### Pitfall 5: Accessibility Drift During Visual Refresh

**What goes wrong:** Secondary text and badges lose contrast on light backgrounds.
**Why it happens:** Porting dark palette values directly.
**How to avoid:** Enforce WCAG AA targets for text combinations in token review.
**Warning signs:** muted text hard to read, warning/danger badges too faint.

## Code Examples

Verified patterns from official sources:

### Bootstrap Variable-Driven Theme Foundation

```css
/* Source: https://getbootstrap.com/docs/5.3/customize/css-variables/ */
:root,
[data-bs-theme="light"] {
  --bs-body-bg: #ffffff;
  --bs-body-color: #212529;
  --bs-border-color: #dee2e6;
  --bs-primary: #0dcaf0;
}
```

### Scoped Component Theme Override

```html
<!-- Source: https://getbootstrap.com/docs/5.3/customize/color-modes/ -->
<div class="dropdown" data-bs-theme="light">
  ...
</div>
```

### Bootstrap Mobile-First Breakpoint Pattern

```css
/* Source: https://getbootstrap.com/docs/5.3/layout/breakpoints/ */
/* xs default styles here */

@media (min-width: 576px) {
  /* sm+ */
}

@media (min-width: 768px) {
  /* md+ */
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded page colors | Semantic tokens + CSS variables | Mainstream in modern CSS and Bootstrap 5.x | Faster, safer theme consistency across components. |
| Theme via many utility overrides | Root/component variable alignment | Bootstrap 5.2-5.3 expansion | Lower maintenance and easier migration. |
| Desktop-first patching | Mobile-first base then upscale | Standard responsive best practice | Better UX for dominant phone viewport sizes. |

**Deprecated/outdated:**

- Dark-by-default hardcoding in v1 scope: conflicts with UI-01 target (light-mode dominant UX).
- Inline style-driven color management: prevents scalable token governance.

## Open Questions

1. **Should Bootstrap CDN be upgraded during Phase 03 or deferred?**
   - What we know: project uses `5.3.0`, latest is `5.3.8`.
   - What's unclear: whether release delta impacts existing custom CSS assumptions.
   - Recommendation: keep migration on current version first, then perform isolated CDN bump with visual regression check.

2. **Should Turnstile theme be config-driven?**
   - What we know: templates hardcode `data-theme="dark"` in login/register/report.
   - What's unclear: whether ops wants environment-specific theme override.
   - Recommendation: introduce a single template variable defaulting to light.

3. **How much of network-canvas dark ambience should remain in light mode?**
   - What we know: `base.js` uses cyan particles and dark-biased atmosphere.
   - What's unclear: desired brand balance between cybersecurity feel and daytime readability.
   - Recommendation: keep motion, reduce opacity/contrast, and ensure text contrast remains AA.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python `unittest` (stdlib) |
| Config file | none |
| Quick run command | `python -m unittest discover tests/antispam -v` |
| Full suite command | `python -m unittest discover tests/antispam -v && python -m unittest discover tests/privacy -v` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| UI-01 | Light mode consistency across auth/quiz/report/profile/leaderboard | UI smoke (manual + future automated) | `python -m unittest discover tests/antispam -v` (regression safety only) | ❌ Wave 0 |
| UI-02 | Tokenized color/font/spacing consistency on priority pages | Unit-ish static contract + manual visual check | `python -m unittest discover tests/privacy -v` (regression safety only) | ❌ Wave 0 |
| UI-03 | Mobile-first UX quality on quiz/report for 360-430px | Responsive UI smoke | `python -m unittest discover tests/antispam -v && python -m unittest discover tests/privacy -v` (non-UI safety net) | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python -m unittest discover tests/antispam -v`
- **Per wave merge:** `python -m unittest discover tests/antispam -v && python -m unittest discover tests/privacy -v`
- **Phase gate:** Full suite green + manual viewport pass (360/390/430px) for login/register/report/quiz/leaderboard/profile

### Wave 0 Gaps

- [ ] `tests/ui/test_light_mode_contract.py` - asserts required token class usage and bans `bg-dark/text-white` on phase-target templates.
- [ ] `tests/ui/test_turnstile_theme_alignment.py` - verifies auth/report turnstile theme follows light-mode policy.
- [ ] `tests/ui/test_mobile_layout_smoke.py` - checks critical container classes/markup needed for small screens on report/quiz.
- [ ] `tests/ui/__init__.py` - enables organized test discovery for UI checks.
- [ ] Add `beautifulsoup4` to support template static analysis tests if chosen.

## Sources

### Primary (HIGH confidence)

- Project source files (`templates/base.html`, `templates/login.html`, `templates/register.html`, `templates/profile.html`, `templates/quiz.html`, `templates/report_scammer.html`, `templates/leaderboard.html`, `templates/scammer_profile.html`, `static/css/style.css`, `static/css/base.css`, `static/css/quiz.css`) - verified current implementation hotspots.
- <https://getbootstrap.com/docs/5.3/customize/css-variables/> - root/component variable strategy and variable behavior.
- <https://getbootstrap.com/docs/5.3/customize/color-modes/> - `data-bs-theme` scoping model and light/dark behavior.
- <https://getbootstrap.com/docs/5.3/layout/breakpoints/> - mobile-first breakpoint architecture.
- <https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html> - WCAG AA contrast thresholds.

### Secondary (MEDIUM confidence)

- npm registry version metadata via `npm view` for Bootstrap/AOS/Font Awesome latest versions and publish times.

### Tertiary (LOW confidence)

- None.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - backed by official Bootstrap docs + current project dependencies.
- Architecture: HIGH - based on direct codebase analysis and established Bootstrap variable patterns.
- Pitfalls: HIGH - derived from concrete template/CSS evidence in current phase scope.

**Research date:** 2026-03-20
**Valid until:** 2026-04-19
