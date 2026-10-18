#!/usr/bin/env python3
"""Check source identity, excerpt locations and declared reading coverage.

Hashes cannot prove comprehension, transcription fidelity or actual listening.
"""
import argparse
import hashlib
import json
from pathlib import Path

KINDS={'transcript','edited_speech','live_summary','video_transcript','catalogue','blocked'}
EXTENTS={'complete_page','partial_page','unknown','complete_speech_verified'}
def digest(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()

def check(manifest,bodies):
    errors=[];sources={};ids=set()
    if not isinstance(manifest,dict) or not isinstance(manifest.get('sources'),list) or not isinstance(manifest.get('analyses'),list):
        return {'errors':['sources and analyses arrays required'],'read_and_interpretation_verified':False}
    for s in manifest['sources']:
        if not isinstance(s,dict):errors.append('source object required');continue
        ident=s.get('id');kind=s.get('kind');body=bodies.get(ident)
        if not isinstance(ident,str) or not ident.strip() or ident in sources:errors.append('source id missing/duplicate');continue
        sources[ident]=s
        if kind not in KINDS:errors.append(f'{ident}: unknown kind')
        if s.get('extent') not in EXTENTS:errors.append(f'{ident}: unknown extent')
        if s.get('extent')=='complete_speech_verified' and kind not in ('transcript','video_transcript'):
            errors.append(f'{ident}: summaries or edited versions cannot establish a complete speech')
        if s.get('extent')=='complete_speech_verified' and (not isinstance(s.get('verification_record'),str) or not s['verification_record'].strip()):
            errors.append(f'{ident}: complete speech claim requires an actual verification record')
        if not isinstance(body,str) or not body.strip():errors.append(f'{ident}: actual body missing');continue
        if 'CF_APP_WAF' in body and 'var requestInfo' in body:
            errors.append(f'{ident}: known web verification interstitial, not a speech body')
        if s.get('body_sha256')!=digest(body):errors.append(f'{ident}: source body changed')
        ranges=s.get('reviewed_ranges')
        if not isinstance(ranges,list):errors.append(f'{ident}: reviewed ranges missing');continue
        for span in ranges:
            if not isinstance(span,list) or len(span)!=2 or any(type(n) is not int for n in span) or not 0<=span[0]<span[1]<=len(body):
                errors.append(f'{ident}: invalid reviewed range')
    for a in manifest['analyses']:
        if not isinstance(a,dict):errors.append('analysis object required');continue
        ident=a.get('id');sid=a.get('source_id');s=sources.get(sid);body=bodies.get(sid)
        if not isinstance(ident,str) or not ident.strip() or ident in ids:errors.append('analysis id missing/duplicate');continue
        ids.add(ident)
        if not s or not isinstance(body,str):errors.append(f'{ident}: source missing');continue
        if s.get('kind') in ('catalogue','blocked'):errors.append(f'{ident}: catalogue/blocked page cannot support speech analysis')
        start=a.get('start');end=a.get('end')
        if type(start) is not int or type(end) is not int or not 0<=start<end<=len(body):errors.append(f'{ident}: invalid analysis span');continue
        if a.get('span_sha256')!=digest(body[start:end]):errors.append(f'{ident}: analysis span changed')
        good=[x for x in s.get('reviewed_ranges',[]) if isinstance(x,list) and len(x)==2 and all(type(n) is int for n in x)]
        if not any(x[0]<=start and end<=x[1] for x in good):errors.append(f'{ident}: analysis extends beyond declared reviewed text')
        if not isinstance(a.get('inference'),str) or not a['inference'].strip():errors.append(f'{ident}: specific inference required')
    return {'errors':errors,'source_count':len(sources),'analysis_count':len(ids),
            'read_and_interpretation_verified':False,
            'checked':'body hashes, source types, locations and declared coverage; reviewer must verify meaning and actual reading'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('manifest',type=Path);parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    try:
        m=json.loads(args.manifest.read_text(encoding='utf-8'));bodies={s['id']:(args.manifest.parent/s['body_file']).read_text(encoding='utf-8') for s in m['sources']}
        result=check(m,bodies);output=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.out:args.out.write_text(output,encoding='utf-8')
        else:print(output,end='')
        return int(bool(result['errors']))
    except (OSError,ValueError,KeyError,TypeError) as e:parser.exit(2,f'ERROR: {e}\n')
if __name__=='__main__':raise SystemExit(main())
