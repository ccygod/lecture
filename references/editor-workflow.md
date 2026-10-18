# 解释、反差与记忆的编辑工作流

完整中文讲座或口播明显平、硬、失去主张时使用；只核查事实、改格式、用户要求严肃操作说明时缩减到对应检查。技能中的代码负责机制检索、候选版本校验和验收记录，模型负责理解需求、原创写作与语义判断。代码不调用外部模型，不要求新API密钥，不宣称自动测得幽默效果。

## 借鉴优先级与路由

先按已确认目的决定语气。客户/领导汇报以当前样稿和[汇报分寸](purpose-and-client-briefing.md)为先，不自动使用课堂练习或舞台笑点。需要表达机制时，罗永浩补充具体问题、判断变化与细节回扣；雷军、王自如、混子曰分别按叙事、体验与因果关系补充。机制不等于作者口吻，不设固定比例；用户指定和当前场合覆盖默认顺序。

[机制库](editor-mechanisms.json)保存来源、适用的教学需要、可观察兑现和失败边界。库里没有必须复用的作者台词、校园案例或个人经历；按需要只取相关卡片，不将四位作者所有特征塞进每段。卡片是编辑归纳，来源证据不等同于方法有效性的实测证明。

罗永浩卡片的evidence_ids对应[原文证据卡](luo-source-evidence.json)，具体迁移按[原文依据与迁移](luo-source-grounded-analysis.md)。检索到机制后读相关证据的过程与边界，不仅看一个风格词；新增来源或重做分析用source_grounding绑定实际正文与片段。

带episode_ids的卡片可用 `python3 scripts/editor_workflow.py episode <ID>` 读取[连续片段记录](source-episodes.json)：来源位置、发生顺序、视觉作用和迁移边界。罗永浩的采购/宣传片段让具体约束和自我反查继续推动判断；混子曰的图文片段让关系变化接回正式名称。记录是编辑转述，不是逐字稿；需要分析原作者措辞时，须按定位读实际正文或原图，不能称已读转述为通读原作。按当前需要选一段，不将所有动作拼成固定模板。

已有对应正文缓存时，episode加 `--body <正文.txt>` 按原文指纹和连续位置抽出真实片段；图文作品用 `--image <原图路径>`，核对身份后还须实际看图。换文件、换版本会拒绝，不把另一篇整理稿套到原位置。缓存缺失可按已知URL重新取得并做来源核对；页面正文版本已变时重新定位，不伪造旧指纹。纯记录阅读只算结构参考；实际原文阅读与模型是否读懂分别记录。工具不复制整篇原作进技能，也不把图像文件存在当看过。

connect_value的受众价值桥接由本技能独立方法承担，不归因给某位演讲者。它可以走直接解释并保留relevance链条；不为得到名人机制候选，给不相关原文强加机会或就业含义。

## 前置状态

本轮实际生成须先完成intake_gate问答。内部子任务共用已确认主任务的run_id，不把测试或模型回答当用户选择。下面的机制计划和候选比较均在确认之后执行。

## 最小执行路径

### 1 确定问题位置

先按主张清单写连续的直接解释；可以与主题设计同步，不要求先写完一个冗长整场草稿。只为关键或有缺陷的位置建立 beat：当前主张是什么、听众可能怎么想、听完应该多明白什么、哪项材料支撑。无需反转的位置声明 plain。不用题材关键词或听众是否知道某个数字决定是否需要惊喜。

将这些位置写入 editorial-request.json。need 的选项见脚本 `plan --help` 及下例；它由模型根据真实内容判断，脚本只执行已声明的选择。用户指定其他借鉴顺序时可传 inspiration_priority（如 ["wang","luo"]）；只允许某类机制时传 allowed_inspirations，空数组仅保留直接讲法；这两项覆盖默认参考顺序与范围。用户指定库外的新语体时可先用 allowed_inspirations=[] 保留直接讲法，再按当次要求写作与审查，不把库中四人当成允许风格的边界：

```json
{
  "purpose_mode": "teaching",
  "humor": "light",
  "required_effects": ["curiosity"],
  "beats": [
    {"id":"b1","claim_id":"c1","need":"challenge_default","critical_instruction":false,"required_effects":["humor","curiosity"]},
    {"id":"b2","claim_id":"c2","need":"explain_mechanism","critical_instruction":false},
    {"id":"b3","claim_id":"c3","need":"plain","critical_instruction":true}
  ]
}
```

