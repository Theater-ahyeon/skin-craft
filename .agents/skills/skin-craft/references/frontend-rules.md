# Frontend Fusion Rules — five rules for a reversible overlay skin

These rules are platform-agnostic: they apply to a chat-app web GUI, an
IDE theme, or any website frontend. The host exposes *some* stable seam —
semantic CSS variables, data attributes, a plugin manifest — everything
below hangs off that seam.

## Rule 1 — One scope attribute gates everything

Every skin rule starts with the same scope (e.g.
`body[data-dsh-skin="myskin"]` or the loader-owned
`html[data-dsh-skin="myskin"] body`). On: styles apply. Off: the attribute
is removed and the UI is pristine.

Uninstall audit — all of these must be reverted on removal:

- every DOM node the skin inserted (keep a registry);
- every attribute value the skin wrote (store originals, restore on removal;
  reference-count leases when several skins may coexist);
- every stylesheet tag, listener, observer, and timer (disposables).

Verify: install → uninstall → screenshot-diff against the pristine UI.

## Rule 2 — Remap semantic tokens, not components

Hosts style themselves through semantic variables
(`--button-fill`, `--label-primary`, `--border-l2`, `--bg-overlay`, ...).
Override THOSE, scoped to the skin scope, in both themes:

```css
body[data-dsh-skin="myskin"] {
  --host-button-fill: #d9c089;
  --host-label-primary: #2a3450;
  /* ...full set, light theme */
}
body[data-dsh-skin="myskin"][data-theme="dark"] { /* dark set */ }
```

One token block = whole-app reskin, and it survives host updates far better
than component overrides. Only fall back to component selectors for
decorations the host does not tokenize.

## Rule 3 — Decoration layers live inside host layout boxes

Backdrop + character layers go INSIDE the content container (absolute,
inset 0) — not fixed to the viewport. Layout pushes (side panels, modals)
then move/re-fit the artwork with the content. Keep the content itself
`position: relative` WITHOUT a z-index: it paints above the decoration by
DOM order while popups keep their page-level tier.

## Rule 4 — Plate craft: nine-slice, hollow plates, and fallbacks

- Nine-slice: `border-image-source: var(--skin-plate); border-image-slice:
  <cap-width-px>; border-image-width: <display cap px>;` — ornament caps
  fixed, middle stretches. Record cap widths when cutting the asset.
- Hollow plates (frames over live controls): source image center is
  transparent; the element under it keeps working.
- **Every art variable carries a fallback**:
  `var(--skin-plate, url('assets/...'))` or at minimum
  `var(--skin-plate, linear-gradient(transparent, transparent))`.
  An undefined `border-image-source` combined with a declared
  `border-style`/`border-width` paints a solid currentColor slab. This is
  the "dark slab in static preview" bug.
- Reference assets with paths that resolve in EVERY context the stylesheet
  appears in (static previewer, marketplace CDN, runtime). If the runtime
  rewrites asset URLs through an API base, do it in script and use absolute
  URLs in CSS variables.

## Rule 5 — State projection and motion discipline

Project app state onto attributes (landing vs chat, modal open, sidebar
width bucket) from script; CSS reacts with attribute selectors only:

```css
body[data-dsh-skin="myskin"][data-state="chat"] .my-character { height: 64%; }
```

Motion: transform/opacity only; one-shot effects remove their trigger
attribute after the animation; `will-change` only during the animation;
a full `prefers-reduced-motion` block. Ship light/dark token sets and a
narrow-layout degradation (hide large art, shrink ornaments).

## Launch checklist

- [ ] Scope on/off leaves zero residue (install → uninstall → diff).
- [ ] Both themes complete; contrast checked on both.
- [ ] Narrow layout degrades (large art hidden, ornaments shrink).
- [ ] Static previewer (if any) renders stylesheet correctly without JS.
- [ ] All art vars have fallbacks; no dark slabs in any preview.
- [ ] Performance spot-check: resize storm, long conversation, dark theme.
- [ ] Attribution files present; license stated (fan art → non-commercial).
