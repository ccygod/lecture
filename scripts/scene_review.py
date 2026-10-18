#!/usr/bin/env python3
"""Extract selected cases, analogies and callbacks from spoken text for version-bound review.

This tool checks provenance and ordering, not plausibility, humor or audience response.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROLES={'case':('goal','obstacle','response','consequence','insight'),
       'analogy':('familiar_relation','technical_relation','boundary','return_to_term'),
       'causal':('baseline','intervention','mediating_change','outcome','boundary'),
       'callback':('introduction','payoff')}
GATES=('grounded','relation_preserved','speakable','useful')

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def packet(spoken,plan):
    if not isinstance(spoken,list) or not spoken or any(not isinstance(p,str) or not p.strip() for p in spoken):
        raise ValueError('spoken must contain actual spoken paragraphs')
    if not isinstance(plan,dict) or not isinstance(plan.get('scenes'),list):
        raise ValueError('scenes list required')
    rows=[];seen=set()
    for scene in plan['scenes']:
        if not isinstance(scene,dict):raise ValueError('scene object required')
        ident=scene.get('id');kind=scene.get('kind')
        if not isinstance(ident,str) or not ident.strip() or ident in seen:raise ValueError('missing/duplicate scene id')
        seen.add(ident)
        if kind not in ROLES:raise ValueError('unknown scene kind')
        basis=scene.get('basis',{})
        if not isinstance(basis,dict) or basis.get('status') not in ('user_reported','source_supported','hypothetical'):
            raise ValueError('basis must distinguish observed material from teaching hypothesis')
        if not isinstance(basis.get('evidence'),str) or not basis['evidence'].strip():raise ValueError('basis evidence required')
        anchors=scene.get('anchors',{})
        if not isinstance(anchors,dict):raise ValueError('anchors object required')
        positions={}
        for role in ROLES[kind]:
            q=anchors.get(role)
            if not isinstance(q,str) or not q.strip():raise ValueError(f'{ident}: missing {role}')
            hits=[i for i,p in enumerate(spoken) if q in p]
            if len(hits)!=1:raise ValueError(f'{ident}/{role}: quote missing or ambiguous in spoken text')
            positions[role]=hits[0]
        if kind=='callback' and positions['payoff']<=positions['introduction']:
            raise ValueError('callback payoff must follow introduction')
        # Case sequences can show a failed attempt before the response; do not prescribe one narrative order.
        start=max(0,min(positions.values())-1);end=min(len(spoken),max(positions.values())+2)
        rows.append({**scene,'positions':positions,'context_start':start,'context':spoken[start:end]})
    result={'version':1,'spoken_sha256':digest(spoken),'scenes':rows,
            'checked':'quotes in actual spoken paragraphs, unique locations, callback order',
            'not_checked':['audience belief','causal validity','humor','live delivery']}
    result['packet_sha256']=digest(result)
    return result

def accept(p,review):
    if not isinstance(p,dict) or not isinstance(review,dict):raise ValueError('packet/review objects required')
    unsigned={k:v for k,v in p.items() if k!='packet_sha256'}
    if p.get('packet_sha256')!=digest(unsigned) or review.get('packet_sha256')!=p['packet_sha256']:
        raise ValueError('review is stale or packet was modified')
    ids={s['id'] for s in p['scenes']};seen=set();issues=[]
    if not isinstance(review.get('items'),list):raise ValueError('review items required')
    for item in review['items']:
        if not isinstance(item,dict) or item.get('id') not in ids or item['id'] in seen:raise ValueError('unknown/duplicate review id')
        seen.add(item['id'])
        if any(type(item.get(g)) is not bool for g in GATES):raise ValueError('all semantic gates must be booleans')
        if not isinstance(item.get('feedback'),str) or not item['feedback'].strip():raise ValueError('specific feedback required')
        if not all(item[g] for g in GATES):issues.append({'id':item['id'],'feedback':item['feedback']})
    if seen!=ids:raise ValueError('every selected scene must be reviewed')
    return {'accepted':not issues,'issues':issues,'packet_sha256':p['packet_sha256'],
            'reviewer_kind':review.get('reviewer_kind','unspecified'),
            'semantic_judgments':'provided by reviewer, not established by code','audience_effect':'not_measured'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('packet');p.add_argument('spoken',type=Path);p.add_argument('plan',type=Path);p.add_argument('--out',type=Path,required=True)
    a=sub.add_parser('accept');a.add_argument('packet',type=Path);a.add_argument('review',type=Path);a.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();load=lambda p:json.loads(p.read_text(encoding='utf-8'))
    try:
        result=packet(load(args.spoken),load(args.plan)) if args.cmd=='packet' else accept(load(args.packet),load(args.review))
        args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('quotes and order checked' if args.cmd=='packet' else ('review accepted' if result['accepted'] else 'revision required'))
        return int(result.get('accepted') is False)
    except (OSError,ValueError,TypeError,KeyError) as exc:parser.exit(2,f'ERROR: {exc}\n')

if __name__=='__main__':raise SystemExit(main())
