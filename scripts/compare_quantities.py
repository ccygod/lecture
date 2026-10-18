#!/usr/bin/env python3
"""Calculate supplied data references; does not verify sources or rhetorical fit."""
from __future__ import annotations
import argparse
from decimal import Decimal, InvalidOperation, localcontext
import json
from pathlib import Path

UNITS={
    '元':('money:CNY','1'),'万元':('money:CNY','10000'),'亿元':('money:CNY','100000000'),
    '美元':('money:USD','1'),'万美元':('money:USD','10000'),'亿美元':('money:USD','100000000'),
    '人':('people','1'),'万人':('people','10000'),'亿人':('people','100000000'),
    '秒':('duration','1'),'分钟':('duration','60'),'小时':('duration','3600'),
    '项':('items','1'),'万项':('items','10000'),'%':('rate','0.01')
}
STATUSES={'actual','forecast','estimate','hypothetical'}
PURPOSES={'scale_reference','like_for_like','trend'}

def validate(q):
    if not isinstance(q,dict): raise ValueError('quantity must be an object')
    for field in ['id','value','unit','metric','subject','period','status','source']:
        if field not in q or q[field] is None or not str(q[field]).strip():
            raise ValueError('quantity requires '+field)
    for field in ['id','unit','metric','subject','period','status','source']:
        if not isinstance(q[field],str): raise ValueError(field+' must be text')
    if q['unit'] not in UNITS: raise ValueError('unsupported unit: '+str(q['unit']))
    if q['status'] not in STATUSES: raise ValueError('unknown factual status')
    try: value=Decimal(str(q['value']))
    except InvalidOperation: raise ValueError('value must be numeric') from None
    if not value.is_finite() or value<0: raise ValueError('value must be finite and nonnegative')
    dimension,factor=UNITS[q['unit']]
    return value*Decimal(factor),dimension

def decimal_text(x):
    rounded=x.quantize(Decimal('0.000001'))
    return format(rounded,'f').rstrip('0').rstrip('.') if rounded else '0'

def compare(target,reference,purpose):
    if purpose not in PURPOSES: raise ValueError('unknown comparison purpose')
    with localcontext() as context:
        context.prec=40
        left,dim_left=validate(target);right,dim_right=validate(reference)
        if dim_left!=dim_right: raise ValueError('incompatible dimensions/currencies; no implicit conversion')
        if right==0: raise ValueError('reference must be greater than zero')
        if purpose=='like_for_like' and (target['metric']!=reference['metric'] or target['period']!=reference['period']):
            raise ValueError('like_for_like requires the same metric and period')
        if purpose=='trend' and (target['metric']!=reference['metric'] or target['subject']!=reference['subject']):
            raise ValueError('trend requires the same metric and subject')
        warnings=[]
        if purpose=='scale_reference':
            warnings.append('scale reference only; this ratio is not market share, revenue equivalence or causal evidence')
        if target['metric']!=reference['metric'] or target['period']!=reference['period']:
            warnings.append('retain the different metrics/periods in the spoken explanation')
        if target['status']!='actual' or reference['status']!='actual':
            warnings.append('forecast/estimate/hypothetical status is preserved; do not describe as observed actuals')
        ratio=left/right
        result={'purpose':purpose,'target':dict(target),'reference':dict(reference),
                'ratio':decimal_text(ratio),'percentage_of_reference':decimal_text(ratio*100),
                'warnings':warnings,
                'assessment':{'arithmetic':'calculated','source_truth':'not_assessed','audience_fit':'not_assessed'}}
        if left: result['reference_multiple_of_target']=decimal_text(right/left)
        if purpose=='trend': result['relative_change_percent']=decimal_text((ratio-1)*100)
        return result

def evaluate(plan):
    if not isinstance(plan,dict) or not isinstance(plan.get('quantities'),list) or not isinstance(plan.get('comparisons'),list):
        raise ValueError('plan requires quantities and comparisons arrays')
    quantities={}
    for q in plan['quantities']:
        validate(q)
        if q['id'] in quantities: raise ValueError('duplicate quantity id: '+q['id'])
        quantities[q['id']]=q
    results=[];seen=set()
    for c in plan['comparisons']:
        if not isinstance(c,dict): raise ValueError('comparison must be an object')
        for field in ['id','target','reference','purpose']:
            if not isinstance(c.get(field),str) or not c[field].strip(): raise ValueError('comparison requires text '+field)
        if c['id'] in seen: raise ValueError('duplicate comparison id: '+c['id'])
        seen.add(c['id'])
        if c['target'] not in quantities or c['reference'] not in quantities: raise ValueError('comparison references an unknown quantity')
        r=compare(quantities[c['target']],quantities[c['reference']],c['purpose'])
        results.append({'id':c['id'],**r})
    return {'comparisons':results,'assessment':'arithmetic only; supplied sources and audience fit require review'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    try: result=evaluate(json.loads(args.plan.read_text(encoding='utf-8')))
    except (ValueError,TypeError,KeyError,InvalidOperation) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False));return 1
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if args.out: args.out.write_text(text,encoding='utf-8')
    else: print(text)
    return 0

if __name__=='__main__': raise SystemExit(main())
