param([Parameter(Mandatory=$true)][string]$Directory,[switch]$ReportOnly)
$ErrorActionPreference='Stop'
$app=New-Object -ComObject Excel.Application
$book=$null;$owned=$false
try {
 if($app.Workbooks.Count -ne 0){throw 'Existing user workbook; stop'}
 $owned=$true;$app.Visible=$false;$app.DisplayAlerts=$false;$app.AutomationSecurity=3
 # Artifact在此导入文件的编辑回写中保留旧公式；仅缺失的配置精确编辑能力使用原生Excel。
 $data=Get-Content -LiteralPath (Join-Path $Directory 'bet-dev-inputs.json') -Raw -Encoding UTF8 | ConvertFrom-Json
 $candidate=Join-Path $Directory 'candidate';New-Item -ItemType Directory -Force $candidate | Out-Null
 if(-not $ReportOnly){foreach($name in @('SlotsCasinoBetList.xlsx','SlotsCasinoBetUnlock.xlsx')){
  $destination=Join-Path $candidate $name
  Copy-Item -LiteralPath (Join-Path (Join-Path $Directory 'source') $name) -Destination $destination
  $book=$app.Workbooks.Open($destination,0,$false)
  if($book.ReadOnly){throw 'Config candidate is locked'}
  if($name -eq 'SlotsCasinoBetList.xlsx'){
   $s=$book.Worksheets.Item('Sheet1')
   foreach($c in $data.candidates){
    if($c.proposed_exp -ne $c.current_exp){$s.Range(($c.source_cell -split '!')[1]).Value2=[double]$c.proposed_exp}
   }
  } else {
   $s=$book.Worksheets.Item('Sheet2');$count=$data.unlock_rows.Count-4
   $values=New-Object 'object[,]' $count,27
   for($i=0;$i -lt $count;$i++){for($j=0;$j -lt 27;$j++){
    $v=$data.unlock_rows[$i+4][$j]
    $values[$i,$j]=$(if($null -eq $v){$null}elseif($v -is [string]){$v}else{[double]$v})
   }}
   $s.Range("A5:AA$($data.unlock_rows.Count)").Value2=$values
  }
  $app.CalculateFullRebuild();$book.Save();$book.Close($false);$book=$null
 }}
 $file=Join-Path $Directory 'CR_CF_等级体验_简表.xlsx'
 $book=$app.Workbooks.Open($file,0,$false)
 if($book.ReadOnly){throw 'Output workbook is locked'}
 $receipt=Join-Path $Directory 'svn-result.json'
 if(Test-Path -LiteralPath $receipt){
  $result=Get-Content -LiteralPath $receipt -Raw -Encoding UTF8 | ConvertFrom-Json
  $book.Worksheets.Item(1).Range('A5').Value2="dev r$($result.committed_revision)；按Bet、金币价值及模式变化点列示，完整曲线在表后，逐级数据见明细。"
  $book.Worksheets.Item(2).Range('A5').Value2="CR dev r$($result.committed_revision)已提交Bet/EXP；LevelCfg不改。5000为终点，无下一次升级成本。"
 }
 $src=$book.Worksheets.Item('SRC');$src.Visible=0
 foreach($s in $book.Worksheets){
  if($s.Visible -ne -1){continue}
  $s.Activate();$app.ActiveWindow.FreezePanes=$false;$app.ActiveWindow.SplitRow=0;$app.ActiveWindow.SplitColumn=0
  $app.ActiveWindow.ScrollRow=1;$app.ActiveWindow.ScrollColumn=1;$null=$s.Range('A1').Select()
  $last=$(if($s.Index -eq 2){5007}else{$data.overview.Count+7})
  $s.Range("C8:D$last").HorizontalAlignment=-4152;$s.Range("H8:I$last").HorizontalAlignment=-4152
  $null=$s.Range("A7:D$last").AutoFilter()
  for($i=1;$i -le $s.ChartObjects().Count;$i++){
   $c=$s.ChartObjects().Item($i).Chart;$c.ChartType=4;$c.PlotVisibleOnly=$false;$c.DisplayBlanksAs=1
   $c.Axes(1).TickLabelSpacing=25;$c.Axes(1).HasMajorGridlines=$false;$c.Axes(2).MinimumScale=0
   $c.ChartArea.Font.Name='Microsoft YaHei';$c.HasLegend=$true;$c.Legend.Position=-4160
   foreach($series in $c.SeriesCollection()){$series.AxisGroup=1;$series.Smooth=$false;$series.MarkerStyle=-4142}
  }
 }
 $app.CalculateFullRebuild()
 $detail=$book.Worksheets.Item(2);$driver=$src.Range('N4');$old=$driver.Value2;$before=$detail.Range('I57').Value2
 $driver.Value2=$old*2;$app.CalculateFull()
 if([Math]::Abs($detail.Range('I57').Value2-$before*2) -gt 0.0000001){throw 'CF discount formula did not respond'}
 $driver.Value2=$old;$app.CalculateFullRebuild()
 if([Math]::Abs($detail.Range('I57').Value2-$before) -gt 0.0000001){throw 'CF discount restore failed'}
 foreach($p in @('Author','Last Author','Company','Manager')){try{$book.BuiltinDocumentProperties.Item($p).Value=''}catch{}}
 $over=$book.Worksheets.Item(1);$over.Activate();$book.Save()
 $previews=Join-Path $Directory 'previews'
 for($i=1;$i -le $over.ChartObjects().Count;$i++){
  $obj=$over.ChartObjects().Item($i);$null=$obj.Activate();$png=Join-Path $previews "comparison-$i.png"
  $null=$obj.Chart.Export($png,'PNG');if(-not(Test-Path -LiteralPath $png)){throw 'Chart export missing'}
 }
 foreach($view in @(@(1,'A1:I28','overview'),@(2,'A297:I317','boundary300'),@(2,'A4990:I5007','terminal5000'))){
  $s=$book.Worksheets.Item($view[0]);$s.Activate();$s.PageSetup.Orientation=2;$s.PageSetup.PaperSize=9
  $s.PageSetup.Zoom=$false;$s.PageSetup.FitToPagesWide=1;$s.PageSetup.FitToPagesTall=1;$s.PageSetup.PrintArea=$view[1]
  $s.ExportAsFixedFormat(0,(Join-Path $previews ($view[2]+'.pdf')))
 }
 Write-Output 'Native recalc, CF discount response/restore, 3 charts and 3 table PDF views completed.'
} finally {
 if($book){$book.Close($false)}
 if($owned){$app.Quit()}
 [Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null
}
