# Lecture

**把大纲做成能讲、能听懂、能配页面的内容。**

![项目封面](assets/cover.png)

[English](README.md) · [快速开始](#快速开始) · [发布版本](https://github.com/ccygod/lecture/releases) · [验证记录](docs/validation.md)

## 为什么做这个工具

大纲写得对，不代表现场讲得顺；PPT做得漂亮，也不代表听众知道该记住什么。Lecture把这几件事连起来：听众是谁、想改变哪个判断、口播怎样解释、页面怎样提供证据。

它适用于中文授课、客户和领导汇报、公开演讲及合作发言。授课关注理解和迁移，汇报关注对方关切与推进，公开发言关注表达与承接。用途不同，结构也不同。

## 看一个变化

**原始大纲：**“AI提升工作效率，介绍应用、风险和未来趋势。”

**一种可讲的改写：**“明早之前，你要看完十份报告。AI可以先帮你找出反复出现的问题。但决定之前，你还得知道：每个结论从哪份材料来？真正节省时间的，是让它先整理线索，再把关键核查留在流程里。”

**对应页面：**十份报告流向三个问题，每个问题旁保留来源标记。页面呈现关系，讲稿解释为什么这样做。

这是原创示意例子，不代表模型实测成绩或听众效果保证。[查看完整前后对比](examples/briefing-before-after.md)。

## 可以交付什么

| 环节 | 产物 |
| --- | --- |
| 用途与大纲诊断 | 受众、核心主张、希望促成的变化与关键缺口 |
| 连续口播 | 解释、例子、转场、数据参照与适当分寸 |
| 逐页制作说明 | 页面主张、逐字文案、视觉论证、布局、讲者配合 |
| 配套框架 | 教学目标、汇报与推进、表达与承接，按用途选择 |
| 定向检查 | 来源、算术、版本、主张保留、结构和讲稿Word角色格式 |

## 快速开始

```bash
git clone https://github.com/ccygod/lecture.git
cd lecture
python3 -m pip install -r requirements.txt
python3 scripts/install_skill.py --host codex
```

Claude Code使用 `--host claude`；其他宿主使用 `--dest /你的技能目录/lecture`。安装器遇到已有目录会停止，保留你自己的修改。[兼容性说明](docs/compatibility.md)。

安装后可以这样说：

```text
用 $lecture 处理这份20分钟的客户汇报大纲。
听众：高校领导团队。
目标：说明试点范围，以及需要对方决定的下一步。
交付：连续中文口播和逐页PPT制作说明。
页面：原生可编辑图文。
语气：专业、自然、克制。
[粘贴大纲与依据]
```

完整制作前，Skill会确认用途、诊断大纲，并核对交付物、页面方式和场合条件。已有明确答复应沿用；缺口只在会影响讲法和实施时追问。

## 它怎样工作

`确定用途 → 诊断大纲 → 写顺口播 → 编写页面简报 → 定向复核`

口语化不等于加语气词；数据参照不等于机械换算；吸引力不等于每段塞一个悬念。Lecture将普通解释、类比、案例、数据、幽默和回扣按表达需要组合。承诺了悬念，就要兑现；严肃解释可以直接讲。

用户只要口播时，可以只交连续稿；完整配套任务才按需要组织页面说明和相应框架。

## 本地体验

```bash
python3 scripts/editor_workflow.py --help
python3 scripts/intake_gate.py --help
python3 scripts/compare_quantities.py examples/quantity-reference.json
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

示例中的120与180是假设数据，仅演示同口径比较。[示例索引](examples/README.md)。

## 验证范围

项目提供Skill、参考方法和检查脚本；模型、联网、生图、PPT制作与渲染由宿主提供。主要内容专长是中文讲述，中英双语说明便于安装和理解。

脚本可以检查结构、版本绑定、数量计算和来源位置，不能代替幽默感判断、教学效果验证或真人试讲。研究参考也不等于整个Skill经过科学效果验证。

[实际验证记录](docs/validation.md) · [研究边界](references/oral-research.md) · [来源与权利说明](NOTICE.md)

## 参与与交流

作者：[ccygod](https://github.com/ccygod)。相关工具：[Long Mission](https://github.com/ccygod/long-mission)、[Web Search Router](https://github.com/ccygod/web-search-router)。

[贡献指南](CONTRIBUTING.md) · [帮助](SUPPORT.md) · [中英文发布文案](docs/launch-kit.md) · [MIT许可证](LICENSE)
