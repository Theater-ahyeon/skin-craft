# Asset Prompt Pack — templates

Paste-and-adapt prompt templates. Replace `{...}` placeholders. Keep a
locked palette (4-5 named hexes) and paste it into every prompt; use the
same values for post-processing color grading.

## Global blocks

**Character block** (shared by every character prompt):

```text
{角色全名}，{发型发色}，{瞳色}，{标志性部件：光环/兽耳/翅膀/帽子}，
{服装主色与风格描述}，{白色过膝袜/长靴等下装}，{气质关键词}
```

**Scene suffix**:

```text
完全对称构图，{两侧结构：彩窗/立柱/拱门}，{中央区域留空明亮——界面会压在
这里}，{光效：晨光斜射/星穹烛光}，月白与圣金主色调（#F7F5EE / #D9C089），
辉光蓝点缀（#A9C6E8），柔和光感，轻柔景深，精致动漫美术，游戏官方美术风格，
高细节，无文字，无边框，无UI
```

**Object suffix**:

```text
正视图，无透视，平面纹理视图，边缘干净利落，高细节，精致游戏UI素材风格
```

**Negative prompt**:

```text
文字，水印，签名，UI元素，边框，低质量，过曝，畸形手指，多余肢体，杂乱背景
```

**Character cutout suffix**:

```text
全身，完整露出双脚和鞋子，纯浅灰背景，single full-body
```

## Asset checklist (with structural requirements)

| Asset | Size / ratio | Hard requirement |
| --- | --- | --- |
| Scene light | 1920×1080+ (16:9) | center area empty (UI lands there); both sides are safe zones for characters |
| Scene dark | same | same composition as light (image-to-image from the light one); only lighting changes |
| Main cutout L/R | 1024×1536+ (2:3), uniform light-gray bg | feet fully visible (bottom-anchored), subject ≥90% height |
| Third-form cutout | same | alternate pose/form (pair it with a model-family or mode switch) |
| Chibi | 768×768+, uniform bg | single character, head-to-body ≈ 1:2 |
| Top/bottom trim tile | 2048×256 / 2048×128 | horizontally seamless, repeatable |
| Corner ornament | 1024×1024 | draw ONE corner only (frontend mirrors to four) |
| Nine-slice plate (button/ribbon) | 2048×256 | ornament caps ~15% each end; middle plain and stretchable |
| Hollow frame (composer panel) | 2048×512 | center pure black (keyed to transparent later); bar ~12% of height |
| U-drape / crest / bow | square-ish | symmetric, plain background, closed shapes survive cutout |
| Icon | 256×256 | crop from the main cutout's head region; no separate generation |

## Workflow rules

1. Generate/approve the scene first; it becomes the style reference
   (垫图) for every decorative plate.
2. Scene pair (light/dark): identical composition, image-to-image the
   light one into night. Composition drift is what makes theme switches
   feel broken.
3. Characters: feet complete, subject ≥90% of frame height, plain
   light-gray background (easiest to key out).
4. Nine-slice plates: record the cap width in pixels after cutting — the
   frontend `border-image-slice` must match it.
5. Midjourney users: add `--ar` per the table and `--cref <official art URL>`
   for character consistency; niji model for anime.

## Midjourney quick examples

```text
Scene:
grand white cathedral nave interior, symmetrical composition, golden strings
of light hanging from the dome, floating golden halo rings, polished ivory
marble floor reflecting holy light, empty bright center area, ivory and gold
palette with pale blue accents, anime game official art style --ar 16:9 --niji 6

Character:
Phoebe-style oracle maiden, full body, silver-white hair with icy blue tips,
golden halo beside her head, nun-style white dress with gold trim, holding
strings of golden light, light gray background --ar 2:3 --niji 6 --cref <URL>
```
