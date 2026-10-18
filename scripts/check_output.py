#!/usr/bin/env python3
"""Check lecture structure and explicit mode conflicts, never oral quality."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REQUIRED_FIELDS = ["口播作用", "对应知识点", "PPT内容", "互动与过渡"]
REQUIRED_MARKERS = ["第一部分", "第二部分", "第三部分"]
PURPOSES = ('teaching','briefing','public_talk','mixed','custom')
GENERAL_FIELDS = ["表达作用", "核心信息", "PPT内容", "衔接与推进"]
ORAL_REVIEW = {"code": "oral-review-required", "detail":
    "Structure checks do not assess speakability, one-hearing comprehension, engagement or factual accuracy. Record actual review/listening coverage separately."}
TRIVIAL_PATTERNS = {
    "trivial-scale-hook": [
        r"一千万、一亿，还是更多",
        r"7亿人有多大.{0,100}(一半|相当于|约占|接近)",
        r"这个数字有多大.{0,100}(一半|相当于|约占|接近)",
    ],
}

PAGE_FIELDS = ["页面角色", "页面中心句", "认知动作", "视觉论证", "上屏文字",
               "布局与阅读顺序", "讲者配合", "制作模式", "验收标准"]


def check_page_briefs(text: str) -> dict:
    """Check only explicit fields and mode conflicts; this is NOT semantic QA."""
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    # Do not let fields in the next slide or teaching framework fill this slide.
    section = re.search(r"(?ms)^#{1,3} 第二部分[^\n]*\n(.*?)(?=^#{1,3} 第三部分|\Z)", text)
    body = section.group(1) if section else text
    headings = list(re.finditer(r"(?m)^#{2,4} 页面(?:\d+|示例)[^\n]*$", body))
    if not headings:
        errors.append({"code": "missing-page-briefs", "detail": "no page brief headings"})
    for i, heading in enumerate(headings):
        block = body[heading.end():headings[i + 1].start() if i + 1 < len(headings) else len(body)]
        fields = {}
        for line in block.splitlines():
            m = re.match(r"^-\s+([^：:]+)[：:]\s*(.*)$", line.replace("**", ""))
            if m:
                fields[m.group(1).strip()] = m.group(2).strip()
        name = heading.group().lstrip("# ")
        for field in PAGE_FIELDS:
            if not fields.get(field) or fields[field] in {"待补", "TODO", "TBD", "...", "…"}:
                errors.append({"code": "incomplete-page-brief", "detail": f"{name}: {field}"})
        mode = fields.get("制作模式", "")
        modes = [x for x in ["局部素材+原生页面", "整页ImageGen", "原生图文", "网页/互动页面", "待确认"] if x in mode]
        if len(modes) != 1:
            if not modes and mode.startswith("用户指定：") and fields.get("模式依据"):
                warnings.append({"code": "custom-mode-review", "detail": name})
            else:
                errors.append({"code": "ambiguous-page-mode", "detail": name})
            continue
        prompt = fields.get("生图提示词", "")
        if modes[0] in {"局部素材+原生页面", "整页ImageGen"} and not prompt:
            errors.append({"code": "missing-image-prompt", "detail": name})
        if modes[0] == "待确认":
            if prompt or fields.get("PPT Master成品指令"):
                errors.append({"code": "pending-mode-production", "detail": name})
            warnings.append({"code": "pending-mode-not-final-deck", "detail": name})
        if modes[0] == "网页/互动页面" and not fields.get("交互状态"):
            errors.append({"code": "missing-interaction-states", "detail": name})
        if modes[0] == "整页ImageGen":
            if re.search(r"NO text of any kind|Text policy:\s*none|画面(?:不|不要|禁止)出现(?:任何|可读)?文字", prompt, re.I):
                errors.append({"code": "full-slide-text-conflict", "detail": name})
            # Only inspect operative production instructions, not negative QA examples.
            implementation = " ".join(fields.get(f, "") for f in ["讲者配合", "PPT Master成品指令"])
            if re.search(r"每次点击|点击后逐项|先隐藏(?:答案|数值|\d+(?:\.\d+)?%)|逐步揭示节点|用原生大标题|标题用原生文本", implementation):
                errors.append({"code": "static-slide-instruction-conflict", "detail": name})
            if not re.search(r"逐字|Text policy:\s*exact", prompt, re.I):
                errors.append({"code": "missing-exact-text-policy", "detail": name})
        if modes[0] == "局部素材+原生页面" and re.search(r"Text policy:\s*exact", prompt, re.I) and not fields.get("内嵌文字用途"):
            errors.append({"code": "local-asset-text-policy-review", "detail": name})
    warnings.append({"code": "semantic-review-required", "detail":
        "Field checks cannot verify user confirmation, claim-image alignment, data geometry, visual quality or learning outcomes."})
    return {"errors": errors, "warnings": warnings}


def check(text: str, purpose: str = 'teaching') -> dict:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = [ORAL_REVIEW.copy()]
    if purpose not in PURPOSES:raise ValueError('unknown confirmed purpose')
    required_fields=REQUIRED_FIELDS if purpose=='teaching' else GENERAL_FIELDS
    marker_positions = []
    headings = {}
    for marker in REQUIRED_MARKERS:
        match = re.search(r"(?m)^#{1,3}\s+" + re.escape(marker) + r"[^\n]*$", text)
        if not match:
            errors.append({"code": "missing-major-section", "detail": marker})
        else:
            headings[marker] = match.start()
            marker_positions.append(match.start())
    if len(marker_positions) == len(REQUIRED_MARKERS) and marker_positions != sorted(marker_positions):
        errors.append({"code": "major-section-order", "detail": "sections must be 第一部分 → 第二部分 → 第三部分"})
    first_start = headings.get("第一部分", -1)
    second_start = headings.get("第二部分", -1)
    first_part = text[first_start:second_start] if 0 <= first_start < second_start else ""
    mapping_title='本段对应的知识点与PPT内容' if purpose=='teaching' else '本段对应的核心信息与PPT内容'
    mapping_blocks = re.split(r"(?m)^#{3,4} "+mapping_title+r"\s*$", first_part)
    mapping_blocks = mapping_blocks[1:]
    if not mapping_blocks:
        errors.append({"code": "missing-mapping-blocks", "detail": "no paragraph-to-slide mapping block"})
    else:
        for index, block in enumerate(mapping_blocks, start=1):
            block = re.split(r"(?m)^#{1,4}\s+", block, maxsplit=1)[0]
            fields = {}
            for line in block.splitlines():
                match = re.match(r"^-\s+([^：:]+)[：:]\s*(.*)$", line.replace("**", ""))
                if match:
                    fields[match.group(1).strip()] = match.group(2).strip()
            missing = [field for field in required_fields if not fields.get(field) or fields[field] in {"待补", "TODO", "TBD", "...", "…"}]
            if missing:
                errors.append({"code": "partial-mapping-fields", "detail": f"block {index}: {', '.join(missing)}"})
    third=text[headings.get('第三部分',len(text)):].replace('**','')
    if purpose in ('briefing','public_talk') and re.search(r'(?m)^#{1,3}\s+第三部分\s+教学框架\s*$',third):
        errors.append({'code':'purpose-framework-conflict','detail':'confirmed non-teaching purpose still uses the teaching framework'})
    if purpose=='teaching' and re.search(r'(?m)^#{1,3}\s+第三部分\s+(?:汇报与推进框架|表达与承接框架)\s*$',third):
        errors.append({'code':'purpose-framework-conflict','detail':'confirmed teaching purpose uses a non-teaching framework'})
    if purpose in ('teaching','briefing','public_talk'):
        if purpose=='briefing':
            framework=[('汇报目标|沟通目标|本次目标','report-goal'),('关键依据|支撑依据|事实与依据','report-evidence'),('对方关切|对方可能关切|听众关切|客户关切','report-concerns'),('能力与合作边界|能力边界|合作边界','report-boundaries'),('下一步|推进安排|待确认事项|讨论事项','report-next-step')]
        elif purpose=='public_talk':
            framework=[('表达目标|交流目标|汇报目标|本次目标','speech-goal'),('核心主张|核心信息|关键依据|支撑依据','speech-claim'),('收束|收束与承接|收束安排|礼仪收束|后续承接|行动邀请','speech-closing')]
        else:
            framework=[('知识与技能|知识技能|学习目标|培训目标','teaching-goal'),('过程与方法','teaching-method'),('重点与难点|重点难点','teaching-focus'),('情感态度价值观|态度与责任','teaching-attitude'),('学生误区|常见误区|学员误区','teaching-misconceptions'),('理解证据|理解证据/验收方式|验收方式','teaching-evidence')]
        prefix=r'^(?:#{1,5}\s+)?(?:(?:[-*+]|\d+[.)、])\s+)?'
        boundary_pattern=prefix+r'(?:'+'|'.join(a for a,_ in framework)+r')(?:[：:]|\s*$)'
        lines=third.splitlines()
        for aliases,code in framework:
            present=False
            for index,line in enumerate(lines):
                m=re.match(prefix+r'(?:'+aliases+r')(?:[：:]\s*(.*))?\s*$',line.strip())
                if m:value=m.group(1) or ''
                else:
                    heading=re.match(r'^#{1,5}\s+([^：:]+?)(?:[：:]\s*(.*))?$',line.strip())
                    if not heading or not re.search(r'(?:'+aliases+r')',heading.group(1)):continue
                    value=heading.group(2) or ''
                if not value.strip():
                    for following in lines[index+1:]:
                        following=following.strip()
                        if not following:continue
                        if following.startswith('#') or re.match(boundary_pattern,following):break
                        candidate=re.sub(r'^(?:[-*+]|\d+[.)、])\s+','',following).strip()
                        if candidate:value=candidate;break
                if value.strip() and value.strip() not in {'待补','TODO','TBD','...','…'}:present=True;break
            if not present:errors.append({'code':'missing-'+code,'detail':purpose+' framework requires '+aliases})
    for code, patterns in TRIVIAL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.S):
                # A phrase alone cannot establish audience mismatch or a weak hook.
                warnings.append({"code": code, "detail": pattern + "; review the audience and the cognitive payoff"})
                break
    if first_start >= 0 and second_start > first_start:
        if any(line.lstrip().startswith("|") for line in first_part.splitlines()):
            warnings.append({"code": "table-in-first-part", "detail": "口播部分可能使用了表格"})
    return {"errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--scope", choices=["full", "spoken", "pages"], default="full",
                        help="Validate the requested artifact only; no automatic oral quality rating")
    parser.add_argument("--page-briefs", action="store_true", help="Require page-brief v2 fields and check obvious mode conflicts")
    parser.add_argument("--source", type=Path, help="Original user outline and corrections")
    parser.add_argument("--contract", type=Path, help="Versioned intent and landing evidence")
    parser.add_argument("--intake-run", type=Path)
    parser.add_argument("--intake-receipt", type=Path)
    parser.add_argument("--intake-source", type=Path)
    parser.add_argument("--intake-outline", type=Path, help="Actual outline when stored separately from this round's request")
    parser.add_argument("--audit-only", action="store_true", help="Read-only audit of existing material; not a generation completion gate")
    parser.add_argument("--purpose",choices=PURPOSES,help="Audit purpose; generation must match current intake choice")
    args = parser.parse_args()
    if bool(args.source) != bool(args.contract):
        parser.error("--source and --contract must be supplied together")
    if args.scope == "spoken" and args.page_briefs:
        parser.error("--page-briefs is incompatible with --scope spoken")
    text = args.path.read_text(encoding="utf-8")
    confirmed_mode=None
    if args.intake_receipt:
        try:
            saved=json.loads(args.intake_receipt.read_text(encoding='utf-8'))
            candidate=saved.get('answers',{}).get('purpose',{}).get('mode')
            if candidate in PURPOSES:confirmed_mode=candidate
        except (OSError,ValueError,TypeError,AttributeError):pass
    purpose=args.purpose or confirmed_mode or 'teaching'
    if args.scope == "spoken":
        result = {"errors": [] if text.strip() else [{"code": "empty-spoken-script", "detail": "no spoken text"}],
                  "warnings": [ORAL_REVIEW.copy()]}
    elif args.scope == "pages":
        result = check_page_briefs(text)
    else:
        result = check(text,purpose=purpose)
    if args.page_briefs and args.scope == "full":
        pages = check_page_briefs(text)
        for kind in ["errors", "warnings"]:
            result[kind].extend(pages[kind])
    if args.audit_only:
        result["intake"] = {"status": "audit_only", "ready_for_generation": False}
    elif not all((args.intake_run, args.intake_receipt, args.intake_source)):
        result["errors"].append({"code": "missing-intake", "detail": "generation requires fresh current questions and reply receipt"})
        result["intake"] = {"status": "blocked", "ready_for_generation": False}
    else:
        from intake_gate import check_gate
        try:
            intake = check_gate(args.intake_source.read_text(encoding="utf-8"),
                                json.loads(args.intake_run.read_text(encoding="utf-8")),
                                json.loads(args.intake_receipt.read_text(encoding="utf-8")),
                                args.intake_outline.read_text(encoding="utf-8") if args.intake_outline else None)
            result["intake"] = intake
            result["errors"].extend({"code": "intake-gate", "detail": e} for e in intake["errors"])
            if intake.get('ready_for_generation') and args.purpose and args.purpose!=intake.get('purpose_mode'):
                result['errors'].append({'code':'purpose-mismatch','detail':'CLI purpose differs from current confirmed purpose'})
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            result["errors"].append({"code": "invalid-intake", "detail": str(exc)})
    if args.contract:
        from check_delivery_contract import check as check_contract
        try:
            contract_result = check_contract(args.source.read_text(encoding="utf-8"), text,
                                            json.loads(args.contract.read_text(encoding="utf-8")))
            result["errors"].extend({"code": "delivery-contract", "detail": e} for e in contract_result["errors"])
            result["delivery_contract"] = contract_result["assessment"]
        except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
            result["errors"].append({"code": "invalid-delivery-contract", "detail": str(exc)})
    else:
        result["warnings"].append({"code": "intent-traceability-not-checked", "detail": "Use --source and --contract for full rewrites; structure alone cannot establish intent preservation."})
    result["assessment"] = {"scope": args.scope,
                            "purpose_mode":purpose,
                            "structure": "fail" if result["errors"] else "pass",
                            "oral_delivery": "not_assessed", "audience_effect": "not_assessed"}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in result["errors"]:
            print(f"ERROR {item['code']}: {item['detail']}")
        for item in result["warnings"]:
            print(f"WARN {item['code']}: {item['detail']}")
        if not result["errors"]:
            print("lecture structure check: PASS; oral delivery and audience effect: NOT ASSESSED")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