运行 `python3 scripts/editor_workflow.py plan editorial-request.json --out editorial-plan.json`。脚本按 need 检索机制，匹配后才按参考顺序排序；操作指令走直接说明，humor=off不添加幽默机制，但仍允许有依据的判断反转。价值关联另用 connect_value，按[受众价值关联](audience-value-bridge.md)填写链条、证据状态及可选时间运算。其他 needs：develop_choice、translate_impact、consolidate、close、humanize。上下文保存在工作资料，不能让生成只看一句主张。

v2将humor=light/moderate视为计划中已声明的幽默意图，将required_effects用于其他明确目标。目标分配给实际适合的少量beat，不要求每段都有笑点。意图无位置承接时ready_for_selection=false，不能跳到选稿。当前局部工作不承担某效果时，用effect_omissions记录具体原因，如幽默安排在本次未处理的开场；这只是公开取舍，不算效果完成，不能用来悄悄取消用户整场要求。未被请求的效果不用添加。

新任务带入intake返回的purpose_mode。非教学用途未声明humor时默认off，不自动增加幽默目标；用户明确希望轻松幽默时可设light/moderate并按场合审查。客户汇报仍应自然、有具体观察，off只表示不要求笑点，不等于写成公文。这里不另造目的选择，以当前真实确认作依据。

### 2 写相邻口播候选

选中的关键位置，比较同主张的直接讲法与一个机制讲法；若机制确实不适合，直接解释可获选。不为每页生成多版。候选包含邻近铺垫、解释和转场，不只写一句金句。关系清楚后再改口吻，不用热词、反问、短句数量代替可念性。可以先解释再收束，也可以先制造预期再用事实改变它；若演示才是关键，就让演示承担落点。

每个候选记录 id 和完整 text。事实、数字、来源及用户核心主张在各版本中保持相同，修订时沿用事实账本。生活类比须指出关键关系与停止适用之处，不得凭比喻补新事实。拟人化只帮助理解角色关系，不变成机器人画风或系统事实。情境浅、反差靠臆造受众误解、类比只贴标签时，按[情境与关系专项](scene-and-relation-pass.md)展开关键例子并抽取上下文审查；不让新增审查成为每个普通段落的表单任务。

先校准真正薄弱的完整片段，再扩展全稿。故事段看正常尝试怎样遇到具体后果、下一步为何改变；类比段看一个新条件如何沿熟悉关系传导，再接到术语；普通解释看不借包袱时能否直接讲顺。讲者的判断和关切须可辨认，没有真实经历就用明确设想。先写连续口播，再放翻页和映射，不按每页字段拼台词。

### 3 给具体反馈并选择

先检查faithful（主张与条件保留）、grounded（无虚构事实与亲历）、speakable（当前讲者可自然说出）、useful（解释或判断有进展），有一项不满足就修。不要把一段很刺激但不忠实的内容评成总分高而放行。

有价值关联的候选同时问：这段能否回答听众的“所以呢”，推理从事实到个人选择有没有跳步，是否落实到可念正文？

再比较记忆价值：预期是什么、哪一步出乎意料、为何有用、去掉后损失什么。总结句允许只有凝练而没有笑点。反馈必须引用具体句子与问题；如“原稿讲的是返工成本，这个候选转成了嘲笑执行人员”，不写“更生动一点”就结束。默认一次针对性修订；仍有具体缺陷可再一次，之后保留最佳合格版本并标明未解决点，不循环刷分。

选择时记录 candidates.json 和 review.json，运行：

`python3 scripts/editor_workflow.py select candidates.json review.json --plan editorial-plan.json --beat b1 --out editorial-selection.json`

review 示例：

```json
{
  "reviewer_kind":"model_text_review",
  "required_effects":["humor","curiosity"],
  "preferred":"direct",
  "reason":"机制版增加了新比喻，但没有增加理解，直接版更贴合场合。",
  "candidates":[
    {"id":"direct","text":"实际候选完整原文","faithful":true,"grounded":true,"speakable":true,"useful":true,"evidence":"具体原句以及保留了哪项关系","effects":{"humor":{"passes":false,"evidence":"这版只有解释，没有本处希望的轻松落点。"},"curiosity":{"passes":true,"evidence":"实际指出了哪项未知及后续兑现。"}}}
  ]
}
```

脚本核对每一候选均有对应的实际文本审查，不接受旧文本、漏审或用字符串冒充布尔判断；拒绝选中不合格候选。语义判断仍是审稿者提供的，不因JSON通过变成客观测得的质量。

上例的direct未满足humor，故会返回revision_required，不能因其清楚而放行。若决定平讲，说明取舍并重建相关计划/选稿；不能只删review的required_effects。绑定选择核对计划版本及效果集合。不带--plan/--beat的旧接口仅保留审计用途，返回unbound_legacy_audit，不算新稿表达验收。

