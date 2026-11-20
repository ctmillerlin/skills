# Visual Foundation (Static & Interactive Diagrams)

Shared visual tokens, single-screen card shell, dark mode setup, and SVG defaults for all diagrams produced by `tech-diagram`. Adapt semantic color names to match your domain—do not copy unrelated domain names.

## 1. Single-Screen Card Shell

Wrap the diagram in one centered `.fig` card (`max-width: 1280px`) with minimal outer margin:

1. **Header (`.fig-head`)**: Diagram title on the left; optional short hint + `Theme: Auto` button on the right.
2. **SVG Canvas (`.svg-scroll > svg.diagram`)**: Responsive width (`width: 100%; min-width: 960px; height: auto`) with a fixed `viewBox`.
3. **Legend (`.legend`)**: Single compact row at the bottom listing only line/color styles actually used in the SVG.

## 2. Color & Typography Tokens

Neutral cool-slate surfaces paired with up to 5 high-contrast semantic accents. **Both** `@media (prefers-color-scheme: dark)` and `:root[data-theme="dark"]` must declare the full dark token set so system preference, the Theme button, and `?theme=dark` all work identically.

```css
:root {
  --bg: #f3f6fa;
  --surface: #ffffff;
  --surface-alt: #f8fafd;
  --ink: #131d2b;
  --muted: #566376;
  --line: #d6dde8;
  --line-strong: #b6c2d4;
  --shadow: 0 1px 3px rgba(16, 28, 46, 0.05);

  /* Rename accents to match domain roles (e.g., source, target, proxy, warn, danger) */
  --c1: #1a66a8; --c1-soft: #eaf2fb; --c1-border: #9ec3e6;
  --c2: #118276; --c2-soft: #e6f5f3; --c2-border: #8ad1c8;
  --c3: #6e44bc; --c3-soft: #f2ecfc; --c3-border: #bfa7ec;
  --warn: #b86b00; --warn-soft: #fff5e3; --warn-border: #ebbf6e;
  --danger: #c4471c; --danger-soft: #fdeee8; --danger-border: #eb9f85;

  --font-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0d131c; --surface: #151e2b; --surface-alt: #1a2535;
    --ink: #e7edf6; --muted: #95a3b8; --line: #273447; --line-strong: #3b4d66;
    --shadow: 0 2px 6px rgba(0, 0, 0, 0.28);
    --c1: #66b0f0; --c1-soft: #132233; --c1-border: #2a527a;
    --c2: #3fd0c0; --c2-soft: #112729; --c2-border: #235c59;
    --c3: #b898f6; --c3-soft: #211a34; --c3-border: #503b80;
    --warn: #f2b84b; --warn-soft: #2b2212; --warn-border: #6e521e;
    --danger: #f4865c; --danger-soft: #2d1c17; --danger-border: #733928;
    color-scheme: dark;
  }
}

:root[data-theme="dark"] {
  --bg: #0d131c; --surface: #151e2b; --surface-alt: #1a2535;
  --ink: #e7edf6; --muted: #95a3b8; --line: #273447; --line-strong: #3b4d66;
  --shadow: 0 2px 6px rgba(0, 0, 0, 0.28);
  --c1: #66b0f0; --c1-soft: #132233; --c1-border: #2a527a;
  --c2: #3fd0c0; --c2-soft: #112729; --c2-border: #235c59;
  --c3: #b898f6; --c3-soft: #211a34; --c3-border: #503b80;
  --warn: #f2b84b; --warn-soft: #2b2212; --warn-border: #6e521e;
  --danger: #f4865c; --danger-soft: #2d1c17; --danger-border: #733928;
  color-scheme: dark;
}
```

Optional Google Fonts `<link>` (page remains readable offline via fallback stack):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
```

## 3. SVG Typography, Edges & Markers

```css
svg.diagram { width: 100%; min-width: 960px; height: auto; display: block; font-family: var(--font-body); }
svg.diagram text:not([fill]) { fill: var(--ink); }
svg.diagram .zone-title { font-size: 13.5px; font-weight: 700; }
svg.diagram .zone-sub { font-family: var(--font-mono); font-size: 11px; fill: var(--muted); }
svg.diagram .col-hdr { font-family: var(--font-mono); font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; fill: var(--muted); font-weight: 600; }
svg.diagram .node-title { font-size: 13.5px; font-weight: 700; }
svg.diagram .node-line { font-size: 11.5px; fill: var(--muted); }
svg.diagram .node-mono { font-family: var(--font-mono); font-size: 11px; fill: var(--ink); }
svg.diagram .pill-txt { font-family: var(--font-mono); font-size: 10.5px; font-weight: 600; }
svg.diagram .edge-lbl { font-family: var(--font-mono); font-size: 11px; font-weight: 600; }
svg.diagram .edge { fill: none; stroke-linecap: round; stroke-linejoin: round; }

/* Optional animated flow overlay: draw solid .edge underneath + subtle animated .flow-pulse on top
   so active edges stay unmistakably solid in static screenshots (never confused with dashed idle links). */
@keyframes dashFlow { to { stroke-dashoffset: -36; } }
@media (prefers-reduced-motion: no-preference) {
  svg.diagram .flow-pulse {
    fill: none;
    stroke: var(--surface);
    stroke-opacity: 0.35;
    stroke-width: 1.4;
    stroke-linecap: round;
    stroke-dasharray: 6 12;
    animation: dashFlow 1.1s linear infinite;
    pointer-events: none;
  }
}
```

Use CSS variables inside `<marker>` so arrowheads automatically adapt to dark mode:

```xml
<marker id="arrC1" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
  <path d="M0,0.5 L9.5,5 L0,9.5 z" fill="var(--c1)"/>
</marker>
```

## 4. Theme Toggle & `?theme=` Hook (All Diagrams)

```js
(function () {
  var root = document.documentElement;
  var themeBtn = document.getElementById("themeBtn");
  var modes = ["auto", "light", "dark"];
  var modeIdx = 0;

  function applyTheme(m) {
    var idx = modes.indexOf(m);
    if (idx === -1) return;
    modeIdx = idx;
    if (m === "auto") {
      root.removeAttribute("data-theme");
      themeBtn.textContent = "Theme: Auto";
    } else {
      root.setAttribute("data-theme", m);
      themeBtn.textContent = "Theme: " + m.charAt(0).toUpperCase() + m.slice(1);
    }
  }

  themeBtn.addEventListener("click", function () {
    applyTheme(modes[(modeIdx + 1) % modes.length]);
  });

  var params = new URLSearchParams(location.search);
  if (params.get("theme")) applyTheme(params.get("theme"));
})();
```
