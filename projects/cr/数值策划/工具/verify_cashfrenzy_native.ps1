param([Parameter(Mandatory=$true)][string]$Directory)
# 只打开新生成的受控Excel；补齐Artifact未提供的隐藏/打印选项并验证原生重算。
$ErrorActionPreference='Stop'
$app=New-Object -ComObject Excel.Application
$book=$null;$owned=$false
try {
    if($app.Workbooks.Count -ne 0){throw 'COM实例已有工作簿，停止以保护用户会话'}
    $owned=$true
    $app.Visible=$false;$app.DisplayAlerts=$false;$app.AskToUpdateLinks=$false;$app.AutomationSecurity=3
    $file=Join-Path $Directory 'CashFrenzy_数值曲线对照.xlsx'
    $book=$app.Workbooks.Open($file,0,$false)
    if($book.ReadOnly){throw '交付文件正在被占用；未改只读文件'}
    $src=$book.Worksheets.Item('SRC_CashFrenzy');$src.Visible=0
    $checks=@()
    foreach($name in @('VIP_消费门槛','VIP_膨胀系数','等级_升级消耗','等级_Bet曲线','等级_升级消耗返还')){
        $s=$book.Worksheets.Item($name);$s.Activate()
        $s.Columns.Item('AA:AC').Hidden=$true
        $app.ActiveWindow.FreezePanes=$false;$app.ActiveWindow.SplitRow=0;$app.ActiveWindow.SplitColumn=0
        $app.ActiveWindow.ScrollRow=1;$app.ActiveWindow.ScrollColumn=1;$app.ActiveWindow.Zoom=85
        $s.Range('A1').Select()
        $c=$s.ChartObjects().Item(1).Chart
        $c.PlotVisibleOnly=$false;$c.DisplayBlanksAs=1;$c.ChartType=4
        $c.ChartArea.Font.Name='Microsoft YaHei';$c.ChartArea.Font.Size=10
        $c.HasLegend=($name -eq '等级_Bet曲线')
        for($i=1;$i -le $c.SeriesCollection().Count;$i++){
            $series=$c.SeriesCollection($i);$series.Smooth=$false;$series.AxisGroup=1
            $series.MarkerStyle=if($name.StartsWith('VIP')){8}else{-4142}
        }
        $c.Axes(1).TickLabelSpacing=if($name.StartsWith('VIP')){1}else{25}
        $c.Axes(1).HasMajorGridlines=$false;$c.Axes(1).HasMinorGridlines=$false
        $c.Axes(2).MinimumScale=0
        if($name -eq '等级_Bet曲线'){$c.Axes(2).HasTitle=$true;$c.Axes(2).AxisTitle.Text='百万金币'}
        $last=if($name.StartsWith('VIP')){13}else{305}
        $lastCol=if($name -eq '等级_Bet曲线'){'F'}elseif($name -eq 'VIP_消费门槛'){'C'}else{'D'}
        if(-not $s.AutoFilterMode){$s.Range(('A5:'+ $lastCol + $last)).AutoFilter() | Out-Null}
        $s.PageSetup.PrintArea='$A$1:$R$28';$s.PageSetup.Orientation=2
        $s.PageSetup.PaperSize=9;$s.PageSetup.Zoom=$false
        $s.PageSetup.FitToPagesWide=1;$s.PageSetup.FitToPagesTall=1
        $s.PageSetup.LeftMargin=12;$s.PageSetup.RightMargin=12;$s.PageSetup.TopMargin=12;$s.PageSetup.BottomMargin=12
        $s.PageSetup.CenterHorizontally=$true
        $checks+=@{sheet=$name;charts=$s.ChartObjects().Count;series=$c.SeriesCollection().Count;freeze=$app.ActiveWindow.FreezePanes}
    }
    $app.CalculateFullRebuild()
    # 临时修改生成包内CF价值驱动，验证成本/奖励/$1等值和返还率依赖；随后还原。
    $driver=$src.Range('O4');$original=$driver.Value2
    $cost=$book.Worksheets.Item('等级_升级消耗').Range('B15')
    $rec=$book.Worksheets.Item('等级_Bet曲线').Range('D15')
    $ret=$book.Worksheets.Item('等级_升级消耗返还').Range('B15')
    $beforeCost=$cost.Value2;$beforeRec=$rec.Value2;$beforeRet=$ret.Value2
    $driver.Value2=$original*2;$app.CalculateFull()
    if([Math]::Abs($cost.Value2*2-$beforeCost) -gt 0.000001 -or [Math]::Abs($rec.Value2-$beforeRec*2) -gt 0.000001 -or [Math]::Abs($ret.Value2-$beforeRet) -gt 0.000001){throw 'CF价值驱动依赖验证失败'}
    $driver.Value2=$original;$app.CalculateFullRebuild()
    if(@($book.LinkSources(1)).Where({$_}).Count -ne 0){throw '发现非预期外链'}
    foreach($name in @('Author','Last Author','Company','Manager')){try{$book.BuiltinDocumentProperties.Item($name).Value=''}catch{}}
    $book.Worksheets.Item(1).Activate();$book.Save()
    $preview=Join-Path $Directory 'previews';New-Item -ItemType Directory -Force -Path $preview|Out-Null
    foreach($item in $checks){
        $c=$book.Worksheets.Item($item.sheet).ChartObjects().Item(1).Chart
        $image=Join-Path $preview ($item.sheet+'.png')
        $null=$c.Export($image,'PNG')
        # 本机COM可能返回空值，但文件已成功生成；按实际产物检查，随后解码/视觉验收。
        if(-not (Test-Path -LiteralPath $image) -or (Get-Item -LiteralPath $image).Length -eq 0){throw '原生图表导出失败'}
    }
    $book.ExportAsFixedFormat(0,(Join-Path $preview 'five-sheets.pdf'))
    @{application=$app.Name;version=$app.Version;native_recalculation='passed';driver_change_restored='passed';sheets=$checks} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $Directory 'native-validation.json') -Encoding utf8
    Write-Output 'Native recalculation, driver restore, 5 line charts and 0 external links verified.'
} finally {
    if($book){$book.Close($false)}
    if($owned){$app.Quit()}
    [Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null
}
