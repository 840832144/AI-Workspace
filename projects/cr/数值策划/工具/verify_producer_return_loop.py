"""装配Artifact定向单元格编辑、原生重算与返还闭环验收，不重建原始源。

python verify_producer_return_loop.py --baseline <Dashboard目录> --directory <本轮目录> --assemble
只在首次装配使用--assemble；本轮版式修改后可使用--native，再用无参数模式检查。
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import re
import subprocess
from producer_workbook_links import read_parts, write_parts, sheets, E, NS, M, R, P, C, xml, sub, sanitize, snapshot, read_cells, validate_pair
from build_producer_workbook import col


def assemble(baseline: Path, directory: Path, plan: dict, patch: dict) -> None:
    data=read_parts(baseline/'CR_9.22_数值体验表_r7013_MASTER.xlsx');art=read_parts(directory/'return-patch.xlsx')
    mapping=sheets(data);amap=sheets(art)
    shared=[''.join(s.itertext()) for s in E.fromstring(art['xl/sharedStrings.xml'])] if 'xl/sharedStrings.xml' in art else []
    wb=E.fromstring(data['xl/workbook.xml']);rels=E.fromstring(data['xl/_rels/workbook.xml.rels']);ct=E.fromstring(data['[Content_Types].xml'])
    for ps in patch['changed']:
        name=ps['name'];spec=next(s for s in plan['sheets'] if s['name']==name)
        if name not in mapping:
            sid=max(int(s.get('sheetId')) for s in wb.find('m:sheets',NS))+1
            part=f'xl/worksheets/sheet{sid}.xml';assert part not in data
            rid='rIdReturn'+str(sid);E.SubElement(wb.find('m:sheets',NS),'{'+M+'}sheet',{'name':name,'sheetId':str(sid),'state':'hidden','{'+R+'}id':rid})
            E.SubElement(rels,'{'+P+'}Relationship',Id=rid,Type=R+'/worksheet',Target=f'worksheets/sheet{sid}.xml')
            E.SubElement(ct,'{'+C+'}Override',PartName='/'+part,ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml')
            data[part]=art[amap[name]];mapping[name]=part
        root=E.fromstring(data[mapping[name]]);sd=root.find('m:sheetData',NS)
        existing={c.get('r'):c for c in sd.findall('m:row/m:c',NS)};rows={int(r.get('r')):r for r in sd}
        incoming={c.get('r'):c for c in E.fromstring(art[amap[name]]).findall('m:sheetData/m:row/m:c',NS)}
        for rownum,column,value in ps['edits']:
            address=col(column)+str(rownum);prior=existing.get(address)
            if prior is not None:prior.getparent().remove(prior)
            if value is None:continue
            assert address in incoming,(name,address)
            cell=copy.deepcopy(incoming[address]);cell.attrib.pop('s',None)
            if prior is not None and prior.get('s') is not None:cell.set('s',prior.get('s'))
            if cell.get('t')=='s':
                v=cell.find('m:v',NS);text=shared[int(v.text)];cell.remove(v);cell.set('t','inlineStr');sub(sub(cell,'is'),'t').text=text
            if rownum not in rows:rows[rownum]=sub(sd,'row',r=str(rownum))
            rows[rownum].append(cell)
        sd[:]=sorted(rows.values(),key=lambda r:int(r.get('r')))
        for row in sd:row[:]=sorted(row,key=lambda c:(len(re.match('[A-Z]+',c.get('r'))[0]),re.match('[A-Z]+',c.get('r'))[0]))
        end=f'{col(max(len(r) for r in spec["rows"]))}{len(spec["rows"])}'
        dimension=root.find('m:dimension',NS)
        if dimension is not None:dimension.set('ref','A1:'+end)
        data[mapping[name]]=xml(root)
    for root in (rels,ct):
        for el in list(root):
            if 'calcChain' in el.get('Type','')+el.get('PartName',''):root.remove(el)
    data.pop('xl/calcChain.xml',None)
    data['xl/workbook.xml']=xml(wb);data['xl/_rels/workbook.xml.rels']=xml(rels);data['[Content_Types].xml']=xml(ct)
    write_parts(directory/'CR_9.22_数值体验表_r7013_MASTER.xlsx',data)


NATIVE=r'''
param([string]$Directory)
$ErrorActionPreference='Stop'
$meta=Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $Directory 'return-native-plan.json') | ConvertFrom-Json
$app=New-Object -ComObject Excel.Application;$book=$null
try{
 $app.Visible=$false;$app.DisplayAlerts=$false;$app.AskToUpdateLinks=$false;$app.AutomationSecurity=3
 $book=$app.Workbooks.Open((Join-Path $Directory 'CR_9.22_数值体验表_r7013_MASTER.xlsx'),0,$false)
 $tableIndex=0
 foreach($p in $meta.sheets){
  $s=$book.Worksheets.Item($p.name)
  if($p.hidden){$s.Visible=0;continue}
  $s.Activate()
  while($s.ListObjects.Count -gt 0){$s.ListObjects.Item(1).Unlist()}
  if($p.dashboard){
   $s.Range('A1:M4').Font.Name='宋体';$s.Range('A3:L3').WrapText=$true;$s.Rows.Item('3').RowHeight=60
   $s.Range('A7:L8').HorizontalAlignment=-4108
   $s.Range('A30:M'+$p.end).Font.Name='宋体';$s.Range('A30:M'+$p.end).Font.Size=11
   $s.Range('A30:M'+$p.end).VerticalAlignment=-4108
   $s.Range('A30:M'+$p.end).WrapText=$true
   $s.Range('A30:M'+$p.end).NumberFormat='#,##0'
   $s.Columns.Item('A:M').ColumnWidth=17
  }
  foreach($sec in $p.sections){
   if($sec.span -or $sec.end -le $sec.row){continue}
   $range=$s.Range($s.Cells.Item([int]$sec.row,1),$s.Cells.Item([int]$sec.end,[int]$sec.columns))
   $table=$s.ListObjects.Add(1,$range,$null,1);$tableIndex++
   $table.Name='CRReturnTable'+$tableIndex;$table.TableStyle='TableStyleLight9';$table.ShowTableStyleRowStripes=$false
   if($p.dashboard){
    $title=$s.Range($s.Cells.Item([int]$sec.row-1,1),$s.Cells.Item([int]$sec.row-1,[int]$sec.columns));$title.UnMerge();$title.Merge()
    $title.Font.Bold=$true;$title.Interior.Color=16050925;$title.RowHeight=32
    $head=$s.Range($s.Cells.Item([int]$sec.row,1),$s.Cells.Item([int]$sec.row,[int]$sec.columns));$head.Font.Bold=$true;$head.Interior.Color=6045749;$head.Font.Color=16777215;$head.RowHeight=52
    $body=$s.Range($s.Cells.Item([int]$sec.row+1,1),$s.Cells.Item([int]$sec.end,[int]$sec.columns));$body.RowHeight=76;$body.WrapText=$true
    $body.Font.Color=4937764
    for($col=1;$col -le [int]$sec.columns;$col++){
     $label=[string]$s.Cells.Item([int]$sec.row,$col).Value2
     $columnRange=$s.Range($s.Cells.Item([int]$sec.row+1,$col),$s.Cells.Item([int]$sec.end,$col))
     if($label -match '成本|净耗|支付'){$columnRange.Font.Color=2378156}
     elseif($label -match '奖励|返还|礼包|回补'){$columnRange.Font.Color=4756515}
    }
   }
  }
  foreach($f in $p.formats){$s.Range([string]$f[0]).NumberFormat=[string]$f[1]}
  if($p.dashboard){
   $ci=0
   foreach($ch in $p.charts){
    $ci++;$obj=$s.ChartObjects().Item($ci);$chart=$obj.Chart
    $chart.HasTitle=$true;$chart.ChartTitle.Text=[string]$ch.title
    while($chart.SeriesCollection().Count -gt ($ch.columns.Count-1)){$chart.SeriesCollection($chart.SeriesCollection().Count).Delete()}
    while($chart.SeriesCollection().Count -lt ($ch.columns.Count-1)){$null=$chart.SeriesCollection().NewSeries()}
    for($si=1;$si -lt $ch.columns.Count;$si++){
     $series=$chart.SeriesCollection($si)
     $series.Name=[string]$s.Cells.Item([int]$ch.start,[int]$ch.columns[$si]).Value2
     $series.XValues=$s.Range($s.Cells.Item([int]$ch.start+1,[int]$ch.columns[0]),$s.Cells.Item([int]$ch.end,[int]$ch.columns[0]))
     $series.Values=$s.Range($s.Cells.Item([int]$ch.start+1,[int]$ch.columns[$si]),$s.Cells.Item([int]$ch.end,[int]$ch.columns[$si]))
    }
    $chart.Axes(2).TickLabels.NumberFormat=[string]$ch.format
   }
  }
  $freeze=6;if($p.dashboard){$freeze=30}
  $app.ActiveWindow.FreezePanes=$false;$s.Range(('B'+($freeze+1))).Select();$app.ActiveWindow.SplitColumn=1;$app.ActiveWindow.SplitRow=$freeze;$app.ActiveWindow.FreezePanes=$true
 }
 $app.CalculateFullRebuild()
 # 实际变更关键返还输入后回读：只修改派生包内已导出公式输入，不修改源工作簿。
 $src=$book.Worksheets.Item('SRC_DECISIONS').Range('B3');$original=$src.Value2
 $vip=$book.Worksheets.Item('VIP_概览');$before=$vip.Range('L31').Value2
 $src.Value2=200;$app.CalculateFull();$after=$vip.Range('L31').Value2
 if([Math]::Abs($after-2*$before) -gt 0.000001){throw 'VIP返还率驱动未响应'}
 $src.Value2=$original;$app.CalculateFullRebuild()
 $links=@($book.LinkSources(1));$resolved=@($links | Where-Object {Test-Path -LiteralPath ([string]$_)})
 if($links.Count -ne 44 -or $resolved.Count -ne 44){throw '44条固定相对外链未解析'}
 $book.Worksheets.Item(1).Activate();$book.Save()
 $chartdir=Join-Path $Directory 'native-charts';$null=New-Item -ItemType Directory -Force -Path $chartdir
 $charts=0
 foreach($p in $meta.sheets | Where-Object {$_.dashboard}){
  $s=$book.Worksheets.Item($p.name)
  for($i=1;$i -le $s.ChartObjects().Count;$i++){
   $file=Join-Path $chartdir ($p.name+'-'+$i+'.png');$null=$s.ChartObjects().Item($i).Chart.Export($file,'PNG')
   if(-not (Test-Path -LiteralPath $file)){throw '原生图表导出文件缺失'};$charts++
  }
 }
 @{relative_link_count=$links.Count;resolved_links=$resolved.Count;vip_return_driver=$true;inputs_restored=$true;native_chart_images=$charts;source_saved=$false;engine=$app.Name;version=$app.Version}|ConvertTo-Json|Set-Content -Encoding UTF8 -LiteralPath (Join-Path $Directory 'return-native-validation.json')
}finally{if($book){$book.Close($false);[Runtime.InteropServices.Marshal]::FinalReleaseComObject($book)|Out-Null};$app.Quit();[Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null}
'''


def validate_closure(plan: dict, values: dict, evidence: dict) -> dict:
    checks=0
    def equal(a: float, b: float) -> None:
        nonlocal checks
        assert isinstance(a,(int,float)) and abs(a-b)<=max(1e-7,abs(b)*1e-9),(a,b)
        checks+=1
    def v(sheet: str, address: str) -> object:return values[sheet+'!'+address]
    sheets_by_name={s['name']:s for s in plan['sheets']}
    for i in range(31,sheets_by_name['等级_阶段概览']['sections'][0]['end']+1):
        cost=v('等级_阶段概览',f'E{i}')
        if cost:equal(v('等级_阶段概览',f'K{i}'),v('等级_阶段概览',f'F{i}')/cost)
        else:assert str(v('等级_阶段概览',f'K{i}')).startswith('N/A')
        sr=int(sheets_by_name['等级_阶段概览']['rows'][i-1][0].split('–')[1])+1
        equal(v('等级_阶段概览',f'L{i}'),v('CALC_PRO_LEVEL',f'P{sr}')/v('CALC_PRO_LEVEL',f'N{sr}'))
    for i in range(31,46):
        equal(v('VIP_概览',f'L{i}'),v('VIP_概览',f'F{i}')/v('VIP_概览',f'D{i}'))
        equal(v('VIP_概览',f'M{i}'),sum(v('VIP_概览',f'F{j}') for j in range(31,i+1))/v('VIP_概览',f'E{i}'))
    for i in range(31,sheets_by_name['BET_RTP_概览']['sections'][0]['end']+1):equal(v('BET_RTP_概览',f'D{i}')+v('BET_RTP_概览',f'I{i}'),1)
    cards=evidence['simulation_rows']['cards'];assert all(r['complete'] for r in cards)
    for i in range(31,91):
        row=sheets_by_name['卡包_概览']['rows'][i-1];sample=[r for r in cards if r['profile']==row[0] and r['chapter']==row[1]]
        equal(v('卡包_概览',f'D{i}'),sum(r['spins'] for r in sample)/len(sample))
        equal(v('卡包_概览',f'K{i}'),sum(r['spins']<=r['horizon'] for r in sample)/len(sample))
        equal(v('卡包_概览',f'H{i}'),v('卡包_概览',f'G{i}')/v('卡包_概览',f'F{i}'))
        equal(v('卡包_概览',f'I{i}'),v('卡包_概览',f'F{i}')-v('卡包_概览',f'G{i}'))
    for prof in evidence['profiles']:
        for sample in range(100):
            rows=[r for r in cards if r['profile']==prof['name'] and r['sample']==sample]
            album=next(r for r in rows if r['chapter']=='整册');equal(album['spins'],max(r['spins'] for r in rows if r['chapter']!='整册'))
    circle=sheets_by_name['777_概览']['sections'][1]
    for i in range(circle['row']+1,circle['end']+1):
        equal(v('777_概览',f'I{i}'),sum(v('777_概览',f'{c}{i}') for c in 'FGH'))
        if v('777_概览',f'E{i}')>0:equal(v('777_概览',f'J{i}'),v('777_概览',f'I{i}')/v('777_概览',f'E{i}'))
        else:assert v('777_概览',f'J{i}')=='N/A：本圈新增净耗为0'
        equal(v('777_概览',f'K{i}'),v('777_概览',f'E{i}')-v('777_概览',f'I{i}'))
    for rd in range(3):
        first=circle['row']+1+rd*3
        equal(sum(v('777_概览',f'I{i}') for i in range(first,first+3)),v('777_概览',f'H{34+rd}'))
        equal(sum(v('777_概览',f'E{i}') for i in range(first,first+3)),v('777_概览',f'D{34+rd}'))
    ss=sheets_by_name['薯片_概览'];unreachable=0
    for i in range(31,52):
        label=ss['rows'][i-1][0];rows=[r for r in evidence['simulation_rows']['snack'] if r['stage']==label]
        if any(r['draws']>160 for r in rows):assert v('薯片_概览',f'C{i}')=='自然渠道不可达';unreachable+=1
        equal(v('薯片_概览',f'H{i}'),sum(max(0,r['draws']-160) for r in rows)/len(rows))
        equal(v('薯片_概览',f'G{i}'),sum(r['draws']<=160 for r in rows)/len(rows))
    last=ss['sections'][-1]
    for i in range(last['row']+1,last['end']+1):
        equal(v('薯片_概览',f'F{i}'),v('薯片_概览',f'C{i}')+v('薯片_概览',f'D{i}'))
        equal(v('薯片_概览',f'G{i}'),v('薯片_概览',f'E{i}')/v('薯片_概览',f'F{i}'))
        equal(v('薯片_概览',f'H{i}'),v('薯片_概览',f'F{i}')-v('薯片_概览',f'E{i}'))
    for row in (31,32,37,38,39):
        denom=v('总览',f'H{row}');equal(v('总览',f'F{row}'),v('总览',f'E{row}')/denom);equal(v('总览',f'G{row}'),denom-v('总览',f'E{row}'))
    assert v('总览','F34')==v('总览','F35')=='N/A'
    assert '待启用确认' in v('总览','H40')
    return {'closure_checks':checks,'card_completion_samples':len(cards),'natural_unreachable_targets':unreachable,'album_is_same_path_terminal':True,'reward_denominators_separate':True}


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--directory',type=Path,required=True);ap.add_argument('--baseline',type=Path);ap.add_argument('--assemble',action='store_true');ap.add_argument('--native',action='store_true');a=ap.parse_args()
    d=a.directory.resolve();assert not any((p/'.git').exists() for p in (d,*d.parents))
    plan=json.loads((d/'return-plan.json').read_text(encoding='utf-8'));patch=json.loads((d/'return-patch.json').read_text(encoding='utf-8'))
    if a.assemble:assert a.baseline;assemble(a.baseline,d,plan,patch)
    if a.assemble or a.native:
        names={s['name'] for s in patch['changed']}
        meta={'sheets':[{k:v for k,v in s.items() if k in ('name','hidden','sections','formats','dashboard','charts')}|{'end':len(s['rows'])} for s in plan['sheets'] if s['name'] in names]}
        (d/'return-native-plan.json').write_text(json.dumps(meta,ensure_ascii=False),encoding='utf-8')
        (d/'return-native.ps1').write_text(NATIVE,encoding='utf-8-sig')
        subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(d/'return-native.ps1'),'-Directory',str(d)],check=True,timeout=1200)
    master=d/'CR_9.22_数值体验表_r7013_MASTER.xlsx';display=d/'CR_9.22_数值体验表_r7013_飞书展示版.xlsx'
    sanitize(plan,master);snapshot(master,display)
    # 本轮不重复旧36项/969项验收；仅复核当前产物完整性与本轮闭环。
    pairplan=dict(plan,checks=[]);result=validate_pair(pairplan,master,display)
    values,metrics=read_cells(master);evidence=json.loads((d/'simulation-evidence.json').read_text(encoding='utf-8'))
    result.update(validate_closure(plan,values,evidence));result['native']=json.loads((d/'return-native-validation.json').read_text(encoding='utf-8-sig'))
    result['status']='Review';result['no_hash']=True;result['revision']=7013
    (d/'return-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    # 当前前台缓存预览；不重渲染未变原始明细。
    preview={'title':'return-preview','sheets':[],'checks':[]}
    for s in plan['sheets']:
        if not s.get('dashboard') and s['name']!='Unknown':continue
        ps=copy.deepcopy(s);limit=len(s['rows'])
        ps['rows']=[[values.get(s['name']+'!'+col(c+1)+str(i+1),v) for c,v in enumerate(row)] for i,row in enumerate(s['rows'])]
        ps['preview_range']='A1:M43' if s.get('dashboard') else 'A1:E15'
        preview['sheets'].append(ps)
    (d/'return-preview-plan.json').write_text(json.dumps(preview,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
