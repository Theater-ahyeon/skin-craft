---
name: skin-craft
description: >-
  End-to-end workflow for crafting high-quality skins/themes for agent-tool
  web GUIs and website frontends using AI image generation plus reversible
  CSS overlays. Use when the user wants to make a skin, theme, or reskin an
  interface; generate character backdrops, sidebars, ornamental trim plates,
  or nine-slice UI textures; cut out characters or assets from generated
  images; fix cutout artifacts on dark UIs (fringes, hard glow edges,
  semi-transparent garments); or package and submit a finished skin to a
  skin marketplace.
---

# Skin Craft

Build a marketplace-quality skin in six phases. Division of labor: the agent
owns engineering correctness; the user owns every aesthetic decision. Never
generate final art without the user approving a style anchor first.

```text
DISSECT -> SCAFFOLD -> ART -> CUTOUT -> FUSE -> VERIFY/PUBLISH
 (1 day)   (0.5 day)   (2-3d)   (1 day)    (1-2d)    (0.5 day)
```

Read [references/asset-prompts.md](references/asset-prompts.md) before phase
ART, [references/image-pitfalls.md](references/image-pitfalls.md) before
phase CUTOUT, and [references/frontend-rules.md](references/frontend-rules.md)
before phase FUSE.

## Phase DISSECT — dissect one excellent exemplar

Never start from zero. Ask the user for an exemplar skin they like (repo URL
or local path), then produce a dissection note answering exactly three
questions:

1. **Scope switch** — what single attribute/class scopes every skin rule?
   (e.g. `body[data-dsh-<id>]`; on = styled, off = pristine.)
2. **Token remap** — which semantic variables (button fills, label colors,
   borders, overlays) does it override instead of touching components?
3. **Asset usage** — which art is a backdrop, which is a nine-slice plate,
   which is pure CSS, where do CSS variables carry images.

Keep the note; every later decision defers to it. If an exemplar exposes a
marketplace contract (manifest schema, validation script, catalog checks),
record those commands too.

## Phase SCAFFOLD — skeleton

Create the skin project by adapting the exemplar's layout, never from an
empty folder: manifest (name/author/version/license/preview paths), an empty
stylesheet seeded with the exemplar's semantic-token block, `assets/src/`
for source art, `preview/`, and attribution files (LICENSE/NOTICE) whenever
third-party characters or game art are involved — fan works are
non-commercial; write the attribution chain down now.

Have the user lock a **palette** (4-5 named hex values, e.g. porcelain /
gold / accent / ink / night) and a **subject block** (one reusable character
description paragraph). Everything downstream references these.

## Phase ART — generate the asset pack

Read [references/asset-prompts.md](references/asset-prompts.md) for the
prompt templates and the full asset checklist. Non-negotiables:

- **Reference-image consistency**: pin the official/character reference in
  the image tool; generate the scene first, approve it, then reuse it as the
  style anchor for every decorative plate.
- **Spec table before generating**: for each asset record target file name,
  aspect ratio, background color (uniform light/dark for cutouts), and the
  structural requirement (seamless tile, nine-slice caps, hollow center,
  single-corner ornament to be mirrored).
- **Color lock**: paste the palette hexes into every prompt; the finished
  renders get color-graded against the same values.
- Reuse a fabric/trim sheet for multiple bands when sensible; never reuse
  the same frame art on two different UI frames.

## Phase CUTOUT — cutouts and post-processing

Use `scripts/skin_image_tools.py` (PIL only). Default pipeline for uniform
background art:

```sh
python scripts/skin_image_tools.py floodcut IN.png OUT.png          # boundary flood, interior untouched
python scripts/skin_image_tools.py decontam OUT.png                 # kill light fringe (dark UIs)
python scripts/skin_image_tools.py glow-restore ORIG.png OUT.png    # only for cut-through glow discs
python scripts/skin_image_tools.py verify OUT.png --bg navy         # self-check renders
```

Hard rules (details and failure gallery in
[image-pitfalls.md](references/image-pitfalls.md)):

- Uniform solid background → boundary flood fill; the interior keeps 100%
  original pixels. Semantic matting (rembg-class) is a last resort: it
  renders sheer garments semi-transparent, darkens premultiplied regions,
  and keeps glass-bubble effects.
- Blue-phase blocking stays ON for neutral-gray backgrounds under blue/
  pale characters (stops gradient leaks into skirts).
- On dark UIs always run `decontam` after the cut; light residual fringes
  glow on dark panels.
- Glow discs cut mid-gradient need `glow-restore` (distance-field alpha
  rebuilt from the original, unioned with the figure mask) plus feathering.
- Every cutout passes the three-backdrop check: red / dark-navy / checker.
  A cutout that fails one backdrop ships a bug.

## Phase FUSE — frontend fusion

Implement [references/frontend-rules.md](references/frontend-rules.md) as
five rules the agent must follow:

1. One scope attribute gates every rule; uninstall removes it and the UI is
   pristine. Keep an uninstall audit: registered nodes, backed-up attribute
   values, disposables.
2. Remap host semantic tokens instead of overriding components one by one.
3. Decoration layers live inside the host's content containers (not fixed to
   the viewport) so layout pushes move them with the content.
4. Nine-slice plates: fixed ornament caps, stretchable middle; **every art
   CSS variable must carry a fallback** (`url(relative asset)` or a
   transparent gradient) — an undefined `border-image-source` var plus a
   set border-style/width paints a solid currentColor slab.
5. Project app state (landing/chat/modal) onto attributes and let CSS react;
  animate only transform/opacity; ship full light/dark token sets and
  narrow-layout degradation.

Wire the verification harness: a local mock page reproducing the host's DOM
structure with the real skin code loaded, one URL parameter per state
(landing/chat/modal, light/dark). Capture screenshots per state.

## Phase VERIFY/PUBLISH — ship it

Self-check list before any push: cutouts pass three backdrops on dark UI;
light/dark complete; narrow layout holds; uninstall restores the pristine
UI; no emoji in code/docs/commits if the target marketplace forbids them.

Publishing path (adapt to the target marketplace):

1. **Distribution repo** (own GitHub): manifest + build artifacts + previews
   + attribution, one-line install command in the README.
2. **Marketplace inclusion**: fork the market repo, adapt the package to its
   published contract (pure-asset manifest + stylesheet + optional hooks),
   run its validation/build/catalog scripts locally, commit the rebuilt
   dist artifacts, open the PR against its integration branch with the
   template filled: category, light/dark try-on screenshots, test evidence,
   and an honest AI-coding disclosure.

Update the distribution repo README with full-page renders; link them from
the PR as review references (static marketplace previews do not execute
hook-driven art layers — disclose that difference).

## Ground rules

- Disclose AI assistance honestly in any submission.
- Third-party characters/game art → non-commercial fan license + attribution
  chain in NOTICE. This gates marketplace acceptance.
- Never modify the host application's source; a skin is a reversible overlay.
- The user approves every art asset before it enters the pipeline; the agent
  never substitutes its own taste for the user's.
