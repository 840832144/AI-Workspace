param([Parameter(Mandatory=$true)][string]$Directory)
# 仅打开新合并表。旧CR/CF文件不打开、不重算、不保存。
$ErrorActionPreference='Stop';$app=New-Object -ComObject Excel.Application
$book=$null;$owned=$false
try{
 if($app.Workbooks.Count -ne 0){throw 'COM已有用户工作簿，停止'}
 $owned=$true;$app.Visible=$false;$app.DisplayAlerts=$false;$app.AskToUpdateLinks=$false;$app.AutomationSecurity=3
 $book=$app.Workbooks.Open((Join-Path $Directory 'CR_vs_CashFrenzy_数值曲线对照.xlsx'),0,$false)
 if($book.ReadOnly){throw '输出被占用，停止'}
 $book.Worksheets.Item('SRC_CR').Visible=0;$book.Worksheets.Item('SRC_CF').Visible=0
 $names=@('VIP_消费门槛','VIP_膨胀系数','等级_升级消耗','等级_Bet曲线','等级_升级消耗返还')
 $ends=@(46,47,5030,5031,5030);$columns=@('K','F','G','K','G')
 for($i=0;$i -lt 5;$i++){
  $s=$book.Worksheets.Item($names[$i]);$s.Activate();$s.Columns.Item('W:AA').Hidden=$true
  $app.ActiveWindow.FreezePanes=$false;$app.ActiveWindow.SplitRow=0;$app.ActiveWindow.SplitColumn=0
  $app.ActiveWindow.ScrollRow=1;$app.ActiveWindow.ScrollColumn=1;$app.ActiveWindow.Zoom=80;$s.Range('A1').Select()
  if(-not $s.AutoFilterMode){$null=$s.Range(('A31:'+$columns[$i]+$ends[$i])).AutoFilter()}
  $obj=$s.ChartObjects().Item(1);$box=$s.Range('A7:N27')
  $obj.Left=$box.Left;$obj.Top=$box.Top;$obj.Width=$box.Width;$obj.Height=$box.Height
  $c=$obj.Chart;$c.ChartType=4;$c.PlotVisibleOnly=$false;$c.DisplayBlanksAs=1
  $c.ChartArea.Font.Name='Microsoft YaHei';$c.ChartArea.Font.Size=10;$c.HasLegend=$true;$c.Legend.Position=-4160
  $c.Axes(1).TickLabelSpacing=if($i -lt 2){1}else{25}
  $c.Axes(1).HasMajorGridlines=$false;$c.Axes(1).HasMinorGridlines=$false;$c.Axes(2).MinimumScale=0
  $c.Axes(2).HasTitle=$true;$c.Axes(2).AxisTitle.Text=if($i -eq 1){'倍数x'}elseif($i -eq 4){'百分比'}elseif($i -eq 3){'百万金币'}else{'USD'}
  if($i -eq 1){$c.Axes(2).TickLabels.NumberFormat='0.0"x"';$s.Range('B32:C47').NumberFormat='0.00"x"'}
  if($i -eq 2){$s.Range(('B32:G'+$ends[$i])).NumberFormat='"$"#,##0.0000;[Red]("$"#,##0.0000);"$"0.0000'}
  if($i -eq 4){$s.Range(('D32:G'+$ends[$i])).NumberFormat='"$"#,##0.0000;[Red]("$"#,##0.0000);"$"0.0000'}
  for($j=1;$j -le $c.SeriesCollection().Count;$j++){
   $series=$c.SeriesCollection($j);$series.AxisGroup=1;$series.Smooth=$false;$series.MarkerStyle=-4142
  }
  $s.PageSetup.PrintArea='$A$1:$N$48';$s.PageSetup.Orientation=2;$s.PageSetup.PaperSize=9
  $s.PageSetup.Zoom=$false;$s.PageSetup.FitToPagesWide=1;$s.PageSetup.FitToPagesTall=1
  $s.PageSetup.LeftMargin=12;$s.PageSetup.RightMargin=12;$s.PageSetup.TopMargin=12;$s.PageSetup.BottomMargin=12
 }
 $app.CalculateFullRebuild()
 $vip=$book.Worksheets.Item($names[0]);$inflation=$book.Worksheets.Item($names[1])
 # 固定分析汇率，无可编辑输入；只读验证新公式的两条USD边界。
 if($book.Worksheets.Item('SRC_CF').Range('X5').Value2 -ne 0.78408){throw '固定汇率错误'}
 for($r=32;$r -le 38;$r++){
  if([Math]::Abs($vip.Range("G$r").Value2-$vip.Range("E$r").Value2*0.78408) -gt 0.000001 -or [Math]::Abs($vip.Range("H$r").Value2-$vip.Range("F$r").Value2*0.78408) -gt 0.000001){throw '固定汇率换算失败'}
  if($vip.Range("C$r").Value2 -ne ('VIP'+($r-31))){throw 'CF前台标签错误'}
 }
 if($inflation.Range('B47').Value2 -ne 2.5 -or $inflation.Range('C39').Value2 -ne 40){throw '商城金币倍率错误'}
 $preview=Join-Path $Directory 'previews';New-Item -ItemType Directory -Force -Path $preview|Out-Null
 if(@($book.LinkSources(1)).Where({$_}).Count -ne 0){throw '非预期外链'}
 foreach($p in @('Author','Last Author','Company','Manager')){try{$book.BuiltinDocumentProperties.Item($p).Value=''}catch{}}
 $book.Worksheets.Item(1).Activate();$book.Save()
 # 重新只读打开已保存输出，让原生打印引擎刷新首次调整尺寸后的图表布局。
 $book.Close($false);$book=$null
 $book=$app.Workbooks.Open((Join-Path $Directory 'CR_vs_CashFrenzy_数值曲线对照.xlsx'),0,$true)
 foreach($n in $names){
  $file=Join-Path $preview ($n+'.png');$null=$book.Worksheets.Item($n).ChartObjects().Item(1).Chart.Export($file,'PNG')
  if(-not (Test-Path -LiteralPath $file) -or (Get-Item -LiteralPath $file).Length -eq 0){throw '图像导出失败'}
 }
 $book.ExportAsFixedFormat(0,(Join-Path $preview 'five-sheets.pdf'))
 @{native_recalculation='passed';fixed_fx_bounds='passed';shop_coin_multipliers='passed';CF_labels='VIP1-VIP7';fx_delivered=0.78408;old_workbooks_opened=$false;charts=5} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Directory 'native-validation.json') -Encoding utf8
 Write-Output 'Native comparison checks passed; fixed FX, shop multipliers and labels verified; original models untouched.'
}finally{
 if($book){$book.Close($false)}
 if($owned){$app.Quit()}
 [Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null
}
