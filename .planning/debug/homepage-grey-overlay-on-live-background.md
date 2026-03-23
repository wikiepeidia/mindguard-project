---
status: awaiting_human_verify
trigger: "A faint grey background/overlay is covering the live animated (node-network) background on the homepage hero section"
created: 2026-03-23T00:00:00Z
updated: 2026-03-23T00:00:00Z
---

## Current Focus

hypothesis: CONFIRMED — .hero-section had a near-opaque light grey/white gradient background covering the canvas
test: Changed background to transparent in static/css/homepage.css line 4
expecting: Canvas network animation now visible through hero section
next_action: Human verification — load homepage in browser and confirm canvas is visible

## Symptoms

expected: The live animated network/node background should be fully visible behind the hero content — no grey wash or overlay covering it.
actual: There is a faint grey background on a section/element that sits on top of the animated background, obscuring it. Visible in the hero area of the homepage (index.html).
errors: No runtime errors — purely visual/CSS issue.
reproduction: Load the homepage / route in a browser. The grey overlay/background is visible in the hero section.
started: Present in current state; exact origin unknown.

## Eliminated

(none yet)

## Evidence

- timestamp: 2026-03-23T00:00:00Z
  checked: static/css/homepage.css lines 3-5
  found: .hero-section { background: linear-gradient(180deg, #f3f9ff 0%, #f8fbff 65%, transparent 100%) }
  implication: #f3f9ff and #f8fbff are near-opaque light grey/white — solid cover over canvas

- timestamp: 2026-03-23T00:00:00Z
  checked: static/css/base.css lines 15-22
  found: #network-canvas { position: fixed; z-index: 0; opacity: 0.56 }; body > :not(#network-canvas) { z-index: 1 }
  implication: Canvas is behind all page content at z-index 0; hero-section at z-index 1 with opaque background hides it

- timestamp: 2026-03-23T00:00:00Z
  checked: static/js/base.js lines 26-27
  found: fillStyle = '#0ea5e9' (cyan-blue), strokeStyle = 'rgba(14, 165, 233, 0.34)'
  implication: Canvas draws cyan network animation on light body background — colorful and visible once overlay removed

- timestamp: 2026-03-23T00:00:00Z
  checked: static/css/homepage.css lines 56-63 and static/css/tokens.css line 8
  found: .hero-section .text-white overridden to var(--mg-text-primary) = #0f172a (dark navy)
  implication: Text will remain readable after removing grey backdrop — dark text on light background

## Resolution

root_cause: .hero-section in static/css/homepage.css had background: linear-gradient(180deg, #f3f9ff 0%, #f8fbff 65%, transparent 100%). The colours #f3f9ff and #f8fbff are near-opaque light grey/white, forming a solid cover over the fixed-position #network-canvas (z-index 0) which sits below all page content (z-index 1).
fix: Changed .hero-section background from the grey/white gradient to `transparent` in static/css/homepage.css line 4.
verification: pending human confirmation
files_changed: [static/css/homepage.css]
