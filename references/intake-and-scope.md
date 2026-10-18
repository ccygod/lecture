# 目的优先的前置确认

## 何时启动

每次用lecture新加工、生成或重做授课、汇报、演讲，均执行本轮确认。当前用户明确的免问指令优先；“开工”“按上次”不自动等于免问。已知信息带入确认，不把历史偏好、附件或模型推断冒充当前答复。同一未完成流程的回答与补资料不重启问卷，子任务共享已确认主任务。

只维护技能、提炼风格、只读审稿和内部测试不向真实用户发起制作问卷，也不伪造回答。

## 首项是目的，共四个确认项

1. **目的 purpose**：授课/培训、客户或领导汇报、公开演讲/合作发言、混合用途或其他？想让听众理解、认同、判断或决定什么？可明确委托。已有目的仍作为本轮首项带入确认，不能靠听众有学生或客户就推定用途。
2. **交付物 deliverable**：完整Word讲稿与配套说明、实际PPT、两者、仅口播或仅页面说明？教学可选完整教参；汇报不要求教学框架。
3. **PPT方式 slide_mode**：可编辑原生图文、局部生成配图、整页ImageGen、网页互动、混合、暂不定或不做？可委托，不默认为整页图。
4. **场合条件 brief**：承接已知目的及大纲诊断，只补会改变结构或实施的缺口，如听众角色、已有共识、时间是否含交流、期待后续、事实状态和口吻。客户培训的重点可能是会不会用；客户方案会谈则可能是要不要试，不照抄同一问法。

目的尚不明确时，先用问答工具问目的，再按结果给针对性的大纲诊断和其余确认；可以先做中性的材料梳理，不能先按课堂或销售场景写稿。目的已清楚时，给简短诊断后可一次展示四项，purpose排第一。工具单次容量不足就分组，当前已答项不重问；展示和回复位置可记录多次。没有工具时用文本。已展示、空回执或时间流逝均不等于已回答。

诊断维度仍见[大纲诊断](outline-preflight-and-questions.md)，风格与分支见[目的与客户汇报](purpose-and-client-briefing.md)。先保留合理主线，再指出影响效果的具体缺口与可执行建议，不先扩写整稿。

## v3可执行状态门

保存本轮请求原文；实际大纲另存时，start传--outline，不能只审查“继续”几个字。

`python3 scripts/intake_gate.py start request.txt --outline outline.txt --out intake-run.json`

start创建version=3新run_id与四项问卷，拒绝覆盖既有run。诊断仍用version=1的outline-preflight.json，保存实际大纲哈希、diagnosis、recommendation、五维checks、strengths、risks和critical_questions；schema细节见outline-preflight-and-questions.md及脚本。自定义questions必须保留purpose/deliverable/slide_mode/brief，purpose位于第一，关键问题原句进入问项。

`python3 scripts/intake_gate.py prepare intake-run.json outline.txt outline-preflight.json --out intake-prepared.json`

大纲与请求相同时直接用request.txt作outline。prepare核对来源与问卷，不证明诊断合理。目的先单独问过时，沿用同一run并记录该次真实回答；待其余条件完成后保存完整回执，不重新start。

```json
{
  "version":3,
  "run_id":"本轮ID",
  "source_sha256":"请求指纹",
  "preflight_sha256":"prepare产生的诊断指纹",
  "preflight_display_receipt":"实际向用户呈现诊断的位置",
  "question_receipt":"本轮真实提问位置，可列多次工具调用",
  "answers":{
    "purpose":{"value":"客户汇报","mode":"briefing","origin":"user_reply","evidence":"本轮真实回复原文"},
    "deliverable":{"value":"完整Word汇报材料","origin":"user_reply","evidence":"本轮真实回复原文"},
    "slide_mode":{"value":"可编辑原生图文","origin":"user_reply","evidence":"本轮真实回复原文"},
    "brief":{"value":"本轮目标与条件","origin":"user_reply","evidence":"本轮真实回复原文"}
  },
  "resolutions":{
    "关键问题ID":{"value":"当前决定","origin":"user_reply","evidence":"实际用户原话"}
  }
}
```

purpose.mode可为teaching、briefing、public_talk、mixed、custom，表示当前选择或明确委托后的工作模式；不是按受众关键词自动推断。其他目的允许custom并保留原话。具体汇报目标在brief中细化，不把所有汇报都设为争取审批。origin也可为user_delegation，但要有当次明确委托的原话，不能自行填默认回答。

`python3 scripts/intake_gate.py check request.txt intake-prepared.json intake-receipt.json --outline outline.txt`

仅诊断中列出的关键问题需逐项解决。明确委托可解决取舍；普通有用信息不应变成审批。用户改变条件时核对影响，已答项不重复询问，保持真实来源可追溯。

check拒绝缺目的、目的非首项、缺当前答复、错版本及未解决关键问题，成功时返回purpose_mode给后续结构检查。v1/v2回执只供历史审计，不能支持新一轮生成；旧稿审查仍可--audit-only，无须重开制作问卷。

完整材料验收：

`python3 scripts/check_output.py draft.md --page-briefs --intake-source request.txt --intake-outline outline.txt --intake-run intake-prepared.json --intake-receipt intake-receipt.json`

实际大纲未另存则省略--intake-outline。命令从当前回执取目的；--purpose仅用于显式只读用途或与当前选择一致的检查。纯口播用--scope spoken，页面用--scope pages，不强加完整三部分。接口核对记录，不能鉴别伪造回执、确认表达目的被正确理解或安装平台级写入拦截。
