#!/usr/bin/env python3
"""Route rhetorical needs and record reviewed candidate selection. No LLM or API calls."""
import argparse
import hashlib
import json
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / 'references' / 'editor-mechanisms.json'
EPISODES = CATALOG.with_name('source-episodes.json')
NEEDS = {'challenge_default','explain_mechanism','develop_choice','translate_impact',
         'consolidate','close','humanize','plain','connect_value'}
EFFECTS = ('humor','curiosity')

def source_episode(ident,source_body=None,image_files=None):
    rows=json.loads(EPISODES.read_text(encoding='utf-8'))['episodes']
    found=[r for r in rows if r.get('id')==ident]
    if len(found)!=1:raise ValueError('unknown or duplicate source episode')
    row=found[0];source=row['source']
    if source_body is not None and image_files:raise ValueError('choose actual text or visual source for this episode')
    if source_body is not None:
        if not isinstance(source_body,str) or hashlib.sha256(source_body.encode('utf-8')).hexdigest()!=source.get('body_sha256'):
            raise ValueError('source body differs from the located original')
        start,end=source['char_span'];span=source_body[start:end]
        if hashlib.sha256(span.encode('utf-8')).hexdigest()!=source.get('span_sha256'):raise ValueError('source episode span changed')
        row['reading_material']={'kind':'source_text_span','text':span,'source_body_verified':True,'comprehension_verified':False}
    elif image_files:
        records={x['sha256']:x for x in source.get('visual_locations',[])};verified=[]
        for file in image_files:
            path=Path(file);sha=hashlib.sha256(path.read_bytes()).hexdigest()
            if sha not in records:raise ValueError('image is not a located source frame for this episode')
            verified.append({'path':str(path.resolve()),'sha256':sha,'url':records[sha]['url']})
        row['reading_material']={'kind':'source_visual_files','files':verified,'visual_reading_verified':False,'next_action':'Inspect the actual source images with the image reader; file identity is not visual reading.'}
    return row

def fingerprint(value,field):
    body={k:v for k,v in value.items() if k!=field}
    return hashlib.sha256(json.dumps(body,ensure_ascii=False,sort_keys=True).encode('utf-8')).hexdigest()

def effect_list(values):
    if not isinstance(values,list) or any(e not in EFFECTS for e in values) or len(set(values))!=len(values):
        raise ValueError('required_effects must contain distinct humor/curiosity targets')
    return values[:]

def checked_plan(value):
    if not isinstance(value,dict) or value.get('version')!=2 or value.get('plan_sha256')!=fingerprint(value,'plan_sha256'):
        raise ValueError('current unchanged v2 editorial plan required')
    if not value.get('ready_for_selection'):raise ValueError('expression intent is not allocated or explicitly omitted')
    return {b['id']:b for b in value['beats']}

def relevance_bridge(value):
    if not isinstance(value, dict): raise ValueError('connect_value requires relevance bridge')
    fields=('audience_anchor','content_fact','mechanism','consequence','action','boundary')
    for field in fields:
        if not isinstance(value.get(field),str) or not value[field].strip():
            raise ValueError(f'relevance: missing {field}')
    status=value.get('link_status');strength=value.get('wording_strength')
    if status not in ('supported','conditional','unknown'): raise ValueError('invalid link_status')
    if strength not in ('observed','conditional'): raise ValueError('unsupported or guaranteed wording strength')
    if status!='supported' and strength!='conditional': raise ValueError('uncertain link needs conditional wording')
    evidence=value.get('evidence')
    if not isinstance(evidence,list) or not evidence or any(not isinstance(x,str) or not x.strip() for x in evidence):
        raise ValueError('relevance needs evidence or an explicit evidence gap')
    result=dict(value)
    if 'timeline' in result:
        t=result['timeline']
        if not isinstance(t,dict) or any(type(t.get(f)) is not int for f in ('start_year','years','target_year')):
            raise ValueError('timeline years must be integers')
        if t['years']<=0 or t['start_year']+t['years']!=t['target_year']:
            raise ValueError('audience timeline does not align')
        result['timeline']={**t,'calculated_year':t['start_year']+t['years']}
    result['assessment']='bridge fields and arithmetic checked; relevance and causal validity require semantic review'
    return result

