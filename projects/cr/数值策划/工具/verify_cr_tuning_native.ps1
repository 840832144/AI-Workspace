param([Parameter(Mandatory=$true)][string]$Directory)
# 只打开本轮生成文件，不打开任何r7013源或CF历史原表。
$ErrorActionPreference='Stop'
$app=New-Object -ComObject Excel.Application
$book=$null;$owned=$false
try {
 if($app.Workbooks.Count -ne 0){throw 'COM已有用户工作簿，停止'}
 $owned=$true;$app.Visible=$false;$app.DisplayAlerts=$false;$app.AskToUpdateLinks=$false;$app.AutomationSecurity=3
 $file=Join-Path $Directory 'CR_调优候选_vs_CF_POP_数值曲线.xlsx'
 $book=$app.Workbooks.Open($file,0,$false)
 if($book.ReadOnly){throw '候选文件被占用'}
 $book.Worksheets.Item('SRC').Visible=0;$book.Worksheets.Item('CALC_等级').Visible=0
 $names=@('候选总览','VIP_消费门槛','VIP_商城金币','等级_升级消耗','等级_Bet曲线','等级_消耗返还','档位_膨胀','等级_膨胀')
 $ends=@(27,46,47,5031,5031,5031,61,5031);$cols=@('L','G','E','K','G','H','I','E')
 for($i=0;$i -lt $names.Count;$i++){
  $s=$book.Worksheets.Item($names[$i]);$s.Activate();$s.Columns.Item('AZ:BD').Hidden=$true
  $app.ActiveWindow.FreezePanes=$false;$app.ActiveWindow.SplitRow=0;$app.ActiveWindow.SplitColumn=0
  $app.ActiveWindow.ScrollRow=1;$app.ActiveWindow.ScrollColumn=1;$app.ActiveWindow.Zoom=80;$s.Range('A1').Select()
  if($i -gt 0){
   if(-not $s.AutoFilterMode){$null=$s.Range(('A31:'+$cols[$i]+$ends[$i])).AutoFilter()}
   $obj=$s.ChartObjects().Item(1);$box=$s.Range('A7:N27')
   $obj.Left=$box.Left;$obj.Top=$box.Top;$obj.Width=$box.Width;$obj.Height=$box.Height
   $c=$obj.Chart;$c.ChartType=4;$c.PlotVisibleOnly=$false;$c.DisplayBlanksAs=1
   $c.ChartArea.Font.Name='Microsoft YaHei';$c.ChartArea.Font.Size=10;$c.HasLegend=$true;$c.Legend.Position=-4160
   $c.Axes(1).TickLabelSpacing=if($i -in @(3,4,5)){250}elseif($i -eq 7){25}else{1}
   $c.Axes(1).HasMajorGridlines=$false;$c.Axes(2).MinimumScale=0
   $c.Axes(2).HasTitle=$true;$c.Axes(2).AxisTitle.Text=if($i -in @(2,7)){'倍数x'}elseif($i -in @(5,6)){'百分比'}elseif($i -eq 4){'百万金币'}else{'USD'}
   for($j=1;$j -le $c.SeriesCollection().Count;$j++){$ser=$c.SeriesCollection($j);$ser.AxisGroup=1;$ser.Smooth=$false;$ser.MarkerStyle=-4142}
  }
  $s.PageSetup.PrintArea=if($i -eq 0){'$A$1:$L$27'}else{'$A$1:$N$48'}
  $s.PageSetup.Orientation=2;$s.PageSetup.PaperSize=9;$s.PageSetup.Zoom=$false
  $s.PageSetup.FitToPagesWide=1;$s.PageSetup.FitToPagesTall=1
  $s.PageSetup.LeftMargin=12;$s.PageSetup.RightMargin=12;$s.PageSetup.TopMargin=12;$s.PageSetup.BottomMargin=12
 }
 $app.CalculateFullRebuild()
 # 临时改变本候选的拟合锚点来验证尾部门槛公式，随后恢复；不改源表。
 $anchor=$book.Worksheets.Item('SRC').Range('AO7');$before=$anchor.Value2
 $v=$book.Worksheets.Item('VIP_消费门槛');$oldTail=$v.Range('E46').Value2
 $anchor.Value2=$before*2;$app.CalculateFull()
 if([Math]::Abs($v.Range('E46').Value2-$oldTail*2) -gt 1){throw 'VIP拟合公式未响应锚点'}
 $anchor.Value2=$before;$app.CalculateFullRebuild()
 if($v.Range('E46').Value2 -ne $oldTail){throw 'VIP拟合输入恢复失败'}
 if(@($book.LinkSources(1)).Where({$_}).Count -ne 0){throw '非预期外链'}
 foreach($p in @('Author','Last Author','Company','Manager')){try{$book.BuiltinDocumentProperties.Item($p).Value=''}catch{}}
 $book.Worksheets.Item(1).Activate();$book.Save();$book.Close($false);$book=$null
 $book=$app.Workbooks.Open($file,0,$true)
 $preview=Join-Path $Directory 'previews';New-Item -ItemType Directory -Force -Path $preview|Out-Null
 # 逐页导出便于分开读取PDF正文和渲染复核；预览漏绘不能当作源格丢失。
 for($i=0;$i -lt $names.Count;$i++){
  $page=$book.Worksheets.Item($names[$i]);$page.Activate();$null=$page.Range('A1').Select()
  $page.ExportAsFixedFormat(0,(Join-Path $preview ('page-'+($i+1)+'.pdf')))
  if($i -eq 0){continue}
  $p=Join-Path $preview ($names[$i]+'.png');$null=$book.Worksheets.Item($names[$i]).ChartObjects().Item(1).Chart.Export($p,'PNG')
  if(-not (Test-Path -LiteralPath $p) -or (Get-Item -LiteralPath $p).Length -eq 0){throw '图表导出失败'}
 }
 $s=$book.Worksheets.Item('档位_膨胀');$s.PageSetup.PrintArea='$A$30:$I$63'
 $s.ExportAsFixedFormat(0,(Join-Path $preview 'all-price-tiers.pdf'))
 @{recalculation='passed';tail_anchor_response_restore='passed';charts=7;source_workbooks_opened=$false;vip_zero_runtime='not run'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Directory 'native-validation.json') -Encoding utf8
 Write-Output 'Native candidate formula/anchor checks and preview export passed.'
}finally{
 if($book){$book.Close($false)}
 if($owned){$app.Quit()}
 [Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null
}
