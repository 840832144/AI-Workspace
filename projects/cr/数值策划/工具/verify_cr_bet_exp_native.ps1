param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference='Stop'
$app=New-Object -ComObject Excel.Application
$book=$null;$owned=$false
try {
 if($app.Workbooks.Count -ne 0){throw '已有用户工作簿，停止'}
 $owned=$true;$app.Visible=$false;$app.DisplayAlerts=$false;$app.AutomationSecurity=3
 $file=Join-Path $Directory 'CR_vs_CF_Bet解锁与经验对照_r7252.xlsx'
 $book=$app.Workbooks.Open($file,0,$false)
 if($book.ReadOnly){throw '目标工作簿被占用'}
 $app.CalculateFullRebuild()
 foreach($name in @('SRC_DEV','SRC_CF','SRC_BET')){$book.Worksheets.Item($name).Visible=0}
 foreach($s in $book.Worksheets){
  if($s.Visible -ne -1){continue}
  $s.Activate();$app.ActiveWindow.FreezePanes=$false;$app.ActiveWindow.SplitRow=0;$app.ActiveWindow.SplitColumn=0
  $app.ActiveWindow.ScrollRow=1;$app.ActiveWindow.ScrollColumn=1;$null=$s.Range('A1').Select()
  if($s.Name -like '*概览'){
   for($i=1;$i -le $s.ChartObjects().Count;$i++){
    $obj=$s.ChartObjects().Item($i);$box=$s.Range($(if($i -eq 1){'A5:N25'}else{'A29:N49'}))
    $obj.Left=$box.Left;$obj.Top=$box.Top;$obj.Width=$box.Width;$obj.Height=$box.Height
    $c=$obj.Chart;$c.ChartType=4;$c.PlotVisibleOnly=$false;$c.DisplayBlanksAs=1
    $c.Axes(1).TickLabelSpacing=$(if($s.Name -eq 'Bet解锁_概览' -and $i -eq 2){250}else{25})
    $c.Axes(2).MinimumScale=0;$c.Axes(1).HasMajorGridlines=$false
    $c.HasLegend=$true;$c.Legend.Position=-4160;$c.ChartArea.Font.Name='Microsoft YaHei'
    foreach($ser in $c.SeriesCollection()){$ser.AxisGroup=1;$ser.Smooth=$false;$ser.MarkerStyle=-4142}
   }
   $s.Range('P:Y').EntireColumn.Hidden=$true
  } else {
   $last=$s.UsedRange.Rows.Count
   $right=$(if($s.Name -eq '逐级_明细'){'AE'}elseif($s.Name -eq 'Bet经验_候选'){'K'}else{'H'})
   $null=$s.Range("A4:${right}$last").AutoFilter()
  }
 }
 $app.CalculateFullRebuild()
 $src=$book.Worksheets.Item('SRC_CF');$detail=$book.Worksheets.Item('逐级_明细')
 $driver=$src.Range('C13');$old=$driver.Value2;$before=$detail.Range('S13').Value2
 $driver.Value2=$old*2;$app.CalculateFull()
 if([Math]::Abs($detail.Range('S13').Value2-$before/2) -gt 0.0000001){throw '经验反推公式未响应'}
 $driver.Value2=$old;$app.CalculateFullRebuild()
 if([Math]::Abs($detail.Range('S13').Value2-$before) -gt 0.0000001){throw '恢复失败'}
 $candidate=$book.Worksheets.Item('Bet经验_候选')
 foreach($cell in $candidate.Range('K6:K42').Cells){
  if($cell.Value2 -eq '经验倒挂：不可落表'){$cell.Font.Color=156;$cell.Font.Bold=$true;$cell.Interior.Color=14277081}
 }
 foreach($p in @('Author','Last Author','Company','Manager')){try{$book.BuiltinDocumentProperties.Item($p).Value=''}catch{}}
 $book.Worksheets.Item('Bet解锁_概览').Activate();$book.Save()
 $previews=Join-Path $Directory 'previews';New-Item -ItemType Directory -Force $previews|Out-Null
 foreach($v in @(@('Bet解锁_概览',1,'Bet_1-300'),@('Bet解锁_概览',2,'Bet_1-5000'),@('升级体验_概览',1,'同Bet升级体验'),@('升级体验_概览',2,'美元消耗门槛'),@('单Spin经验_概览',1,'单Spin经验'))){
  $s=$book.Worksheets.Item($v[0]);$s.Activate();$obj=$s.ChartObjects().Item($v[1]);$null=$obj.Activate()
  $png=Join-Path $previews ($v[2]+'.chart.png');$null=$obj.Chart.Export($png,'PNG')
  if(-not (Test-Path -LiteralPath $png)){throw '原生图表图片缺失'}
 }
 $views=@(
  @('Bet解锁_概览','A1:O27','Bet_1-300'),@('Bet解锁_概览','A28:O53','Bet_1-5000'),
  @('升级体验_概览','A1:O27','同Bet升级体验'),@('升级体验_概览','A28:O54','美元消耗门槛'),
  @('单Spin经验_概览','A1:O43','单Spin经验'),@('经验约束_明细','A1:H24','经验冲突'),
  @('Bet档位_明细','A1:H32','Bet档位'),@('逐级_明细','A4:L22','逐级前段'),@('Bet经验_候选','A1:K42','经验候选'))
 foreach($v in $views){
  $s=$book.Worksheets.Item($v[0]);$s.Activate()
  $s.PageSetup.Orientation=2;$s.PageSetup.PaperSize=9;$s.PageSetup.Zoom=$false
  $s.PageSetup.FitToPagesWide=1;$s.PageSetup.FitToPagesTall=1
  $s.PageSetup.PrintArea=$v[1]
  $s.ExportAsFixedFormat(0,(Join-Path $previews ($v[2]+'.pdf')))
 }
 Write-Output 'Native recalc, inference driver response/restore and 9 PDF views completed.'
} finally {
 if($book){$book.Close($false)}
 if($owned){$app.Quit()}
 [Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null
}
