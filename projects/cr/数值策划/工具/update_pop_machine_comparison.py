"""POP-only extension of a user workbook; controlled inputs stay outside Git.

prepare --input <user.xlsx> --package <PS_LEVEL_BET_HANDOFF> --out <controlled dir>
finish --out <dir>  (after update_pop_machine_comparison.mjs)
Uses openpyxl for readback only; Artifact authors cells, OOXML preserves user parts.
"""
from __future__ import annotations
import argparse
import copy
import json
import math
import re
import shutil
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import openpyxl
from openpyxl.utils import get_column_letter as col, column_index_from_string as ci
from lxml import etree as E

NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
N={'s':NS}; T=lambda x:'{'+NS+'}'+x
CN='http://schemas.openxmlformats.org/drawingml/2006/chart'
C={'c':CN}; CT=lambda x:'{'+CN+'}'+x
BOOK='CR_CF_POP_等级段横向对比_三档Bet_v4_POP普通特殊.xlsx'
POP_COLS=[5,8,11,14,17,20,23,26,29,32,36]
MAP={c:c+sum(p<c for p in POP_COLS) for c in range(1,37)}

def dump(path: Path, data: object) -> None:
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def prepare(inp: Path, package: Path, out: Path, anchor: Path | None = None) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    backup=out/'user-input.xlsx'
    if backup.exists(): raise ValueError('Use a fresh output directory; do not overwrite user backup')
    shutil.copy2(inp,backup)
    w=openpyxl.load_workbook(backup,data_only=True)
    d=json.loads((package/'PS_LEVEL_BET.json').read_text(encoding='utf-8-sig'))
    s25,s91=d['samples']; assert (s25['level'],s91['level'])==(25,91)
    machines={p.stem:json.loads(p.read_text(encoding='utf-8-sig')) for p in (package/'dataset').glob('machine_*.json')}
    line_groups=sorted({m['lines'] for m in machines.values()}); assert line_groups==[20,40]
    assert all(m['spinFee']==0 and m['betSequence']==s91['ladder'] for m in machines.values())
    assert all(m['defaultBet']*m['lines']==s91['default_total'] for m in machines.values())
    caps={x['level']:x['nextLevelMaxBet'] for x in d['level_cap_breakpoints_measured']}
    # Only missing-window assumptions, not newly asserted observations.
    controls={'normal_lines':20,'special_lines':40,'spin_fee':0,'min_mid_fit':d['mother_ladder_per_line'][1],
              'min_late_fit':s91['min_per_line'],'mid_fit_level':50,'late_fit_level':75,
              'high_round_per_line':d['mother_ladder_per_line'][18]}
    source={
      'V1':20,'V2':40,'V3':0,
      'Y6':25,'Z6':s25['min_per_line'],'Y7':91,'Z7':s91['min_per_line'],
      'Y8':25,'Z8':s25['max_per_line'],'Y9':50,'Z9':caps[50],'Y10':91,'Z10':s91['max_per_line'],
      'Y11':50,'Z11':controls['min_mid_fit'],'Y12':75,'Z12':controls['min_late_fit'],
      'Z13':controls['high_round_per_line'],'Y14':25,'Z14':s25['default_per_line'],
      'Y15':91,'Z15':s91['default_per_line'],'Y16':91,'Z16':s91['default_total']/40,
    }
    for i,b in enumerate(d['mother_ladder_per_line'],6): source[f'U{i}']=i-6;source[f'V{i}']=b
    observation=json.loads(anchor.read_text(encoding='utf-8')) if anchor else None
    if observation:
        assert w['等级段对比'].max_column==47, 'Anchor update expects the v4 layout'
        assert observation['lines']==controls['special_lines']
        source.update(Y17=observation['level'],Z17=observation['minimum']/observation['lines'],
                      Y18=observation['level'],Z18=observation['maximum']/observation['lines'])
        assert source['Z17'] in d['mother_ladder_per_line'] and source['Z18'] in d['mother_ladder_per_line']
    rows=[]
    for level in range(1,1501):
        r=level+5; rate=w['POP明细'].cell(r,14).value;xp=w['POP明细'].cell(r,15).value
        lo=s25['min_per_line'] if level<50 else controls['min_mid_fit'] if level<75 else s91['min_per_line']
        raw=caps[50]+(s91['max_per_line']-caps[50])*(level-50)/(91-50)
        hi=(w['SRC_等级'].cell(r,11).value if level<=50 else
            max(b for b in d['mother_ladder_per_line'] if b<=raw) if level<=91 else
            math.floor(raw/controls['high_round_per_line']+.5)*controls['high_round_per_line'])
        if observation:
            if level>=observation['level']:lo=source['Z17']
            if level>91:
                raw=source['Z10']+(source['Z18']-source['Z10'])*min(level-91,observation['level']-91)/(observation['level']-91)
                hi=max(b for b in d['mother_ladder_per_line'] if b<=raw)
        low=[lo*x for x in line_groups];high=[hi*x for x in line_groups]
        rec=[max(low[i],min(high[i],rate*w['结论与参数']['B11'].value/w['结论与参数']['B12'].value)) for i in range(2)]
        if observation:
            rec=[min([b*lines for b in d['mother_ladder_per_line'] if lo<=b<=hi],key=lambda b:(abs(b-rec[j]),b)) for j,lines in enumerate(line_groups)]
        bets=low+rec+high
        rows.append({'level':level,'bets':bets,'usd':[b/rate for b in bets],
                     'spins':[xp/(b*w['结论与参数']['B28'].value) for b in bets],
                     'cost':xp/(rate*w['结论与参数']['B28'].value),'lo':lo,'hi':hi})
    seeds={'结论与参数':{f'B{i}':w['结论与参数'].cell(i,2).value for i in [11,12,28]},
           'SRC_等级':{f'K{r}':w['SRC_等级'].cell(r,11).value for r in range(6,1506)},
           'POP明细':{f'{c}{r}':w['POP明细'][f'{c}{r}'].value for c in ['A','N','O'] for r in range(6,1506)},
           '等级段对比':{f'{col(c.column if observation else MAP[c.column])}{c.row}':c.value for row in w['等级段对比'] for c in row if c.value is not None}}
    heads=[w['等级段对比'].cell(5,MAP[c] if observation else c).value.split('\n')[0] for c in range(1,37)]
    dump(out/'input.controlled.json',{'source':source,'seeds':seeds,'heads':heads,'controls':controls,
          'same_layout':bool(observation),'anchor':observation,'nearest_rung':bool(observation),
          'generated':d['meta']['generated'],'machines':{k:{f:v[f] for f in ['lines','spinFee','defaultBet']} for k,v in machines.items()}})
    dump(out/'expected.controlled.json',rows)
    dump(out/'input-receipt.json',{'path':str(inp),'mtime_ns':inp.stat().st_mtime_ns,'size':inp.stat().st_size})
    w.close();return {'prepared':True,'source_copy':True,'machine_groups':line_groups,'levels':1500}

