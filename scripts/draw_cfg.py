#!/usr/bin/env python3
"""Draw the lab CFG with real JUnit method names on every edge (Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from analyze_du import B, BTESTS, bonus_trace, analyze
import math
ROOT=Path(__file__).resolve().parents[1]
W,H=5400,3550
im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f=ImageFont.truetype(font,27); small=ImageFont.truetype(font,20);title=ImageFont.truetype(font,44)
pos={'31':(1900,170),'32a':(1900,390),'32b':(1900,610),'33':(3800,500),
'35':(1900,830),'36':(1900,1050),'37':(1900,1270),'38p':(1900,1510),
'38a':(1900,1750),'39':(1900,1990),'40':(1900,2230),'41':(1900,2470),
'42':(1900,2710),'43':(1900,2950),'46':(450,2230),
'49':(3800,1750),'50':(3800,1990),'51':(3800,2230),'53':(3800,2470),
'54':(3800,2710),'56':(3800,2950)}
labels={'31':'31: entry; def attendance, threshold','32a':'32: attendance == null?',
'32b':'32: threshold < 0?','33':'33: throw IllegalArgumentException',
'35':'35: present = 0','36':'36: streak = 0','37':'37: best = 0',
'38p':'38: next element? (p attendance)','38a':'38: a = next element (c attendance)',
'39':'39: a > 0?','40':'40: present = present + 1','41':'41: streak = streak + 1',
'42':'42: streak > best?','43':'43: best = streak','46':'46: streak = 0 (kill)',
'49':'49: score = 0','50':'50: present >= threshold?','51':'51: score = 5',
'53':'53: best >= 5?','54':'54: score = score + 3','56':'56: return score'}
# shortest real method name per edge
hits={}
for _,name,args in BTESTS:
 t=bonus_trace(*args)
 for edge in zip(t,t[1:]):
  if edge not in hits or len(name)<len(hits[edge]):hits[edge]=name
conditional={'32a':('33','32b'),'32b':('33','35'),'38p':('38a','49'),
             '39':('40','46'),'42':('43','38p'),'50':('51','53'),'53':('54','56')}

def line(points,color='#475569'):
 d.line(points,fill=color,width=4)
 x,y=points[-1];px,py=points[-2];ang=math.atan2(y-py,x-px)
 d.polygon([(x,y),(x-18*math.cos(ang-.4),y-18*math.sin(ang-.4)),
            (x-18*math.cos(ang+.4),y-18*math.sin(ang+.4))],fill=color)
def text(x,y,s):
 box=d.textbbox((x,y),s,font=small);d.rectangle((box[0]-5,box[1]-3,box[2]+5,box[3]+3),fill='white')
 d.text((x,y),s,font=small,fill='#0f172a')

for (a,b),name in hits.items():
 x,y=pos[a];xx,yy=pos[b];cond=''
 if a in conditional:cond=('T' if b==conditional[a][0] else 'F')+' | '
 label=cond+name
 if a=='32a' and b=='33':
  points=[(x+370,y),(xx,y),(xx,yy-52)];loc=(2460,y-36)
 elif a=='32b' and b=='33':
  points=[(x+370,y),(xx,y),(xx,yy+52)];loc=(2460,y+20)
 elif a=='38p' and b=='49':
  points=[(x+370,y),(xx,y),(xx,yy-52)];loc=(2460,y-36)
 elif a=='39' and b=='46':
  points=[(x-370,y),(xx,y),(xx,yy-52)];loc=(50,y-40)
 elif a in ['42','43','46'] and b=='38p':
  lane={'42':1120,'43':850,'46':80}[a]
  start=(x-370,y) if a!='46' else (x,y+52)
  points=[start,(lane,start[1]),(lane,1510),(1530,1510)]
  loc=({'42':850,'43':60,'46':30}[a],{'42':2600,'43':3070,'46':2380}[a])
 elif a in ['50','53'] and b in ['53','56']:
  lane=4850 if a=='50' else 5100
  points=[(x+370,y),(lane,y),(lane,yy),(xx+370,yy)]
  loc=(4250, y+95)
 else:
  points=[(x,y+52),(xx,yy-52)];loc=(x+34,(y+yy)//2-15)
 line(points)
 if a in ['42','43','46'] and b=='38p':
  box=d.textbbox((0,0),label,font=small)
  patch=Image.new('RGB',(box[2]+14,36),'white')
  ImageDraw.Draw(patch).text((7,4),label,font=small,fill='#0f172a')
  patch=patch.rotate(90,expand=True)
  im.paste(patch,(lane-42,1630))
 else:
  text(*loc,label)

for n,(x,y) in pos.items():
 fill='#edf4fb' if n in conditional else '#f3f4f6'
 d.rounded_rectangle((x-370,y-52,x+370,y+52),radius=15,fill=fill,outline='#64748b',width=3)
 bb=d.textbbox((0,0),labels[n],font=f);d.text((x-(bb[2]-bb[0])/2,y-18),labels[n],font=f,fill='#111827')
# Explicit exits. Edge annotations are real tests as for all other edges.
line([(3800,552),(4500,552),(4500,3240),(3800,3240)])
text(4510,700,'bonus_nullAttendance_throws')
line([(3800,3002),(3800,3188)])
text(3834,3090,'bonus_allAbsent_returnsZero')
d.rounded_rectangle((3430,3188,4170,3292),radius=15,fill='#edf4fb',outline='#64748b',width=3)
d.text((3700,3215),'EXIT',font=f,fill='black')
d.text((80,35),'Lab 10 bonus control flow graph',font=title,fill='#111827')
d.text((80,3370),'Node numbers = unchanged DataFlowTargets.java lines. 32a/32b show short circuit order.',font=f,fill='black')
d.text((80,3420),'38p = array loop condition; 38a = element load and a definition. Every edge names an actual JUnit test.',font=f,fill='black')
im.save(ROOT/'cfg-bonus.png')
print(ROOT/'cfg-bonus.png')
