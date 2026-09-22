// TASK-0036: ArtifactJS authoring; controlled outputs only.
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const [directory,mode]=process.argv.slice(2);
const d=JSON.parse(await fs.readFile(path.join(directory,'bet-dev-inputs.json'),'utf8'));
const previews=path.join(directory,'previews');
await fs.mkdir(previews,{recursive:true});
if(mode==='preview-source')for(const [filename,sheetName] of [['SlotsCasinoBetList.xlsx','Sheet1'],['SlotsCasinoBetUnlock.xlsx','Sheet2']]){
 const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(directory,'source',filename)));
 if(mode==='preview-source'){
  const png=await wb.render({sheetName,range:'A1:N10',scale:1.5,format:'png'});
  await fs.writeFile(path.join(previews,filename+'.before.png'),new Uint8Array(await png.arrayBuffer()));
 }
}
if(mode==='preview-source')process.exit(0);
// 本机Artifact导入表回写已证实保留旧公式而只改缓存；配置副本由配套原生Excel步骤精确修改。

const wb=Workbook.create(),over=wb.worksheets.add('概览'),detail=wb.worksheets.add('明细'),src=wb.worksheets.add('SRC');
src.getRange('A1:K1').values=[['等级','升级模式','dev门槛','正式Bet','候选EXP','CR金币/USD','CF原始Spin','CF等级倍率','门槛来源','经验来源','CF来源']];
src.getRange('A2:K5001').values=d.cr.map((v,i)=>[v[0],v[1],v[2],v[12],d.calculations[i].candidate_exp,v[6],i<300?d.cf[i][2]:null,i<300?d.cf[i][3]:null,v[7],v[8],i<300?d.cf[i][5]:'CF仅解锁锚点']);
src.getRange('M1:N7').values=[['CR净损率',d.cr_loss],['CF净损率',d.cf_loss],['CF基础金币/USD',d.cf_base],['CF折扣系数',d.cf_discount],['dev基线revision',d.revision],['CF折扣来源','User确认历史理论消耗的1/6'],['EXP补齐','17锚点保留；中间插值、尾段按末档EXP/Bet延伸']];
for(const s of [over,detail]){
 s.showGridLines=false;s.freezePanes.unfreeze();
 const end=s===detail?5007:d.overview.length+7;
 s.getRange(`A1:K${end}`).format={font:{name:'Microsoft YaHei',size:11,color:'#203449'},columnWidth:17,rowHeight:23};
 for(const c of ['A','G'])s.getRange(`${c}1:${c}${end}`).format.columnWidth=10;
 for(const c of ['B','H'])s.getRange(`${c}1:${c}${end}`).format.columnWidth=22;
 for(const c of ['E','K'])s.getRange(`${c}1:${c}${end}`).format.columnWidth=14;
 s.getRange(`F1:F${end}`).format.columnWidth=4;
 s.getRange('A2').values=[[s===over?'CR 与 Cash Frenzy：等级体验概览':'CR 与 Cash Frenzy：完整逐级明细']];
 s.getRange('A2:K2').format={font:{bold:true,size:16},rowHeight:31};
 s.getRange('A3').values=[['消耗美金为单级升级的模型净耗USD，CF已按User确认乘1/6；不是累计金额或实付账单。']];
 s.getRange('A4').values=[['等级膨胀显示整数倍数，1级=1。CR为整Spin，CF保留小数期望；301级后CF Spin/消耗/膨胀为N/A。']];
 s.getRange('A5').values=[[s===over?'仅列最大Bet变化的解锁等级；完整曲线在表后，逐级数据见明细。':`CR dev r${d.revision}基线＋本次Bet/EXP候选；LevelCfg不改。5000为终点，无下一次升级成本。`]];
 s.getRange('A3:K5').format={font:{size:10,color:'#526477'},rowHeight:22};
 s.getRange('A6:E6').format={fill:'#E6EFF6',font:{bold:true,color:'#1F4E78'}};
 s.getRange('G6:K6').format={fill:'#FDF0D9',font:{bold:true,color:'#986418'}};
 s.getRange('A6').values=[['CR']];s.getRange('G6').values=[['Cash Frenzy']];
 for(const range of ['A7:E7','G7:K7']){
  s.getRange(range).values=[['等级','最大解锁Bet','Spin','消耗美金','等级膨胀']];
  s.getRange(range).format={fill:'#213F59',font:{bold:true,color:'#FFFFFF'},rowHeight:26};
 }
 for(const c of ['A','B','G','H','E','K'])s.getRange(`${c}8:${c}${end}`).setNumberFormat('#,##0');
 for(const c of ['C','I'])s.getRange(`${c}8:${c}${end}`).setNumberFormat('#,##0.00');
 for(const c of ['D','J'])s.getRange(`${c}8:${c}${end}`).setNumberFormat('"$"#,##0.0000');
}
detail.getRange('A8:D5007').formulas=d.cr.map((v,i)=>{
 const r=i+8,t=i+2;return [`=SRC!A${t}`,`=SRC!D${t}`,`=IF(A${r}=5000,"N/A",IF(SRC!B${t}=1,SRC!C${t},ROUNDUP(SRC!C${t}/SRC!E${t},0)))`,`=IF(A${r}=5000,"N/A",B${r}*C${r}/SRC!F${t}*SRC!$N$1)`];
});
detail.getRange('E8:E5007').formulas=d.cr.map((v,i)=>[`=SRC!F${i+2}/SRC!$F$2`]);
detail.getRange('G8:K5007').formulas=d.cr.map((v,i)=>{
 const r=i+8,t=i+2;return [`=SRC!A${t}`,`=SRC!D${t}`,`=IF(G${r}>300,"N/A",SRC!G${t})`,`=IF(G${r}>300,"N/A",H${r}*I${r}*SRC!$N$2/(SRC!$N$3*SRC!H${t})*SRC!$N$4)`,`=IF(G${r}>300,"N/A",SRC!H${t}/SRC!$H$2)`];
});
for(const [start,end,cols]of [['A','E',['A','B','C','D','E']],['G','K',['G','H','I','J','K']]]){
 over.getRange(`${start}8:${end}${d.overview.length+7}`).formulas=d.overview.map(l=>cols.map(c=>`='明细'!${c}${l+7}`));
}
for(const [index,col,other,title,format]of [[0,'B','H','最大解锁Bet（金币）','#,##0'],[1,'C','I','单级升级Spin（CF为原始期望）','0'],[2,'D','J','单级升级净耗USD（CF已乘1/6）','$0.00']]){
 const start=String.fromCharCode(80+index*4),a=String.fromCharCode(81+index*4),b=String.fromCharCode(82+index*4);
 src.getRange(`${start}1:${b}1`).values=[['等级','CR','CF']];
 src.getRange(`${start}2:${b}301`).formulas=d.cf.map((v,i)=>{const r=i+8;return [`=""&'明细'!A${r}`,`='明细'!${col}${r}`,`='明细'!${other}${r}`];});
 const chart=over.charts.add('line',src.getRange(`${start}1:${b}301`));
 const y=d.overview.length+11+index*23;chart.setPosition(`A${y}`,`J${y+21}`);chart.title=title;
 chart.legend={position:'top',textStyle:{typeface:'Microsoft YaHei',fontSize:11}};
 chart.titleTextStyle.fontSize=14;chart.titleTextStyle.typeface='Microsoft YaHei';
 chart.xAxis={axisType:'textAxis',tickLabelInterval:25};chart.yAxis={numberFormatCode:format,numberFormatSourceLinked:false};
 chart.series.items.forEach((s,i)=>{s.line={fill:i?'#D28B21':'#28658F',width:2,style:i?'dashed':'solid'};});
}
wb.recalculate();
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(directory,'CR_CF_等级体验_简表.xlsx'));
console.log(JSON.stringify({authored:1,visibleSheets:['概览','明细'],detailLevels:5000}));
