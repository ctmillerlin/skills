# Interactive State-Switching Pattern

Extension on top of [visual-foundation.md](./visual-foundation.md) for diagrams where the same architecture shifts routing, traffic direction, or component roles across phases (migrations, cutovers, rollouts, failover, rollback, state machines). Reuse the mechanics—not fixed column counts or domain labels.

## 1. Five-Band Single-Screen Layout

Inside `.fig`, stack five compact bands from top to bottom:

1. **Card Header (`.fig-head`)**: Title + interaction hint (`Click any state tab or press ← / →`) + `Theme: Auto` toggle.
2. **State Tabs (`.phase-tabs`)**: Equal-width grid (`2–4` tabs, `role="tablist"`). Each tab button contains 3 short lines:
   - `.pnum`: Monospace uppercase label (e.g., `STATE 1 · PRE-CUTOVER`)
   - `.ptitle`: Short action/phase title
   - `.psub`: One-line path summary (e.g., `Apps → Old · Forward Sync → New`)
3. **State Status Banner (`.phase-banner`)**: 3-column summary strip with a 4px left border colored by `--banner-accent`, describing 3 fixed dimensions for the active state (e.g., Traffic / Switch / Replication).
4. **SVG Canvas (`svg.diagram#topoSvg[data-phase="1"]`)**: Component boxes stay at identical coordinates across all states; only per-node status pills and active edges change.
5. **Legend (`.legend`)**: Compact single row listing only line styles actually drawn.

## 2. State Visibility & Flow Animation CSS

Keep active edges as solid `<path class="edge">` elements and layer the optional `.flow-pulse` overlay from [visual-foundation.md](./visual-foundation.md) on top (rather than applying `stroke-dasharray` directly to the primary active path, which makes active edges look dashed in static captures).

```css
svg.diagram .edge { transition: opacity 0.22s ease, stroke-width 0.22s ease; }
svg.diagram .edge-group { transition: opacity 0.22s ease; }

/* Toggle .only-p<N> and .hide-p<N> groups via data-phase (adjust for actual state count) */
#topoSvg[data-phase="1"] .only-p2,
#topoSvg[data-phase="1"] .only-p3,
#topoSvg[data-phase="1"] .only-p4,
#topoSvg[data-phase="1"] .hide-p1 { opacity: 0; pointer-events: none; }
/* Repeat for phases 2..N */
```

Guidelines for grouping SVG elements:
- Put permanent node boxes outside `.only-p*` so live components never blink or grey out.
- Put per-state status pills inside `<g class="only-p1">...</g>` directly below the node body.
- Put active edges inside their respective `<g class="only-pN">` (or `<g class="edge-group hide-p2">`): solid `.edge` (with optional `.flow-pulse` overlay) for live traffic, and dashed `.edge` (`stroke-dasharray="5 4"`) for standby/idle links.

## 3. State Switching + URL Parameter JS Skeleton

Combine with the theme toggle from [visual-foundation.md](./visual-foundation.md):

```js
(function () {
  var phases = {
    "1": { accent: "var(--c1)", col1: "...", col2: "...", col3: "..." }
    // Define states 2..N
  };
  var phaseKeys = Object.keys(phases);
  var svg = document.getElementById("topoSvg");
  var banner = document.getElementById("phaseBanner");
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".ptab"));

  function setPhase(p) {
    var info = phases[p];
    if (!info) return;
    svg.setAttribute("data-phase", p);
    banner.style.setProperty("--banner-accent", info.accent);
    // Update banner column innerHTML values here
    tabs.forEach(function (btn) {
      btn.setAttribute("aria-selected", btn.getAttribute("data-phase") === p ? "true" : "false");
    });
  }

  tabs.forEach(function (btn) {
    btn.addEventListener("click", function () { setPhase(btn.getAttribute("data-phase")); });
  });

  document.addEventListener("keydown", function (e) {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) return;
    var idx = phaseKeys.indexOf(svg.getAttribute("data-phase"));
    if (e.key === "ArrowRight") setPhase(phaseKeys[(idx + 1) % phaseKeys.length]);
    if (e.key === "ArrowLeft") setPhase(phaseKeys[(idx - 1 + phaseKeys.length) % phaseKeys.length]);
  });

  // Theme toggle (Auto -> Light -> Dark)
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

  // Initialize from ?phase=<n>&theme=<light|dark> for automated screenshot verification
  var params = new URLSearchParams(location.search);
  if (params.get("phase")) setPhase(params.get("phase"));
  if (params.get("theme")) applyTheme(params.get("theme"));
})();
```
