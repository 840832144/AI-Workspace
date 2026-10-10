// node <本脚本的受控副本> <cf-inputs.json> <受控输出目录>
// 仅输入CF白名单快照；计算使用本工作簿公式。原生显示/缓存由配套验收脚本核验。
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const [input, dir] = process.argv.slice(2);
const d = JSON.parse(await fs.readFile(input, 'utf8'));
const names=['VIP_消费门槛','VIP_膨胀系数','等级_升级消耗','等级_Bet曲线','等级_升级消耗返还'];
const wb=Workbook.create();
for(const n of [...names,'SRC_CashFrenzy']) wb.worksheets.add(n);
const src=wb.worksheets.getItem('SRC_CashFrenzy');
src.getRange('A1').values=[['来源：'+d.source+'；历史资料，游戏采样日期/版本未标注']];
src.getRange('A2').values=[['主表仅 cashFrenzy等级；VIP仅 vip加成!F:I。原文件修改元数据：'+d.source_modified_metadata+'（非游戏版本）']];
src.getRange('A5:I5').values=[['等级','模型Bet','历史Spin','升级金币奖励','价值倍率','原缓存消耗USD','原缓存奖励USD','原缓存返还率','原始来源坐标']];
src.getRange('A6:I305').values=d.levels.map(r=>r.slice(0,5).concat(r.slice(7)));
src.getRange('N2:P5').values=[['驱动','值','来源'],['历史抽水',d.rake,'cashFrenzy等级!X2'],['基础金币/USD',d.coins_per_usd,'cashFrenzy等级!Y2'],['百万缩放',1e6,'单位换算']];
src.getRange('N10:Q10').values=[['VIP','原表经验（累计属性未注明）','点/USD（来自原公式分母）','来源坐标']];
src.getRange('N11:Q18').values=d.vip;
src.getRange('N21').values=[['来源缺口']];
src.getRange('N22:N27').values=d.gaps.map(g=>[g]);
src.getRange('N31:P31').values=[['解锁等级','普通Bet','来源坐标']];
src.getRange(`N32:P${31+d.unlocks.length}`).values=d.unlocks;
src.showGridLines=false;

const titles=['消费门槛（美金） / VIP等级','膨胀系数（百分比） / VIP等级','升级消耗美金 / 等级','最大Bet & 推荐Bet（$1等值） / 等级','升级消耗返还 / 等级'];
const notes=[
 ['仅VIP0/1可明确累计门槛。VIP2–7经验未注明累计或本级，相关结果为N/A。','缺口：原资料需补累计属性。历史经验及点/美元公式保留在隐藏来源页。'],
 ['绝对膨胀＝当前VIP累计门槛 / VIP1累计门槛。VIP1＝100%，VIP0＝0%。','VIP2–7累计门槛未确认，指数为N/A；不计算相邻环比，不用金币加成替代。'],
 ['历史抽水折算消耗＝原表Bet × Spin × 抽水 /（基础金币每美元 × 等级倍率）。','按原模型完整保留1–300级。不是实付金额；净成本扣除本级可美元化的金币奖励。'],
 ['普通Bet上限须主表与解锁表一致；15–19、250–300级冲突为N/A。highroller条件未明。','$1等值为历史金币价值逆换算，未取整到可下注档。两条线统一用百万金币；缺口不连线。'],
 ['升级返还率＝本级金币奖励USD / 本级历史抽水折算升级消耗USD。','分母直接引用升级消耗页。仅计来源可估值的金币奖励；完整保留1–300级。']
];
const headers=[['VIP等级','累计消费门槛\n（USD）','本级新增消费\n（USD）'],
 ['VIP等级','绝对膨胀系数\n（VIP1=100%）','累计消费门槛\n（USD）','本级新增消费\n（USD）'],
 ['等级','历史抽水折算\n升级消耗（USD）','升级奖励\n（USD）','升级净成本\n（USD）'],
 ['等级','最大Bet\n（普通档金币）','最大Bet\n（百万金币）','$1等值推荐Bet\n（金币）','$1等值推荐Bet\n（百万金币）','最大Bet\n折算USD'],
 ['等级','升级消耗返还率','历史抽水折算\n升级消耗（USD）','升级奖励\n（USD）']];
