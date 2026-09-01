# skin-craft

An agent skill for crafting marketplace-quality skins/themes for agent-tool
web GUIs and website frontends — using AI image generation plus reversible
CSS overlays.

Born from a real shipped skin ([辉弦圣堂 · 菲比 /
phoebe-atelier](https://github.com/Theater-ahyeon/phoebe-atelier), accepted
workflow documented in its [TUTORIAL.md](TUTORIAL link below)).

## Install

Copy (or clone) this repo's `.agents/skills/skin-craft/` directory into your
workspace's `.agents/skills/` — the agent picks it up on the next session.

## What it covers

Six phases: dissect an exemplar → scaffold → generate the art pack → cutouts
and finishing → frontend fusion → verify/publish. Highlights:

- **Image tools** (`scripts/skin_image_tools.py`, Pillow only):
  boundary-flood cutouts that keep the interior at 100% original pixels,
  edge decontamination for dark UIs, glow-disc falloff restoration,
  three-backdrop self-check renders. Every tool encodes a real production
  failure (see `references/image-pitfalls.md`).
- **Prompt pack** (`references/asset-prompts.md`): character/style/negative
  blocks, per-asset structural requirements (seamless tiles, nine-slice
  caps, hollow frames, single-corner ornaments), and workflow order for
  consistency.
- **Frontend rules** (`references/frontend-rules.md`): scope attribute,
  semantic-token remapping, decoration layers inside host layout boxes,
  nine-slice craft with art-variable fallbacks, state projection, and the
  uninstall-reversibility audit.

## License

Apache-2.0 for the skill code. Artwork you create with it is yours to
license — if it derives from game/anime characters, state the
non-commercial fan-work attribution honestly.
