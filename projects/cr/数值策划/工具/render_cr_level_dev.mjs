// TASK-0036: only LevelCfg.levelUpExp; existing 300 CF levels are never stretched.
import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile,Workbook} from '@oai/artifact-tool';
const [input,out]=process.argv.slice(2),d=JSON.parse(await fs.readFile(input,'utf8'));
const wb=Workbook.create(),overview=wb.worksheets.add('等级_概览'),detail=wb.worksheets.add('等级_明细'),src=wb.worksheets.add('SRC');
src.getRange('A1:O1').values=[['等级','模式','原门槛','EXP/Spin','BetUSD','等级倍率','旧净耗','奖励USD','CF同级/拟合目标','预计Spin','拟议门槛','实际成本','误差','来源类型','源行']];
src.getRange('A2:O5001').values=d.rows;
src.getRange('R1:S5').values=[['300级归一成本',d.anchor],['末段拟合斜率',d.slope],['等级净损率',.05],['dev来源revision',d.source_revision],['拟合窗口','CF250–300；净耗×等级倍率']];
src.getRange('R7:S10').values=[['配置来源','CR dev固定导出 LevelCfg / SlotsCasinoBetList / SlotsCasinoBetUnlock / PriceCheatSheet'],['CF来源','CashRoyal数值.xlsx / cashFrenzy等级 A2:I301'],['旧成本来源','TASK-0036既有已验证曲线缓存'],['编辑位置','LevelCfg / Sheet1 / C5:C5003；5000级终点不改']];
const heads=['CR等级','升级模式','原门槛','原净耗USD','目标净耗USD','预计Spin','候选门槛','实际净耗USD','整数落表误差','原奖励USD','实际返还率','证据类型'];
detail.showGridLines=false;detail.freezePanes.unfreeze();
detail.getRange('A1:L5004').format={font:{name:'Microsoft YaHei',size:10,color:'#24364B'},columnWidth:17,rowHeight:20};
detail.mergeCells('A1:L1');detail.getRange('A1').values=[['等级完整明细：1–300同级原值；301–4999拟合；5000终点']];
detail.getRange('A1:L1').format={fill:'#1F4E78',font:{color:'#FFFFFF',bold:true,size:15},rowHeight:32};
detail.mergeCells('A2:L2');detail.getRange('A2').values=[['目标完全逐级对应；整数Spin后的实际成本与误差分别显示。等级RTP=95%；奖励、Bet与价值倍率不改。']];
detail.getRange('A4:L4').values=[heads];detail.getRange('A4:L4').format={fill:'#D9EAF7',font:{bold:true},rowHeight:32,wrapText:true};
const rows=d.rows.map((v,j)=>{const r=j+5,t=j+2;return [
 `=SRC!A${t}`,`=SRC!B${t}`,`=SRC!C${t}`,`=SRC!G${t}`,
 `=IF(A${r}=5000,"N/A",IF(A${r}<=300,SRC!I${t},(SRC!$S$1+SRC!$S$2*(A${r}-300))/SRC!F${t}))`,
 `=IF(A${r}=5000,"N/A",MAX(1,ROUNDUP(ROUND(E${r}/(SRC!E${t}*SRC!$S$3),10),0)))`,
 `=IF(A${r}=5000,C${r},IF(B${r}=1,F${r},ROUNDUP(ROUND(F${r}*SRC!D${t},10),0)))`,
 `=IF(A${r}=5000,"N/A",IF(B${r}=1,G${r},ROUNDUP(ROUND(G${r}/SRC!D${t},10),0))*SRC!E${t}*SRC!$S$3)`,
 `=IF(A${r}=5000,"N/A",H${r}/E${r}-1)`,`=SRC!H${t}`,`=IF(A${r}=5000,"N/A",J${r}/H${r})`,`=SRC!N${t}`];});
detail.getRange('A5:L5004').formulas=rows;
for(const c of ['D','E','H','J'])detail.getRange(`${c}5:${c}5004`).setNumberFormat('"$"#,##0.0000');
for(const c of ['A','B','C','F','G'])detail.getRange(`${c}5:${c}5004`).setNumberFormat('#,##0');
for(const c of ['I','K'])detail.getRange(`${c}5:${c}5004`).setNumberFormat('0.00%');
overview.showGridLines=false;overview.freezePanes.unfreeze();overview.getRange('A1:N54').format={font:{name:'Microsoft YaHei',size:11,color:'#24364B'},columnWidth:13,rowHeight:22};
for(const row of [1,2,3,4,27,52,53,54])overview.mergeCells(`A${row}:N${row}`);
overview.getRange('A1').values=[['CR等级：已有300级完整对标，后续拟合到5000']];overview.getRange('A1:N1').format={fill:'#1F4E78',font:{size:18,bold:true,color:'#FFFFFF'},rowHeight:36};
overview.getRange('A2').values=[[`CR dev r${d.source_revision}基线；只调整等级升级门槛，VIP暂存，非trunk发布。`]];
overview.getRange('A3').values=[['1–300级目标与CF同级数据一致；原A/B拉伸候选作废。']];
overview.getRange('A4').values=[['整Spin向上取整产生实现误差；目标与实际分开，不声称配置成本逐级零误差。']];
overview.getRange('A27').values=[['301级起仅为拟合：按末段250–300的增长趋势外推，保留CR等级金币倍率；非CF真实5000级。']];
overview.getRange('A52').values=[['最大实际取整偏差（前300级）：'+(d.max_rounding_relative*100).toFixed(4)+'%；同级目标对应300/300。']];
overview.getRange('A53').values=[['返还率=原升级奖励USD÷实际机器理论净耗USD；完整明细、候选门槛及误差见“等级_明细”。']];
overview.getRange('A54').values=[['拟合的归一成本=300级锚点+斜率×(等级−300)；目标净耗=归一成本÷CR现有等级金币倍率。']];
src.getRange('U1:X1').values=[['等级','原CR成本','新目标','新实际']];
src.getRange('U2:X5000').formulas=d.rows.slice(0,4999).map((v,j)=>{const r=j+5;return [`=""&'等级_明细'!A${r}`,`='等级_明细'!D${r}`,`='等级_明细'!E${r}`,`='等级_明细'!H${r}`];});
for(const [end,title,start,finish] of [[301,'前300级：目标同级对标与实际落表','A6','N26'],[5000,'完整升级成本：同级对标＋尾部拟合','A29','N50']]){
 const chart=overview.charts.add('line',src.getRange(`U1:X${end}`));chart.title=title;chart.setPosition(start,finish);chart.legend={position:'top'};
 chart.xAxis={axisType:'textAxis',tickLabelInterval:end===301?25:250};chart.yAxis={numberFormatCode:'$#,##0.00',numberFormatSourceLinked:false};
 chart.series.items.forEach((s,k)=>{s.line={fill:['#7F8FA6','#D77A22','#287D55'][k],width:2,style:k===2?'dashed':'solid'};});
}
wb.recalculate();await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,'CR_等级逐级对标及尾部拟合_dev.xlsx'));
const cfg=await SpreadsheetFile.importXlsx(await FileBlob.load(d.source));
cfg.worksheets.getItem('Sheet1').getRange('C5:C5003').values=d.rows.slice(0,4999).map(r=>[r[10]]);
await fs.mkdir(path.join(out,'candidate'),{recursive:true});await (await SpreadsheetFile.exportXlsx(cfg)).save(path.join(out,'candidate','LevelCfg.xlsx'));
console.log('Authored level curve and LevelCfg only; VIP untouched');