const usd='"$"#,##0.00;[Red]("$"#,##0.00);"$"0.00';
for(let i=0;i<names.length;i++){
 const s=wb.worksheets.getItem(names[i]), end=i<2?13:305, cols=headers[i].length;
 const last=String.fromCharCode(64+cols);
 s.showGridLines=false;s.freezePanes.unfreeze();s.tabColor='#1F4E78';
 s.getRange(`A1:R${Math.max(end,32)}`).format={font:{name:'Microsoft YaHei',size:10,color:'#24364B'},rowHeight:20,columnWidth:11,verticalAlignment:'center'};
 s.getRange(`B1:${last}${end}`).format.columnWidth=21;
 for(const r of [1,2,3])s.mergeCells(`A${r}:R${r}`);
 s.getRange('A1').values=[['Cash Frenzy  '+titles[i]]];
 s.getRange('A1:R1').format={fill:'#1F4E78',font:{name:'Microsoft YaHei',size:16,bold:true,color:'#FFFFFF'},rowHeight:34};
 s.getRange('A2').values=[[notes[i][0]]];s.getRange('A3').values=[[notes[i][1]]];
 s.getRange('A2:R3').format={font:{name:'Microsoft YaHei',size:10,color:'#44546A'},rowHeight:27,wrapText:true};
 s.getRange(`A5:${last}5`).values=[headers[i]];
 s.getRange(`A5:${last}5`).format={fill:'#D9EAF7',font:{bold:true,color:'#17365D'},rowHeight:44,wrapText:true,horizontalAlignment:'center'};
 s.getRange(`A6:${last}${end}`).format.horizontalAlignment='right';
 s.getRange(`B6:${last}${end}`).setNumberFormat(usd);
 const rows=[];
 for(let r=6;r<=end;r++){
  const lv=r-6,vsrc=11+lv;
  if(i===0)rows.push([`='SRC_CashFrenzy'!N${vsrc}`,lv<2?`='SRC_CashFrenzy'!O${vsrc}/'SRC_CashFrenzy'!P${vsrc}`:'N/A',lv<2?(lv===0?`=B${r}`:`=B${r}-B${r-1}`):'N/A']);
  if(i===1)rows.push([`='${names[0]}'!A${r}`,lv<2?`=C${r}/$C$7`:'N/A',`='${names[0]}'!B${r}`,`='${names[0]}'!C${r}`]);
  if(i===2)rows.push([`='SRC_CashFrenzy'!A${r}`,`='SRC_CashFrenzy'!B${r}*'SRC_CashFrenzy'!C${r}*'SRC_CashFrenzy'!$O$3/('SRC_CashFrenzy'!$O$4*'SRC_CashFrenzy'!E${r})`,`='SRC_CashFrenzy'!D${r}/('SRC_CashFrenzy'!$O$4*'SRC_CashFrenzy'!E${r})`,`=B${r}-C${r}`]);
  if(i===3)rows.push([`='SRC_CashFrenzy'!A${r}`,`=IF('SRC_CashFrenzy'!B${r}=VLOOKUP(A${r},'SRC_CashFrenzy'!$N$32:$O$${31+d.unlocks.length},2,TRUE),'SRC_CashFrenzy'!B${r},"N/A")`,`=IF(ISNUMBER(B${r}),B${r}/'SRC_CashFrenzy'!$O$5,"N/A")`,`='SRC_CashFrenzy'!$O$4*'SRC_CashFrenzy'!E${r}`,`=D${r}/'SRC_CashFrenzy'!$O$5`,`=IF(ISNUMBER(B${r}),B${r}/D${r},"N/A")`]);
  if(i===4)rows.push([`='${names[2]}'!A${r}`,`=D${r}/C${r}`,`='${names[2]}'!B${r}`,`='${names[2]}'!C${r}`]);
 }
 for(let c=0;c<cols;c++){
  const col=String.fromCharCode(65+c);
  s.getRange(`${col}6:${col}${end}`).values=rows.map(r=>[r[c].startsWith('=')?null:r[c]]);
  // 按连续公式段写入，保留显式N/A文本。
  for(let r=0;r<rows.length;){
   if(!rows[r][c].startsWith('=')){r++;continue;}
   const start=r, formulas=[];
   while(r<rows.length&&rows[r][c].startsWith('='))formulas.push([rows[r++][c]]);
   s.getRange(`${col}${start+6}:${col}${r+5}`).formulas=formulas;
  }
 }
 s.getRange(`A6:A${end}`).setNumberFormat('0');
 if(i===1||i===4)s.getRange(`B6:B${end}`).setNumberFormat('0.0%');
 if(i===3){s.getRange(`B6:B${end}`).setNumberFormat('#,##0');s.getRange(`D6:D${end}`).setNumberFormat('#,##0');for(const col of ['C','E'])s.getRange(`${col}6:${col}${end}`).setNumberFormat('#,##0.00');}
 // 单独的图表辅助区保留真正空格，避免文本N/A被Excel当成0绘制。
 s.getRange(i===3?'AA5:AC5':'AA5:AB5').values=[i===3?['等级','最大Bet（普通档）','$1等值推荐Bet']:['等级',titles[i]]];
 s.getRange(`AA6:AA${end}`).formulas=rows.map((_,k)=>[`=""&A${k+6}`]);
 for(let k=0;k<rows.length;k++){
  const r=k+6, available=i<2?k<2:(i===3?Boolean(d.levels[k][6]):true);
  if(available)s.getRange(`AB${r}`).formulas=[[`=${i===3?'C':'B'}${r}`]];
 }
 if(i===3)s.getRange(`AC6:AC${end}`).formulas=rows.map((_,k)=>[`=E${k+6}`]);
 const chart=s.charts.add('line',s.getRange(`AA5:${i===3?'AC':'AB'}${end}`));
 chart.setPosition(i===3?'H5':'F5',i===3?'R27':'P27');
 chart.title=i<2?'已确认点；其余VIP累计口径待补':titles[i];
 chart.titleTextStyle.fontSize=14;chart.titleTextStyle.typeface='Microsoft YaHei';
 chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Microsoft YaHei',fontSize:11},tickLabelInterval:i<2?1:25};
 chart.yAxis={numberFormatCode:i===1||i===4?'0.0%':i===3?'#,##0.0':'$#,##0.00',numberFormatSourceLinked:false,textStyle:{typeface:'Microsoft YaHei',fontSize:11}};
 chart.legend={position:'top',textStyle:{typeface:'Microsoft YaHei',fontSize:11}};
 for(const [j,series] of chart.series.items.entries())series.line={fill:j===0?'#4472C4':'#ED7D31',style:'solid',width:2};
}
wb.recalculate();
await fs.mkdir(dir,{recursive:true});
await fs.writeFile(path.join(dir,'artifact-errors.ndjson'),(await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:20},maxChars:2000})).ndjson);
const file=await SpreadsheetFile.exportXlsx(wb);
await file.save(path.join(dir,'CashFrenzy_数值曲线对照.xlsx'));
console.log('Authored 5 curve sheets + CF source snapshot; native readback follows.');
