#!/usr/bin/env python3
"""Reproducible source-line CFG model; not a JaCoCo DU measurement.
Uses-before-def ordering handles x=x+1. Walks stop at the next def (kill).
Concrete traces below model exactly the JUnit inputs and short circuit order.
"""
from collections import deque
from pathlib import Path
import json

# node: (definitions, computation uses, predicate uses, successors)
def node(d='', c='', p='', succ=()):
    return (d.split(), c.split(), p.split(), list(succ))
G = {
 '13':node('x y',succ=['15']), '15':node(p='y',succ=['16','20']),
 '16':node('tmp','x y',succ=['17']), '17':node('x','y',succ=['18']),
 '18':node('y','tmp',succ=['15']), '20':node(c='x')}
B = {
 '31':node('attendance threshold',succ=['32a']),
 '32a':node(p='attendance',succ=['33','32b']),
 '32b':node(p='threshold',succ=['33','35']), '33':node(),
 '35':node('present',succ=['36']), '36':node('streak',succ=['37']),
 '37':node('best',succ=['38p']),
 '38p':node(p='attendance',succ=['38a','49']),
 '38a':node('a','attendance',succ=['39']),
 '39':node(p='a',succ=['40','46']),
 '40':node('present','present',succ=['41']),
 '41':node('streak','streak',succ=['42']),
 '42':node(p='streak best',succ=['43','38p']),
 '43':node('best','streak',succ=['38p']), '46':node('streak',succ=['38p']),
 '49':node('score',succ=['50']), '50':node(p='present threshold',succ=['51','53']),
 '51':node('score',succ=['53']), '53':node(p='best',succ=['54','56']),
 '54':node('score','score',succ=['56']), '56':node(c='score')}

def pairs(graph):
    out={}
    for d, (defs,_,_,succ) in graph.items():
        for v in defs:
            q=deque((s,[d,s]) for s in succ); seen=set()
            while q:
                u,path=q.popleft()
                if u in seen: continue
                seen.add(u)
                ds,cs,ps,ss=graph[u]
                if v in cs: out[v,d,u,'c']=path
                if v in ps: out[v,d,u,'p']=path
                if v not in ds: q.extend((s,path+[s]) for s in ss)
    return out

def gcd_trace(x,y):
    out=['13','15']
    while y!=0:
        out+=['16','17','18','15'];x,y=y,x%y
    return out+['20']

def bonus_trace(a,threshold):
    out=['31','32a']
    if a is None:return out+['33']
    out+=['32b']
    if threshold<0:return out+['33']
    out+=['35','36','37','38p'];present=streak=best=0
    for value in a:
        out+=['38a','39']
        if value>0:
            present+=1;streak+=1;out+=['40','41','42']
            if streak>best:best=streak;out+=['43']
        else:streak=0;out+=['46']
        out+=['38p']
    out+=['49','50']
    if present>=threshold:out+=['51']
    out+=['53']
    if best>=5:out+=['54']
    return out+['56']

GTESTS=[('G1','gcd_twoIterations_returnsFour',(12,8)),
        ('G2','gcd_zeroDivisor_returnsSeven',(7,0)),
        ('G3','gcd_zeroDividend_returnsFive',(0,5))]
BTESTS=[
 ('B1','bonus_belowThresholdLongStreak_returnsThree',([1]*5,6)),
 ('B2','bonus_atThresholdInterruptedLongStreak_returnsEight',([1]*5+[0,1],6)),
 ('B3','bonus_emptyZeroThreshold_returnsFive',([],0)),
 ('B4','bonus_emptyPositiveThreshold_returnsZero',([],1)),
 ('B5','bonus_allAbsent_returnsZero',([0,-1,0],1)),
 ('B6','bonus_initialAbsenceThenPresent_returnsFive',([0,1],1)),
 ('B7','bonus_splitFivePresent_returnsFive',([1,1,0,1,1,1],5)),
 ('B8','bonus_nullAttendance_throws',(None,0)),
 ('B9','bonus_negativeThreshold_throws',([],-1)),
 ('B10','bonus_sixConsecutive_returnsEight',([1]*6,6))]

def observed(graph,trace):
    last={};out={}
    for i,u in enumerate(trace):
        ds,cs,ps,_=graph[u]
        for kind,vs in [('c',cs),('p',ps)]:
            for v in vs:
                if v in last:
                    j=last[v];out.setdefault((v,trace[j],u,kind),trace[j:i+1])
        for v in ds:last[v]=i
    return out

def analyze(graph,tests,tracefn):
    expected=pairs(graph);evidence={};edges={}
    for tid,name,args in tests:
        trace=tracefn(*args)
        for a,b in zip(trace,trace[1:]):
            assert b in graph[a][3],(a,b)
            edges.setdefault((a,b),name)
        for pair,path in observed(graph,trace).items():
            assert pair in expected,pair
            evidence.setdefault(pair,[]).append((tid,path))
    assert set(expected)==set(evidence),('Uncovered DU',set(expected)-set(evidence))
    assert set(edges)=={(n,s) for n,v in graph.items() for s in v[3]},'Uncovered CFG edge'
    return expected,evidence,edges

def table(graph,tests,tracefn):
    expected,evidence,_=analyze(graph,tests,tracefn)
    lines=['| Хувьсагч | Def мөр | Use мөр | Төрөл | Def-clear зам | Тестийн ID | Хамрагдсан |',
           '|---|---|---|---|---|---|---|']
    for pair in sorted(expected,key=lambda p:(p[0],int(p[1].rstrip('apb')),p[1],p[2],p[3])):
        v,d,u,kind=pair;hits=evidence[pair];path=min((path for _,path in hits),key=len)
        lines.append(f'| {v} | {d} | {u} | {kind}-use | '+ ' → '.join(path)+' | '+', '.join(t for t,_ in hits)+' | Тийм |')
    return '\n'.join(lines)

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    for title,graph,tests,fn in [('gcd',G,GTESTS,gcd_trace),('bonus',B,BTESTS,bonus_trace)]:
        expected,ev,edges=analyze(graph,tests,fn)
        print(f'{title}: {len(expected)}/{len(expected)} DU pairs; {len(edges)} CFG edges covered')
    # all-defs: every definition with a reachable use has at least one witnessed use.
    ev={p for t in BTESTS[:2] for p in observed(B,bonus_trace(*t[2]))}
    defs={(v,n) for n,(ds,_,_,_) in B.items() for v in ds}
    assert defs=={(v,d) for v,d,u,k in ev}
    print(f'bonus all-defs: {len(defs)}/{len(defs)} definitions with two tests')
    print('Trace model only: JUnit/Maven logs and JaCoCo CSV are separate execution evidence.')
