"""仅验本轮新Excel；可调用独立隐藏Excel实例验证原生重算并设置隐藏Sheet。

python verify_producer_workbook.py --plan <计划JSON> --xlsx <新XLSX> --native
不接触源配置/旧工作簿；无hash。输出脱敏摘要和受控详细失败项。
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

NATIVE = r'''
param([string]$XlsxPath,[string]$SummaryPath,[string]$PlanPath)
$ErrorActionPreference='Stop'
$app=New-Object -ComObject Excel.Application
$book=$null
try {
  $app.Visible=$false
  $app.DisplayAlerts=$false
  $app.AskToUpdateLinks=$false
  $app.AutomationSecurity=3
  $book=$app.Workbooks.Open($XlsxPath,0,$false)
  $book.Worksheets.Item(1).Activate()
  foreach($sheet in $book.Worksheets){
    if($sheet.Name.StartsWith('SRC_') -or $sheet.Name.StartsWith('CALC_')){$sheet.Visible=0}
  }
  $plan=Get-Content -Raw -Encoding UTF8 -LiteralPath $PlanPath | ConvertFrom-Json
  $tableCount=0;$groupCount=0
  foreach($p in $plan.sheets){
    if($p.hidden){continue}
    $s=$book.Worksheets.Item($p.name);$s.Activate()
    foreach($sec in $p.sections){
      if($sec.span -or $sec.end -le $sec.row){continue}
      $range=$s.Range($s.Cells.Item([int]$sec.row,1),$s.Cells.Item([int]$sec.end,[int]$sec.columns))
      $table=$s.ListObjects.Add(1,$range,$null,1);$tableCount++
      $table.Name='CRTable'+$tableCount;$table.TableStyle='TableStyleLight9';$table.ShowTableStyleRowStripes=$false
    }
    foreach($g in $p.groups){$s.Rows.Item(([string]$g[0]+':'+[string]$g[1])).Group()|Out-Null;$groupCount++}
    $s.Outline.SummaryRow=0
    $app.ActiveWindow.FreezePanes=$false;$s.Range('B7').Select();$app.ActiveWindow.SplitColumn=1;$app.ActiveWindow.SplitRow=6;$app.ActiveWindow.FreezePanes=$true
  }
  $app.CalculateFullRebuild()
  $spin=$book.Worksheets.Item('CALC_SPIN')
  $input=$book.Worksheets.Item('SRC_SCENARIOS').Range('E2')
  $savedSpin=$input.Value2
  $oldGross=$spin.Range('J2').Value2
  $input.Value2=[double]$savedSpin+1
  $app.CalculateFull()
  $driver=([Math]::Abs($spin.Range('J2').Value2-$oldGross-$spin.Range('F2').Value2) -lt 0.000001)
  $input.Value2=$savedSpin
  # 第一个USD Bet=1案例的金币Bet引用直接连到SRC。
  $formula=$spin.Range('F5').Formula
  $parts=$formula.TrimStart('=').Split('!')
  $bet=$book.Worksheets.Item($parts[0].Trim("'")).Range($parts[1])
  $savedBet=$bet.Formula
  $bet.Value2=$spin.Range('G5').Value2
  $app.CalculateFull()
  $equal=([Math]::Abs($spin.Range('I5').Value2-0.95) -lt 0.000000001)
  $bet.Value2=$spin.Range('G5').Value2*1.01
  $app.CalculateFull()
  $above=([Math]::Abs($spin.Range('I5').Value2-0.85) -lt 0.000000001)
  $bet.Formula=$savedBet
  $app.CalculateFullRebuild()
  $levels=$book.Worksheets.Item('等级_明细')
  $zero=($levels.Range('H8').Value2 -is [double] -and $levels.Range('H8').Value2 -eq 0)
  $blank=($levels.Range('D8').Value2 -is [string] -and $levels.Range('D8').Value2 -eq '')
  $unknown=($book.Worksheets.Item('CALC_LEVEL').Range('E6').Value2 -eq 'Unknown')
  if(-not($driver -and $equal -and $above -and $zero -and $blank -and $unknown)){throw '原生动态/缺值验证失败'}
  $book.CheckCompatibility=$false
  $book.Worksheets.Item(1).Activate();$book.Save()
  @{engine=$app.Name;version=$app.Version;driver_update=$driver;usd_equal_one_95=$equal;usd_above_one_85=$above;source_zero_preserved=$zero;source_blank_preserved=$blank;growth_unknown_preserved=$unknown;inputs_restored=$true;filter_tables=$tableCount;row_groups=$groupCount} | ConvertTo-Json | Set-Content -Encoding UTF8 -LiteralPath $SummaryPath
} finally {
  if($book){$book.Close($false);[Runtime.InteropServices.Marshal]::FinalReleaseComObject($book)|Out-Null}
  $app.Quit()
  [Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null
}
'''


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--xlsx',type=Path,required=True)
    ap.add_argument('--native',action='store_true')
    ap.add_argument('--portable-check',action='store_true',help='整包复制到新目录后只读核对外链与窗格')
    a=ap.parse_args();path=a.xlsx.resolve()
    if any((p/'.git').exists() for p in (path.parent,*path.parents)):raise ValueError('仅处理Git外新产物')
    assert path.name=='CR_9.22_数值体验表_r7013_MASTER.xlsx','不处理源表或旧附件'
    plan=json.loads(a.plan.read_text(encoding='utf-8'))
    from producer_workbook_links import bind_sources, sanitize, snapshot, validate_pair
    if a.native:
        bind_sources(plan,path)
        script=path.parent/'native-workbook-check.ps1'
        script.write_text(NATIVE,encoding='utf-8-sig')
        command=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),'-XlsxPath',str(path),'-SummaryPath',str(path.parent/'native-validation.json'),'-PlanPath',str(a.plan.resolve())]
        subprocess.run(command,check=True,timeout=600)
    sanitize(plan,path)
    display=path.with_name('CR_9.22_数值体验表_r7013_飞书展示版.xlsx')
    snapshot(path,display)
    print(json.dumps(validate_pair(plan,path,display),ensure_ascii=False))
    if a.portable_check:
        from producer_workbook_links import verify_portable
        print(json.dumps(verify_portable(plan,path),ensure_ascii=False))


if __name__=='__main__':main()