def prepare_candidates(out: Path) -> dict:
    """Authorized two-column candidates; keep the user's old model as history."""
    w=openpyxl.load_workbook(out/'user-input.xlsx',data_only=True)
    d=json.loads((out/'input.controlled.json').read_text(encoding='utf-8'))
    d['seeds']['结论与参数']['B26']=w['结论与参数']['B26'].value
    pop=json.loads((out/'expected.controlled.json').read_text(encoding='utf-8'))
    areas={'SRC_等级':['A6:Q1505'],'SRC_档位':['A6:D798'],'CR明细':['A1:S1505'],'CR调整候选':['A1:AM1505']}
    d['candidate_seeds']={n:[[a,[[c.value for c in row] for row in w[n][a]]] for a in ar] for n,ar in areas.items()}
    pools=list(w['SRC_档位'].iter_rows(min_row=6,max_row=798,max_col=4,values_only=True))
    d['candidate_pool_ranges']=[[min(k+6 for k,x in enumerate(pools) if x[0]==w['CR调整候选'].cell(r,13).value),
                                max(k+6 for k,x in enumerate(pools) if x[0]==w['CR调整候选'].cell(r,13).value)] for r in range(6,1506)]
    pool=sorted({x[2] for x in pools});rounding=w['CR调整候选']['T1'].value
    ceil=lambda x:next((b for b in pool if b>=x),math.ceil(x/rounding)*rounding)
    balance=w['结论与参数']['B11'].value;ratio=w['结论与参数']['B26'].value
    previous_min=[0,0];previous_max=[0,0];expected=[]
    for i,p in enumerate(pop):
        r=i+6;c=w['CR调整候选'];rate=c.cell(r,3).value;local=sorted({x[2] for x in pools if x[0]==c.cell(r,13).value})
        pair=[]
        for j in [0,1]:
            target=p['usd'][j]*rate;take=next((b for b in local if b>=target),max(local))
            minimum=c.cell(r,17).value if i<4 else min(c.cell(r,25).value,max(previous_min[j],take))
            maximum=c.cell(r,25).value if i<4 else max(c.cell(r,25).value,previous_max[j],ceil(p['usd'][4+j]*rate))
            recommended=c.cell(r,18).value if i<4 else max(minimum,min(maximum,ceil(rate*balance/30)))
            if d.get('nearest_rung'):
                allowed=sorted({b for b in pool if minimum<=b<=maximum}|{minimum,maximum})
                target_rec=c.cell(r,18).value if i<4 else rate*balance/30
                recommended=min(allowed,key=lambda b:(abs(b-target_rec),b))
            previous_min[j]=minimum;previous_max[j]=maximum
            need=w['SRC_等级'].cell(r,3).value;kind=w['SRC_等级'].cell(r,2).value
            spins=[need if kind==1 else need/(b*ratio) for b in [minimum,recommended,maximum]]
            cost=[sp*b/rate for sp,b in zip(spins,[minimum,recommended,maximum])]
            pair.append({'minimum':minimum,'recommended':recommended,'maximum':maximum,'spins':spins,'cost':cost})
        expected.append(pair)
    d['dual_candidates']=True
    dump(out/'input.controlled.json',d);dump(out/'candidate-expected.controlled.json',expected)
    w.close();return {'dual_candidates_prepared':True,'levels':len(expected)}


