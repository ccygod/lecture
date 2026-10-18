#!/usr/bin/env python3
"""Per-invocation outline preflight and reply gate. No human authentication or semantic guarantee."""
import argparse,copy,hashlib,json,uuid
from pathlib import Path
from datetime import datetime,timezone
from outline_preflight import check_preflight
REQUIRED=('purpose','deliverable','slide_mode','brief')
PURPOSES=('teaching','briefing','public_talk','mixed','custom')
def digest(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def review_digest(review):return digest(json.dumps(review,ensure_ascii=False,sort_keys=True))
def question_errors(questions,review):
 errors=[]
 if not isinstance(questions,list) or len(questions)!=len(REQUIRED) or not all(isinstance(q,dict) and q.get('id') in REQUIRED and isinstance(q.get('prompt'),str) and q['prompt'].strip() for q in questions) or {q['id'] for q in questions}!=set(REQUIRED):
  return ['four current intake categories and prompts required, including purpose']
 if questions[0]['id']!='purpose':errors.append('purpose must be the first current confirmation')
 prompts='\n'.join(q['prompt'] for q in questions)
 critical=review.get('critical_questions',[]) if isinstance(review,dict) else []
 for q in critical if isinstance(critical,list) else []:
  if isinstance(q,dict) and isinstance(q.get('question'),str) and q['question'] not in prompts:
   errors.append('critical question not included in displayed question inventory: '+str(q.get('id')))
 return errors
def start_run(source,outline=None):
 return {'version':3,'run_id':str(uuid.uuid4()),'source_sha256':digest(source),
         'outline_sha256':digest(source if outline is None else outline),'outline_is_separate':outline is not None,
         'created_at':datetime.now(timezone.utc).isoformat(),'status':'awaiting_user','questions':[
  {'id':'purpose','prompt':'先确认本次目的：授课/培训、客户或领导汇报、公开演讲/合作发言、混合用途，还是其他目的？已有目的也请本轮确认；希望听众理解、认同或决定什么？可明确委托判断。'},
  {'id':'deliverable','prompt':'本轮希望交付完整Word讲稿与配套说明、实际PPT、两者，还是仅口播/页面说明？授课可选完整教参，汇报按汇报用途组织。'},
  {'id':'slide_mode','prompt':'本轮PPT用可编辑原生图文、整页ImageGen、网页互动、混合方式、仅教参暂不定，还是不做PPT？也可委托我选。'},
  {'id':'brief','prompt':'按已确认目的，本轮听众、总时长（是否含交流/互动）、预期结果、场合与口吻有哪些关键缺口？已知条件只确认或调整，不重填长问卷。'}]}
def prepare_run(run,outline,review):
 if not isinstance(run,dict) or run.get('version')!=3:raise ValueError('new authoring needs a current v3 purpose-first run')
 if run.get('outline_sha256')!=digest(outline):raise ValueError('outline changed since run creation')
 errors=check_preflight(outline,review)['errors']
 if errors:raise ValueError('; '.join(errors))
 prepared=copy.deepcopy(run);prepared['preflight']=copy.deepcopy(review)
 if 'questions' in review:prepared['questions']=copy.deepcopy(review['questions'])
 questions=prepared.get('questions',[])
 errors=question_errors(questions,review)
 if errors:raise ValueError('; '.join(errors))
 prepared['preflight_sha256']=review_digest(review)
 return prepared
def check_gate(source,run,receipt,outline=None):
 errors=[]
 def req(ok,msg):
  if not ok:errors.append(msg)
 if not isinstance(run,dict) or not isinstance(receipt,dict):return {'errors':['invalid intake objects'],'ready_for_generation':False}
 req(run.get('version')==3 and receipt.get('version')==3,'new authoring requires v3 purpose-first intake; legacy records are for read-only audit')
 req(isinstance(run.get('run_id'),str) and bool(run.get('run_id')),'missing current run id')
 req(run.get('run_id')==receipt.get('run_id'),'reply belongs to another invocation')
 req(run.get('source_sha256')==digest(source)==receipt.get('source_sha256'),'intake source changed or reply stale')
 actual_outline=outline if outline is not None else source
 req(not run.get('outline_is_separate') or outline is not None,'separate outline body required for generation check')
 req(run.get('outline_sha256')==digest(actual_outline),'actual outline changed or missing')
 review=run.get('preflight')
 preflight=check_preflight(actual_outline,review);errors.extend(preflight['errors'])
 if isinstance(review,dict):
  req(run.get('preflight_sha256')==review_digest(review)==receipt.get('preflight_sha256'),'outline diagnosis changed or reply points to another review')
  if 'questions' in review:req(review['questions']==run.get('questions'),'displayed questions differ from diagnosis question plan')
 display=receipt.get('preflight_display_receipt')
 req(isinstance(display,str) and bool(display.strip()),'missing actual preflight display receipt/location')
 questions=run.get('questions',[])
 errors.extend(question_errors(questions,review))
 qr=receipt.get('question_receipt')
 req(isinstance(qr,str) and bool(qr.strip()),'missing actual current question receipt/location')
 answers=receipt.get('answers',{})
 if not isinstance(answers,dict):answers={};errors.append('invalid answers')
 for key in REQUIRED:
  row=answers.get(key,{})
  if not isinstance(row,dict):row={}
  req(isinstance(row.get('value'),str) and bool(row['value'].strip()),'unanswered: '+key)
  req(row.get('origin') in ('user_reply','user_delegation'),'not a current user answer: '+key)
  req(isinstance(row.get('evidence'),str) and bool(row['evidence'].strip()),'no user reply evidence: '+key)
 purpose=answers.get('purpose',{})
 mode=purpose.get('mode') if isinstance(purpose,dict) else None
 req(mode in PURPOSES,'purpose needs a current selected/delegated mode, not audience-based inference')
 if isinstance(review,dict):
  resolutions=receipt.get('resolutions',{})
  if not isinstance(resolutions,dict):resolutions={}
  for q in review.get('critical_questions',[]) if isinstance(review.get('critical_questions'),list) else []:
   if not isinstance(q,dict):continue
   row=resolutions.get(q.get('id'),{})
   if not isinstance(row,dict):row={}
   req(isinstance(row.get('value'),str) and bool(row['value'].strip()) and row.get('origin') in ('user_reply','user_delegation') and isinstance(row.get('evidence'),str) and bool(row['evidence'].strip()),'unresolved critical outline question: '+str(q.get('id')))
 return {'errors':errors,'ready_for_generation':not errors,'purpose_mode':mode if not errors else None,'assessment':'current purpose choice, source-bound diagnosis, recorded display and replies checked; authenticity, purpose interpretation and outline quality require actual conversation and semantic review'}
def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
 x=sub.add_parser('start');x.add_argument('source',type=Path);x.add_argument('--out',type=Path,required=True)
 x.add_argument('--outline',type=Path,help='Actual outline when different from this request')
 x=sub.add_parser('prepare');x.add_argument('run',type=Path);x.add_argument('outline',type=Path);x.add_argument('review',type=Path);x.add_argument('--out',type=Path,required=True)
 x=sub.add_parser('check');x.add_argument('source',type=Path);x.add_argument('run',type=Path);x.add_argument('receipt',type=Path)
 x.add_argument('--outline',type=Path)
 a=p.parse_args()
 try:
  source=a.source.read_text(encoding='utf-8') if a.cmd!='prepare' else None
  if a.cmd=='start':
   result=start_run(source,a.outline.read_text(encoding='utf-8') if a.outline else None);a.out.parent.mkdir(parents=True,exist_ok=True)
   with a.out.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
  elif a.cmd=='prepare':
   result=prepare_run(json.loads(a.run.read_text(encoding='utf-8')),a.outline.read_text(encoding='utf-8'),json.loads(a.review.read_text(encoding='utf-8')))
   a.out.parent.mkdir(parents=True,exist_ok=True)
   with a.out.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
  else:result=check_gate(source,json.loads(a.run.read_text(encoding='utf-8')),json.loads(a.receipt.read_text(encoding='utf-8')),a.outline.read_text(encoding='utf-8') if a.outline else None)
  print(json.dumps(result,ensure_ascii=False,indent=2));return int(bool(result.get('errors')))
 except (OSError,ValueError,TypeError) as exc:p.exit(2,f'ERROR: {exc}\n')
if __name__=='__main__':raise SystemExit(main())
