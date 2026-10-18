#!/usr/bin/env python3
"""Classify structured lecture paragraphs for separate Word styles. No taste scoring."""
import re
class ParagraphRoles:
 def __init__(self,scope='full'):
  self.spoken_only=scope=='spoken';self.in_first=self.spoken_only;self.active=self.spoken_only
 def role(self,line):
  s=line.strip()
  if not s:return 'blank'
  if re.match(r'^#{1,4}\s',s):
   if '第一部分' in s:self.in_first=True
   elif '第二部分' in s or '第三部分' in s:self.in_first=False
   self.active=self.spoken_only
   return 'heading'
  if s.startswith('**翻页提示'):
   self.active=self.in_first;return 'notes'
  if s.startswith(('【不朗读','> 【不朗读')):return 'stage'
  if s.startswith(('- ','备课提示','**备课提示','时间：','概要：')):return 'notes'
  return 'spoken' if self.in_first and self.active else 'notes'