def sheet_part(parts: dict, name: str) -> str:
    w=E.fromstring(parts['xl/workbook.xml']);rs=E.fromstring(parts['xl/_rels/workbook.xml.rels'])
    s=next(s for s in w.find(T('sheets')) if s.get('name')==name)
    rid=s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    path=next(x.get('Target') for x in rs if x.get('Id')==rid)
    return path.lstrip('/') if path.startswith('/') else 'xl/'+path

def remap_local_formula(formula: str) -> str:
    # User formulas on the moved overview use either local A1 refs or explicit sheet refs.
    from openpyxl.formula.tokenizer import Tokenizer
    tokens=Tokenizer('='+formula).items
    for tok in tokens:
        if tok.type=='OPERAND' and tok.subtype=='RANGE' and '!' not in tok.value:
            tok.value=re.sub(r'(\$?)([A-Z]{1,3})(\$?\d+)',lambda m:m[1]+col(MAP.get(ci(m[2]),ci(m[2])))+m[3],tok.value)
    return ''.join(t.value for t in tokens)

def merge_styles(base: dict, art: dict, cells: list) -> tuple[bytes,dict]:
    old=E.fromstring(base['xl/styles.xml']);new=E.fromstring(art['xl/styles.xml'])
    nums=old.find(T('numFmts'))
    if nums is None:nums=E.Element(T('numFmts'));old.insert(0,nums)
    nextid=max([163]+[int(n.get('numFmtId')) for n in nums])+1;nm={}
    for n in new.findall('s:numFmts/s:numFmt',N):
        x=copy.deepcopy(n);nm[int(n.get('numFmtId'))]=nextid;x.set('numFmtId',str(nextid));nextid+=1;nums.append(x)
    nums.set('count',str(len(nums)));offset={}
    for k in ['fonts','fills','borders','cellStyleXfs']:
        target=old.find(T(k));offset[k]=len(target)
        for n in new.find(T(k)):
            x=copy.deepcopy(n)
            if k=='cellStyleXfs':
                for a,b in [('fontId','fonts'),('fillId','fills'),('borderId','borders')]:x.set(a,str(int(x.get(a,'0'))+offset[b]))
                if int(x.get('numFmtId','0')) in nm:x.set('numFmtId',str(nm[int(x.get('numFmtId'))]))
            target.append(x)
        target.set('count',str(len(target)))
    target=old.find(T('cellXfs'));mp={}
    for i in sorted({int(c.get('s','0')) for c in cells}):
        x=copy.deepcopy(new.find(T('cellXfs'))[i]);mp[i]=len(target)
        for a,b in [('fontId','fonts'),('fillId','fills'),('borderId','borders'),('xfId','cellStyleXfs')]:x.set(a,str(int(x.get(a,'0'))+offset[b]))
        if int(x.get('numFmtId','0')) in nm:x.set('numFmtId',str(nm[int(x.get('numFmtId'))]))
        target.append(x)
    target.set('count',str(len(target)));return E.tostring(old),mp

