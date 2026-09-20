"""补充Artifact未公开的外链特性；保留XML命名空间，清理生成物本机元数据。

依赖已配置运行时的lxml（保留Excel扩展命名空间）；不修改原始导出文件。
"""
from __future__ import annotations
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote, unquote
import shutil
import subprocess
from copy import deepcopy
from lxml import etree as E

M='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P='http://schemas.openxmlformats.org/package/2006/relationships'
C='http://schemas.openxmlformats.org/package/2006/content-types'
NS={'m':M}


def read_parts(path: Path) -> dict[str,bytes]:
    with zipfile.ZipFile(path) as z:return {n:z.read(n) for n in z.namelist() if not n.endswith('/')}


def write_parts(path: Path, data: dict) -> None:
    temp=path.with_suffix('.building.xlsx')
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
        for n,value in data.items():z.writestr(n,value)
    temp.replace(path)


def xml(root: E._Element) -> bytes:
    return E.tostring(root,encoding='utf-8',xml_declaration=True)


def sub(root: E._Element, tag: str, **attributes: str) -> E._Element:
    return E.SubElement(root,'{'+M+'}'+tag,attributes)


def sheets(data: dict) -> dict[str,str]:
    rel={r.get('Id'):r.get('Target') for r in E.fromstring(data['xl/_rels/workbook.xml.rels'])}
    result={}
    for s in E.fromstring(data['xl/workbook.xml']).find('m:sheets',NS):
        target=rel[s.get('{'+R+'}id')]
        result[s.get('name')]=target.lstrip('/') if target.startswith('/') else 'xl/'+target
    return result


