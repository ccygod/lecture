#!/usr/bin/env python3
"""Validate provenance and located delivery evidence, not rhetorical quality."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def check(source, draft, contract):
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(message)
    require(contract.get('version') in (1, 2), 'unsupported contract version')
    require(contract.get('source_sha256') == digest(source), 'source changed: rebuild intent inventory')
    require(contract.get('draft_sha256') == digest(draft), 'draft changed: review and refresh evidence')
    regions = {}
    for name, spec in contract.get('regions', {}).items():
        start, end = spec.get('start', ''), spec.get('end', '')
        if not start or not end or draft.count(start) != 1 or draft.count(end) != 1:
            errors.append(f'{name}: region boundaries must be nonempty and unique')
            continue
        a, b = draft.index(start) + len(start), draft.index(end)
        require(a < b, f'{name}: reversed region')
        if a < b:
            regions[name] = draft[a:b]
    def evidence(item, field, region):
        quote = item.get(field, '')
        require(isinstance(quote, str) and bool(quote.strip()) and quote in regions.get(region, ''),
                f"{item.get('id', '?')}: missing {field} in {region}")
    claims = contract.get('claims', [])
    require(isinstance(claims, list) and bool(claims), 'missing intent inventory')
    ids = set()
    for item in claims:
        ident = item.get('id')
        require(bool(ident) and ident not in ids, 'missing or duplicate claim id')
        ids.add(ident)
        quote = item.get('source_quote', '')
        require(isinstance(quote, str) and bool(quote.strip()) and quote in source,
                f'{ident}: source quote absent')
        require(item.get('kind') in ('thesis', 'fact', 'rhetoric', 'constraint'), f'{ident}: invalid kind')
        status = item.get('status')
        require(status in ('preserved', 'qualified', 'corrected', 'omitted'), f'{ident}: invalid status')
        if status != 'omitted':
            evidence(item, 'spoken_quote', 'spoken')
            if item.get('on_slide'):
                evidence(item, 'slide_quote', 'slides')
        if status != 'preserved':
            require(bool(item.get('reason', '').strip()), f'{ident}: change needs explanation')
            evidence(item, 'disclosure_quote', 'notes')
    lines = contract.get('landings', [])
    for item in lines:
        require(item.get('claim_id') in ids, 'landing references unknown claim')
        for field in ('setup', 'line', 'explanation'):
            evidence(item, field, 'spoken')
        block = regions.get('spoken', '')
        if all(item.get(f) and item[f] in block for f in ('setup', 'line', 'explanation')):
            sequence = item.get('sequence') if contract.get('version') == 2 else ['setup', 'line', 'explanation']
            valid = isinstance(sequence, list) and len(sequence) == 3 and set(sequence) == {'setup', 'line', 'explanation'}
            require(valid, f"{item.get('id')}: sequence must contain setup, line, explanation exactly once")
            if valid:
                positions = [block.index(item[f]) for f in sequence]
                require(positions[0] < positions[1] < positions[2], f"{item.get('id')}: declared delivery sequence differs from draft")
        if item.get('on_slide'):
            evidence(item, 'slide_quote', 'slides')
        require(bool(item.get('semantic_review', '').strip()), 'landing needs semantic review note')
    if not lines:
        require(bool(contract.get('no_landings_reason', '').strip()), 'explain why no memorable landings fit')
    return {'errors': errors, 'assessment': {'traceability': 'fail' if errors else 'pass',
            'intent_completeness': 'human_or_model_review_required',
            'meaning_fidelity': 'human_or_model_review_required',
            'surprise_humor_and_audience_effect': 'not_measured'}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('draft', type=Path)
    p.add_argument('contract', type=Path)
    args = p.parse_args()
    try:
        result = check(args.source.read_text(encoding='utf-8'), args.draft.read_text(encoding='utf-8'),
                       json.loads(args.contract.read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
        result = {'errors': [f'invalid input: {exc}']}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(result['errors']))


if __name__ == '__main__':
    raise SystemExit(main())