def finish(out: Path) -> dict:
    global BOOK
    with ZipFile(out/'user-input.xlsx') as z:base={n:z.read(n) for n in z.namelist()}
    with ZipFile(out/'delta.xlsx') as z:art={n:z.read(n) for n in z.namelist()}
    changed=json.loads((out/'changed-cells.json').read_text(encoding='utf-8'))
    inputs=json.loads((out/'input.controlled.json').read_text(encoding='utf-8'))
    same=inputs.get('same_layout',False)
    if same:BOOK=BOOK.replace('v4_POP普通特殊','v5_POP百级修订')
    changes={};pairs={};allcells=[]
    for name,refs in changed.items():
        src=E.fromstring(base[sheet_part(base,name)]);ext=E.fromstring(art[sheet_part(art,name)])
        cells={c.get('r'):c for c in ext.findall('.//s:sheetData/s:row/s:c',N)}
        pairs[name]=(src,{ref:cells[ref] for ref in refs});allcells.extend(pairs[name][1].values())
    st,sm=merge_styles(base,art,allcells);changes['xl/styles.xml']=st
    strings=list(E.fromstring(art['xl/sharedStrings.xml'])) if 'xl/sharedStrings.xml' in art else []
    for name,(src,cells) in pairs.items():
        data=src.find(T('sheetData'));rows={int(r.get('r')):r for r in data}
        if name=='等级段对比' and not same:
            for row in data:
                for c in row:
                    letter,num=openpyxl.utils.cell.coordinate_from_string(c.get('r'))
                    c.set('r',col(MAP[ci(letter)])+str(num))
                    f=c.find(T('f'))
                    if f is not None:
                        if f.text:f.text=remap_local_formula(f.text)
                        if f.get('ref'):f.set('ref',remap_local_formula(f.get('ref')))
            oldcols=src.find(T('cols'));expanded=[]
            for x in oldcols:
                for i in range(int(x.get('min')),int(x.get('max'))+1):
                    if i>36:continue
                    cp=copy.deepcopy(x);cp.set('min',str(MAP[i]));cp.set('max',str(MAP[i]));expanded.append(cp)
                    if i in POP_COLS:
                        cp=copy.deepcopy(cp);cp.set('min',str(MAP[i]+1));cp.set('max',str(MAP[i]+1));expanded.append(cp)
            oldcols[:]=expanded;src.find(T('dimension')).set('ref','A1:AU111')
        for ref,c in cells.items():
            cp=copy.deepcopy(c);cp.set('s',str(sm[int(c.get('s','0'))]))
            if cp.get('t')=='s':
                val=cp.find(T('v'));idx=int(val.text);cp.remove(val);cp.set('t','inlineStr');ins=E.SubElement(cp,T('is'))
                for node in strings[idx]:ins.append(copy.deepcopy(node))
            rn=openpyxl.utils.cell.coordinate_from_string(ref)[1]
            if rn not in rows:rows[rn]=E.SubElement(data,T('row'),r=str(rn))
            old=next((x for x in rows[rn] if x.get('r')==ref),None)
            if (name=='结论与参数' or ref in ['A2','A3']) and old is not None and old.get('s'):
                cp.set('s',old.get('s'))
            if old is not None:rows[rn].remove(old)
            rows[rn].append(cp)
        for row in data:row[:]=sorted(row,key=lambda x:ci(openpyxl.utils.cell.coordinate_from_string(x.get('r'))[0]))
        data[:]=sorted(data,key=lambda r:int(r.get('r')))
        if name=='POP明细':
            cols=src.find(T('cols'));cols[:]=[E.Element(T('col'),min='1',max='1',width='12',customWidth='1'),
              E.Element(T('col'),min='2',max='19',hidden='1',width='18',customWidth='1'),
              E.Element(T('col'),min='20',max='45',width='21',customWidth='1'),
              E.Element(T('col'),min='46',max='46',width='54',customWidth='1'),
              E.Element(T('col'),min='47',max='48',width='24',customWidth='1'),
              E.Element(T('col'),min='54',max='63',hidden='1',width='16',customWidth='1')]
            src.find(T('dimension')).set('ref','A1:BK1505')
            rows[5].set('ht','58');rows[5].set('customHeight','1')
            # Filtering is owned by the existing structured table, extended below.
        if name=='SRC_POP':
            src.find(T('dimension')).set('ref','A1:AA100')
            cols=src.find(T('cols'))
            if not same:
                for a,b,width in [(21,23,20),(24,26,25),(27,27,65)]:E.SubElement(cols,T('col'),min=str(a),max=str(b),width=str(width),customWidth='1')
        if name=='结论与参数':
            merges=src.find(T('mergeCells'))
            for rn in [43,44,45]:
                ref=f'A{rn}:L{rn}'
                if not any(m.get('ref')==ref for m in merges):E.SubElement(merges,T('mergeCell'),ref=ref)
                rows[rn].set('ht','34');rows[rn].set('customHeight','1')
            merges.set('count',str(len(merges)))
        if name=='CR调整候选':
            cols=src.find(T('cols'));cols[:]=[
                E.Element(T('col'),min='1',max='1',width='12',customWidth='1'),
                E.Element(T('col'),min='2',max='39',width='18',hidden='1',customWidth='1'),
                E.Element(T('col'),min='40',max='69',width='23',customWidth='1'),
                E.Element(T('col'),min='70',max='71',width='50',customWidth='1'),
                E.Element(T('col'),min='72',max='78',width='16',hidden='1',customWidth='1')]
            src.find(T('dimension')).set('ref','A1:BZ1505');rows[5].set('ht','66');rows[5].set('customHeight','1')
            for rn in [2,3]:
                merges=src.find(T('mergeCells'));ref=f'AN{rn}:AW{rn}'
                if not any(m.get('ref')==ref for m in merges):E.SubElement(merges,T('mergeCell'),ref=ref)
                merges.set('count',str(len(merges)))
        if name=='等级段对比':
            merges=src.find(T('mergeCells'))
            if merges is None:
                merges=E.Element(T('mergeCells'));src.insert(list(src).index(data)+1,merges)
            for ref in ['A107:N107','J109:N109','J110:N110']:
                if not any(m.get('ref')==ref for m in merges):E.SubElement(merges,T('mergeCell'),ref=ref)
            merges.set('count',str(len(merges)));rows[108].set('ht','55');rows[108].set('customHeight','1')
        changes[sheet_part(base,name)]=E.tostring(src,xml_declaration=True,encoding='UTF-8',standalone=True)
    # Extend the existing overview's structured table without rebuilding user columns.
    av=openpyxl.load_workbook(out/'delta.xlsx',data_only=True)
    for name,payload in base.items():
        if same:continue
        if name.startswith('xl/tables/') and name.endswith('.xml'):
            t=E.fromstring(payload)
            if t.get('name')=='Candidate' and inputs.get('dual_candidates'):
                t.set('ref','A5:BS1505');af=t.find(T('autoFilter'))
                if af is not None:af.set('ref','A5:BS1505')
                tc=t.find(T('tableColumns'))
                for c in range(40,72):E.SubElement(tc,T('tableColumn'),id=str(c),name=av['CR调整候选'].cell(5,c).value)
                tc.set('count',str(len(tc)));changes[name]=E.tostring(t);continue
            if t.get('name')=='Model2':
                t.set('ref','A5:AV1505');af=t.find(T('autoFilter'))
                if af is None:af=E.Element(T('autoFilter'));t.insert(0,af)
                af.set('ref','A5:AV1505');tc=t.find(T('tableColumns'))
                for c in range(20,49):E.SubElement(tc,T('tableColumn'),id=str(c),name=av['POP明细'].cell(5,c).value)
                tc.set('count',str(len(tc)));changes[name]=E.tostring(t);continue
            if t.get('name')!='StageComparison':continue
            t.set('ref','A5:AU104');af=t.find(T('autoFilter'))
            if af is not None:af.set('ref','A5:AU104')
            tc=t.find(T('tableColumns'));original=list(tc);tc[:]=[]
            for i,x in enumerate(original,1):
                cp=copy.deepcopy(x);cp.set('id',str(MAP[i]))
                if i in POP_COLS:cp.set('name',cp.get('name')+'\n普通20线')
                tc.append(cp)
                if i in POP_COLS:
                    sp=copy.deepcopy(cp);sp.set('id',str(MAP[i]+1));sp.set('name',x.get('name')+'\n特殊40线');tc.append(sp)
            tc.set('count',str(len(tc)));changes[name]=E.tostring(t)
    # Preserve CR/CF chart series byte-for-byte; replace POP and add its 40-line series.
    for no,(normal,special) in enumerate([('Z','AA'),('AB','AC'),('AD','AE'),('AL','AM')],1):
        name=f'xl/charts/chart{no}.xml';x=E.fromstring(base[name]);series=x.findall('.//c:lineChart/c:ser',C)
        old=series[2];parent=old.getparent();position=list(parent).index(old)
        for previous in series[2:]:parent.remove(previous)
        for j,letter in enumerate([normal,special]):
            cp=copy.deepcopy(old);cp.find(CT('idx')).set('val',str(2+j));cp.find(CT('order')).set('val',str(2+j))
            tx=cp.find(CT('tx'));tx.clear();E.SubElement(tx,CT('v')).text='POP普通20线' if j==0 else 'POP特殊40线'
            val=cp.find('c:val/c:numRef',C);val.find(CT('f')).text=f"'POP明细'!${letter}$6:${letter}$1505"
            cache=val.find(CT('numCache'));cache.clear();E.SubElement(cache,CT('formatCode')).text='0.000';E.SubElement(cache,CT('ptCount'),val='1500')
            for k,r in enumerate(range(6,1506)):
                pt=E.SubElement(cache,CT('pt'),idx=str(k));E.SubElement(pt,CT('v')).text=str(av['POP明细'][f'{letter}{r}'].value)
            for color in cp.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr'):
                color.set('val','207760' if j==0 else '9B5AB5')
            parent.insert(position+j,cp)
        changes[name]=E.tostring(x)
    av.close()
    if 'xl/calcChain.xml' in base:raise ValueError('Unexpected calcChain: preserve/rebuild explicitly before delivery')
    with ZipFile(out/BOOK,'w',ZIP_DEFLATED) as z:
        for name,payload in base.items():z.writestr(name,changes.get(name,payload))
    return verify(out,base,changes)