当本处明确追求好笑或好奇心，按[效果审查](current-culture-and-effect-review.md)声明required_effects及各候选effects反馈。缺少所需效果反馈或被评为未完成时不能用四项基础门槛代替放行；普通解释不强加幽默目标。

重要整场修改有独立审查能力且允许时，用新上下文评估：提供用户要求、两版相邻段落及事实账本，隐藏作者名、版本标签和预设优胜答案；必要时调换两版顺序复查争议项。没有独立调用条件时，主Agent分阶段审查并如实标注。不强制所有讲座开多Agent，也不擅自调用新外部服务。

### 4 合稿与复查全场

选中的段落重新连读，检查是否因各处局部优化而全场太密、反差重复、类比来回切换或转场失去方向。普通解释段也要口语化；不给每节安排相同句式。落点写入交付契约，使用version=2的sequence声明实际顺序；页面引用、文字与画面一起同步，不能只换标题保留不相干的图。

将各处实际selection输出汇成JSON数组selections.json，另从最终可念正文导出spoken.txt。运行 `python3 scripts/editor_workflow.py coverage editorial-plan.json selections.json spoken.txt --out expression-coverage.json`。它拒绝漏选、跨计划旧记录、删掉效果判断和获选文字未进入正文；普通direct且无效果目标的位置不强制候选。改稿导致完整候选不再匹配时重审实际片段，不刷新哈希冒充已审。转成平讲的目标在effect_omissions中披露，不称幽默成功。该步骤不替代intake授权、事实或整场语义审查，也不是平台级拦截。

覆盖报告只证明已声明的目标进入相应记录。全场意图是否被忠实分配、过多免责说明是否打断口播、是否总用同一类失败笑点，仍须独立于字段检查。条件允许时实际朗读代表片段，分别记录时长、卡顿与听众反应；没有实际朗读就标文字估算，不由字数等式宣称40分钟已实测。

spoken.txt只放最终可念正文，排除未采用候选、评审和制作备注。coverage中的包含检查不识别否定引用、段落位置或实际讲授顺序；文本存在不证明选稿在正确位置被采用。合稿回读时须核对这一点。episode的来源身份核对也不自动构成已阅读或选稿已依据原作的回执；缺少实际读取就披露结构参考的范围。

最终同时运行结构、数据与交付契约检查。局部候选合格不等于全场通过；文件导出后回读确保选中段落与文案存在。工作JSON与候选默认留工作目录，不把分析字段送进可朗读正文或PPT。

## 更新与回归

用户指出失败时，先归入主张遗漏、反差无收益、口吻书面、类比失真、位置不对或场合不符，保留具体对照样例。只有同类机制问题在新题材复现，才调整通用规则；一次讲座观点留在本次任务。使用[回归场景](editor-evaluation-cases.json)区分开发样例与留出题材；更换模型后复测真实生成，不把程序测试算成演讲效果测试。不要未经授权把用户反馈写入长期记忆。

## 参考依据及采用程度

- [Anthropic工作流实践](https://www.anthropic.com/engineering/building-effective-agents)：已读路由、步骤间程序门槛、生成—反馈—修订与成本取舍。采用分工和简单可组合步骤，不增加无必要框架。
- [Self-Refine](https://arxiv.org/abs/2303.17651)：已读作者摘要，支持研究生成—反馈—修订；不把论文任务表现外推到中文讲座。
- [自我修订中的奖励投机研究](https://arxiv.org/abs/2407.04549)：已读作者摘要与论文相关正文，写作任务中模型评分与人类判断可能分离；因此不靠幽默分数驱动无限重写。
- [MT-Bench评审研究](https://arxiv.org/abs/2306.05685)：已读作者摘要的评审顺序、冗长与自偏好局限；采用匿名成对比较，保留争议，不宣称模型盲评等同真人。
- [DSPy GEPA文档](https://dspy.ai/3.0.4/tutorials/gepa_ai_program/)与[实现仓库](https://github.com/stanfordnlp/dspy)：已读基于执行轨迹和具体文本反馈的优化介绍。采用记录失败机制的思想，未安装或运行GEPA，也不自动进化本skill。
- [Promptfoo select-best](https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/select-best/)及[Agent Skill最佳实践](https://www.promptfoo.dev/docs/integrations/agent-skill/)：已读比较同任务版本、向评审提供原文、客观条件用程序检验等说明；采用这些原则，未接入Promptfoo API或声称其评分已执行。

核查日期2026-10-14。当前Firecrawl CLI未暴露research子命令，宿主亦无对应论文MCP；论文由原生检索发现并用arXiv作者页/正文核查。工程来源按官网与官方GitHub读取。
