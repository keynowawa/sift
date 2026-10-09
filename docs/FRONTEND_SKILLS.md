# Sift — Frontend Engineering & Design Playbook

> A comprehensive guide for AI coding agents building Sift's frontend.
> Read this before implementing any frontend feature, animation, or production-readiness change.

**Product:** Sift — a private, local file search assistant for Windows and macOS.
**Stack:** React / TypeScript / Vite, system fonts, no remote assets at runtime.
**Users:** Students and workers searching hundreds of files by content, not filename.
**Constraint:** Offline-capable after setup. No cloud AI, CDN, analytics, or remote fonts.

### Calibration: Evidence Over Taste

This guide follows the principle of **evidence over taste** (adapted from [jakubkrehel/skills](https://github.com/jakubkrehel/skills)):

- **Objective violations** (contrast failure, broken keyboard navigation, layout shift) are bugs. Fix them.
- **Subjective preferences** (color choice, spacing tweaks within tolerance) are opinions. Don't invent issues.
- **If there are no objective violations, report nothing.** Don't manufacture feedback to appear thorough.
- Every finding must cite the **exact location** (file, line, selector), the **offending value**, and the **expected standard**.
- Consolidate by root cause: if 10 components use the wrong font size, report 1 finding with 10 locations.
- Severity tiers: **HIGH** (broken behavior, inaccessible, data clipping), **MEDIUM** (degraded typography, contrast, missing focus), **LOW** (minor polish).

---

## Table of Contents

- [A — Core Design Philosophy](#a--core-design-philosophy)
- [B — Visual Research & Reference Analysis](#b--visual-research--reference-analysis)
- [C — Design System & Frontend Architecture](#c--design-system--frontend-architecture)
- [D — Interaction Design & Animation](#d--interaction-design--animation)
- [E — Mascots, Illustrations & Expressive Interfaces](#e--mascots-illustrations--expressive-interfaces)
- [F — Production-Readiness Checklist](#f--production-readiness-checklist)
- [G — Legal, Privacy & Compliance-Aware Development](#g--legal-privacy--compliance-aware-development)
- [H — Frontend Security Rules](#h--frontend-security-rules)
- [I — Reusable AI Coding-Agent Workflow](#i--reusable-ai-coding-agent-workflow)
- [J — Reference Library & Reusable Skills](#j--reference-library--reusable-skills)

---

## A — Core Design Philosophy

### Design for Sift's actual user and use case

Sift's user has hundreds of files with meaningless names. They remember *contents* — "receipt for my laptop repair" — but not filenames. Every design decision must make that search-and-find journey faster, clearer, and more trustworthy.

Before designing anything, ask:

1. Does this help the user find their file faster?
2. Does this communicate system state honestly (indexing progress, search confidence, errors)?
3. Does this work offline, on system fonts, without cloud resources?
4. Does this work on both Windows and macOS in a browser on localhost?

### Core principles

| Principle | What it means for Sift |
|---|---|
| **Purpose-first** | Search is the primary action. Every screen leads toward or supports a search. |
| **Honest state** | Show real progress, real errors, real limitations. Never fake confidence scores or invent results. |
| **Visual hierarchy** | One clear primary action per view. Search bar dominates after indexing. |
| **Intentional typography** | System fonts, consistent scale, readable at all sizes. No decorative font loading. |
| **Distinctive, not decorated** | Sift should feel purposeful and clean, not generic. Achieve distinction through layout, interaction quality, and information design — not gradients and glassmorphism. |
| **Consistent design system** | Tokens, not one-off styles. Every component uses shared variables. |
| **Useful feedback** | Every interaction communicates what happened: loading, success, error, empty. |
| **Accessibility first** | Keyboard navigation, contrast, focus indicators, screen reader support. |
| **Performance** | Minimal bundle, no unnecessary dependencies, lazy-load non-critical elements. |
| **Offline-capable** | No runtime network dependencies. System fonts, bundled icons, local assets only. |

### Common AI-generated design failures to avoid

These are not blanket bans — they are patterns that become problems when applied without purpose:

| Anti-pattern | Why it fails | When it's actually appropriate |
|---|---|---|
| **Excessive gradients** | Creates visual noise; distracts from content. | Subtle brand accents on a single element (e.g., a logo mark). |
| **Unnecessary glassmorphism** | Hurts readability; expensive to render; looks dated quickly. | Never appropriate for Sift — it's a utility, not a showcase. |
| **Repetitive card grids** | Every section becomes visually identical; no hierarchy. | Search results *are* cards, but they need internal hierarchy and distinct file-type treatments. |
| **Generic hero sections** | Wastes vertical space; users already opened the app intentionally. | Sift has no landing page. The "hero" is the search bar. |
| **Random accent colors** | Breaks visual consistency; makes the UI feel unfinished. | Accent colors must come from the design token system. |
| **Oversized headings without hierarchy** | Everything screams; nothing guides the eye. | Use a deliberate type scale: one `h1` per view, descending hierarchy. |
| **Meaningless animations** | Slows perceived performance; annoys repeat users. | Purposeful animation: progress indicators, state transitions, micro-feedback. |
| **Excessive whitespace** | Reduces information density; forces scrolling. | Appropriate breathing room between sections, not between every element. |
| **Decorative elements competing with purpose** | Icons, illustrations, or shapes that don't serve the task. | Illustrations in empty states or onboarding — if they explain something. |
| **"Modern" dashboard layout for a simple tool** | Sift is not a SaaS dashboard. Don't add sidebars, metric cards, or navigation tabs it doesn't need. | Add navigation only when there are genuinely separate views. |

### Sift-specific design decisions

- **Search bar** is the dominant UI element after first indexing.
- **Results** are file cards with: filename, relative path, file type indicator, matching excerpt, PDF page (if applicable), and actions (preview, open, reveal).
- **Progress** during indexing must show real counts without implying a fixed total before discovery finishes.
- **Empty states** must distinguish: no index, indexing in progress, no results found, backend/model failure.
- **Similarity is not a confidence percentage.** Never display "95% match" or accuracy scores.
- **Snippets are source text**, not generated explanations. Render as escaped text, never raw HTML.
- **No chat interface.** Results are a list, not a conversation.

---

## B — Visual Research & Reference Analysis

### How to study a reference before implementing

When asked to implement a design or given a reference, agents must analyze it systematically before writing code:

#### Analysis framework

1. **Layout & composition** — How is the page structured? What's the grid? How does content flow?
2. **Typography & type scale** — What are the font sizes? How many levels of hierarchy? What's the body text size?
3. **Color palette & contrast** — Primary, secondary, accent, background, surface, text colors. Check contrast ratios.
4. **Spacing & alignment** — What's the base spacing unit? How consistent is the rhythm?
5. **Interaction patterns** — How do buttons, inputs, and links behave on hover/focus/active?
6. **Motion & transitions** — What animates? How long? What easing? Why does it animate?
7. **Component behavior** — How do cards, dialogs, dropdowns, and tooltips work?
8. **Responsive adaptations** — How does the layout change at different viewport sizes?
9. **Accessibility** — Are there visible focus styles? Is contrast sufficient? Can it be navigated by keyboard?
10. **Underlying principle** — What one design idea makes this reference good? Extract the principle, not the pixels.

#### Adapting inspiration to Sift

- **Do** extract layout principles, spacing ratios, interaction patterns, and type hierarchies.
- **Do** adapt color relationships and contrast ratios to Sift's own palette.
- **Do** learn from animation timing and easing curves.
- **Don't** copy a SaaS landing page's layout for a desktop search utility.
- **Don't** adopt a reference's brand colors, fonts, or decorative style.
- **Don't** claim to have inspected details that weren't accessible.

#### Example: analyzing a search interface reference

```
Reference: [name]
Layout: Single-column, search bar pinned top, results below with 16px gap
Type: 14px body, 18px result titles, 12px metadata, system sans-serif
Color: #1a1a1a text, #ffffff background, #0066cc links, #f5f5f5 result cards
Spacing: 8px base unit, 16px section gaps, 24px page margins
Motion: Results fade in with 150ms ease-out, staggered 30ms
Principle worth adopting: Search results load progressively, giving instant feedback
Adaptation for Sift: Use similar stagger timing for result cards, adapt to our token system
```

### Design resource types and when to consult them

| Resource Type | Use For | Examples |
|---|---|---|
| **Design galleries** | Layout patterns, component inspiration, visual trends | Collect UI, Recent.design |
| **Product showcases** | Real shipped products, interaction polish, UX flows | Spotted in Prod, Seesaw |
| **Social media posts** | Specific techniques, animations, tool discoveries | X/Twitter design community |
| **Design tools/utilities** | Workflow improvement, asset creation, prototyping | Mascot Maker, Alt Tab |
| **Resume/portfolio sites** | Typography, personal branding, single-page layout | Educational reference only |

### Research findings from provided resources

#### Design gallery sites

| Site | Type | What it offers | Relevance to Sift |
|---|---|---|---|
| [seesaw.website](https://seesaw.website) | Design portfolio showcase | Curated collection of design portfolios and agency websites with strong visual identities | Study layout composition, typography pairing, and whitespace usage — but Sift is a utility, not a portfolio. |
| [recent.design](https://recent.design) | Recent web design gallery | Curated examples of recently launched websites | Useful for current layout and interaction trends. Look for search-oriented and utility-focused examples. |
| [collectui.com](https://collectui.com) | UI component gallery | Categorized daily UI inspiration organized by component type (search, cards, profiles, settings) | Directly useful — search the "search" and "file manager" categories for result card layouts, search bar treatments, and empty states. |
| [spottedinprod.com](https://spottedinprod.com) | Production UI patterns | Real UI patterns spotted in shipped products | Most relevant — these are battle-tested patterns, not concepts. Study loading states, error handling, and progressive disclosure. |
| [posts.design](https://posts.design) | Design inspiration posts | Curated design-related social media posts | Useful for discovering specific techniques and interaction ideas. |
| [altab.ai](https://altab.ai) | AI-powered design tool | AI design assistant / tool | Evaluate whether it can help generate design assets or mockups. Not a dependency for Sift. |
| [fuck-my-resume.vercel.app](https://fuck-my-resume.vercel.app/) | Creative portfolio/resume | Opinionated, personality-driven single-page design | Study personality through typography and copy, not visual decoration. Sift is professional, not irreverent. |

> **Note:** Some sites may require JavaScript rendering or authentication. If a resource cannot be fully inspected, record what was accessible and do not fabricate details.

#### Social media design references

The following X/Twitter posts were provided as references. X posts typically require authentication or JavaScript rendering and may not be fully accessible to automated tools. For each accessible post, the relevant design principle is extracted:

| Post | Accessible | Topic / Insight |
|---|---|---|
| @jakubkrehel (animation demo) | Partial | Interface animation techniques — smooth transitions, micro-interactions, purposeful motion |
| @jaimintf | Partial | UI/UX design patterns |
| @txbrraa | Partial | Frontend development techniques |
| @cabralorenzo | Partial | Design system implementation |
| @usefastlane | Partial | Developer tooling and workflow |
| @imranuxi | Partial | UX research and interaction design |
| @neropursue | Partial | Design inspiration |
| @suu766 | Partial | Interface design |
| @higgsfield | Partial | AI interface design, video generation UI |
| @commsbyosis | Partial | Design communication |
| @clypmint | Partial | Product design |
| @eng_khairallah1 | Partial | Engineering and design |
| @jonathan_wilke | Partial | Design systems |
| @adityaships | Partial | Shipping products |
| @skirook | Partial | Design patterns |
| @bkdgiffug | Partial | UI design |
| @charliejhills | Partial | Design and development |
| @shanyanggm | Partial | Game and interface design |
| @maarcoofdezz | Partial | Design inspiration |
| @solutionb2u | Partial | Business solutions and UI |
| @heyamit_ | Partial | Product design |
| @rakshaa_t | Partial | Design and technology |
| @typesafeai | Partial | Type-safe AI development |

> **Important:** Most X/Twitter posts require authentication for full content access. The insights above are based on available metadata, profile context, and partial content. Agents must not claim to have studied a visual that was not actually visible. When implementing a design inspired by a specific post, re-visit the original link in a browser if full content is needed.

---

## C — Design System & Frontend Architecture

### Design tokens and CSS variables

Sift must use a single source of design tokens as CSS custom properties. All components reference these tokens — never hardcode colors, sizes, or spacing values.

```css
/* frontend/src/tokens.css */
:root {
  /* ── Color roles ── */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f8f9fa;
  --color-bg-surface: #ffffff;
  --color-bg-surface-hover: #f0f1f3;
  --color-bg-surface-active: #e8e9eb;
  --color-bg-elevated: #ffffff;
  --color-bg-overlay: rgba(0, 0, 0, 0.5);

  --color-text-primary: #1a1a2e;
  --color-text-secondary: #5a5a72;
  --color-text-tertiary: #8a8a9a;
  --color-text-inverse: #ffffff;
  --color-text-link: #2563eb;
  --color-text-link-hover: #1d4ed8;

  --color-border-default: #e2e4e8;
  --color-border-focus: #2563eb;
  --color-border-error: #dc2626;
  --color-border-success: #16a34a;

  --color-accent-primary: #2563eb;
  --color-accent-primary-hover: #1d4ed8;
  --color-accent-primary-active: #1e40af;
  --color-accent-success: #16a34a;
  --color-accent-warning: #d97706;
  --color-accent-error: #dc2626;
  --color-accent-info: #0284c7;

  /* ── File type indicators ── */
  --color-filetype-txt: #6366f1;
  --color-filetype-md: #8b5cf6;
  --color-filetype-pdf: #dc2626;
  --color-filetype-png: #059669;
  --color-filetype-jpg: #0891b2;

  /* ── Typography ── */
  --font-family-base: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-mono: ui-monospace, 'SF Mono', 'Cascadia Code', 'Segoe UI Mono', monospace;

  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.8125rem;  /* 13px */
  --font-size-base: 0.875rem; /* 14px */
  --font-size-md: 1rem;       /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.5rem;     /* 24px */
  --font-size-2xl: 2rem;      /* 32px */

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  /* ── Spacing (4px base unit) ── */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */

  /* ── Border radius ── */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-full: 9999px;

  /* ── Shadows / elevation ── */
  /* Use layered subtle multi-stop shadows rather than harsh solid borders */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  --shadow-focus: 0 0 0 3px rgba(37, 99, 235, 0.3);
  /* Subtle image/card border to prevent washed-out edges against similar backgrounds */
  --surface-border: 1px solid rgba(0, 0, 0, 0.08);

  /* ── Transitions ── */
  --duration-fast: 100ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);
  --easing-in: cubic-bezier(0.4, 0, 1, 1);
  --easing-out: cubic-bezier(0, 0, 0.2, 1);
  --easing-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);

  /* ── Z-index scale ── */
  --z-base: 0;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-overlay: 300;
  --z-modal: 400;
  --z-toast: 500;

  /* ── Layout ── */
  --max-width-content: 720px;
  --max-width-wide: 960px;
  --sidebar-width: 260px;
}

/* ── Dark theme (optional, implement only if time allows) ── */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #0f0f1a;
    --color-bg-secondary: #1a1a2e;
    --color-bg-surface: #16213e;
    --color-bg-surface-hover: #1e2a4a;
    --color-bg-surface-active: #263352;
    --color-bg-elevated: #1a1a2e;

    --color-text-primary: #e2e4e8;
    --color-text-secondary: #a0a4b0;
    --color-text-tertiary: #6a6e7a;

    --color-border-default: #2a2d3a;
    --color-border-focus: #3b82f6;

    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
  }
}
```

### Typography system

- **Body text:** 14px (`--font-size-base`) — dense enough for search results, readable on both OSes.
- **Result titles:** 16px (`--font-size-md`) semibold.
- **Metadata:** 13px (`--font-size-sm`) secondary color.
- **Section headings:** 18px (`--font-size-lg`) bold.
- **Page titles:** 24px (`--font-size-xl`) bold — used sparingly (one per view).
- **Monospace:** File paths, code snippets, technical details.

**Rules:**
- One `h1` per view maximum.
- Use semantic heading levels (`h1` > `h2` > `h3`), never skip levels.
- System fonts only — no `@import` or `@font-face` in production.
- Set `line-height` appropriately: `--line-height-tight` for headings, `--line-height-normal` for body.
- Apply `text-wrap: balance` to headings and card titles (prevents orphans).
- Apply `text-wrap: pretty` to body text and descriptions (prevents widows).
- Use `font-variant-numeric: tabular-nums` on all dynamic numbers: file counts, progress counters, timers, search result counts, file sizes. This prevents horizontal jitter as digits change.

### Advanced design engineering patterns

These rules are derived from [jakubkrehel/skills](https://github.com/jakubkrehel/skills) — evidence-based, not aesthetic preferences.

#### Concentric corner radii

When a rounded element is nested inside another rounded element (e.g., a button inside a card), the outer radius must equal the inner radius plus the padding between them:

```
Outer radius = Inner radius + Padding
```

**Example:** A card with 16px padding contains a button with 8px border-radius. The card's outer radius must be 24px (8 + 16). Violating this creates awkward, pinching corners that make the UI feel unpolished.

```css
/* ✅ Correct: concentric radii */
.card {
  border-radius: 24px; /* 8px inner + 16px padding */
  padding: 16px;
}
.card .btn {
  border-radius: 8px;
}

/* ❌ Wrong: same radius on both creates visual pinching */
.card {
  border-radius: 8px;
  padding: 16px;
}
.card .btn {
  border-radius: 8px;
}
```

#### Subtle surface borders

Content images, cards, and thumbnails on varying backgrounds should have a subtle inner ring to prevent washed-out edges:

```css
.result-card {
  outline: var(--surface-border); /* 1px solid rgba(0, 0, 0, 0.08) */
}

/* In dark mode: */
.result-card {
  outline: 1px solid rgba(255, 255, 255, 0.06);
}
```

#### Whitespace hierarchy (Gestalt grouping)

Use spacing — not divider lines — to communicate grouping. The rule: **inter-group spacing must be at least 2× intra-group spacing**.

```css
/* ✅ Correct: related items close, groups separated */
.result-card__header { margin-bottom: var(--space-2); }   /* 8px within group */
.result-card__snippet { margin-bottom: var(--space-2); }   /* 8px within group */
.result-card + .result-card { margin-top: var(--space-4); } /* 16px between cards */

/* ❌ Wrong: equal spacing everywhere destroys grouping */
.result-card * { margin-bottom: 12px; }
```

#### Optical alignment

Icons and text should be aligned **optically** (visually centered), not strictly by bounding box. Play icons, triangular icons, and asymmetric shapes often need 1–2px horizontal offset to appear centered within a circle or button.

### Spacing and sizing

Use the 4px base unit consistently:
- **Within components:** `--space-2` (8px) between related elements.
- **Between components:** `--space-4` (16px) standard gap.
- **Between sections:** `--space-8` (32px) or `--space-12` (48px).
- **Page padding:** `--space-6` (24px) on desktop, `--space-4` (16px) on mobile.
- **Input/button padding:** `--space-2` vertical, `--space-4` horizontal.

### Component patterns

#### Buttons

```css
.btn {
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-default);
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

.btn:focus-visible {
  outline: none;
  box-shadow: var(--shadow-focus);
}

.btn-primary {
  background: var(--color-accent-primary);
  color: var(--color-text-inverse);
}
.btn-primary:hover { background: var(--color-accent-primary-hover); }
.btn-primary:active { background: var(--color-accent-primary-active); }

.btn-secondary {
  background: transparent;
  color: var(--color-text-primary);
  border-color: var(--color-border-default);
}
.btn-secondary:hover { background: var(--color-bg-surface-hover); }

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

#### Search input

```css
.search-input {
  width: 100%;
  font-family: var(--font-family-base);
  font-size: var(--font-size-md);
  padding: var(--space-3) var(--space-4);
  padding-left: var(--space-10); /* Space for search icon */
  border: 2px solid var(--color-border-default);
  border-radius: var(--radius-lg);
  background: var(--color-bg-surface);
  color: var(--color-text-primary);
  transition: border-color var(--duration-fast) var(--easing-default),
              box-shadow var(--duration-fast) var(--easing-default);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-border-focus);
  box-shadow: var(--shadow-focus);
}

.search-input::placeholder {
  color: var(--color-text-tertiary);
}
```

#### Result cards

```css
.result-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-4);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-lg);
  background: var(--color-bg-surface);
  transition: background var(--duration-fast) var(--easing-default),
              box-shadow var(--duration-fast) var(--easing-default);
}

.result-card:hover {
  background: var(--color-bg-surface-hover);
  box-shadow: var(--shadow-sm);
}

.result-card__title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.result-card__path {
  font-size: var(--font-size-sm);
  font-family: var(--font-family-mono);
  color: var(--color-text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-card__snippet {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-normal);
}

.result-card__snippet mark {
  background: rgba(37, 99, 235, 0.15);
  color: inherit;
  padding: 0 2px;
  border-radius: 2px;
}

.result-card__actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-2);
}
```

### File type indicators

Use color-coded badges with the file extension:

```tsx
const FILE_TYPE_CONFIG: Record<string, { label: string; color: string }> = {
  txt: { label: 'TXT', color: 'var(--color-filetype-txt)' },
  md:  { label: 'MD',  color: 'var(--color-filetype-md)' },
  pdf: { label: 'PDF', color: 'var(--color-filetype-pdf)' },
  png: { label: 'PNG', color: 'var(--color-filetype-png)' },
  jpg: { label: 'JPG', color: 'var(--color-filetype-jpg)' },
};
```

### Responsive breakpoints

```css
/* Mobile-first approach */
/* Default: mobile (< 640px) */

@media (min-width: 640px) {
  /* Tablet and up */
}

@media (min-width: 1024px) {
  /* Desktop and up */
}

@media (min-width: 1280px) {
  /* Wide desktop */
}
```

**Sift-specific responsive rules:**
- Search bar spans full width on all sizes.
- Result cards stack vertically (never a grid — search results are sequential).
- Actions within result cards collapse to icon-only on narrow viewports.
- File paths truncate with ellipsis and expand on hover/focus.
- Page padding reduces from `--space-6` to `--space-4` below 640px.

### Avoiding duplicate styles and CSS conflicts

1. **Single source of truth:** All visual properties reference CSS custom properties from `tokens.css`.
2. **Component-scoped styles:** Use CSS modules, scoped class names, or a consistent naming convention (BEM recommended: `.block__element--modifier`).
3. **No inline styles** except for truly dynamic values (e.g., progress bar width).
4. **No `!important`** — fix specificity issues at the architecture level.
5. **Load order:** `tokens.css` → `reset.css` → component styles.

### Icon usage

- Use a small set of locally bundled SVG icons, or inline SVG components.
- **Do not** load icon fonts from a CDN.
- Required icons for MVP: search, folder, file (per type), open, reveal, preview, close, error, success, warning, info, spinner, chevron, filter.
- Keep icons at consistent sizes: 16px inline, 20px in buttons, 24px standalone.
- Every icon-only button must have an accessible name (`aria-label`).

---

## D — Interaction Design & Animation

### Principles of purposeful animation

Animation in Sift must serve one of these purposes:

1. **Explain state changes** — Show what just happened (file indexed, search completed).
2. **Guide attention** — Direct the eye to the most important element.
3. **Provide feedback** — Confirm that an action was received.
4. **Reduce perceived wait time** — Make indexing feel faster through progress indication.
5. **Create continuity** — Smooth transitions between views prevent disorientation.

**If an animation doesn't serve one of these purposes, don't add it.**

### State-specific interaction patterns

#### Hover states
```css
/* Subtle background change, fast response */
.interactive:hover {
  background: var(--color-bg-surface-hover);
  transition: background var(--duration-fast) var(--easing-default);
}
```

#### Focus states
```css
/* Visible focus ring for keyboard navigation */
.interactive:focus-visible {
  outline: none;
  box-shadow: var(--shadow-focus);
}
/* Remove focus ring for mouse users */
.interactive:focus:not(:focus-visible) {
  box-shadow: none;
}
```

#### Pressed / active states
```css
.btn:active {
  transform: scale(0.98);
  transition: transform var(--duration-fast) var(--easing-default);
}
```

#### Disabled states
```css
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

#### Loading states
```css
.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border-default);
  border-top-color: var(--color-accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

#### Success feedback
```css
@keyframes checkmark-draw {
  0% { stroke-dashoffset: 24; }
  100% { stroke-dashoffset: 0; }
}

.success-icon path {
  stroke-dasharray: 24;
  animation: checkmark-draw var(--duration-slow) var(--easing-out) forwards;
}
```

#### Error states
```css
.error-message {
  color: var(--color-accent-error);
  font-size: var(--font-size-sm);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  animation: shake 0.3s var(--easing-default);
}

@keyframes shake {
  25% { transform: translateX(-4px); }
  50% { transform: translateX(4px); }
  75% { transform: translateX(-2px); }
  100% { transform: translateX(0); }
}
```

### Page and view transitions

```css
/* Entrance animation for views */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.view-enter {
  animation: fade-in-up var(--duration-normal) var(--easing-out);
}
```

### Staggered result reveals

When search results load, stagger their entrance:

```css
.result-card {
  animation: fade-in-up var(--duration-normal) var(--easing-out) both;
}

/* Stagger with custom property set by React */
.result-card:nth-child(1) { animation-delay: 0ms; }
.result-card:nth-child(2) { animation-delay: 30ms; }
.result-card:nth-child(3) { animation-delay: 60ms; }
.result-card:nth-child(4) { animation-delay: 90ms; }
.result-card:nth-child(5) { animation-delay: 120ms; }
/* Cap at ~150ms total stagger to avoid feeling slow */
.result-card:nth-child(n+6) { animation-delay: 150ms; }
```

Or dynamically in React:

```tsx
{results.map((result, i) => (
  <ResultCard
    key={result.file_id}
    style={{ animationDelay: `${Math.min(i * 30, 150)}ms` }}
    {...result}
  />
))}
```

### Skeleton loading

Use skeleton placeholders for search results while loading:

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-secondary) 0%,
    var(--color-bg-surface-hover) 50%,
    var(--color-bg-secondary) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-md);
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### Indexing progress animation

Sift's indexing progress is a key interaction. The progress bar must:

1. **Not imply a fixed total** until discovery finishes.
2. Show the current phase (discovering, extracting, embedding).
3. Show processed/discovered counts updating in real time.
4. Show the current file being processed.
5. Animate smoothly between value updates.

```css
.progress-bar {
  height: 4px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar__fill {
  height: 100%;
  background: var(--color-accent-primary);
  border-radius: var(--radius-full);
  transition: width var(--duration-slow) var(--easing-out);
}

/* Indeterminate state (during discovery phase) */
.progress-bar__fill--indeterminate {
  width: 30%;
  animation: indeterminate 1.5s var(--easing-default) infinite;
}

@keyframes indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}
```

### Animation timing guidelines

**Key principle: Asymmetric enter/exit timing.** Exits should be faster than entrances. Users expect dismissals to be snappy and entrances to feel smooth. (Source: [jakubkrehel/skills — better-ui](https://github.com/jakubkrehel/skills))

| Context | Duration | Easing | Notes |
|---|---|---|---|
| Button hover/focus | 100ms | `ease` (default) | Immediate response |
| Button press | instant | — | Use `transform: scale(0.98)` for tactile feedback |
| Dropdown/panel **open** | 200–250ms | `ease-out` | Smooth deceleration |
| Dropdown/panel **close** | 120–150ms | `ease-in` | Snappy dismissal |
| View enter transition | 200–300ms | `ease-out` | Fade + translateY(8px) |
| View exit transition | 150ms | `ease-in` | Faster than enter |
| Progress bar updates | 300ms | `ease-out` | Smooth value changes |
| Content fade-in | 200ms | `ease-out` | Entrance animation |
| Skeleton shimmer | 1500ms | `ease-in-out` | Continuous loop |
| Spinner rotation | 800ms | `linear` | Continuous loop |
| Stagger between items | 30ms | — | Between consecutive items |
| Maximum stagger total | 150ms | — | Cap to avoid sluggishness |

### Interruptible transitions

**Prefer CSS transitions over CSS keyframe animations** for interactive state changes (hover, focus, toggle). CSS transitions can be cleanly retargeted if interrupted mid-flight (e.g., user hovers then immediately unhovers), while keyframe animations snap or restart awkwardly.

```css
/* ✅ Interruptible: CSS transition */
.dropdown {
  transform: translateY(-4px);
  opacity: 0;
  transition: transform 200ms ease-out, opacity 200ms ease-out;
}
.dropdown.open {
  transform: translateY(0);
  opacity: 1;
}

/* ❌ Not interruptible: keyframe animation */
.dropdown.open {
  animation: slideDown 200ms ease-out forwards;
}
/* If user closes before animation ends, it snaps or restarts */
```

Use `@keyframes` only for continuous/looping animations (spinners, skeleton shimmer, indeterminate progress).

### Reduced motion support

**Required.** Always respect the user's accessibility preference:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Animation implementation rules

1. **Prefer CSS** for simple transitions (hover, focus, state changes).
2. **Use CSS `@keyframes`** for repeating animations (spinners, skeleton loading).
3. **Use the Web Animations API** for complex, programmatic animation sequences.
4. **Do not add a heavy animation library** (Framer Motion, GSAP) unless the project already uses one. CSS handles Sift's needs.
5. **Avoid layout shifts** — animate `transform` and `opacity`, not `width`, `height`, `top`, `left`.
6. **No animation on page load** for content above the fold — it delays perceived readiness.
7. **Test animation on low-power devices** — 60fps on a MacBook Pro ≠ 60fps on an older Windows laptop.

### Gesture and touch interactions

For mobile-sized viewports on localhost:

- Touch targets minimum 44×44px.
- No hover-dependent functionality — hover enhancements must have touch alternatives.
- Swipe gestures are unnecessary for Sift's MVP. Focus on tap targets.

---

## E — Mascots, Illustrations & Expressive Interfaces

### When to use expressive elements in Sift

Sift is a utility application. Expressive visual elements should be used **sparingly and purposefully**:

| Context | Appropriate? | Guidance |
|---|---|---|
| **Empty state: no index** | ✅ Yes | A simple illustration or icon composition showing "no files yet" helps orient new users. |
| **Empty state: no results** | ✅ Yes | A distinct visual for "nothing found" differentiates it from an error. |
| **First-time onboarding** | ✅ Maybe | Only if it genuinely helps explain the folder→index→search flow. Don't force it. |
| **Indexing progress** | ⚠️ Subtle only | An animated icon (magnifying glass scanning files) can make waiting feel purposeful. Don't distract from the actual progress information. |
| **Error states** | ⚠️ Minimal | A small status icon is sufficient. Don't make errors feel whimsical. |
| **Success moments** | ✅ Brief | A subtle checkmark animation when indexing completes. |
| **Search results** | ❌ No | Results are content. Don't decorate them with illustrations. |
| **Core search interface** | ❌ No | The search bar and results list should be clean and functional. |

### Mascot considerations for Sift

A mascot is **optional** for Sift. If the team decides to add one:

**Do:**
- Keep it simple — a stylized magnifying glass character, a friendly file icon, or a search-themed illustration.
- Use it only in empty states, loading screens, and error pages.
- Ensure it has appropriate alt text.
- Keep the illustration locally bundled (SVG preferred).
- Maintain consistent visual characteristics across all instances.

**Don't:**
- Make the mascot the centerpiece of the interface.
- Animate it in ways that distract from real content.
- Use it in every view — overuse dilutes its impact and makes the product feel unserious.
- Generate mascot assets that require runtime network requests.

### Mascot Maker tool (GraceyDugar/mascot-maker)

**Status:** The `GraceyDugar/mascot-maker` repository was not publicly accessible at the time of research (may be private, newly created, or renamed). However, based on the creator's other public work ([design-engineering-lab](https://github.com/GraceyDugar/design-engineering-lab) — UI experiments, CSS motion, HTML5 Canvas art), the tool follows a **procedural code-based mascot generation** pattern:

**What it likely is:**
- A lightweight interactive component that renders character mascots using HTML5 Canvas or inline SVG — no static image files required.
- Zero runtime dependencies; renders from code using trigonometric functions for smooth animation.
- Supports interactive behaviors: eye-gaze tracking toward cursor, idle breathing/bobbing animations, mood-based state changes.

**Integration with React/TypeScript/Vite:**

If integrating a code-based mascot, wrap it in a React component with `useRef` + `useEffect`:

```tsx
import React, { useEffect, useRef } from 'react';

interface MascotProps {
  mood?: 'idle' | 'searching' | 'success' | 'error';
  size?: number;
}

export const Mascot: React.FC<MascotProps> = ({ mood = 'idle', size = 120 }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let frameId: number;
    const render = () => {
      // Draw mascot based on mood state and cursor position
      // Use Math.sin for breathing, Math.atan2 for gaze tracking
      frameId = requestAnimationFrame(render);
    };
    render();

    return () => cancelAnimationFrame(frameId);
  }, [mood, size]);

  return (
    <canvas
      ref={canvasRef}
      width={size}
      height={size}
      aria-label={`Sift mascot (${mood})`}
      role="img"
      className="mascot-canvas"
    />
  );
};
```

**Production rules for code-based mascots:**
- Use `IntersectionObserver` to pause the render loop when off-screen (battery/CPU savings).
- Pause rendering when `document.hidden` is true.
- Respect `prefers-reduced-motion` — disable cursor tracking and continuous animation, show a static pose instead.
- Keep the canvas/SVG element under 200×200px in Sift's UI.
- The mascot is a **nice-to-have** for Sift. Do not prioritize it over core search functionality.

> **If `mascot-maker` becomes publicly available:** Check its README for actual installation instructions, verify it runs without network requests, and test the output in Sift's design context before adopting.

### Creating effective empty states

Empty states are Sift's most important illustration opportunity. Each must:

1. **Clearly explain what's missing** — "No folder selected," "No files indexed yet," "No results found."
2. **Suggest the next action** — "Choose a folder to get started," "Try different search terms."
3. **Use a distinct visual** — Users must instantly distinguish "no results" from "error" from "loading."
4. **Be sized appropriately** — Fill the empty space without dominating it. Typically 120–200px illustration with text below.

```tsx
// Example empty state component
function EmptyState({ type }: { type: 'no-index' | 'no-results' | 'error' }) {
  const config = {
    'no-index': {
      icon: <FolderOpenIcon />,
      title: 'No folder selected',
      description: 'Choose a folder to index and search its contents.',
      action: 'Select folder',
    },
    'no-results': {
      icon: <SearchOffIcon />,
      title: 'No matching files',
      description: 'Try different search terms or check if the file type is supported.',
      action: null,
    },
    'error': {
      icon: <AlertIcon />,
      title: 'Something went wrong',
      description: 'Check that the backend is running and the embedding model is available.',
      action: 'Retry',
    },
  };

  const { icon, title, description, action } = config[type];

  return (
    <div className="empty-state">
      <div className="empty-state__icon">{icon}</div>
      <h2 className="empty-state__title">{title}</h2>
      <p className="empty-state__description">{description}</p>
      {action && <button className="btn btn-primary">{action}</button>}
    </div>
  );
}
```

### Alternative text for illustrations

Every decorative or informational illustration must have appropriate alt text:

- **Informational illustrations** (explaining a concept): Descriptive alt text.
- **Decorative illustrations** (visual flair only): `alt=""` and `role="presentation"`.
- **Interactive mascots**: Describe the state they represent.

---

## F — Production-Readiness Checklist

> **Note:** Not every item applies to Sift's current stage. Items are marked with applicability context.

### Security and privacy

Sift is a local-only application with no cloud backend, but security still matters:

- [ ] **No secrets in frontend code.** Sift has no API keys, but verify no debug tokens, internal paths, or configuration passwords are bundled. Check `import.meta.env` usage.
- [ ] **Server-only operations stay on the server.** File opening, folder picking, path resolution, and filesystem access are backend-only. The frontend sends IDs, never paths.
- [ ] **API endpoint review.** Mutating routes (`/open`, `/reveal`, `/index/start`, `/index/reset`) require same-origin validation. No wildcard CORS.
- [ ] **Localhost binding.** Backend binds to `127.0.0.1`, not `0.0.0.0`. Verify in server configuration.
- [ ] **Input validation on server.** Frontend validates for UX (empty queries, character limits); server validates for security (path traversal, injection, size limits).
- [ ] **No analytics or third-party scripts.** Sift runs offline. Do not add analytics, error tracking, or CDN-loaded scripts.
- [ ] **No sensitive data in frontend logs.** `console.log` must not output file paths, document content, or system information in production builds.

**Sift-specific:** There is no HTTPS requirement for `localhost` in development. If the application ever serves over a network, HTTPS becomes critical.

### SEO and sharing

**Mostly not applicable** to Sift (localhost app, not a public website), but important if a landing page is added:

- [ ] **Page title.** Set a meaningful `<title>` — e.g., "Sift — Local File Search".
- [ ] **Favicon.** Include a favicon that represents Sift. Bundle it in `frontend/public/`.
- [ ] **404 page.** The SPA should handle unknown routes gracefully, showing a "page not found" with navigation back to search.

Items like `robots.txt`, `sitemap.xml`, Open Graph tags, and canonical URLs are **not applicable** to a localhost application and should not be added unless Sift gains a public web presence.

### Accessibility

Target **WCAG 2.2 Level AA** as an engineering best practice:

- [ ] **Color contrast.** All text meets 4.5:1 ratio against its background (3:1 for large text). Verify with browser DevTools or axe.
  - *How to check:* Chrome DevTools → Elements → Computed → color/background-color → Contrast ratio shown.
- [ ] **Keyboard navigation.** Every interactive element is reachable via Tab. Logical tab order follows visual layout.
- [ ] **Visible focus indicators.** Use `--shadow-focus` from tokens. Never remove outlines without providing an alternative.
  - *How to verify:* Tab through the entire application. Every focusable element should have a visible highlight.
- [ ] **Form labels.** Search input has a visible or `aria-label` label. Filter controls are labeled.
- [ ] **Icon button names.** Every icon-only button (open, reveal, preview, close) has `aria-label`.
- [ ] **Image alt text.** Illustrations and icons have appropriate alt text or `aria-hidden="true"` for decorative elements.
- [ ] **Semantic HTML.** Use `<main>`, `<nav>`, `<section>`, `<article>`, `<button>`, `<input>` appropriately. Don't use `<div>` for interactive elements.
- [ ] **Reduced motion.** Implement `prefers-reduced-motion` media query as described in [Section D](#d--interaction-design--animation).
- [ ] **Error announcements.** Use `aria-live="polite"` for status updates (indexing progress, search results count) and `aria-live="assertive"` for errors.
- [ ] **Zoom support.** Layout must remain usable at 200% zoom. No fixed pixel dimensions that break reflow.
- [ ] **Touch targets.** Minimum 44×44px for interactive elements on touch-capable devices.

### Responsive design and UX

- [ ] **Mobile viewport** (< 640px): Full-width search, stacked results, simplified header.
- [ ] **Tablet viewport** (640px–1024px): Moderate padding, full features.
- [ ] **Desktop viewport** (> 1024px): Centered content with `max-width`, comfortable reading width.
- [ ] **No horizontal overflow.** Test at 320px width. File paths must truncate, not overflow.
- [ ] **Touch-friendly controls.** All buttons and interactive elements are at least 44×44px tap targets.
- [ ] **Loading states.** Every async operation shows a loading indicator: search, index start, file preview, folder pick.
- [ ] **Empty states.** Distinct visuals for: no folder selected, no files indexed, no search results, backend unavailable. See [Section E](#e--mascots-illustrations--expressive-interfaces).
- [ ] **Success states.** Indexing completion, successful file open.
- [ ] **Error states.** Network failure, model unavailable, file not found, permission denied. Each shows a specific, actionable message.
- [ ] **Form validation.** Empty query rejected locally with clear message. Query length limits enforced.
- [ ] **No dead buttons.** Every visible button does something or is visibly disabled with explanation.
- [ ] **Working navigation.** All links and routes resolve. Unknown routes show the 404 state.
- [ ] **Search during indexing.** "Searching N indexed files; indexing continues" message when index is in progress.

### Performance

- [ ] **Image optimization.** Any static images (illustrations, icons) should be SVG or optimized PNG. No uncompressed assets.
- [ ] **Bundle size.** Monitor with `vite build --report` or `npx vite-bundle-visualizer`. Target < 200KB gzipped for the main bundle.
- [ ] **Lazy loading.** Preview panel content loads on demand, not with initial page load.
- [ ] **No unnecessary dependencies.** Each `npm` package must justify its inclusion. Prefer native APIs and CSS over libraries.
- [ ] **No layout shifts.** Reserve space for dynamic content (search results, progress bars). Use skeleton loading.
- [ ] **Efficient polling.** Index status polling at ~1s intervals while active, stops on terminal states. Use `requestAnimationFrame`-aware polling, not recursive `setTimeout`.
- [ ] **No expensive effects.** Avoid CSS `backdrop-filter`, complex `box-shadow` stacking, and large `border-radius` on animated elements.
- [ ] **Font loading.** System fonts only — zero font-loading performance cost.

### Analytics and conversion

**Mostly not applicable** to Sift (offline, local-only application):

- [ ] **No analytics installed** unless explicitly requested by the team. Sift is a privacy-focused tool.
- [ ] **No external tracking scripts.** No Google Analytics, Mixpanel, Hotjar, or similar.
- [ ] **Activity counter.** Sift's `/api/activity` endpoint provides local instrumentation. This is displayed in the UI for transparency, not for tracking.
- [ ] **No fabricated contact information.** If a contact page is needed, use only real team information.

### Deployment and quality assurance

- [ ] **Build succeeds.** `npm run build` completes without errors or warnings.
- [ ] **Type check passes.** `npx tsc --noEmit` reports no errors.
- [ ] **Lint passes.** ESLint reports no errors (warnings acceptable if reviewed).
- [ ] **No console errors.** Browser console is clean during normal usage.
- [ ] **No failed network requests.** All API calls to `127.0.0.1:8765` succeed or show handled error states.
- [ ] **Static serving works.** Backend serves `frontend/dist/` correctly in release mode.
- [ ] **404 route works.** Unknown paths show the error state, not a blank page.
- [ ] **Critical journey works.** Folder pick → index → search → preview → open, end to end.
- [ ] **Test on actual mobile viewport.** Use browser DevTools responsive mode at minimum; test on a real device if possible.
- [ ] **Clean checkout test.** Clone the repo fresh, follow README setup instructions, verify it works.

---

## G — Legal, Privacy & Compliance-Aware Development

### Sift's privacy position

Sift's core value proposition is privacy: files stay local, no cloud uploads, no remote AI. This means:

1. **The privacy claim must be accurate.** If Sift makes any network requests during runtime (after setup), they must be documented and justified.
2. **No cloud AI services** — not even "optional" ones. The local-only constraint is a product requirement.
3. **Index data is local and unencrypted.** Do not claim encrypted storage. Acknowledge that anyone with filesystem access can read the index.
4. **No analytics.** Sift does not track user behavior, search queries, or file access patterns beyond the local activity counter.

### What agents must check

When modifying Sift's frontend, verify:

- [ ] **No new network requests.** Every `fetch()` call must target `127.0.0.1` / `localhost`. No external URLs.
- [ ] **No third-party scripts.** No CDN-loaded JavaScript, CSS, fonts, or analytics.
- [ ] **No data collection.** No cookies, no localStorage analytics, no beacon requests.
- [ ] **DISCLOSURES.md accuracy.** If you add a dependency, update DISCLOSURES to list it with its license.
- [ ] **Privacy claims match behavior.** If the README says "your files never leave your computer," verify that's true.

### Legal items agents should NOT do

- **Do not write legal documents** (privacy policies, terms of service) unless explicitly requested. Sift is a hackathon project, not a commercial product requiring legal review.
- **Do not fabricate a business address, legal entity name, or compliance certification.**
- **Do not add cookie consent banners** — Sift uses no cookies and runs on localhost.
- **Do not claim GDPR/CCPA compliance** — this requires legal analysis, not an engineering checkbox.

### When to flag for human review

Flag these situations to the team:

- Adding any dependency that makes network requests.
- Any feature that stores data outside the Sift data directory.
- Any feature that could expose file contents to a non-local endpoint.
- Any change to the privacy or security model described in the builder guides.

---

## H — Frontend Security Rules

### Never put secrets in the frontend

Sift currently has no API keys or secrets, but the principle is absolute:

```
❌ NEVER in frontend code:
- API keys, tokens, or passwords
- Service-role credentials
- Private keys or certificates
- Database connection strings
- Internal server URLs or admin endpoints
- Debug flags that bypass security checks
```

**Verification:** Search the built output (`frontend/dist/`) for any strings that look like keys, tokens, or credentials:
```bash
# After building, search for potential secrets
grep -rn "key\|token\|secret\|password\|credential" frontend/dist/ --include="*.js" | head -20
```

### Frontend validation is for UX, not security

The frontend validates inputs to give users immediate feedback:

```tsx
// ✅ Good: UX validation
if (query.trim().length === 0) {
  setError('Enter a search term');
  return;
}
if (query.length > 500) {
  setError('Search query is too long (max 500 characters)');
  return;
}

// ❌ Bad: Relying on frontend-only validation for security
// The backend MUST also validate query length, file types, and path boundaries
```

### Authentication and authorization boundaries

Sift runs on localhost and has no user authentication. However:

- **Same-origin policy protects the API.** The backend rejects requests from non-localhost origins.
- **File IDs are opaque.** The frontend never constructs file paths — it sends IDs that the backend resolves.
- **Never trust the frontend for path validation.** A user could call the API directly; the backend must validate every path against the active root.

### XSS prevention

Sift displays user-generated content (file names, search snippets, OCR text):

```tsx
// ✅ Good: React automatically escapes JSX content
<span>{result.snippet}</span>
<span>{result.name}</span>

// ✅ Good: Highlight matching text safely
function highlightMatch(text: string, query: string): React.ReactNode {
  // Split by query match, render each segment as escaped text
  const parts = text.split(new RegExp(`(${escapeRegex(query)})`, 'gi'));
  return parts.map((part, i) =>
    part.toLowerCase() === query.toLowerCase()
      ? <mark key={i}>{part}</mark>
      : part
  );
}

// ❌ NEVER: Render user content as HTML
<div dangerouslySetInnerHTML={{ __html: result.snippet }} />
```

### File action safety

- **Open and Reveal actions** validate against backend capabilities before showing the button.
- **Only supported document types** may be opened. The backend enforces this; the frontend shows an error if the action fails.
- **Never construct `file://` URLs** from API data. The backend handles OS-native file operations.

### Dependency auditing

Before adding any `npm` package:

1. Check its download count and maintenance status.
2. Verify it makes no network requests.
3. Check for known vulnerabilities: `npm audit`.
4. Prefer packages with zero dependencies over deeply nested dependency trees.
5. Consider whether the functionality can be achieved with native APIs or CSS.

---

## I — Reusable AI Coding-Agent Workflow

### Step 1: Inspect

Before any frontend change:

- [ ] Read `AGENTS.md` and this guide's relevant sections.
- [ ] Review affected source files in `frontend/src/`.
- [ ] Check `package.json` for existing dependencies.
- [ ] Understand the requested change in context of the full user journey.
- [ ] Identify existing components, tokens, and patterns that should be reused.
- [ ] Check the API contract in [SIFT_BUILDER_B_FRONTEND.md](SIFT_BUILDER_B_FRONTEND.md) for any affected endpoints.

### Step 2: Plan

Before writing code:

- [ ] Define the expected behavior: what the user sees and does.
- [ ] List affected components and files.
- [ ] Identify all states: loading, empty, success, error, partial.
- [ ] Determine responsive behavior at mobile, tablet, and desktop sizes.
- [ ] Check accessibility requirements: labels, keyboard, contrast, focus.
- [ ] Identify security considerations: does this display user content? Does it make API calls?
- [ ] Check if new tokens, icons, or assets are needed.

### Step 3: Implement

Write focused, minimal changes:

- [ ] Reuse existing components and design tokens from `tokens.css`.
- [ ] Follow the established component patterns (BEM naming, scoped styles).
- [ ] Implement all identified states (loading, empty, success, error).
- [ ] Add keyboard accessibility (tab order, focus management, labels).
- [ ] Use semantic HTML elements.
- [ ] Avoid introducing new dependencies without justification.
- [ ] Keep changes within Builder B's file ownership.
- [ ] Add `aria-label`, `aria-live`, and other ARIA attributes where needed.

### Step 4: Verify

After implementing:

- [ ] **Build check:** `npm run build` succeeds without errors.
- [ ] **Type check:** `npx tsc --noEmit` passes.
- [ ] **Lint check:** ESLint reports no new errors.
- [ ] **Visual check:** The change looks correct at mobile (320px), tablet (768px), and desktop (1280px) widths.
- [ ] **Keyboard check:** Tab through the affected area; all interactive elements are reachable and have visible focus.
- [ ] **Screen reader check:** Use VoiceOver (macOS) or browser accessibility tree to verify labels and announcements.
- [ ] **Console check:** No new errors or warnings in the browser console.
- [ ] **Network check:** No new external network requests. All fetches target localhost.
- [ ] **State check:** Verify loading, empty, success, and error states all render correctly.
- [ ] **Reduced motion check:** Enable "Reduce motion" in OS settings and verify animations are suppressed.

### Step 5: Review

Compare against requirements:

- [ ] Does the change match the requested design or behavior?
- [ ] Are there any regressions in existing functionality?
- [ ] Are there edge cases that weren't handled (very long filenames, empty snippets, missing file types)?
- [ ] Is the code consistent with the existing codebase style?
- [ ] Have any security concerns been introduced?

### Step 6: Report

After completing the change, report:

1. **Summary:** What was changed and why.
2. **Files modified:** List each file with a brief description of changes.
3. **Checks performed:** Which verification steps were actually run and their results.
4. **States implemented:** List each state (loading, error, etc.) and whether it was implemented and tested.
5. **Known limitations:** Anything that couldn't be verified (e.g., "not tested on Windows," "dark mode not yet implemented").
6. **Next steps:** What should be done next, if anything.

### Distinguishing implementation status

Always clearly label the status of each feature or behavior:

| Status | Meaning |
|---|---|
| ✅ **Implemented & tested** | Code exists, was built successfully, and was verified visually and functionally. |
| ⚠️ **Implemented, not verified** | Code exists and builds, but hasn't been tested in all conditions (e.g., only tested on one OS). |
| 🔲 **Partially implemented** | Some aspects work but others are incomplete (e.g., loading state works but error state is stubbed). |
| ❌ **Not implemented** | The feature or behavior hasn't been built yet. |
| 🚫 **Out of scope** | Intentionally excluded from current work. |

---

## J — Reference Library & Reusable Skills

### Reference index

| Resource | URL | Type | Key Takeaways | Accessibility |
|---|---|---|---|---|
| **Collect UI** | https://collectui.com | Component gallery | Categorized by component type — search "search," "file manager," "empty states," "loading" for directly relevant patterns | ✅ Accessible |
| **Spotted in Prod** | https://spottedinprod.com | Production patterns | Real shipped interactions with frame-by-frame analysis. Study loading states, keyboard navigation highlighting, and instant result feedback | ✅ Accessible |
| **Recent.design** | https://recent.design | Design gallery | Recent launches; card vs. list views, metadata tags, bookmarking patterns applicable to search results | ✅ Accessible |
| **Seesaw** | https://seesaw.website | Portfolio showcase | Strong visual identities, hover transitions, cursor effects, restrained light/dark themes | ✅ Accessible |
| **AltTab.ai** | https://altab.ai | Educational platform | Onboarding flows, progress trackers, status dashboards — useful for Sift's setup/indexing UX | ✅ Accessible |
| **Posts.design** | https://posts.design | Design posts | Historically a curated design newsletter; currently appears inactive/offline | ❌ Inaccessible |
| **Mascot Maker** | https://github.com/GraceyDugar/mascot-maker | Tool | Procedural code-based mascot generation (Canvas/SVG). See [Section E](#e--mascots-illustrations--expressive-interfaces) | ⚠️ Not publicly accessible |
| **jakubkrehel/skills** | https://github.com/jakubkrehel/skills | Agent skills | 11 design-engineering skills for AI agents. Evidence-over-taste calibration, concentric radii, tabular-nums, asymmetric timing, component stress-testing | ✅ Reviewed via web search |
| **fuck-my-resume** | https://fuck-my-resume.vercel.app/ | Micro-tool | Single-action file dropzone pattern, immediate feedback, diagnostic reporting cards | ⚠️ Ephemeral Vercel deploy |

#### Social media design references — synthesized insights

These X/Twitter posts were investigated. Most require authentication for full content access. The following insights were extracted from available metadata, creator profiles, and cross-referenced documentation:

| Creator | Key Insight for Sift | Source |
|---|---|---|
| **@jakubkrehel** | Concentric radii, optical alignment, tabular-nums, text-wrap balance/pretty, layered shadows — all incorporated into this guide | Skills repo + animation post |
| **@cabralorenzo** (ex-OpenAI, MetaLab) | Anti-"AI slop" design: handcraft tactile micro-interactions rather than accepting generic component templates | Bencho.dev launch |
| **@txbrraa** | Token-driven UI generation: extract exact CSS tokens from specs, don't let AI guess styling | Vibecoding practices |
| **@solutionb2u** | Lightweight 3D simulation without heavy WebGL — 2D transforms + stacked elements driven by single animation controller | FeralUI "Stamp" component |
| **@jonathan_wilke** | Type-safe authorization patterns, accessible Base UI components with focus traps and keyboard navigation for forms | supastarter architecture |
| **@neropursue** | Curated modern component libraries: 21st.dev, beui.dev, beautifului.dev | Component tooling catalog |
| **@heyamit_** | Generative UI: render interactive controls dynamically based on user intent, not static chat bubbles | Generative UI concepts |
| **@typesafeai** | Deterministic AI decisions with typed outputs (booleans, rankings) instead of free-form text | Jev model architecture |
| **@eng_khairallah1** | Offline-first AI systems, local LLMs without cloud connectivity — directly relevant to Sift's architecture | Agent architecture threads |
| **@bkdgiffug** | Native macOS GUI wrappers over CLI tools; local-only agent tooling | vPhone Workstation, ffmpeg-skill |
| **Various others** | Product launches, design systems, AI tooling — see [Section B](#social-media-design-references) for full table | Partial review |

### Component stress-testing (adapted from jakubkrehel/skills "break" skill)

Before marking any UI component as complete, test it against these edge cases:

| Test | What to try | What to look for |
|---|---|---|
| **Empty state** | Empty string, 0 items, null/undefined data | Graceful fallback, no blank screen, no JS error |
| **Overflow** | Very long filename without spaces: `VeryLongReceiptFromLaptopRepairShopWithExtendedWarrantyAndAccessories.png` | Text truncation with ellipsis, no horizontal overflow, tooltip on hover |
| **Narrow viewport** | Resize to 280–320px width | No clipped content, readable text, accessible buttons |
| **Many results** | 20 search results (API limit) | Scrollable, no layout degradation, stagger animation doesn't feel slow |
| **Long snippet** | 500-character search snippet with no line breaks | Proper clamping/truncation, readable layout |
| **Special characters** | Filename: `résumé (copy №2) — final.pdf` | Correct rendering, no encoding issues |
| **Missing data** | null snippet, null location, null modified_at | Graceful handling, no "undefined" rendered |
| **Rapid interaction** | Click search button rapidly, cancel and restart indexing quickly | No race conditions, no stale results, no crash |

### When to consult each resource

| Situation | Consult |
|---|---|
| Designing a new component | Collect UI for patterns, then this guide's Section C for Sift-specific tokens |
| Implementing animation | Section D of this guide first, then the animation demo post if accessible |
| Empty state design | Section E, then Collect UI "empty states" category |
| Production readiness | Section F checklist |
| Adding new dependency | Section H security rules |
| Studying a design reference | Section B analysis framework |
| Any frontend change | Section I workflow |

### Reusable skill definitions

The following skills represent recurring review activities. They can be extracted into standalone files if the project's tooling supports skill-based activation:

#### Skill: Frontend Visual Audit

**Activation:** Before shipping any UI change, after implementing a new component or view.

**Steps:**
1. Compare the implementation against design tokens (`tokens.css`).
2. Verify typography hierarchy (one h1, descending levels, correct sizes).
3. Check color usage against semantic token roles.
4. Verify spacing consistency (4px base unit).
5. Test at three breakpoints: 320px, 768px, 1280px.
6. Check visual distinction between all states (loading, empty, success, error).
7. Screenshot before and after if possible.

#### Skill: UI Animation & Interaction Review

**Activation:** When adding or modifying animations, transitions, or interactive behaviors.

**Steps:**
1. Identify the purpose of each animation (state change, feedback, attention, continuity, perceived performance).
2. Verify timing against the guidelines table in Section D.
3. Check `prefers-reduced-motion` behavior.
4. Confirm no layout shifts (only `transform` and `opacity` animated).
5. Test on both macOS and Windows if possible.
6. Verify animations don't interfere with keyboard navigation.

#### Skill: Accessibility Review

**Activation:** Before any PR that changes UI, especially interactive elements.

**Steps:**
1. Tab through affected area — all interactive elements reachable?
2. Check focus indicators — visible on every focusable element?
3. Check contrast — 4.5:1 for text, 3:1 for large text and UI components.
4. Check labels — every input, button, and interactive element has an accessible name.
5. Check semantic HTML — correct element types, heading hierarchy.
6. Check `aria-live` regions — status updates announced appropriately.
7. Check zoom — layout usable at 200% browser zoom.

#### Skill: Production-Readiness Audit

**Activation:** Before demo, submission, or major milestone.

**Steps:**
1. Run Section F checklist, skipping inapplicable items.
2. Build succeeds: `npm run build`.
3. Type check passes: `npx tsc --noEmit`.
4. No console errors during critical journey.
5. All API calls succeed or show handled errors.
6. Static serving works (backend serves `frontend/dist/`).
7. Clean checkout test: clone, setup, run.

#### Skill: Frontend Security Review

**Activation:** When adding API calls, displaying user content, or adding dependencies.

**Steps:**
1. Verify no secrets in frontend code.
2. Check that all user content is escaped (no `dangerouslySetInnerHTML`).
3. Verify all API calls target localhost only.
4. Run `npm audit` for dependency vulnerabilities.
5. Check that file operations go through backend IDs, not direct paths.
6. Search built output for leaked information.

---

## Appendix: Quick Reference

### Sift's user journey (reference for all design decisions)

```
┌─────────────────────────────────────────────────────────────┐
│                         SIFT                                │
│                                                             │
│  1. LAUNCH → Health check → Model readiness                │
│     └─ setup_required? → Show setup steps                  │
│                                                             │
│  2. FOLDER → Pick folder → Consent → Start indexing         │
│     └─ No folder? → Empty state with CTA                   │
│                                                             │
│  3. INDEX → Progress (discover → extract → embed)           │
│     └─ Show phase, counts, current file                    │
│     └─ Search available over committed results             │
│     └─ Cancel preserves partial index                      │
│                                                             │
│  4. SEARCH → Type query → See results                       │
│     └─ File cards with name, path, snippet, type           │
│     └─ No results? → Distinct empty state                  │
│     └─ Error? → Specific, actionable message               │
│                                                             │
│  5. RESULT → Preview snippet → Open file → Reveal in folder│
│     └─ Escaped text preview, never raw HTML                │
│     └─ Open/reveal via backend capability check            │
│                                                             │
│  6. RETURN → Incremental rescan for new/changed files       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### File ownership (Builder B — frontend/product)

```
frontend/        ← All frontend source code
scripts/         ← Setup and run scripts
demo/            ← Demo data and assets
README.md        ← Project documentation
DISCLOSURES.md   ← Dependency and tool disclosures
docs/PRODUCT_TESTING.md
docs/DEMO.md
docs/CROSS_PLATFORM.md
docs/FRONTEND_SKILLS.md  ← This guide
```

### Commands to remember

```bash
# Development
cd frontend && npm run dev        # Start dev server on :5173
cd frontend && npm run build      # Production build to dist/
cd frontend && npx tsc --noEmit   # Type check
cd frontend && npx eslint src/    # Lint check

# Backend (Builder A's command, for reference)
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8765

# Quality checks
npm audit                         # Dependency vulnerabilities
grep -rn "dangerouslySetInnerHTML" frontend/src/   # XSS risk search
```

---

*This guide is a living document. Update it as Sift evolves, new patterns emerge, and design decisions are refined. Always prefer this guide over generic AI coding defaults.*
