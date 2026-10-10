param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference='Stop'
$app=New-Object -ComObject Excel.Application
$book=$null;$owned=$false
try {
 if($app.Workbooks.Count -ne 0){throw 'Existing user workbook; stop'}
 $owned=$true;$app.Visible=$false;$app.DisplayAlerts=$false;$app.AutomationSecurity=3
 $preview=Join-Path $Directory 'previews';New-Item -ItemType Directory -Force $preview | Out-Null
 foreach($name in @('CR_vs_CF_最新实测_数值曲线.xlsx','r7258_vs_CF_最新实测_差异.xlsx')){
  $book=$app.Workbooks.Open((Join-Path $Directory $name),0,$false)
  if($book.ReadOnly){throw 'Output workbook locked'}
  foreach($s in $book.Worksheets){
   if($s.Name -in @('CALC','SRC_CR','SRC_CF')){$s.Visible=0;continue}
   $s.Activate();$app.ActiveWindow.FreezePanes=$false;$app.ActiveWindow.SplitRow=0;$app.ActiveWindow.SplitColumn=0
   $app.ActiveWindow.ScrollRow=1;$app.ActiveWindow.ScrollColumn=1;$app.ActiveWindow.Zoom=85
   $null=$s.Range('A1').Select();$s.Columns('AA:AZ').Hidden=$true
   $end=$s.UsedRange.Rows.Count;$width=$(if($s.Name -eq 'r7258差异'){19}elseif($s.Name -eq 'VIP_消费门槛'){8}elseif($s.Name -eq 'VIP_膨胀系数'){4}elseif($s.Name -eq '等级_升级消耗返还'){10}else{9})
   $null=$s.Range($s.Cells.Item(31,1),$s.Cells.Item($end,$width)).AutoFilter()
   for($i=1;$i -le $s.ChartObjects().Count;$i++){
    $c=$s.ChartObjects().Item($i).Chart;$c.ChartType=4;$c.PlotVisibleOnly=$false;$c.DisplayBlanksAs=1
    $c.Axes(1).TickLabelSpacing=$(if($s.Name -like 'VIP*'){1}else{5})
    $c.Axes(1).HasMajorGridlines=$false;$c.Axes(2).MinimumScale=0
    $c.ChartArea.Font.Name='Microsoft YaHei';$c.HasLegend=$true;$c.Legend.Position=-4160
    foreach($series in $c.SeriesCollection()){$series.AxisGroup=1;$series.Smooth=$false;$series.MarkerStyle=-4142}
   }
  }
  $app.CalculateFullRebuild()
  # Independent driver response: double A efficiency, costs/rewards halve, return rate unchanged; B unchanged.
  $cf=$book.Worksheets.Item('SRC_CF');$calc=$book.Worksheets.Item('CALC')
  $old=$cf.Range('N4').Value2;$cost=$calc.Range('J53').Value2;$reward=$calc.Range('L53').Value2
  $rate=$calc.Range('N53').Value2;$other=$calc.Range('K53').Value2
  $cf.Range('N4').Value2=$old*2;$app.CalculateFull()
  if([Math]::Abs($calc.Range('J53').Value2-$cost/2) -gt 1e-8){throw 'Scenario A cost response failed'}
  if([Math]::Abs($calc.Range('L53').Value2-$reward/2) -gt 1e-8){throw 'Scenario A reward response failed'}
  if([Math]::Abs($calc.Range('N53').Value2-$rate) -gt 1e-8){throw 'Return invariance failed'}
  if([Math]::Abs($calc.Range('K53').Value2-$other) -gt 1e-8){throw 'Scenario B changed'}
  $cf.Range('N4').Value2=$old;$app.CalculateFullRebuild()
  if([Math]::Abs($calc.Range('J53').Value2-$cost) -gt 1e-8){throw 'Restore failed'}
  foreach($p in @('Author','Last Author','Company','Manager')){try{$book.BuiltinDocumentProperties.Item($p).Value=''}catch{}}
  $book.Worksheets.Item(1).Activate();$book.Save()
  foreach($s in $book.Worksheets){
   if($s.Visible -ne -1){continue}
   $s.Activate()
   if($s.ChartObjects().Count -gt 0){
    $obj=$s.ChartObjects().Item(1);$null=$obj.Activate();$png=Join-Path $preview ($s.Name+'.png')
    $null=$obj.Chart.Export($png,'PNG');if(-not(Test-Path -LiteralPath $png)){throw 'Chart preview missing'}
   }
   $null=$s.Range('A1').Select()
   $s.PageSetup.Orientation=2;$s.PageSetup.PaperSize=9;$s.PageSetup.Zoom=$false
   $s.PageSetup.FitToPagesWide=1;$s.PageSetup.FitToPagesTall=1
   $s.PageSetup.PrintArea=$(if($s.Name -eq 'r7258差异'){'A31:S46'}else{'A1:L45'})
   $s.ExportAsFixedFormat(0,(Join-Path $preview ($s.Name+'.pdf')))
  }
  $book.Close($false);$book=$null
 }
 Write-Output 'Native Excel: recalc, scenario response/restore, equal return rates, five chart PNGs and six table PDFs complete.'
} finally {
 if($book){$book.Close($false)}
 if($owned){$app.Quit()}
 [Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null
}