def plan(request):
    if not isinstance(request,dict): raise ValueError('request must be object')
    purpose=request.get('purpose_mode','teaching')
    if purpose not in ('teaching','briefing','public_talk','mixed','custom'):raise ValueError('unknown purpose mode')
    humor=request.get('humor','light' if purpose=='teaching' else 'off')
    if humor not in ('off','light','moderate'): raise ValueError('invalid humor')
    beats=request.get('beats')
    if not isinstance(beats,list) or not beats: raise ValueError('beats must be nonempty list')
    requested=effect_list(request.get('required_effects',[]))
    if humor!='off' and 'humor' not in requested:requested.append('humor')
    if humor=='off' and 'humor' in requested:raise ValueError('humor off conflicts with humor target')
    omissions=request.get('effect_omissions',{})
    if not isinstance(omissions,dict) or any(k not in requested or not isinstance(v,str) or not v.strip() for k,v in omissions.items()):
        raise ValueError('effect omissions need a requested effect and a concrete reason')
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    known=catalog['priority']
    def inspiration_list(field,default):
        values=request.get(field,default)
        if not isinstance(values,list) or any(not isinstance(v,str) or v not in known for v in values) or len(set(values))!=len(values):
            raise ValueError(f'{field}: unknown or duplicate inspiration')
        return values
    preferred=inspiration_list('inspiration_priority',known)
    priority=preferred+[v for v in known if v not in preferred]
    allowed=set(inspiration_list('allowed_inspirations',known))
    ranking={name:i for i,name in enumerate(priority)}
    result=[];ids=set()
    for beat in beats:
        if not isinstance(beat,dict): raise ValueError('beat must be object')
        ident=beat.get('id');need=beat.get('need')
        if not isinstance(ident,str) or not ident.strip() or ident in ids: raise ValueError('beat id missing/duplicate')
        ids.add(ident)
        if need not in NEEDS: raise ValueError('unknown rhetorical need')
        if not isinstance(beat.get('claim_id'),str) or not beat['claim_id'].strip(): raise ValueError('claim_id missing')
        relevance=relevance_bridge(beat.get('relevance')) if need=='connect_value' else None
        critical=beat.get('critical_instruction',False)
        if type(critical) is not bool: raise ValueError('critical_instruction must be boolean')
        targets=effect_list(beat.get('required_effects',[]))
        if 'humor' in targets and (humor=='off' or critical):raise ValueError('humor target conflicts with current instruction mode')
        for effect in targets:
            if effect not in requested:requested.append(effect)
        direct=need=='plain' or critical
        cards=[] if direct else [dict(card) for card in catalog['cards']
                                 if need in card['needs'] and card['inspiration'] in allowed and not (humor=='off' and card['requires_humor'])]
        cards.sort(key=lambda c:ranking[c['inspiration']])
        direct = direct or not cards
        cards.append({'id':'plain','inspiration':None,'requires_humor':False,
                      'move':'直接解释同一主张，保留必要条件。作为比较基线，也可成为最终选择。'})
        row={'id':ident,'claim_id':beat['claim_id'],'need':need,
                       'generation':'direct' if direct else 'compare', 'options':cards,
                       'review_focus':['faithful','grounded','speakable','useful'],
                       'required_effects':targets,
                       'context_required':['original_claim','audience','before_and_after'],
                       'stop':'发现具体缺陷才改写；通常一次修订，仍有缺陷最多再一次，之后保留最佳合格版本并报告缺口。'}
        if relevance is not None:row['relevance']=relevance
        result.append(row)
    covered={e for b in result for e in b['required_effects']}
    if covered.intersection(omissions):raise ValueError('same effect cannot be both targeted and globally omitted')
    unresolved=[e for e in requested if e not in covered and e not in omissions]
    output={'version':2,'routing_basis':'declared rhetorical need, not topic keywords or humor score',
            'purpose_mode':purpose,'humor':humor,'requested_effects':requested,'effect_omissions':dict(omissions),
            'unresolved_effects':unresolved,'ready_for_selection':not unresolved,
            'beats':result,'model_calls_performed':0}
    output['plan_sha256']=fingerprint(output,'plan_sha256')
    return output

