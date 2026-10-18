#!/usr/bin/env python3
"""Resolve stable slide IDs after final page ordering; leave unrelated numbers alone."""
import argparse,json,re
from pathlib import Path
TOKEN=re.compile(r'\{\{slide:([^{}]+)\}\}')
def compile_refs(text,pages):
 if not isinstance(pages,list):raise ValueError('page index must be ordered list')
 index={}
 for n,p in enumerate(pages,1):
  if not isinstance(p,dict) or not isinstance(p.get('id'),str) or not re.fullmatch(r'[A-Za-z0-9_-]+',p['id']):raise ValueError('invalid slide id')
  if p['id'] in index:raise ValueError('duplicate slide id')
  if not isinstance(p.get('title'),str) or not p['title'].strip():raise ValueError('slide title missing')
  index[p['id']]=n
 def replace(m):
  ident=m.group(1)
  if ident not in index:raise ValueError('unknown slide id: '+ident)
  return '页面'+str(index[ident])
 result=TOKEN.sub(replace,text)
 if '{{slide:' in result:raise ValueError('malformed slide token')
 return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('draft',type=Path);p.add_argument('index',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 try:
  result=compile_refs(a.draft.read_text(encoding='utf-8'),json.loads(a.index.read_text(encoding='utf-8')))
  a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(result,encoding='utf-8')
 except (ValueError,OSError,TypeError) as exc:p.exit(2,f'ERROR: {exc}\n')
 return 0
if __name__=='__main__':raise SystemExit(main())
