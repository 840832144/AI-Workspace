param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference='Stop'
$app=New-Object -ComObject Excel.Application
$book=$null;$owned=$false
try {
 if($app.Workbooks.Count -ne 0){throw '已有用户工作簿，停止'}
 $owned=$true;$app.Visible=$false;$app.DisplayAlerts=$false;$app.AutomationSecurity=3
 $file=Join-Path $Directory 'CR_等级逐级对标及尾部拟合_dev.xlsx'
 $book=$app.Workbooks.Open($file,0,$false)
 if($book.ReadOnly){throw '候选被占用'}
 $src=$book.Worksheets.Item('SRC');$src.Visible=0
 $overview=$book.Worksheets.Item('等级_概览');$detail=$book.Worksheets.Item('等级_明细')
 foreach($s in @($overview,$detail)){$s.Activate();$app.ActiveWindow.FreezePanes=$false;$app.ActiveWindow.SplitRow=0;$app.ActiveWindow.SplitColumn=0;$app.ActiveWindow.ScrollRow=1;$app.ActiveWindow.ScrollColumn=1;$null=$s.Range('A1').Select()}
 if(-not $detail.AutoFilterMode){$null=$detail.Range('A4:L5004').AutoFilter()}
 for($i=1;$i -le 2;$i++){
  $obj=$overview.ChartObjects().Item($i);$box=$overview.Range($(if($i -eq 1){'A6:N26'}else{'A29:N50'}))
  $obj.Left=$box.Left;$obj.Top=$box.Top;$obj.Width=$box.Width;$obj.Height=$box.Height
  $c=$obj.Chart;$c.ChartType=4;$c.PlotVisibleOnly=$false;$c.DisplayBlanksAs=1
  $c.Axes(1).TickLabelSpacing=$(if($i -eq 1){25}else{250});$c.Axes(2).MinimumScale=0
  $c.Axes(1).HasMajorGridlines=$false
  $c.Axes(2).HasTitle=$true;$c.Axes(2).AxisTitle.Text='机器理论净耗 USD'
  $c.HasLegend=$true;$c.Legend.Position=-4160;$c.ChartArea.Font.Name='Microsoft YaHei'
  foreach($ser in $c.SeriesCollection()){$ser.AxisGroup=1;$ser.Smooth=$false;$ser.MarkerStyle=-4142}
 }
 $app.CalculateFullRebuild()
 $slope=$src.Range('S2');$old=$slope.Value2;$point300=$detail.Range('E304').Value2;$point301=$detail.Range('E305').Value2
 $slope.Value2=$old*1.1;$app.CalculateFull()
 if($detail.Range('E304').Value2 -ne $point300 -or $detail.Range('E305').Value2 -le $point301){throw '拟合响应越界或不响应'}
 $slope.Value2=$old;$app.CalculateFullRebuild()
 if($detail.Range('E305').Value2 -ne $point301){throw '拟合输入恢复失败'}
 foreach($p in @('Author','Last Author','Company','Manager')){try{$book.BuiltinDocumentProperties.Item($p).Value=''}catch{}}
 $overview.Activate();$book.Save();$book.Close($false);$book=$app.Workbooks.Open($file,0,$true)
 $p=Join-Path $Directory 'previews';New-Item -ItemType Directory -Force $p|Out-Null
 foreach($s in @($book.Worksheets.Item('等级_概览'),$book.Worksheets.Item('等级_明细'))){$s.PageSetup.Orientation=2;$s.PageSetup.PaperSize=9;$s.PageSetup.Zoom=$false;$s.PageSetup.FitToPagesWide=1;$s.PageSetup.FitToPagesTall=1}
 $s=$book.Worksheets.Item('等级_概览');$s.Activate();$s.PageSetup.PrintArea='$A$1:$N$27';$s.ExportAsFixedFormat(0,(Join-Path $p 'first300.pdf'))
 $s.PageSetup.PrintArea='$A$28:$N$54';$s.ExportAsFixedFormat(0,(Join-Path $p 'full5000.pdf'))
 $s=$book.Worksheets.Item('等级_明细');$s.Activate();$s.PageSetup.PrintTitleRows='$4:$4';$s.PageSetup.PrintArea='$A$290:$L$315';$s.ExportAsFixedFormat(0,(Join-Path $p 'boundary300.pdf'))
 Write-Output 'Native calculation / first300 immutability / tail slope response and restore / previews passed'
} finally {if($book){$book.Close($false)};if($owned){$app.Quit()};[Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null}
