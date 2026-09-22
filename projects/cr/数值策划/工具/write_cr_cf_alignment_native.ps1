param([Parameter(Mandatory=$true)][string]$Directory,[switch]$ReportOnly)
$ErrorActionPreference='Stop'
$d=Get-Content -LiteralPath (Join-Path $Directory 'alignment-inputs.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$app=New-Object -ComObject Excel.Application;$book=$null;$owned=$false
function Values($rows,$width){$a=New-Object 'object[,]' $rows.Count,$width;for($i=0;$i -lt $rows.Count;$i++){for($j=0;$j -lt $width;$j++){$v=$rows[$i][$j];$a[$i,$j]=$(if($null -eq $v){$null}elseif($v -is [string]){$v}else{[double]$v})}};return ,$a}
try {
 if($app.Workbooks.Count -ne 0){throw 'Existing user workbook; stop'}
 $owned=$true;$app.Visible=$false;$app.DisplayAlerts=$false;$app.AutomationSecurity=3
 $candidate=Join-Path $Directory 'candidate';New-Item -ItemType Directory -Force $candidate|Out-Null
 if(-not $ReportOnly){foreach($name in @('LevelCfg','SlotsCasinoBetList','SlotsCasinoBetUnlock','SlotsCasinoBetShow','PriceCheatSheet')){
  $target=Join-Path $candidate ($name+'.xlsx');Copy-Item -LiteralPath (Join-Path (Join-Path $Directory 'source') ($name+'.xlsx')) -Destination $target
  $book=$app.Workbooks.Open($target,0,$false);if($book.ReadOnly){throw 'Candidate locked'}
  $sheet=$book.Worksheets.Item(1)
  if($name -eq 'SlotsCasinoBetUnlock'){
   $sheet.Range("A5:AA$($sheet.UsedRange.Rows.Count)").ClearContents();$last=$d.unlock_rows.Count+4
   $sheet.Range("A5:AA$last").Value2=(Values $d.unlock_rows 27)
  }elseif($name -eq 'LevelCfg'){
   $a=New-Object 'object[,]' 4999,1
   for($i=0;$i -lt 4999;$i++){$a[$i,0]=[double]$d.rows[$i][3]}
   $sheet.Range('C5:C5003').Value2=$a
  }elseif($name -eq 'PriceCheatSheet'){
   $last=$sheet.UsedRange.Rows.Count;$a=$sheet.Range("E5:T$last").Value2
   foreach($change in $d.changes.$name){$address=$change[1];$r=[int]($address -replace '\D','');$letters=$address -replace '\d','';$c=0;foreach($ch in $letters.ToCharArray()){$c=$c*26+[int]$ch-64};$a[($r-4),($c-4)]=[double]$change[3]}
   $sheet.Range("E5:T$last").Value2=$a
  }else{foreach($change in $d.changes.$name){$sheet.Range($change[1]).Value2=[double]$change[3]}}
  $app.CalculateFullRebuild();$book.Save();$book.Close($false);$book=$null
 }}
 $book=$app.Workbooks.Open((Join-Path $Directory 'CR_CF_等级对齐候选_5000级.xlsx'),0,$false)
 if($book.ReadOnly){throw 'Report locked'}
 $preview=Join-Path $Directory 'previews';New-Item -ItemType Directory -Force $preview|Out-Null
 foreach($s in $book.Worksheets){
  if($s.Name -in @('SRC','CALC')){$s.Visible=0;continue}
  $s.Activate();$app.ActiveWindow.FreezePanes=$false;$app.ActiveWindow.SplitRow=0;$app.ActiveWindow.SplitColumn=0
  $app.ActiveWindow.ScrollRow=1;$app.ActiveWindow.ScrollColumn=1;$app.ActiveWindow.Zoom=85;$s.Columns('AA:AZ').Hidden=$true
  if($s.Name -eq '等级_明细'){$null=$s.Range('A7:O5007').AutoFilter()}
  if($s.Name -eq '等级_概览'){$null=$s.Range("A7:O$($d.overview.Count+7)").AutoFilter()}
  for($i=1;$i -le $s.ChartObjects().Count;$i++){
   $c=$s.ChartObjects().Item($i).Chart;$c.ChartType=4;$c.PlotVisibleOnly=$false;$c.DisplayBlanksAs=1;$c.Axes(1).HasMajorGridlines=$false
   $c.Axes(1).TickLabelSpacing=$(if($s.Name -eq '商城档位'){3}elseif($i -eq 4){250}else{25});$c.Axes(2).MinimumScale=0
   $c.HasLegend=$true;$c.Legend.Position=-4160;$c.ChartArea.Font.Name='Microsoft YaHei'
   foreach($se in $c.SeriesCollection()){$se.AxisGroup=1;$se.Smooth=$false;$se.MarkerStyle=-4142}
  }
 }
 $app.CalculateFullRebuild()
 $src=$book.Worksheets.Item('SRC');$detail=$book.Worksheets.Item('等级_明细');$old=$src.Range('AB5').Value2;$before=$detail.Range('D57').Value2
 $src.Range('AB5').Value2=$old*2;$app.CalculateFull()
 if([Math]::Abs($detail.Range('D57').Value2-$before/2) -gt 1e-8){throw 'USD driver response failed'}
 $src.Range('AB5').Value2=$old;$app.CalculateFullRebuild()
 if([Math]::Abs($detail.Range('D57').Value2-$before) -gt 1e-8){throw 'Restore failed'}
 foreach($p in @('Author','Last Author','Company','Manager')){try{$book.BuiltinDocumentProperties.Item($p).Value=''}catch{}}
 $book.Worksheets.Item(1).Activate();$book.Save()
 foreach($s in $book.Worksheets){
  if($s.Visible -ne -1){continue};$s.Activate()
  for($i=1;$i -le $s.ChartObjects().Count;$i++){$obj=$s.ChartObjects().Item($i);$null=$obj.Activate();$null=$obj.Chart.Export((Join-Path $preview ($s.Name+"-$i.png")),'PNG')}
  $null=$s.Range('A1').Select();$s.PageSetup.Orientation=2;$s.PageSetup.PaperSize=9;$s.PageSetup.Zoom=$false;$s.PageSetup.FitToPagesWide=1;$s.PageSetup.FitToPagesTall=1
  $s.PageSetup.PrintArea=$(if($s.Name -eq '候选说明'){'A1:C18'}elseif($s.Name -eq '商城档位'){'A1:L37'}else{'A1:O24'})
  $s.ExportAsFixedFormat(0,(Join-Path $preview ($s.Name+'.pdf')))
 }
 Write-Output 'Controlled candidate copies and report recalc/response/restore/previews completed; no SVN operations.'
}finally{if($book){$book.Close($false)};if($owned){$app.Quit()};[Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null}