def verify(out: Path, base: dict, changes: dict) -> dict:
    old=openpyxl.load_workbook(out/'user-input.xlsx',data_only=True)
    oldf=openpyxl.load_workbook(out/'user-input.xlsx',data_only=False)
    wf=openpyxl.load_workbook(out/BOOK);w=openpyxl.load_workbook(out/BOOK,data_only=True)
    expected=json.loads((out/'expected.controlled.json').read_text(encoding='utf-8'))
    inputs=json.loads((out/'input.controlled.json').read_text(encoding='utf-8'));controls=inputs['source']
    same=inputs.get('same_layout',False)
    for r,letter,want in [(30,'AU',controls['Z14']*controls['V1']),(30,'AV','N/A'),
                          (96,'AU',controls['Z15']*controls['V1']),(96,'AV',controls['Z16']*controls['V2'])]:
        assert w['POP明细'][f'{letter}{r}'].value==want
    for x in expected:
        r=x['level']+5
        for c,want in list(zip(range(20,26),x['bets']))+list(zip(range(26,32),x['usd']))+list(zip(range(32,38),x['spins']))+[(c,x['cost']) for c in range(38,44)]:
            got=w['POP明细'].cell(r,c).value
            assert isinstance(got,(int,float)) and math.isclose(got,want,rel_tol=1e-9,abs_tol=1e-6),(r,c,got,want)
        assert w['POP明细'].cell(r,21).value==2*w['POP明细'].cell(r,20).value
        assert w['POP明细'].cell(r,25).value==2*w['POP明细'].cell(r,24).value
    preserved=0
    for row in old['等级段对比']:
        for c in row:
            excluded=({MAP[n]+j for n in POP_COLS for j in [0,1]}|{MAP[33]}) if same else set(POP_COLS+[33])
            if c.row<5 or c.row>104 or c.column in excluded:continue
            before=oldf['等级段对比'][c.coordinate]
            dest=c.column if same else MAP[c.column]
            assert w['等级段对比'].cell(c.row,dest).value==c.value,(c.coordinate,'user value changed')
            if before.data_type=='f':
                assert wf['等级段对比'].cell(c.row,dest).value==(before.value if same else '='+remap_local_formula(before.value[1:])),(c.coordinate,'user formula changed')
            preserved+=1
    errors=[(s.title,c.coordinate) for s in w for row in s for c in row if c.data_type=='e'];assert not errors,errors[:10]
    with ZipFile(out/BOOK) as z:
        unchanged=[n for n in base if n not in changes];assert all(z.read(n)==base[n] for n in unchanged)
        for sn in ['CR明细','CF明细','VIP对比','SRC_等级','SRC_档位','SRC_VIP']:
            p=sheet_part(base,sn);assert z.read(p)==base[p]
        for no in range(1,5):
            p=f'xl/charts/chart{no}.xml'
            before=E.fromstring(base[p]).findall('.//c:ser',C);after=E.fromstring(z.read(p)).findall('.//c:ser',C)
            assert len(after)==4
            assert all(E.tostring(before[i])==E.tostring(after[i]) for i in [0,1])
            for ser,letter in zip(after[2:],[('Z','AA'),('AB','AC'),('AD','AE'),('AL','AM')][no-1]):
                pts=ser.findall('c:val/c:numRef/c:numCache/c:pt/c:v',C);assert len(pts)==1500
                assert all(math.isclose(float(pt.text),w['POP明细'][f'{letter}{i+6}'].value,rel_tol=1e-9) for i,pt in enumerate(pts))
    for row in w['等级段对比'].iter_rows(min_row=6,max_row=104):
        r=row[0].value+5
        for oldcol,modelcol in zip(POP_COLS,['T','V','X','Z','AB','AD','AL','AN','AP','AR',None]):
            for j in (0,1):
                got=row[MAP[oldcol]+j-1].value
                want=(sum(w['POP明细'].cell(k,38+j).value for k in range(row[0].value+5,row[1].value+6)) if modelcol is None else
                      w['POP明细'].cell(r,ci(modelcol)+(j if modelcol!='AR' else 0)).value)
                assert math.isclose(got,want,rel_tol=1e-9,abs_tol=1e-6),(row[0].value,oldcol,j,got,want)
                if oldcol in [14,17,20,23,26,29,36]:
                    assert wf['等级段对比'].cell(row[0].row,MAP[oldcol]+j).number_format=='"$"#,##0.000'
    receipt=json.loads((out/'input-receipt.json').read_text(encoding='utf-8'));inp=Path(receipt['path'])
    assert inp.stat().st_mtime_ns==receipt['mtime_ns'] and inp.stat().st_size==receipt['size'],'User edited input during work'
    assert not wf._external_links
    if inputs.get('dual_candidates'):
        exp=json.loads((out/'candidate-expected.controlled.json').read_text(encoding='utf-8'))
        for i,pair in enumerate(exp):
            for j,x in enumerate(pair):
                for c,key in [(40+j,'minimum'),(42+j,'recommended'),(44+j,'maximum')]:
                    assert math.isclose(w['CR调整候选'].cell(i+6,c).value,x[key],rel_tol=1e-9,abs_tol=1e-6),(i+1,c)
                for k in range(3):
                    assert math.isclose(w['CR调整候选'].cell(i+6,52+2*k+j).value,x['spins'][k],rel_tol=1e-9,abs_tol=1e-6)
                    assert math.isclose(w['CR调整候选'].cell(i+6,58+2*k+j).value,x['cost'][k],rel_tol=1e-9,abs_tol=1e-6)
        for row in oldf['CR调整候选']:
            for c in row:
                if c.coordinate in ['A2','A3'] or (same and c.column>39):continue
                assert wf['CR调整候选'][c.coordinate].value==c.value,(c.coordinate,'User history changed')
                assert w['CR调整候选'][c.coordinate].value==old['CR调整候选'][c.coordinate].value,(c.coordinate,'User history cache changed')
    result={'levels_each_machine_type':1500,'stage_rows_preserved':99,'user_non_POP_stage_cells_preserved':preserved,
       'CR_two_candidate_columns_updated':inputs.get('dual_candidates',False),'CR_CF_source_values_preserved':True,'unrelated_package_parts_identical':len(unchanged),
       'charts_total':7,'charts_with_two_POP_series':4,'CF_chart_series_identical':True,
       'formula_errors':len(errors),'external_links':0,'native_WPS_open':False,'source_untouched':True,
       'assumptions_separate_from_observations':True,'USD_decimals':3,'changed_parts':list(changes)}
    if same:
        ladder=[controls[f'V{r}'] for r in range(6,35)]
        for x in expected:
            for j,lines in enumerate([controls['V1'],controls['V2']]):
                assert x['bets'][2+j]/lines in ladder
                assert x['bets'][j]<=x['bets'][2+j]<=x['bets'][4+j]
        result.update(nearest_POP_rung_verified=True,nearest_CR_candidate_rung_verified=True,
                      new_User_anchor_verified=True,post_anchor_bounds_carried_forward_not_observed=True)
    areas={'等级段对比':['A1:AU111'],'POP明细':['A1:BD1505'],'CR明细':['A6:S1505'],'CF明细':['A6:S1505'],
           'Bet曲线':['AA5:BB3010'],'结论与参数':['A1:L57'],'CR调整候选':['A1:BS1505']}
    dump(out/'render-caches.controlled.json',{n:[[rg,[[c.value for c in row] for row in w[n][rg]]] for rg in ranges] for n,ranges in areas.items()})
    chartdata=[]
    with ZipFile(out/BOOK) as z:
        for no,title in [(1,'最低Bet每转USD'),(3,'最大Bet每转USD')]:
            series=E.fromstring(z.read(f'xl/charts/chart{no}.xml')).findall('.//c:ser',C);labels=[];values=[]
            for ser in series:
                labels.append(''.join(ser.find(CT('tx')).itertext()).split('"')[1] if ser.find('c:tx/c:strRef',C) is not None else ser.find('c:tx/c:v',C).text)
                values.append([float(x.text) for x in ser.findall('c:val/c:numRef/c:numCache/c:pt/c:v',C)])
            chartdata.append({'title':title,'labels':labels,'rows':[[i+1]+[v[i] for v in values] for i in range(1500)]})
    dump(out/'chart-preview.controlled.json',chartdata)
    if same:
        views=[]
        for name,label,columns,rows in [
            ('POP明细','final-pop-bounds',[1]+list(range(20,32)),[5,96,104,105,106,1505]),
            ('CR调整候选','final-candidates',[1]+list(range(40,52)),[5,96,104,105,106,1505]),
            ('等级段对比','final-observations',list(range(1,10)),[108,109,110,111])]:
            values=[]
            for rn in rows:
                line=[]
                for cn in columns:
                    c=wf[name].cell(rn,cn);color=c.fill.fgColor
                    line.append({'value':w[name].cell(rn,cn).value,'format':c.number_format,
                                 'fill':'#'+color.rgb[-6:] if c.fill.patternType=='solid' and color.type=='rgb' else None})
                values.append(line)
            views.append({'source':name,'label':label,'width':23,'cells':values})
        dump(out/'layout-preview.controlled.json',views)
    dump(out/'validation.json',result);old.close();oldf.close();w.close();wf.close();return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','candidates','finish']);p.add_argument('--input',type=Path);p.add_argument('--package',type=Path);p.add_argument('--anchor',type=Path);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(prepare(a.input,a.package,a.out,a.anchor) if a.action=='prepare' else prepare_candidates(a.out) if a.action=='candidates' else finish(a.out),ensure_ascii=False))
