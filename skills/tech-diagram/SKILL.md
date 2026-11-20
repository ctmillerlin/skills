---
name: tech-diagram
description: >-
  Design or redesign technical diagrams (system architecture, network topology,
  data flow, multi-stage migration or cutover workflows) as a single-screen,
  self-contained HTML/SVG file. Use when the user asks to draw a diagram,
  redesign an existing diagram, or visualize how a technical design works.
---

# Technical Diagram

Produce a single-screen, self-contained HTML/SVG diagram so a reader can understand how a system or workflow works without reading long prose.

## Core Principles

- **Single-screen restraint by default**: A diagram is not a report. Unless the user explicitly asks, do not add extra hero summary cards, multiple stacked figures, progress/status tables, open-questions tables, or long prose.
- **Facts first, never fabricate**: Component names, ports, IPs, switching mechanisms, and state transitions must come from user input or verified docs/repos. If a mechanism or rationale is missing from the source material, ask the user rather than inventing an explanation.
- **Self-contained single HTML file**: Inline all CSS, JS, and SVG so the file opens offline with zero build step. Do not pull external chart/CSS/JS CDNs (only optional web font `<link>` tags with clean system-font fallbacks).
- **Choose the right mode—never force tabs**:
  - **Static single diagram**: Deployment topologies, layered architectures, or single-path data flows where one view shows everything clearly. Use [references/visual-foundation.md](./references/visual-foundation.md).
  - **Interactive state-switching diagram**: Migrations, traffic cutovers, rollouts, failover, rollback, or state machines where **paths change or are mutually exclusive across phases**. Never stack before/after or mutually exclusive routes onto one static diagram. Use both [references/visual-foundation.md](./references/visual-foundation.md) and [references/interactive-state-pattern.md](./references/interactive-state-pattern.md).

## Workflow

### 1. Align Scope & Facts

Check provided docs or quickly scan the current workspace for relevant docs/configs first. Do not re-ask anything already clear from context; ask remaining gaps in one concise batch:

- **Audience & language**: Match the target readers and source docs (ask if unclear).
- **Primary mechanism & states**: Which components, data paths, or control switches are the main story (cut unrelated details). For multi-stage workflows, confirm whether to use interactive states and the exact phase list / switching mechanism.
- **Conflicting sources**: If docs/repos contain old vs. new approaches, confirm which one to depict.
- **Output path**: Use the user-specified path or workspace convention if one exists; otherwise ask where to save the file (suggest a descriptive filename such as `<topic>-diagram.html`).

### 2. Design Layout & Visual Semantics

- **Consistent flow direction**: Arrange the primary flow along one axis (default left-to-right, e.g., Sources/Clients → Control/Routing → Core Processing → Storage/Downstream). Group cloud, cluster, or trust boundaries inside labeled zone containers to minimize line crossings.
- **Stable skeleton across states (interactive diagrams)**: Keep component positions identical across all states; change only the top status banner, per-node status pills, and active edges so readers immediately spot differences when switching tabs.
- **Distinguish three link/runtime semantics**:
  - **Active traffic**: Solid colored line; optionally add a subtle dual-layer flowing highlight (see [references/visual-foundation.md](./references/visual-foundation.md)) so active paths stay unmistakably solid in static screenshots while animating in browsers.
  - **Idle, standby, or fallback paths** (e.g., 0-traffic standby links, health checks, DLQs): Keep live components highlighted normally (**never dim/grey out a running component**), show runtime status in a pill (e.g., `RUNNING · 0 traffic`), and draw standby/fallback links as **dashed lines** with a label.
  - **Inactive / non-existent route in this state**: **Hide completely**—do not leave faint ghost lines.
- **Minimal legend**: Include only line/color styles actually used in the diagram.

### 3. Build the HTML/SVG (Engineering Guardrails)

