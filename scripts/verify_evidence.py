#!/usr/bin/env python3
"""Cross-check submitted logs, CSVs, JUnit names, model and original source."""
from pathlib import Path
import csv,re,subprocess
from analyze_du import G,B,GTESTS,BTESTS,analyze,gcd_trace,bonus_trace
ROOT=Path(__file__).resolve().parents[1]

def totals(name,expected,success):
    text=(ROOT/'results'/name).read_text(encoding='utf-8')
    rows=re.findall(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)',text)
    assert rows,name
    assert tuple(map(int,rows[-1]))==expected,(name,rows[-1])
    assert ('BUILD SUCCESS' if success else 'BUILD FAILURE') in text,name

def coverage(name,expected):
    with (ROOT/'results'/name).open() as f:rows=list(csv.DictReader(f))
    assert len(rows)==1 and rows[0]['CLASS']=='DataFlowTargets'
    keys=['BRANCH_MISSED','BRANCH_COVERED','LINE_MISSED','LINE_COVERED']
    assert tuple(int(rows[0][k]) for k in keys)==expected,(name,rows)

for name,total,fail in [('mvn-verify-alldefs.txt',5,0),('mvn-verify-final.txt',13,0),
                       ('mvn-test-M1.txt',13,3),('mvn-test-M2.txt',13,1),
                       ('mvn-test-M3.txt',13,0),('mvn-verify-branch100-not-du.txt',8,0)]:
    totals(name,(total,fail,0,0),fail==0)
coverage('jacoco-alldefs.csv',(3,13,2,22))
coverage('jacoco-final.csv',(0,16,1,23))
coverage('jacoco-branch100-not-du.csv',(0,16,1,23))
source=ROOT/'src/main/java/mn/edu/must/sqat/DataFlowTargets.java'
original=subprocess.check_output(['git','show','1c1119e:starter/lab10-dataflow/src/main/java/mn/edu/must/sqat/DataFlowTargets.java'],cwd=ROOT)
assert source.read_bytes()==original,'Production source differs from starter'
readme=(ROOT/'README.md').read_text()
for graph,tests,fn,file,count in [(G,GTESTS,gcd_trace,'GcdTest.java',11),(B,BTESTS,bonus_trace,'BonusTest.java',24)]:
    expected,hits,edges=analyze(graph,tests,fn)
    assert len(expected)==count
    text=(ROOT/'src/test/java/mn/edu/must/sqat'/file).read_text()
    assert text.count('@Test')==len(tests)
    for tid,name,args in tests:
        assert f'void {name}()' in text,name
        assert name in readme,name
    assert set(edges.values()) <= {name for _,name,_ in tests}
# p-use edges: verify both outcomes for each reaching definition, excluding proven infeasible edges.
for graph,tests,fn,impossible in [
    (G,GTESTS,gcd_trace,set()),
    (B,BTESTS,bonus_trace,{('best','37','42','38p'),('best','37','53','54')})]:
    seen=set()
    for _,_,args in tests:
        trace=fn(*args);last={}
        for i,u in enumerate(trace):
            ds,cs,ps,succ=graph[u]
            for v in ps:
                if v in last: seen.add((v,last[v],u,trace[i+1]))
            for v in ds:last[v]=u
    expected={ (v,d,u,dest) for v,d,u,k in analyze(graph,tests,fn)[0]
              if k=='p' for dest in graph[u][3] }
    assert not (seen & impossible)
    assert expected-impossible==seen,('Uncovered feasible p-use edges',expected-impossible-seen)
assert 'best = present' not in source.read_text()
assert "local variable 'total' is never read" in (ROOT/'results/static-M3.txt').read_text()
for mid,fragments in {
    'M1':['bonus_belowThresholdLongStreak_returnsThree:12 expected: <3> but was: <0>',
          'bonus_atThresholdInterruptedLongStreak_returnsEight:18 expected: <8> but was: <5>',
          'bonus_sixConsecutive_returnsEight:66 expected: <8> but was: <5>'],
    'M2':['bonus_splitFivePresent_returnsFive:48 expected: <5> but was: <8>']}.items():
    log=(ROOT/f'results/mvn-test-{mid}.txt').read_text()
    for fragment in fragments:assert fragment in log and fragment in readme
assert (ROOT/'cfg-bonus.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
print('PASS: logs, CSV totals, 35 DU pairs, feasible p-use outcomes, 13 tests, mutation quotes and unchanged starter.')
