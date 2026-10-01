# Skin Craft · 参考图前端还原

把喜欢的概念图落实为真实、可操作的前端：先理解源码与参考图，再用绘图服务生成定制素材，将素材融合到组件，最后用浏览器截图对照修正。

This agent skill covers reference-to-code frontend work, AI-generated UI assets, and reversible application skins. It keeps the existing `skin-craft` name and install path.

## 使用

克隆本仓库，将 [.agents/skills/skin-craft](.agents/skills/skin-craft) **整个目录**放到所用 Agent 的 skill 目录。Codex 可安装到 `~/.codex/skills/skin-craft/`，也可保留工作区的 `.agents/skills/skin-craft/`，具体发现方式以宿主为准。新会话加载后调用：

```text
$skin-craft 根据这些参考图和项目源码重新设计完整前端，必须使用生图生成侧栏、图标和 logo，保留真实业务，并附运行截图。
```

也可只要求设计图/素材，或要求不修改宿主源码的可卸载皮肤。skill 根据用户目标选择路线，不把一种交付方式套到所有项目。

## 这套方法

| 阶段 | 产出 |
| --- | --- |
| 源码与视觉依据 | 页面/状态矩阵、主/辅助参考、锁定原图、拒绝版本 |
| 设计与生图 | 整体设计、素材规格、真实绘图回执、独立透明组件 |
| 组件融合 | 定制侧栏、可伸缩装饰、清晰 DOM 文案、原生交互 |
| 运行对照 | 实际 HTTP 服务、桌面/移动截图、行为验证与差异修正 |
| 交付 | 源图/运行资源映射、真实 README 截图、验证边界与获准发布 |

入口：[SKILL.md](.agents/skills/skin-craft/SKILL.md)。按任务读取参考：

- [视觉契约](.agents/skills/skin-craft/references/visual-contract.md)：多张参考如何分工，全套界面如何覆盖，用户更换原图如何更新选择。
- [生图与素材规格](.agents/skills/skin-craft/references/asset-prompts.md)：页面、侧栏、镂空框、封蜡、导航与无字 logo 的提示词和资源清单。
- [前端融合](.agents/skills/skin-craft/references/frontend-rules.md)：原生改造/可卸载皮肤、装饰分层、nine-slice、状态与响应式。
- [素材与工具排查](.agents/skills/skin-craft/references/image-pitfalls.md)：真实服务失败的诊断、透明度、角色漂移、裁切和资源路径。
- [浏览器验收](.agents/skills/skin-craft/references/verification.md)：设计、真实运行和隔离示例分别记录；检查交互、字体、长内容和移动版。
- [零点契约案例](.agents/skills/skin-craft/references/midnight-contract-case.md)：这次完整定制前端的可迁移决策。

此前的 [辉弦圣堂 · 菲比](https://github.com/Theater-ahyeon/phoebe-atelier) 提供了可卸载皮肤经验；本轮加入零点契约的源码改造经验。角色、配色和布局尺寸是案例，不强制其他项目使用。

## 只读素材审计

生图与图片编辑使用实际服务及宿主工具规则。旧版默认抠图/去边脚本已替换为只读审计器，不自动修改用户图片。

可选运行依赖为 Python 3.10+ 与 Pillow：

```sh
python -m pip install Pillow
python .agents/skills/skin-craft/scripts/audit_assets.py --root ./project --manifest ./project/docs/design/assets.json
```

检查图片可读性、运行尺寸、透明度、源文件 SHA-256 与可选静态 RGBA 像素一致。格式见 [素材清单](.agents/skills/skin-craft/references/asset-prompts.md#素材清单与只读审计)。它不负责生图、美感打分或证明完整界面逐像素还原。

维护者可运行：

```sh
python -m unittest discover -s tests -v
```

测试覆盖无损像素比较、RGB 漂移、透明度、路径越界、损坏文件、动态图边界和不覆盖素材的报告写入；跨平台 CI 运行同一套检查。skill frontmatter 与文件引用也由仓库检查脚本验证。

## 边界

不发布私有验证账号、密钥、运行数据库或未获准公开的壁纸。无真实模型/渠道凭据时不伪造成功回复。自动检查通过不代表用户已接受视觉结果；GitHub 上传、付费调用、部署和市场提交沿用用户明确授权。

## 许可

技能代码延续 Apache-2.0。第三方角色、参考图和生成素材的使用权应分别记录，不能从技能代码许可证推断其授权。本仓库不分发案例中的人物插画或壁纸。
