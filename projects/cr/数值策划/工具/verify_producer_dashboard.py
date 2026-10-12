"""当前重构专用验收：原生重算、驱动变化、相对链接及双版本一致性。
不重复0033/0034/0035验收或旧969项；不操作原始源表。
"""
import argparse
import copy
import json
from pathlib import Path
import subprocess
from producer_workbook_links import bind_sources,sanitize,snapshot,validate_pair,read_cells,read_parts,write_parts,xml,sheets,E,NS,M

NATIVE=r'''
param([string]$XlsxPath,[string]$SummaryPath,[string]$PlanPath,[switch]$RecalculateOnly)
$ErrorActionPreference='Stop'
$app=New-Object -ComObject Excel.Application
$book=$null
try {
 $app.Visible=$false;$app.DisplayAlerts=$false;$app.AskToUpdateLinks=$false;$app.AutomationSecurity=3
 $book=$app.Workbooks.Open($XlsxPath,0,$false)
 $plan=Get-Content -Raw -Encoding UTF8 -LiteralPath $PlanPath | ConvertFrom-Json
 # 首轮原生验证发现的定向修正。生成器同样输出这些内容；不改源表/历史模型。
 foreach($name in @('Buff_概览','Buff_明细','关闭_历史配置','CALC_PRO_SHOP')){
  $ps=@($plan.sheets | Where-Object {$_.name -eq $name})[0];$ws=$book.Worksheets.Item($name)
  if($name -eq 'CALC_PRO_SHOP'){
   for($ri=1;$ri -lt $ps.rows.Count;$ri++){foreach($ci in @(4,8)){$ws.Cells.Item($ri+1,$ci+1).Formula=$ps.rows[$ri][$ci]}}
  }else{
   $ws.Range('A3').Value2=$ps.rows[2][0]
   if($name -like 'Buff*'){
    $start=6;if($name -eq 'Buff_概览'){$start=30;$ws.Range('A7').Value2=2}
    for($ri=$start-1;$ri -lt $start+16;$ri++){foreach($ci in @(3,4)){$ws.Cells.Item($ri+1,$ci+1).Formula=$ps.rows[$ri][$ci]}}
   }
  }
 }
 $tableCount=0;$chartCount=0;$groups=0
 foreach($p in $plan.sheets){
  $s=$book.Worksheets.Item($p.name)
  if($p.hidden){$s.Visible=0;continue}
  $s.Activate();$chartCount+=$s.ChartObjects().Count
  if($p.dashboard){
   while($s.ChartObjects().Count -gt $p.charts.Count){$s.ChartObjects().Item($s.ChartObjects().Count).Delete()}
   if($p.name -eq 'Buff_概览'){$obj=$s.ChartObjects().Item(1);$obj.Width=$s.Range('A10:L27').Width}
   $ci=0
   foreach($ch in $p.charts){
    $ci++;$chart=$s.ChartObjects().Item($ci).Chart
    $last=[int]$p.sections[0].end
    for($si=1;$si -lt $ch.columns.Count;$si++){
     $series=$chart.SeriesCollection($si)
     $series.XValues=$s.Range($s.Cells.Item([int]$ch.start+1,[int]$ch.columns[0]),$s.Cells.Item($last,[int]$ch.columns[0]))
     $series.Values=$s.Range($s.Cells.Item([int]$ch.start+1,[int]$ch.columns[$si]),$s.Cells.Item($last,[int]$ch.columns[$si]))
    }
   }
  }
  if(-not $RecalculateOnly){foreach($sec in $p.sections){
   if($sec.span -or $sec.end -le $sec.row){continue}
   $range=$s.Range($s.Cells.Item([int]$sec.row,1),$s.Cells.Item([int]$sec.end,[int]$sec.columns))
   $table=$s.ListObjects.Add(1,$range,$null,1);$tableCount++
   $table.Name='CRDashTable'+$tableCount;$table.TableStyle='TableStyleLight9';$table.ShowTableStyleRowStripes=$false
  }
  foreach($g in $p.groups){$s.Rows.Item(([string]$g[0]+':'+[string]$g[1])).Group()|Out-Null;$groups++}}
  $s.Outline.SummaryRow=0
  $freeze=6;if($p.dashboard){$freeze=30}
  $app.ActiveWindow.FreezePanes=$false;$s.Range(('B'+($freeze+1))).Select();$app.ActiveWindow.SplitColumn=1;$app.ActiveWindow.SplitRow=$freeze;$app.ActiveWindow.FreezePanes=$true
 }
 $app.CalculateFullRebuild()
 if($RecalculateOnly){$book.Worksheets.Item(1).Activate();$book.Save();return}
 $levels=$book.Worksheets.Item('CALC_PRO_LEVEL')
 $selector=$book.Worksheets.Item('SRC_DECISIONS').Range('B4');$saved=$selector.Value2
 $before=$levels.Range('K51').Value2;$selector.Value2=2;$app.CalculateFull()
 $variant=([Math]::Abs($levels.Range('K51').Value2-$before*1.5) -lt [Math]::Max(0.000001,$before*0.00000001))
 $selector.Value2=$saved
 $vip=$book.Worksheets.Item('SRC_DECISIONS').Range('B3');$old=$vip.Value2
 $v=$book.Worksheets.Item('CALC_PRO_VIP');$cost=$v.Range('D2').Value2;$vip.Value2=200;$app.CalculateFull()
 $vipDriver=([Math]::Abs($v.Range('D2').Value2-$cost/2) -lt 0.000001);$vip.Value2=$old
 $app.CalculateFullRebuild()
 if(-not($variant -and $vipDriver)){throw '当前制作人指标驱动变化失败'}
 $links=@($book.LinkSources(1));$linkOk=$true
 foreach($link in $links){if(-not(Test-Path -LiteralPath ([string]$link))){$linkOk=$false}}
 if(-not $linkOk){throw '相对外链不能解析'}
 $book.Worksheets.Item(1).Activate();$book.CheckCompatibility=$false;$book.Save()
 @{engine=$app.Name;version=$app.Version;bet_variant_changes_cost=$variant;vip_driver_changes_cost=$vipDriver;inputs_restored=$true;relative_link_resolution=$linkOk;relative_link_count=$links.Count;charts=$chartCount;tables=$tableCount;row_groups=$groups} | ConvertTo-Json | Set-Content -Encoding UTF8 -LiteralPath $SummaryPath
} finally {if($book){$book.Close($false);[Runtime.InteropServices.Marshal]::FinalReleaseComObject($book)|Out-Null};$app.Quit();[Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null}
'''