- **SVG CSS pitfalls**:
  - Explicitly set `fill: none` on all edge `<path>`/`<polyline>` elements (otherwise curved or multi-segment paths render as solid black shapes).
  - Scope default SVG text color as `svg.diagram text:not([fill]) { fill: var(--ink); }`—never `svg.diagram text { fill: ... }`, which overrides inline colored `fill` attributes on titles, pills, and edge labels.
  - Drive every node, border, edge, and arrowhead `<marker>` from CSS variables (no hardcoded hex). Define dark variables under **both** `@media (prefers-color-scheme: dark)` and `:root[data-theme="dark"]`, with a top-right `Theme: Auto / Light / Dark` toggle.
- **Overflow & spacing**:
  - Account for character width (especially monospace identifiers and CJK text) and keep ≥ 14px horizontal padding inside node boxes. Avoid wide middle-dot separators (` · `) inside tight monospace pills; prefer parentheses or slashes (e.g., `100% (:8080)`, `4 pods / :8080`).
  - Place edge labels on their own background `<rect fill="var(--surface)">` with ≥ 8px clearance from adjacent node borders and arrowheads so labels never collide with boxes or lines.
- **URL-driven preview hooks**:
  - Parse `URLSearchParams(location.search)` on load: support `?theme=light|dark` (all diagrams) and `?phase=<n>` (interactive diagrams) so headless verification can render every state cleanly.

### 4. Visual Verification (Required Before Delivery)

Render screenshots to a reusable `/tmp` directory (never clutter the project directory, and avoid `rm -rf` cleanup commands that interrupt users with shell approval prompts), then inspect every PNG with your image-reading tool before delivering.

Detect an available Chromium/Chrome binary and capture views in parallel—give each parallel process its own `--user-data-dir` and `--virtual-time-budget=1500` to avoid profile lock contention and slow external font timeouts:

```bash
OUT_DIR="/tmp/tech-diagram-preview"
mkdir -p "$OUT_DIR"
CHROME=""
for bin in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Chromium.app/Contents/MacOS/Chromium" \
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
  google-chrome chromium chromium-browser; do
  if command -v "$bin" >/dev/null 2>&1 || [ -x "$bin" ]; then CHROME="$bin"; break; fi
done

FLAGS=(--headless=new --disable-gpu --no-first-run --no-default-browser-check --virtual-time-budget=1500 --window-size=1400,1080)

# Static diagram: light + dark
"$CHROME" "${FLAGS[@]}" --user-data-dir="$OUT_DIR/p-light" --screenshot="$OUT_DIR/light.png" "file://<ABS_PATH>?theme=light" 2>/dev/null &
"$CHROME" "${FLAGS[@]}" --user-data-dir="$OUT_DIR/p-dark"  --screenshot="$OUT_DIR/dark.png"  "file://<ABS_PATH>?theme=dark"  2>/dev/null &
wait
# Interactive diagram: capture ?phase=1..N&theme=light plus at least one &theme=dark in parallel (each with its own --user-data-dir)
```

- **Coverage**:
  - Static diagram: `light` + `dark` (2 captures).
  - Interactive diagram: **every state** (`phase=1..N`) + at least 1 `dark` capture.
- **Inspection checklist (fix and re-capture if any item fails)**:
  1. No solid black path fills, misaligned/reversed arrowheads, or lines crossing through text/boxes.
  2. No text overflow or truncation; edge label pills have visible clearance from neighboring borders and arrowheads.
  3. Colored titles, pills, and edge labels keep their intended accent colors; active solid edges remain visually distinct from dashed standby/fallback edges.
  4. Dark mode contrast is crisp across surfaces, borders, text, and arrows.
  5. Entire diagram (including bottom legend) fits cleanly in a single screen without wasted whitespace.
- If no headless browser or image-reading capability exists in the environment, state that clearly and ask the user to inspect each state and dark mode in their browser.

### 5. Deliver

- Open the file in a desktop browser when available (`open "<PATH>"` on macOS, `xdg-open "<PATH>"` on Linux; skip in headless/remote sessions).
- Reply with the file path, a concise summary of the mechanism/states depicted and what changed, plus any unverified assumptions that need user confirmation.
