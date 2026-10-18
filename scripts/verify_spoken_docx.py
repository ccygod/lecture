#!/usr/bin/env python3
"""Verify speech paragraph styles and real OOXML font properties, not rendered appearance."""
import argparse,json,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def check_docx_roles(path,expected=None,spoken_font='Microsoft YaHei',staff_font='FangSong',spoken_size=13.5,staff_size=11):
 errors=[]
 with zipfile.ZipFile(path) as z:doc=ET.fromstring(z.read('word/document.xml'));styles=ET.fromstring(z.read('word/styles.xml'))
 style_map={s.get(W+'styleId'):s for s in styles.findall(W+'style')}
 def inherited(ident,tag,attr,visited=None):
  visited=set() if visited is None else visited
  if ident in visited or ident not in style_map:return None
  visited.add(ident);s=style_map[ident];e=s.find(W+'rPr/'+W+tag)
  if e is not None and e.get(W+attr) is not None:return e.get(W+attr)
  based=s.find(W+'basedOn');return inherited(based.get(W+'val'),tag,attr,visited) if based is not None else None
 oral=[];staff=0
 for p in doc.findall('.//'+W+'body/'+W+'p'):
  text=''.join(x.text or '' for x in p.findall('.//'+W+'t'))
  e=p.find(W+'pPr/'+W+'pStyle');style=e.get(W+'val') if e is not None else 'Normal'
  if style=='LectureSpoken':
   oral.append(text)
   if '【不朗读' in text:errors.append('stage direction assigned to spoken style')
  elif style=='LectureNotes':staff+=1
  if style not in ('LectureSpoken','LectureNotes'):continue
  required_font=spoken_font if style=='LectureSpoken' else staff_font
  required_size=spoken_size if style=='LectureSpoken' else staff_size
  for run in p.findall(W+'r'):
   if not run.findall(W+'t'):continue
   f=run.find(W+'rPr/'+W+'rFonts');font=f.get(W+'eastAsia') if f is not None else inherited(style,'rFonts','eastAsia')
   sz=run.find(W+'rPr/'+W+'sz');val=sz.get(W+'val') if sz is not None else inherited(style,'sz','val')
   if font!=required_font:errors.append(f'{style}: actual font {font!r} != {required_font!r}')
   try: actual=float(val)/2
   except (ValueError,TypeError):actual=None
   if actual!=required_size:errors.append(f'{style}: actual size {actual} != {required_size}')
 if not oral:errors.append('no spoken paragraphs')
 if spoken_font==staff_font:errors.append('spoken and staff font families must differ')
 if expected is not None:
  for para in expected:
   if para not in oral:errors.append('expected spoken paragraph absent or wrongly styled: '+para[:35])
 return {'errors':errors,'spoken_paragraphs':len(oral),'notes_paragraphs':staff,'actual_font_properties':'fail' if errors else 'pass','rendered_appearance':'not_assessed'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('docx',type=Path);p.add_argument('--expected',type=Path);p.add_argument('--spoken-font',default='Microsoft YaHei');p.add_argument('--staff-font',default='FangSong');p.add_argument('--spoken-size',type=float,default=13.5);p.add_argument('--staff-size',type=float,default=11);a=p.parse_args()
 try:r=check_docx_roles(a.docx,json.loads(a.expected.read_text(encoding='utf-8')) if a.expected else None,a.spoken_font,a.staff_font,a.spoken_size,a.staff_size)
 except (OSError,ValueError,KeyError,zipfile.BadZipFile,ET.ParseError) as exc:p.exit(2,f'ERROR: {exc}\n')
 print(json.dumps(r,ensure_ascii=False,indent=2));return int(bool(r['errors']))
if __name__=='__main__':raise SystemExit(main())