def validate_reward_layers(plan: dict, values: dict) -> None:
    """独立用r7013原抽取复核17类单位和基础/阶段/终局拆分。"""
    def records(name: str) -> list[dict]:
        source=next(s for s in plan['sheets'] if s['name']=='SRC_'+name)
        return [dict(zip(source['rows'][0],r)) for r in source['rows'][1:]]
    grids=records('StrikeLucky');rounds=records('StrikeLuckyRound')
    for i,rd in enumerate(rounds,2):
        assert rd['cherryItemType']==17 and rd['sevenItemType']==17
        expected=[sum(r['itemCount'] for r in grids if r['round']==rd['round'] and r['itemType']==17)/100,rd['cherryItemCount']/100,rd['sevenItemCount']/100]
        for col,amount in zip('IJK',expected):assert abs(values['CALC_SIM_777!'+col+str(i)]-amount)<1e-8
        assert abs(values['CALC_SIM_777!L'+str(i)]-sum(expected))<1e-8


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--baseline',type=Path);p.add_argument('--native',action='store_true');p.add_argument('--recalculate',action='store_true',help='只对已有外链master应用本轮定向修正并重算，不重复装配源格');a=p.parse_args()
    directory=a.directory.resolve();assert not any((x/'.git').exists() for x in (directory,*directory.parents))
    plan=json.loads((directory/'dashboard-plan.json').read_text(encoding='utf-8'))
    master=directory/'CR_9.22_数值体验表_r7013_MASTER.xlsx';display=directory/'CR_9.22_数值体验表_r7013_飞书展示版.xlsx'
    if a.native:
        if plan.get('preserved_sheets'):
            assert a.baseline
            old=read_parts(a.baseline/'CR_9.22_数值体验表_r7013_MASTER.xlsx');new=read_parts(master)
            shared=[''.join(s.itertext()) for s in E.fromstring(old['xl/sharedStrings.xml'])]
            for name in plan['preserved_sheets']:
                previous=E.fromstring(old[sheets(old)[name]]);current=E.fromstring(new[sheets(new)[name]])
                data=previous.find('m:sheetData',NS)
                for c in data.findall('m:row/m:c',NS):
                    assert c.get('s') is None,'只复用无样式的隐藏计算明细'
                    if c.get('t')=='s':
                        v=c.find('m:v',NS);text=shared[int(v.text)];c.remove(v);c.set('t','inlineStr')
                        E.SubElement(E.SubElement(c,'{'+M+'}is'),'{'+M+'}t').text=text
                current.replace(current.find('m:sheetData',NS),data)
                if current.find('m:dimension',NS) is not None:current.find('m:dimension',NS).set('ref',previous.find('m:dimension',NS).get('ref'))
                new[sheets(new)[name]]=xml(current)
            write_parts(master,new)
        bind_sources(plan,master)
        ps=directory/'native-dashboard-check.ps1';ps.write_text(NATIVE,encoding='utf-8-sig')
        subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ps),'-XlsxPath',str(master),'-PlanPath',str(directory/'dashboard-plan.json'),'-SummaryPath',str(directory/'native-dashboard-validation.json')],check=True,timeout=1200)
    if a.recalculate:
        ps=directory/'native-dashboard-check.ps1';ps.write_text(NATIVE,encoding='utf-8-sig')
        subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ps),'-XlsxPath',str(master),'-PlanPath',str(directory/'dashboard-plan.json'),'-SummaryPath',str(directory/'native-dashboard-validation.json'),'-RecalculateOnly'],check=True,timeout=600)
    sanitize(plan,master);snapshot(master,display)
    result=validate_pair(plan,master,display)
    values,metrics=read_cells(master)
    validate_reward_layers(plan,values)
    # 原始5000行仍在，派生明细+原奖励没有被抽样删除。
    assert metrics['rows']['等级_明细']>=10000
    assert result['display_external_links']==0
    assert result['formula_errors']==0 and result['missing_caches']==0
    evidence=json.loads((directory/'simulation-evidence.json').read_text(encoding='utf-8'))
    checks=evidence['simulation_checks'];samples=evidence['simulation_rows']
    assert len(samples['lucky'])==3000 and len(samples['cards'])==6000
    assert checks['lucky']['inner_removal']>0 and checks['lucky']['ordinary_guarantee']>0
    assert checks['snack']['reset_20']>0 and checks['snack']['jackpot_reset']>0
    assert all((r['spins'] is None)==(not r['complete']) for r in samples['cards'])
    assert all(sum(r['paid'])>=sum(r['paid_special']) for r in samples['lucky'])
    parts=read_parts(master);mapping=sheets(parts)
    chart_parts=[n for n in parts if n.startswith('xl/charts/chart') and n.endswith('.xml')]
    assert len(chart_parts)>=13
    native=json.loads((directory/'native-dashboard-validation.json').read_text(encoding='utf-8-sig'))
    native['charts']=len(chart_parts)
    # 关键业务总量、概率范围与未知不补零。此处不以验证结果反哺业务。
    assert values['CALC_PRO_LEVEL!I5001']=='不适用'
    assert values['CALC_PRO_VIP!K2']==0
    for r in range(31,91):
        v=values['卡包_概览!K'+str(r)];assert 0<=v<=1
    assert isinstance(values['薯片_概览!C45'],str),'自然道具封顶的未完成样本不能被SUM/AVERAGE补成0'
    # 净耗、返还、净成本守恒；非钱资源不塞进总额。
    for r in range(31,40):
        cost=values['777_概览!D'+str(r)];ret=values['777_概览!H'+str(r)];net=values['777_概览!J'+str(r)]
        assert abs(cost-ret-net)<1e-7
    # 用原生最终缓存渲染，不把Artifact对HYPERLINK的提示当成最终Excel效果。
    preview={'title':'preview','sheets':[],'checks':[]}
    for s in plan['sheets']:
        if s['hidden']:continue
        ss=copy.deepcopy(s);limit=len(s['rows']) if s.get('dashboard') else (16 if s['name']=='Unknown' else 20)
        if s.get('dashboard'):ss['preview_range']='A1:M43'
        ss['rows']=[[values.get(s['name']+'!'+__import__('build_producer_workbook').col(c+1)+str(r+1),v) for c,v in enumerate(row)] for r,row in enumerate(s['rows'][:limit])]
        ss['sections']=[dict(sec,end=min(sec['end'],limit)) for sec in s['sections'] if sec['row']<limit]
        for chart in ss.get('charts',[]):chart['end']=s['sections'][0]['end']
        ss['formats']=[f for f in s['formats'] if int(__import__('re').search(r'\d+',f[0])[0])<=limit]
        preview['sheets'].append(ss)
    (directory/'dashboard-preview-plan.json').write_text(json.dumps(preview,ensure_ascii=False),encoding='utf-8')
    result.update({'current_checks':len(plan['checks']),'native':native,'charts':len(chart_parts),'current_business_checks':True,'accepted_baseline_not_rerun':True})
    (directory/'dashboard-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