def select(candidates,review,editorial_plan=None,beat_id=None):
    if not isinstance(candidates,list) or not candidates or not isinstance(review,dict):
        raise ValueError('invalid candidates/review')
    candidate_map={}
    for c in candidates:
        if not isinstance(c,dict):raise ValueError('candidate must be object')
        ident=c.get('id');text=c.get('text')
        if not isinstance(ident,str) or not ident.strip() or ident in candidate_map:raise ValueError('duplicate/missing candidate id')
        if not isinstance(text,str) or not text.strip():raise ValueError('empty candidate')
        candidate_map[ident]=text
    rows=review.get('candidates');checks={}
    effects=effect_list(review.get('required_effects',[]))
    if editorial_plan is not None or beat_id is not None:
        beats=checked_plan(editorial_plan)
        if beat_id not in beats:raise ValueError('selection beat missing from plan')
        if set(effects)!=set(beats[beat_id]['required_effects']):raise ValueError('review effects differ from planned position')
        effects=beats[beat_id]['required_effects'][:]
    if not isinstance(rows,list):raise ValueError('reviews missing')
    for row in rows:
        if not isinstance(row,dict):raise ValueError('review must be object')
        ident=row.get('id')
        if ident not in candidate_map or ident in checks or row.get('text')!=candidate_map[ident]:
            raise ValueError('review stale, duplicate or references unknown candidate')
        for f in ('faithful','grounded','speakable','useful'):
            if type(row.get(f)) is not bool:raise ValueError('review gates must be booleans')
        if not isinstance(row.get('evidence'),str) or not row['evidence'].strip():raise ValueError('specific feedback required')
        for effect in effects:
            result=row.get('effects',{}).get(effect) if isinstance(row.get('effects',{}),dict) else None
            if not isinstance(result,dict) or type(result.get('passes')) is not bool or not isinstance(result.get('evidence'),str) or not result['evidence'].strip():
                raise ValueError('each requested effect needs a boolean judgment and specific feedback')
        checks[ident]=row
    if set(checks)!=set(candidate_map):raise ValueError('every candidate needs a review')
    chosen=review.get('preferred')
    if chosen not in candidate_map or not isinstance(review.get('reason'),str) or not review['reason'].strip():raise ValueError('preference/reason missing')
    eligible=all(checks[chosen][f] for f in ('faithful','grounded','speakable','useful'))
    eligible=eligible and all(checks[chosen]['effects'][e]['passes'] for e in effects)
    output={'status':'selected' if eligible else 'revision_required',
            'selected':chosen if eligible else None,'text':candidate_map[chosen] if eligible else None,
            'reason':review['reason'],'reviewer_kind':review.get('reviewer_kind','unspecified'),
            'semantic_judgments':'supplied by reviewer; not independently established by this script',
            'required_effects':effects,
            'effect_judgments':{e:checks[chosen]['effects'][e] for e in effects},
            'coverage_state':'plan_bound' if editorial_plan is not None else 'unbound_legacy_audit',
            'audience_effect':'not_measured'}
    if editorial_plan is not None:output.update(plan_sha256=editorial_plan['plan_sha256'],beat_id=beat_id)
    output['selection_sha256']=fingerprint(output,'selection_sha256')
    return output

