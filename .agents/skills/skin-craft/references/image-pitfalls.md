# Image Pitfalls — failure gallery and exact fixes

Every entry is a real production failure from a shipped skin. Symptoms are
what the user sees; verify with the three-backdrop check (red / dark-navy /
checker) after every fix.

## 1. "Transparent person" — garments see-through

- **Seen as**: dress/skirt shows the background through it; whole figure
  looks ghosted on dark UIs.
- **Cause**: semantic matting (rembg-class models) classifies painted sheer
  fabric as "background visible" and assigns partial alpha (40-200).
- **Fix order**:
  1. Prefer boundary flood fill on uniform backgrounds (see
     `skin_image_tools.py floodcut`) — the interior keeps 100% original
     pixels.
  2. If matting output must be used: solidify alpha — `a >= 110 → 255`,
     `a <= 22 → 0`, linear ramp between.
- **Why not just raise alpha on matted output**: matted RGB in low-alpha
  regions is premultiplied against the original background — raising alpha
  exposes dark smudges (see #2).

## 2. Dark smudge blobs on garments

- **Seen as**: irregular near-black patches on white/pale clothing after
  forcing opacity.
- **Cause**: matting models emit RGB premultiplied by alpha; low-alpha
  fabric pixels carry darkened colors. Forcing opacity exposes them.
- **Fix**: for interior pixels take RGB from the ORIGINAL image (matting
  output is pixel-aligned with its input); only the alpha comes from the
  matte. Or unpremultiply: `rgb' = clamp(rgb * 255 / max(a, 1))`.

## 3. Glass-bubble / dirty dome over head

- **Seen as**: semi-transparent whitish dome covering hair/head.
- **Cause**: the artwork's glass/light-bubble effect survived matting as a
  translucent region.
- **Fix**: re-cut with an anime-specialized matting model
  (`isnet-anime`-class), or drop the dome via a whitish-translucent rule
  (low saturation + high lightness + alpha < 235 → 0) outside the solid
  body mask.

## 4. Light fringe / glowing outline on dark UIs

- **Seen as**: 1-2px pale halo around the whole silhouette; screams on
  dark backgrounds, invisible on light ones.
- **Cause**: the original light background's antialiased edge remains in
  the boundary band.
- **Fix**: boundary-band decontamination — for opaque pixels with a
  transparent 4-neighbor, `dist(rgb, bg) < kill → alpha 0`;
  `kill..soft → alpha scaled by (d - kill) / (soft - kill)`. Use the
  ORIGINAL image's corner-average background color. Never globally key out
  near-white: interior satin highlights get eaten.

## 5. Hard rectangular patch behind a glow

- **Seen as**: a pale rectangle with straight edges behind/around the
  character (halo burst, radiant aura) — only obvious on dark UIs.
- **Cause**: the flood boundary crossed the middle of a wide soft glow
  gradient; the glow outside the cut was removed, leaving a hard edge
  through a bright region.
- **Fix**: distance-field alpha restoration — for currently-transparent
  pixels, `alpha = clamp((dist(rgb, bg) - 16) * 3, 0..235)` computed from
  the ORIGINAL image, unioned with the figure mask (max), then 1-2 rounds
  of feather (Gaussian-blur alpha, max-blend) and one decontam pass.
  The glow fades radially again; the figure mask keeps the body solid.

## 6. Dark solid slab where a decorative plate should be

- **Seen as**: a solid dark-navy rounded slab around/in place of a framed
  element — only in static previews or after skin reloads.
- **Cause**: a CSS rule sets `border-style: solid; border-width: 42px;`
  and `border-image-source: var(--plate-art)` — when the variable is
  undefined the browser falls back to painting the border in currentColor
  at the declared width.
- **Fix**: give every art variable a fallback:
  `border-image-source: var(--plate-art, url('relative/or/transparent-gradient'))`.
  Audit all `var(--*art*)` uses; one missed var is one dark slab.

## 7. Styles missing in the marketplace static previewer

- **Seen as**: marketplace preview shows default UI; local render looks
  perfect.
- **Cause**: static previewers inject the stylesheet and set a
  loader-owned scope attribute (e.g. `html[data-dsh-skin="<id>"]`); they
  never execute skin JavaScript. A skin whose CSS scopes under an
  attribute set by its own script renders as nothing.
- **Fix**: scope the stylesheet under the loader-owned attribute; keep
  script-set attributes for internal state only. Add declarative
  background media in the manifest if the contract supports it (the
  static previewer paints those).

## 8. Enclosed white pockets between ornament curls

- **Seen as**: white patches inside filigree/openwork after edge flood.
- **Cause**: enclosed background pockets are not connected to the canvas
  edge, so edge flood never reaches them.
- **Fix**: classify remaining connected components after the flood; a
  component whose mean color is near the background (and roughly uniform)
  is a background pocket → remove. Guard the tolerance so a uniform pale
  object interior (e.g. a satin band) is not removed — compare component
  mean distance to bg against a tight threshold and require neutrality.

## 9. Same texture reused on two frames

- **Seen as**: users call it lazy; reviewers flag it.
- **Fix**: each framed slot gets its own plate. A fabric sheet MAY be
  cropped into different bands (top/bottom trim) when the crops read as
  distinct ornaments.

## Self-check (three backdrops) — after every fix

```sh
python scripts/skin_image_tools.py verify OUT.png --bg red
python scripts/skin_image_tools.py verify OUT.png --bg navy
python scripts/skin_image_tools.py verify OUT.png --bg checker
```

Red exposes light/white residue; navy simulates the dark theme and exposes
gray fringes; checker exposes semi-transparent garbage. Look at silhouette
edges, garment interiors, and enclosed holes.
