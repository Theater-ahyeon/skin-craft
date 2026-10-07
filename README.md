# Skin Craft · 从灵感到完整前端

从一句想法或一张喜欢的图开始，做出真实、可操作的完整前端：启发设计方向、寻找图片参考、选择可用生图来源，确定概念后拆解素材、实现页面与交互，再用运行截图和用户反馈逐步修正。没有参考图也可以开始。

This agent skill takes an idea from discovery through reference search, image-provider selection, concept design, custom assets, implementation and runtime verification. It supports projects without initial reference images and keeps the existing `skin-craft` install path.

## 使用

克隆本仓库，将 [.agents/skills/skin-craft](.agents/skills/skin-craft) **整个目录**放到所用 Agent 的 skill 目录。Codex 可安装到 `~/.codex/skills/skin-craft/`，也可保留工作区的 `.agents/skills/skin-craft/`，具体发现方式以宿主为准。新会话加载后调用：

```text
$skin-craft 我没有参考图，想做一套有独特风格的聊天皮肤。先帮我找方向和素材，让我选择可用的生图来源，再从概念做到完整可运行版本。
```

已有明确参考时可以直接继续：

```text
$skin-craft 根据这些参考图和项目源码重新设计完整前端，必须使用生图生成侧栏、图标和 logo，保留真实业务，并附运行截图。
```

也可只要求设计图/素材，或要求不修改宿主源码的可卸载皮肤。沿用已经选定的方向、素材和服务，从当前缺少的步骤继续，不重复开场问卷。

## 这套方法

| 阶段 | 产出 |
| --- | --- |
| 灵感探索 | 少量有区别的方向、角色/场景/材料线索与用户选择 |
| 素材与来源 | 本地或网上参考、使用范围、可用生图服务与用户偏好 |
| 源码与视觉依据 | 页面/状态矩阵、角色身份与位置、主/辅助参考、锁定原图 |
| 设计与生图 | 选定完整概念、素材规格、真实绘图回执、独立透明组件 |
| 组件融合 | 定制侧栏、可伸缩装饰、清晰 DOM 文案、原生交互 |
| 运行与反馈 | 实际 HTTP 服务、桌面/移动截图、行为验证、局部修正和可控回退 |
| 交付 | 源图/运行资源映射、真实 README 截图、验证边界与获准发布 |

入口：[SKILL.md](.agents/skills/skin-craft/SKILL.md)。按任务读取参考：

- [从零探索](.agents/skills/skin-craft/references/discovery.md)：启发方向、搜索素材、处理视频参考、选择生图来源和能力不足时的交接。
- [视觉契约](.agents/skills/skin-craft/references/visual-contract.md)：多角色与Q版如何区分、概念如何选定、全套界面如何覆盖，用户更换原图如何更新选择。
- [生图与素材规格](.agents/skills/skin-craft/references/asset-prompts.md)：页面、侧栏、镂空框、封蜡、导航与无字 logo 的提示词和资源清单。
- [前端融合](.agents/skills/skin-craft/references/frontend-rules.md)：原生改造/可卸载皮肤、装饰分层、nine-slice、状态与响应式。
- [素材与工具排查](.agents/skills/skin-craft/references/image-pitfalls.md)：真实服务失败的诊断、透明度、角色漂移、裁切和资源路径。
- [浏览器验收](.agents/skills/skin-craft/references/verification.md)：设计、真实运行和隔离示例分别记录；检查交互、字体、长内容和移动版。
- [角色主题案例](.agents/skills/skin-craft/references/midnight-contract-case.md)：Maid Atelier、手记/星夜、赛博终端与零点契约的可迁移决策。

此前的 [辉弦圣堂 · 菲比](https://github.com/Theater-ahyeon/phoebe-atelier) 提供了可卸载皮肤经验；零点契约补充源码改造、素材锁定、反馈回退与发布检查，用户提供的其他概念过程补充主题探索。角色、配色和布局尺寸是案例，不强制其他项目使用；故事中的生图耗时不是交付承诺。

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
python tests/validate_skill.py
python -m unittest discover -s tests -v
```

测试覆盖无损像素比较、RGB 漂移、透明度、路径越界、损坏文件、动态图边界和不覆盖素材的报告写入；跨平台 CI 运行同一套检查。skill frontmatter 与文件引用也由仓库检查脚本验证。

## 边界

这是可复用的 Agent 工作方法，不内置图片搜索服务、生图服务或某个前端运行时。它使用当前环境实际可用的工具，允许选择内置生图、已有服务或外部生图后回传文件；不假装连接未配置的供应商。服务、凭据或运行环境不足时，继续完成可做部分并明确剩余步骤，不能把提示词包当作完整版交付。

不发布私有验证账号、密钥、运行数据库或未获准公开的壁纸。无真实模型/渠道凭据时不伪造成功回复。自动检查通过不代表用户已接受视觉结果；GitHub 上传、付费调用、部署和市场提交沿用用户明确授权。

## 许可

技能代码延续 Apache-2.0。第三方角色、参考图和生成素材的使用权应分别记录，不能从技能代码许可证推断其授权。本仓库不分发案例中的人物插画或壁纸。