def check_coverage(editorial_plan,selections,spoken):
    errors=[];found={}
    try:beats=checked_plan(editorial_plan)
    except ValueError as exc:return {'errors':[str(exc)],'ready_for_delivery':False,'audience_effect':'not_measured'}
    if not isinstance(selections,list):selections=[];errors.append('selection array required')
    if not isinstance(spoken,str) or not spoken.strip():spoken='';errors.append('actual spoken text required')
    for row in selections:
        if not isinstance(row,dict):errors.append('selection object required');continue
        ident=row.get('beat_id');beat=beats.get(ident) if isinstance(ident,str) else None
        if beat is None or ident in found:errors.append('unknown, duplicate or unbound selected position');continue
        found[ident]=row
        if row.get('plan_sha256')!=editorial_plan['plan_sha256'] or row.get('coverage_state')!='plan_bound':errors.append(ident+': selection belongs to another plan')
        if row.get('selection_sha256')!=fingerprint(row,'selection_sha256'):errors.append(ident+': selected record changed')
        if row.get('status')!='selected':errors.append(ident+': candidate not selected')
        if row.get('required_effects')!=beat['required_effects']:errors.append(ident+': effects differ from plan')
        judgments=row.get('effect_judgments',{})
        for effect in beat['required_effects']:
            j=judgments.get(effect,{}) if isinstance(judgments,dict) else {}
            if not isinstance(j,dict) or j.get('passes') is not True or not isinstance(j.get('evidence'),str) or not j['evidence'].strip():errors.append(ident+': planned effect has no passing feedback: '+effect)
        if not isinstance(row.get('text'),str) or not row['text'].strip() or row['text'] not in spoken:errors.append(ident+': selected text absent from actual spoken draft')
    for ident,beat in beats.items():
        if (beat['generation']=='compare' or beat['required_effects']) and ident not in found:errors.append(ident+': selected position missing')
    return {'errors':errors,'ready_for_delivery':not errors,'covered_positions':list(found),
            'effect_omissions':editorial_plan['effect_omissions'],'audience_effect':'not_measured',
            'spoken_sha256':hashlib.sha256(spoken.encode('utf-8')).hexdigest(),
            'assessment':'plan, declared semantic feedback and actual selected text linked; not proof of humor, comprehension or authentic independent review'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('plan',help='Route declared need',description='Needs: '+', '.join(sorted(NEEDS)));p.add_argument('request',type=Path);p.add_argument('--out',type=Path)
    p=sub.add_parser('select');p.add_argument('candidates',type=Path);p.add_argument('review',type=Path);p.add_argument('--out',type=Path)
    p.add_argument('--plan',type=Path);p.add_argument('--beat')
    p=sub.add_parser('coverage');p.add_argument('plan',type=Path);p.add_argument('selections',type=Path);p.add_argument('spoken',type=Path);p.add_argument('--out',type=Path)
    p=sub.add_parser('episode');p.add_argument('id');p.add_argument('--out',type=Path)
    p.add_argument('--body',type=Path);p.add_argument('--image',type=Path,action='append')
    args=parser.parse_args()
    try:
        load=lambda p:json.loads(p.read_text(encoding='utf-8'))
        if args.cmd=='plan':result=plan(load(args.request))
        elif args.cmd=='episode':result=source_episode(args.id,args.body.read_text(encoding='utf-8') if args.body else None,args.image)
        elif args.cmd=='coverage':result=check_coverage(load(args.plan),load(args.selections),args.spoken.read_text(encoding='utf-8'))
        else:result=select(load(args.candidates),load(args.review),load(args.plan) if args.plan else None,args.beat)
        output=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(output,encoding='utf-8')
        else:print(output,end='')
        return int(result.get('status')=='revision_required' or result.get('ready_for_selection') is False or result.get('ready_for_delivery') is False)
    except (ValueError,OSError,TypeError,AttributeError) as exc:
        parser.exit(2,f'ERROR: {exc}\n')
if __name__=='__main__':raise SystemExit(main())