def bind_sources(plan: dict, path: Path) -> None:
    data=read_parts(path);mapping=sheets(data);specs=plan['source_specs'];ids={n:i for i,n in enumerate(specs,1)}
    bindings=defaultdict(list);cache=defaultdict(dict)
    for b in plan['bindings']:bindings[b['sheet']].append(b);cache[b['table']][b['source_cell']]=b['value']
    for sn,rr in bindings.items():
        root=E.fromstring(data[mapping[sn]])
        cells={c.get('r'):c for c in root.findall('.//m:sheetData/m:row/m:c',NS)}
        rows={r.get('r'):r for r in root.findall('m:sheetData/m:row',NS)}
        for b in rr:
            c=cells.get(b['cell'])
            if c is None:c=sub(rows[re.search(r'\d+',b['cell'])[0]],'c',r=b['cell'])
            for e in list(c):c.remove(e)
            ref="'["+str(ids[b['table']])+']'+specs[b['table']]['sheet'].replace("'","''")+"'!"+re.sub(r'([A-Z]+)(\d+)',r'$\1$\2',b['source_cell'])
            sub(c,'f').text=f'IF(ISBLANK({ref}),"",{ref})'
            value=b['value']
            if value is None or isinstance(value,str):c.set('t','str');value='' if value is None else value
            elif isinstance(value,bool):c.set('t','b');value=int(value)
            else:c.attrib.pop('t',None)
            sub(c,'v').text=str(value)
        for row in rows.values():row[:]=sorted(row,key=lambda c:(len(re.match('[A-Z]+',c.get('r'))[0]),c.get('r')))
        data[mapping[sn]]=xml(root)
    wb=E.fromstring(data['xl/workbook.xml']);wr=E.fromstring(data['xl/_rels/workbook.xml.rels']);ct=E.fromstring(data['[Content_Types].xml'])
    assert wb.find('m:externalReferences',NS) is None,'已绑定外链，不能重复执行'
    refs=E.Element('{'+M+'}externalReferences')
    pos=next((i for i,e in enumerate(wb) if E.QName(e).localname in ('definedNames','calcPr','extLst')),len(wb));wb.insert(pos,refs)
    for name,i in ids.items():
        rid='rIdSource'+str(i)
        E.SubElement(refs,'{'+M+'}externalReference',{'{'+R+'}id':rid})
        E.SubElement(wr,'{'+P+'}Relationship',Id=rid,Type=R+'/externalLink',Target=f'externalLinks/externalLink{i}.xml')
        E.SubElement(ct,'{'+C+'}Override',PartName=f'/xl/externalLinks/externalLink{i}.xml',ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.externalLink+xml')
        root=E.Element('{'+M+'}externalLink',nsmap={None:M,'r':R});eb=E.SubElement(root,'{'+M+'}externalBook',{'{'+R+'}id':'rId1'})
        sub(sub(eb,'sheetNames'),'sheetName',val=specs[name]['sheet'])
        sd=sub(sub(eb,'sheetDataSet'),'sheetData',sheetId='0');rows={}
        for address,value in cache[name].items():
            rn=re.search(r'\d+',address)[0]
            if rn not in rows:rows[rn]=sub(sd,'row',r=rn)
            c=sub(rows[rn],'cell',r=address)
            if value is None:continue
            if isinstance(value,str):c.set('t','str')
            elif isinstance(value,bool):c.set('t','b');value=int(value)
            sub(c,'v').text=str(value)
        data[f'xl/externalLinks/externalLink{i}.xml']=xml(root)
        er=E.Element('{'+P+'}Relationships',nsmap={None:P})
        E.SubElement(er,'{'+P+'}Relationship',Id='rId1',Type=R+'/externalLinkPath',Target=quote(specs[name]['file']),TargetMode='External')
        data[f'xl/externalLinks/_rels/externalLink{i}.xml.rels']=xml(er)
    data['xl/workbook.xml']=xml(wb);data['xl/_rels/workbook.xml.rels']=xml(wr);data['[Content_Types].xml']=xml(ct);write_parts(path,data)


def sanitize(plan: dict, path: Path) -> None:
    data=read_parts(path)
    styles=E.fromstring(data['xl/styles.xml']);xfs=styles.find('m:cellXfs',NS);centered={}
    visible={s['name'] for s in plan['sheets'] if not s['hidden']}
    for name,part in sheets(data).items():
        if name not in visible:continue
        root=E.fromstring(data[part])
        spec=next(s for s in plan['sheets'] if s['name']==name)
        if spec.get('dashboard'):
            for c in root.findall('m:sheetData/m:row/m:c',NS):
                if c.get('r') not in ('A7','D7','G7','J7'):continue
                original=int(c.get('s','0'))
                if original not in centered:
                    xf=deepcopy(xfs[original]);alignment=xf.find('m:alignment',NS)
                    if alignment is None:alignment=sub(xf,'alignment')
                    alignment.set('horizontal','center');xf.set('applyAlignment','1')
                    centered[original]=len(xfs);xfs.append(xf)
                c.set('s',str(centered[original]))
            if name in ('卡包_概览','777_概览','商城_Pass_概览','常驻_概览'):
                for row in root.findall('m:sheetData/m:row',NS):
                    if any(sec['row']<int(row.get('r'))<=sec['end'] for sec in spec['sections']):row.set('ht','80');row.set('customHeight','1')
        for pane in root.findall('m:sheetViews/m:sheetView/m:pane',NS):
            # 概览只冻结标题区，不能把30行图表区冻结到WPS可见区域外。
            count=4 if next(s for s in plan['sheets'] if s['name']==name).get('dashboard') else 6
            pane.attrib.update({'xSplit':'1','ySplit':str(count),'topLeftCell':'B'+str(count+1),'activePane':'bottomRight','state':'frozen'})
        data[part]=xml(root)
    xfs.set('count',str(len(xfs)));data['xl/styles.xml']=xml(styles)
    if 'docProps/custom.xml' in data:
        del data['docProps/custom.xml']
        for name in ('_rels/.rels','[Content_Types].xml'):
            root=E.fromstring(data[name])
            for e in list(root):
                if 'custom-properties' in e.get('Type','') or e.get('PartName')=='/docProps/custom.xml':root.remove(e)
            data[name]=xml(root)
    for name,raw in list(data.items()):
        if not name.endswith(('.xml','.rels')):continue
        if name.startswith('xl/externalLinks/_rels/'):
            root=E.fromstring(raw)
            for e in root:
                basename=unquote(e.get('Target','')).replace('\\','/').rsplit('/',1)[-1]
                matches=[s['file'] for s in plan['source_specs'].values() if s['file'].rsplit('/',1)[-1]==basename]
                assert len(matches)==1,'出现不在本轮原始源白名单内的外链'
                e.set('Target',quote(matches[0]))
            data[name]=xml(root)
        elif name in ('xl/workbook.xml','docProps/core.xml','docProps/app.xml'):
            root=E.fromstring(raw)
            for e in list(root.iter()):
                local=E.QName(e).localname
                if local=='absPath':e.getparent().remove(e)
                elif local in ('creator','lastModifiedBy','Company','Manager','HyperlinkBase'):e.text=None
            data[name]=xml(root)
    write_parts(path,data)


def snapshot(master: Path, display: Path) -> None:
    data=read_parts(master)
    for n in sheets(data).values():
        root=E.fromstring(data[n]);jumps=[]
        for c in root.findall('.//m:sheetData/m:row/m:c',NS):
            f=c.find('m:f',NS)
            if f is None:continue
            match=re.fullmatch(r'HYPERLINK\("#([^"\n]+)","([^"\n]*)"\)',f.text or '',re.I)
            if match:jumps.append((c.get('r'),match[1],match[2]))
            c.remove(f)
            if c.get('t')=='str':
                v=c.find('m:v',NS);text=v.text if v is not None and v.text else ''
                if v is not None:c.remove(v)
                c.set('t','inlineStr');sub(sub(c,'is'),'t').text=text
        links=root.find('m:hyperlinks',NS)
        if jumps and links is None:
            links=E.Element('{'+M+'}hyperlinks')
            pos=next((i for i,e in enumerate(root) if E.QName(e).localname in ('printOptions','pageMargins','pageSetup','headerFooter','drawing','tableParts','extLst')),len(root));root.insert(pos,links)
        for address,location,label in jumps:sub(links,'hyperlink',ref=address,location=location,display=label)
        data[n]=xml(root)
    for n in list(data):
        if n.startswith('xl/externalLinks/') or n=='xl/calcChain.xml':del data[n]
        elif n.startswith('xl/tables/') and n.endswith('.xml'):
            root=E.fromstring(data[n])
            for e in list(root.iter()):
                if E.QName(e).localname in ('calculatedColumnFormula','totalsRowFormula'):e.getparent().remove(e)
            data[n]=xml(root)
    for n in ('xl/_rels/workbook.xml.rels','[Content_Types].xml','xl/workbook.xml'):
        root=E.fromstring(data[n])
        for e in list(root):
            if E.QName(e).localname=='externalReferences' or any(k in e.get('Type','')+e.get('PartName','') for k in ('externalLink','calcChain')):root.remove(e)
        data[n]=xml(root)
    write_parts(display,data)


def read_cells(path: Path) -> tuple[dict,dict]:
    data=read_parts(path);ss=[];cells={};metrics={'formulas':0,'errors':[],'missing':[],'tables':0,'grouped_rows':0,'frozen':0,'rows':{}}
    if 'xl/sharedStrings.xml' in data:ss=[''.join(s.itertext()) for s in E.fromstring(data['xl/sharedStrings.xml'])]
    for name,n in sheets(data).items():
        root=E.fromstring(data[n]);rr=root.findall('m:sheetData/m:row',NS);metrics['rows'][name]=len(rr)
        metrics['tables']+=len(root.findall('m:tableParts/m:tablePart',NS));metrics['grouped_rows']+=sum(int(r.get('outlineLevel','0'))>0 for r in rr)
        metrics['frozen']+=sum(p.get('state') in ('frozen','frozenSplit') and p.get('xSplit')=='1' and p.get('ySplit') in ('4','6') for p in root.findall('m:sheetViews/m:sheetView/m:pane',NS))
        for c in root.findall('.//m:sheetData/m:row/m:c',NS):
            key=name+'!'+c.get('r');f=c.find('m:f',NS);v=c.find('m:v',NS);t=c.get('t')
            if t=='s':value=ss[int(v.text)] if v is not None and v.text else ''
            elif t=='inlineStr':value=''.join(c.find('m:is',NS).itertext())
            elif t in ('str','e'):value=v.text if v is not None and v.text else ''
            else:value=float(v.text) if v is not None and v.text else None
            cells[key]=value
            if t=='e':metrics['errors'].append(key)
            if f is not None:
                metrics['formulas']+=1
                if v is None:metrics['missing'].append(key)
    return cells,metrics


def validate_pair(plan: dict, master: Path, display: Path) -> dict:
    mc,mm=read_cells(master);dc,dm=read_cells(display);failures=[]
    for c in plan['checks']:
        value=mc.get(c['cell'].replace("'",''))
        if not isinstance(value,(int,float)) or abs(value-c['expected'])>max(1e-8,abs(c['expected'])*1e-9):failures.append(c['cell'])
    mismatch=[k for k,v in mc.items() if v!=dc.get(k)]
    source_mismatch=[]
    for b in plan['bindings']:
        value=mc.get(b['sheet']+'!'+b['cell'])
        if value!=b['value'] and not(b['value'] is None and value==''):source_mismatch.append(b['sheet']+'!'+b['cell'])
    privacy=[];links={};states={}
    for kind,path in (('master',master),('display',display)):
        targets=[];data=read_parts(path)
        if kind=='display':
            assert not any(b'calculatedColumnFormula' in raw or b'totalsRowFormula' in raw for n,raw in data.items() if n.startswith('xl/tables/'))
        states[kind]=[(s.get('name'),s.get('state','visible')) for s in E.fromstring(data['xl/workbook.xml']).find('m:sheets',NS)]
        for n,raw in data.items():
            if not n.endswith(('.xml','.rels')):continue
            text=raw.decode('utf-8')
            if re.search(r'(?<![A-Za-z])[A-Za-z]:[\\/]|file:/|(?:/|\\)Users(?:/|\\)|absPath',text,re.I):privacy.append(kind+':'+n)
            if n=='docProps/core.xml' and any(E.QName(e).localname in ('creator','lastModifiedBy') and e.text for e in E.fromstring(raw)):privacy.append(kind+':author')
            if n.startswith('xl/externalLinks/_rels/'):
                for r in E.fromstring(raw):
                    target=unquote(r.get('Target',''))
                    assert target in [s['file'] for s in plan['source_specs'].values()] and (master.parent/target).is_file()
                    targets.append(target)
        links[kind]=targets
    detail={'accepted':failures,'pair':mismatch,'source':source_mismatch,'privacy':privacy,'errors':mm['errors']+dm['errors'],'missing':mm['missing']}
    result={'manifest_id':plan['manifest_id'],'revision':7013,'source_workbooks':len(plan['source_specs']),
        'visible_sheets':[s['name'] for s in plan['sheets'] if not s['hidden']], 'master_formulas':mm['formulas'],'display_formulas':dm['formulas'],
        'master_relative_links':len(links['master']),'display_external_links':len(links['display']),'accepted_key_outputs':len(plan['checks']),
        'accepted_mismatches':len(failures),'master_display_mismatches':len(mismatch),'linked_source_mismatches':len(source_mismatch),
        'formula_errors':len(detail['errors']),'missing_caches':len(detail['missing']),'metadata_or_absolute_paths':len(privacy),
        'filter_tables':mm['tables'],'grouped_rows':mm['grouped_rows'],'frozen_front_sheets':mm['frozen'],'level_detail_rows':mm['rows']['等级_明细'],
        'price_detail_rows':mm['rows']['美金金币档位_明细'],'unknown_groups':9,'no_hash':True,'old_values_used':False}
    (master.parent/'workbook-validation-details.json').write_text(json.dumps(detail,ensure_ascii=False,indent=2),encoding='utf-8')
    (master.parent/'workbook-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    assert not any(detail.values()),'检查受控验证明细；不能上传'
    assert len(links['master'])==len(plan['source_specs']) and not links['display'] and dm['formulas']==0
    for kind in states:
        assert [n for n,s in states[kind] if s=='visible']==result['visible_sheets']
        assert all(s=='hidden' for n,s in states[kind] if n.startswith(('SRC_','CALC_')))
    from build_producer_workbook import col
    previews=[]
    for s in plan['sheets']:
        if s['hidden']:continue
        limit=15 if s['name']=='Unknown' else 20
        rows=[[mc.get(s['name']+'!'+col(j)+str(i)) if isinstance(v,str) and v.startswith('=') else v for j,v in enumerate(row[:10],1)] for i,row in enumerate(s['rows'][:limit],1)]
        formats=[[re.sub(r'\d+',lambda m:str(min(int(m[0]),limit)),a),f] for a,f in s['formats'] if min(map(int,re.findall(r'\d+',a)))<=limit]
        previews.append(dict(s,rows=rows,formats=formats,sections=[dict(sec,end=min(sec['end'],limit),columns=min(sec['columns'],10)) for sec in s['sections'] if sec['row']<limit]))
    (master.parent/'native-preview-plan.json').write_text(json.dumps(dict(plan,sheets=previews,checks=[]),ensure_ascii=False),encoding='utf-8')
    return result


def verify_portable(plan: dict, master: Path) -> dict:
    """复制到新目录只读打开，验证37条解析及一个真实原格刷新；不保存源或副本。"""
    root=master.parent/'portability-check'
    root.mkdir(exist_ok=True)
    shutil.copy2(master,root/master.name)
    for spec in plan['source_specs'].values():
        relative=Path(spec['file']);assert relative.parts[:2]==('source','r7013') and '..' not in relative.parts
        target=root/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(master.parent/relative,target)
    script=root/'read-only-portability.ps1'
    script.write_text(r'''
param([string]$Root,[string]$Name)
$ErrorActionPreference='Stop';$app=New-Object -ComObject Excel.Application;$b=$null
try{
 $app.Visible=$false;$app.DisplayAlerts=$false;$app.AskToUpdateLinks=$false;$app.AutomationSecurity=3
 $b=$app.Workbooks.Open((Join-Path $Root $Name),0,$true)
 $links=@($b.LinkSources(1));$prefix=[IO.Path]::GetFullPath($Root).TrimEnd('\')+'\'
 $resolved=@($links|Where-Object{[IO.Path]::GetFullPath($_).StartsWith($prefix) -and (Test-Path -LiteralPath $_)})
 $level=@($links|Where-Object{$_ -like '*LevelCfg*'})
 if($level.Count -ne 1){throw '找不到唯一等级外链'}
 $b.UpdateLink($level[0],1);$app.CalculateFull()
 $refresh=($b.Worksheets.Item('SRC_LevelCfg').Range('C2').Value2 -eq 1 -and $b.Worksheets.Item('CALC_LEVEL').Range('E5').Value2 -eq 29)
 $b.Worksheets.Item(1).Activate();$pane=($app.ActiveWindow.SplitRow -eq 6 -and $app.ActiveWindow.SplitColumn -eq 1)
 if($links.Count -ne 37 -or $resolved.Count -ne 37 -or -not $refresh -or -not $pane){throw '整包搬移/源格刷新/冻结窗格不符合要求'}
 @{relative_links_resolved=$resolved.Count;representative_source_refresh=$refresh;native_pane_readback=$pane;read_only=$b.ReadOnly;source_saved=$false}|ConvertTo-Json|Set-Content -Encoding UTF8 -LiteralPath (Join-Path $Root 'result.json')
}finally{if($b){$b.Close($false)};$app.Quit();[Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null}
''',encoding='utf-8-sig')
    subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),'-Root',str(root),'-Name',master.name],check=True,timeout=300)
    result=json.loads((root/'result.json').read_text(encoding='utf-8-sig'))
    (master.parent/'portability-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
