# 主张保真与记忆落点

完整新稿、整场重写或用户反馈核心观点被淡化时读取。本流程适用于不同题材，不预置AI、机器人、某位讲者的立场，也不要求每节都有金句。局部修一句话只核对受影响内容，不强制整场建档。

## 先锁定要讲什么

在工作目录保存本次用户大纲和有效修正原文为 source.txt。写稿前提取少量关键主张、必须保留的关系、事实和明确约束，记录在 delivery-contract.json；主题名不能替代主张。例如“技术普及”只是题目，“入门门槛降低与高阶能力分化可以同时发生”才是要论证的关系。新纠正追加原文并更新清单，不覆盖掉仍有效的要求。

逐条区分 thesis（讲者主张/趋势判断）、fact（可验证事实）、rhetoric（指定表达意图）、constraint（交付约束）。修正事实错误、范围或因果强度时，保留讲者要讨论的机制；局部研究的反例不自动否定另一个层级的主张。不能为了所谓平衡把明确观点改成空泛中立，也不能把观点包装成已证明的普遍规律。确实冲突时，在备课说明写清改了什么、为什么。

## 把句子写在能起作用的位置

围绕核心主张、重要转折或回扣选择落点。先写具体情境与常见直觉，按[编辑工作流](editor-workflow.md)检索机制，并比较少量不同讲法：预期与结果错位、同一起点的不同去向、看似优势的隐性代价、尺度或时间视角转换、前文细节回扣。选择能增进理解且自然说得出口的一句，根据真实段落位置先解释后收束，或先设预期再解释，也可由演示兑现。普通机制段保留平讲。

反差不等于所有句子都写成“不是X而是Y”。幽默、意外、凝练、可记忆是不同维度，不以网络热词或笑话数量评分。候选内部比较即可，不向最终教参堆弃稿。上屏只挑承担页面主张的句子，并同步图形与解释；不能只给原来不相干的图换标题。

文本审查问四件事：
- 听众原本可能怎样想，这一句改变了哪个判断？只换成更响亮的口号不算完成。
- 去掉这句是否损失一个值得记住的关系？如果毫无损失，考虑删掉。
- 铺垫、落点、解释是否在邻近口播里形成完整意义？不得靠备课备注补救听众听不到的论证。
- 是否偷换条件、羞辱受众、抄名人原话，或为了反差牺牲准确性？写出具体审查理由，不用“通过”二字代替。

## 可执行交付契约

运行 `python3 scripts/check_delivery_contract.py source.txt lecture.md delivery-contract.json`。此文件为工作资料，不混入上屏内容。脚本检查原文与稿件哈希、引用真实存在且位于指定区域、核心主张与页面的引用映射、修改说明存在、所声明的实际讲述顺序。它不能判定主张清单是否完整、改写语义是否忠实、句子是否好笑；这些仍需逐项语义审查。哈希改变时先重审受影响条目，再刷新哈希，不能只改哈希掩盖旧审查。

契约格式（所有 quote、setup、line、explanation 必须是对应文件中的真实连续原文；定位边界须唯一，不得只引用标题或备注充当口播）：

```json
{
  "version": 2,
  "source_sha256": "以hashlib.sha256(source.encode('utf-8')).hexdigest()计算",
  "draft_sha256": "同法计算稿件",
  "regions": {
    "spoken": {"start": "唯一口播起始标记", "end": "唯一口播结束标记"},
    "slides": {"start": "唯一页面起始标记", "end": "唯一页面结束标记"},
    "notes": {"start": "唯一说明起始标记", "end": "唯一说明结束标记"}
  },
  "claims": [{
    "id": "c1", "source_quote": "用户原句", "kind": "thesis",
    "status": "preserved", "spoken_quote": "实际口播证据",
    "on_slide": true, "slide_quote": "实际上屏文案"
  }],
  "landings": [{
    "id": "l1", "claim_id": "c1", "setup": "情境铺垫原句",
    "line": "记忆落点原句", "explanation": "机制解释原句",
    "sequence": ["setup", "explanation", "line"],
    "on_slide": true, "slide_quote": "页面文案原句",
    "semantic_review": "具体说明所改变的直觉、保留的条件和潜在误读"
  }]
}
```

version=2 的 sequence 须包含 setup、line、explanation 各一次，顺序与实际稿件一致；例如先解释再收束，使用 setup、explanation、line。旧version=1保持兼容，不再用于新稿。

status 为 qualified / corrected / omitted 时还须 reason 和 disclosure_quote（notes区的真实说明）。完全不适合设计落点的场合允许 landings 为空，但须 no_landings_reason；不设置固定数量或密度。纯口播可以不定义 slides、所有 on_slide 为 false。完整教参可用现有三部分边界；必须确认 spoken_quote 来自可朗读正文，而非映射里的同词重复。

## 跨题材复查

修改此机制后，至少覆盖：观点明确但需要限定的科技讲座；不需要幽默的严肃安全培训；面向管理者的成本与质量取舍；短篇人文讲解。观察是否保留各自原始观点、是否按场合选择落点、是否出现相同套话或强制三层结构。自动化负例测试只证明检测能力，不能冒充生成效果测试或真人听众测试。

也可在原有结构检查中合并执行：`python3 scripts/check_output.py lecture.md --page-briefs --source source.txt --contract delivery-contract.json`。不传契约时明确报告主张追踪未检查，不能把结构PASS当成主张验收。

以上命令是主张/结构检验部分。实际生成验收还须带本轮 `--intake-source request.txt --intake-run intake-run.json --intake-receipt intake-receipt.json`；只读核查旧稿才用 `--audit-only`，不得将只读结果当作生成放行。
