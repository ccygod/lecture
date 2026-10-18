#!/usr/bin/env python3
"""Check a source-bound outline diagnosis; semantic quality still needs a reader."""
import argparse,hashlib,json
from pathlib import Path
DIMENSIONS=('audience','outcome','scope_time','claims_evidence','delivery')
STATUSES={'provided','unknown','review_needed','not_applicable'}
def digest(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def text(value):return isinstance(value,str) and bool(value.strip())
def check_preflight(outline,review):
    errors=[]
    if not isinstance(review,dict):return {'errors':['outline review missing'],'semantic_quality':'not_assessed'}
    if review.get('version')!=1:errors.append('invalid outline review version')
    if review.get('outline_sha256')!=digest(outline):errors.append('outline review belongs to different or changed outline')
    for f in ('diagnosis','recommendation'):
        if not text(review.get(f)):errors.append('outline review requires '+f)
    checks=review.get('checks');seen=set()
    if not isinstance(checks,list):checks=[];errors.append('outline checks missing')
    for row in checks:
        if not isinstance(row,dict):errors.append('outline check must be object');continue
        ident=row.get('id');status=row.get('status')
        if ident not in DIMENSIONS or ident in seen:errors.append('unknown/duplicate outline dimension')
        seen.add(ident)
        if status not in STATUSES:errors.append('invalid outline evidence status')
        if not text(row.get('decision')):errors.append('dimension needs design consequence or reason not to ask')
        quote=row.get('evidence','')
        if status in ('provided','review_needed') and (not text(quote) or quote not in outline):errors.append('supplied/review evidence must quote actual outline')
        elif quote and (not isinstance(quote,str) or quote not in outline):errors.append('outline evidence quote missing')
    if seen!=set(DIMENSIONS):errors.append('outline review must cover the five decision dimensions')
    for f in ('strengths','risks','critical_questions'):
        if not isinstance(review.get(f),list):errors.append('outline review requires '+f)
    for item in review.get('strengths',[]) if isinstance(review.get('strengths'),list) else []:
        if not text(item):errors.append('strength must be text')
    for risk in review.get('risks',[]) if isinstance(review.get('risks'),list) else []:
        if not isinstance(risk,dict) or any(not text(risk.get(k)) for k in ('problem','consequence','suggestion')):
            errors.append('risk needs problem, consequence and suggestion');continue
        if risk.get('source_quote') and risk['source_quote'] not in outline:errors.append('risk quote absent from outline')
    ids=set()
    for q in review.get('critical_questions',[]) if isinstance(review.get('critical_questions'),list) else []:
        if not isinstance(q,dict) or any(not text(q.get(k)) for k in ('id','question','why')) or q.get('dimension') not in DIMENSIONS:errors.append('critical question needs id, dimension, question and design consequence');continue
        if q['id'] in ids:errors.append('duplicate critical question')
        ids.add(q['id'])
    for row in checks:
        if isinstance(row,dict) and row.get('id') in ('audience','outcome','scope_time') and row.get('status')=='unknown':
            qs=review.get('critical_questions',[])
            if not isinstance(qs,list) or not any(isinstance(q,dict) and q.get('dimension')==row['id'] for q in qs):errors.append('unknown audience/outcome/time needs a targeted question: '+row['id'])
    return {'errors':errors,'semantic_quality':'not_assessed','assessment':'source version, declared dimensions, evidence locations and missing decisions checked; no audience profiling or outline quality guarantee'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('outline',type=Path);p.add_argument('review',type=Path);a=p.parse_args()
    try:
        r=check_preflight(a.outline.read_text(encoding='utf-8'),json.loads(a.review.read_text(encoding='utf-8')));print(json.dumps(r,ensure_ascii=False,indent=2));return int(bool(r['errors']))
    except (OSError,ValueError,TypeError) as e:p.exit(2,f'ERROR: {e}\n')
if __name__=='__main__':raise SystemExit(main())
