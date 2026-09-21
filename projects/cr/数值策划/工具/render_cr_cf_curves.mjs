// 只合并已验证缓存；新公式仅用于CF VIP商城边界及显式货币换算。
// node render_cr_cf_curves.mjs comparison-inputs.json <受控目录>
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const [input,dir]=process.argv.slice(2),d=JSON.parse(await fs.readFile(input,'utf8'));
const names=['VIP_消费门槛','VIP_膨胀系数','等级_升级消耗','等级_Bet曲线','等级_升级消耗返还'];
const wb=Workbook.create();for(const n of [...names,'SRC_CR','SRC_CF'])wb.worksheets.add(n);
const letter=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const cr=wb.worksheets.getItem('SRC_CR'),cf=wb.worksheets.getItem('SRC_CF');
cr.getRange('A1').values=[['来源：'+d.cr_file+'；r7013已交付输出，只读缓存，不重算旧模型']];
cf.getRange('A1').values=[['等级/Bet/返还来源：'+d.cf_file+'；既有历史模型缓存']];
cf.getRange('R1').values=[[d.evidence]];
const oldHeaders=[['VIP','累计USD','新增USD'],['VIP','绝对指数','累计USD','新增USD'],['等级','消耗USD','奖励USD','净成本USD'],['等级','最大Bet','最大Bet百万','等值Bet','等值Bet百万','最大BetUSD'],['等级','返还率','消耗USD','奖励USD']];
for(let i=0;i<5;i++){
 const c=[1,6,12,18,25][i],rows=d.cr[i];
 cr.getRange(`${letter(c)}3:${letter(c+rows[0].length-1)}3`).values=[oldHeaders[i]];
 cr.getRange(`${letter(c)}4:${letter(c+rows[0].length-1)}${rows.length+3}`).values=rows;
}
for(let i=0;i<3;i++){
 const c=[1,6,13][i],rows=d.cf[i];
 cf.getRange(`${letter(c)}3:${letter(c+rows[0].length-1)}3`).values=[oldHeaders[i+2]];
 cf.getRange(`${letter(c)}4:${letter(c+rows[0].length-1)}303`).values=rows;
}
cf.getRange('R3:T3').values=[['VIP序号','累计VIP点','User确认名称']];cf.getRange('R4:T11').values=d.vip;
cf.getRange('W2:Y4').values=[['兑换驱动','VIP点/S$','证据'],['最高效率',d.high,'Task商城截图转录，四位小数'],['最低效率',d.low,'Task商城截图转录，四位小数']];
cf.getRange('W8:Y8').values=[['标价S$','VIP点','证据']];cf.getRange('W9:Y17').values=d.shops.map(r=>[...r,'User 2026-09-21商城截图转录']);
cr.showGridLines=false;cf.showGridLines=false;

const titles=['VIP消费门槛','VIP绝对膨胀指数','等级升级消耗','等级Bet曲线','等级升级消耗返还'];
const conclusions=['CF累计门槛已闭合；美元金额对比需先确认汇率。','兑换上下界改变消费成本，不改变CF的绝对膨胀指数。','两边升级成本沿用各自模型口径，不等同实付金额。','CF普通Bet仍有56个冲突点；其余曲线沿用已验证结果。','返还率按各自升级净耗分母计算，不等同机器RTP。'];
const notes=['CR为r7013 USD；CF原币为S$。填入正数汇率后，CF最低/最高USD成本两条线自动显示。','CR / CF均以各自VIP1=100%；只画一条CF指数线。CF只到VIP7，名称不与CR强行对应。','主图1–300级；CR为机器理论净耗USD，CF为历史抽水折算USD。完整4999级数据在下方。','主图1–300级，四条线共用百万金币轴；CF15–19、250–300级不插值。完整5000级数据在下方。','CR分母为机器理论净耗USD；CF分母为历史抽水折算USD。主图1–300级，同一百分比轴。'];
const heads=[['VIP序号','CR累计成本\nUSD','CF VIP名称','CF累计\nVIP点','CF最低成本\nS$','CF最高成本\nS$','CF最低成本\nUSD','CF最高成本\nUSD','CF最高效率\nVIP点/S$','CF最低效率\nVIP点/S$','CR本级新增\nUSD'],
 ['VIP序号','CR绝对指数\nVIP1=100%','CF绝对指数\nVIP1=100%','CR累计成本\nUSD','CF累计VIP点'],
 ['等级','CR升级净耗\nUSD','CF历史升级消耗\nUSD','CR升级奖励\nUSD','CF升级奖励\nUSD','CR升级净成本\nUSD','CF升级净成本\nUSD'],
 ['等级','CR最大Bet\n金币','CR $1等值Bet\n金币','CF普通最大Bet\n金币','CF $1等值Bet\n金币','CR最大Bet\n百万金币','CR $1等值Bet\n百万金币','CF最大Bet\n百万金币','CF $1等值Bet\n百万金币','CR最大Bet\nUSD','CF最大Bet\nUSD'],
 ['等级','CR返还率','CF返还率','CR升级净耗\nUSD','CF历史升级消耗\nUSD','CR升级奖励\nUSD','CF升级奖励\nUSD']];
const ref=(s,c,r)=>`'${s}'!${c}${r}`;
const usd='"$"#,##0.00;[Red]("$"#,##0.00);"$"0.00';
const sgd='"S$"#,##0.00';
for(let i=0;i<5;i++){
 const s=wb.worksheets.getItem(names[i]),end=d.cr[i].length+31,width=heads[i].length;
 s.showGridLines=false;s.freezePanes.unfreeze();s.tabColor='#1F4E78';
 s.getRange(`A1:N${Math.max(end,46)}`).format={font:{name:'Microsoft YaHei',size:10,color:'#24364B'},rowHeight:21,columnWidth:15,verticalAlignment:'center'};
 s.getRange(`A1:A${Math.max(end,46)}`).format.columnWidth=10;
 for(const r of [1,2,3,5,29])s.mergeCells(`A${r}:N${r}`);
 s.getRange('A1').values=[['CR vs Cash Frenzy  '+titles[i]]];
 s.getRange('A1:N1').format={fill:'#1F4E78',font:{name:'Microsoft YaHei',size:16,bold:true,color:'#FFFFFF'},rowHeight:34};
 s.getRange('A2').values=[[conclusions[i]]];s.getRange('A3').values=[[notes[i]]];
 s.getRange('A2:N3').format={rowHeight:25,font:{size:11,color:'#44546A'}};
 s.getRange('A5').values=[['CR：r7013曲线缓存。CF：历史曲线缓存；VIP累计点及商城边界依据2026-09-21 User确认。']];
 s.getRange('A5:N5').format={font:{size:10,color:'#667788'}};
 s.getRange('A29').values=[['完整数据（可筛选）'+(i>=2?'；CF超过300级无来源，显示N/A。':'；CF超过VIP7无来源，显示N/A。')]];
 s.getRange('A29:N29').format={fill:'#EDF3F8',font:{bold:true},rowHeight:28};
 s.getRange(`A31:${letter(width)}31`).values=[heads[i]];
 s.getRange(`A31:${letter(width)}31`).format={fill:'#D9EAF7',font:{bold:true,color:'#17365D'},rowHeight:48,wrapText:true,horizontalAlignment:'center'};
 s.getRange(`A32:${letter(width)}${end}`).format.horizontalAlignment='right';
 s.getRange(`B32:${letter(width)}${end}`).setNumberFormat(usd);
 if(i===0){
  s.getRange('A4').values=[['1 S$ 兑 USD']];s.getRange('B4').values=[[d.fx]];
  s.getRange('B4').format={fill:'#FFF2CC',font:{bold:true,color:'#156082'},numberFormat:'0.000000',rowHeight:28};
  s.mergeCells('C4:N4');s.getRange('C4').formulas=[['=IF(AND(ISNUMBER(B4),B4>0),"CF美元对比已按输入汇率显示；该值需User确认来源。","需User确认：汇率留空，CF原币上下界完整保留；两条USD线暂不绘制。")']];
 }
 const rows=[];
 for(let j=0;j<d.cr[i].length;j++){
  const r=j+32,t=j+4,vr=j+5,has=j<300;
  if(i===0)rows.push([`=${ref('SRC_CR','A',t)}`,`=${ref('SRC_CR','B',t)}`,j<7?(d.vip[j+1][2]||'名称未提供'):'N/A',j<7?`=${ref('SRC_CF','S',vr)}`:'N/A',j<7?`=D${r}/'SRC_CF'!$X$3`:'N/A',j<7?`=D${r}/'SRC_CF'!$X$4`:'N/A',j<7?`=IF(AND(ISNUMBER($B$4),$B$4>0),E${r}*$B$4,"待汇率")`:'N/A',j<7?`=IF(AND(ISNUMBER($B$4),$B$4>0),F${r}*$B$4,"待汇率")`:'N/A',j<7?`='SRC_CF'!$X$3`:'N/A',j<7?`='SRC_CF'!$X$4`:'N/A',`=${ref('SRC_CR','C',t)}`]);
  if(i===1)rows.push([`=${ref('SRC_CR','F',t)}`,`=${ref('SRC_CR','G',t)}`,j<7?`=E${r}/'SRC_CF'!$S$5`:'N/A',`=${ref('SRC_CR','H',t)}`,j<7?`=${ref('SRC_CF','S',vr)}`:'N/A']);
  if(i===2)rows.push([`=${ref('SRC_CR','L',t)}`,`=${ref('SRC_CR','M',t)}`,has?`=${ref('SRC_CF','B',t)}`:'N/A',`=${ref('SRC_CR','N',t)}`,has?`=${ref('SRC_CF','C',t)}`:'N/A',`=${ref('SRC_CR','O',t)}`,has?`=${ref('SRC_CF','D',t)}`:'N/A']);
  if(i===3)rows.push([`=${ref('SRC_CR','R',t)}`,`=${ref('SRC_CR','S',t)}`,`=${ref('SRC_CR','U',t)}`,has?`=${ref('SRC_CF','G',t)}`:'N/A',has?`=${ref('SRC_CF','I',t)}`:'N/A',`=${ref('SRC_CR','T',t)}`,`=${ref('SRC_CR','V',t)}`,has?`=${ref('SRC_CF','H',t)}`:'N/A',has?`=${ref('SRC_CF','J',t)}`:'N/A',`=${ref('SRC_CR','W',t)}`,has?`=${ref('SRC_CF','K',t)}`:'N/A']);
  if(i===4)rows.push([`=${ref('SRC_CR','Y',t)}`,`=${ref('SRC_CR','Z',t)}`,has?`=${ref('SRC_CF','N',t)}`:'N/A',`=${ref('SRC_CR','AA',t)}`,has?`=${ref('SRC_CF','O',t)}`:'N/A',`=${ref('SRC_CR','AB',t)}`,has?`=${ref('SRC_CF','P',t)}`:'N/A']);
 }
 for(let c=0;c<width;c++){
  const col=letter(c+1);s.getRange(`${col}32:${col}${end}`).values=rows.map(r=>[r[c].startsWith('=')?null:r[c]]);
  let j=0;while(j<rows.length){if(!rows[j][c].startsWith('=')){j++;continue;}const start=j,forms=[];while(j<rows.length&&rows[j][c].startsWith('='))forms.push([rows[j++][c]]);s.getRange(`${col}${start+32}:${col}${j+31}`).formulas=forms;}
 }
 s.getRange(`A32:A${end}`).setNumberFormat('0');
 if(i===0){s.getRange('D32:D46').setNumberFormat('#,##0');s.getRange('E32:F46').setNumberFormat(sgd);s.getRange('I32:J46').setNumberFormat('0.0000');}
 if(i===1||i===4)s.getRange(`B32:C${end}`).setNumberFormat('0.0%');
 if(i===1)s.getRange('E32:E46').setNumberFormat('#,##0');
 if(i===3){s.getRange(`B32:E${end}`).setNumberFormat('#,##0');s.getRange(`F32:I${end}`).setNumberFormat('#,##0.00');}
 const chartEnd=i<2?46:331,seriesCols=[['B','G','H'],['B','C'],['B','C'],['F','G','H','I'],['B','C']][i];
 const labels=[['CR累计成本','CF最低成本','CF最高成本'],['CR绝对指数','CF绝对指数'],['CR机器理论净耗','CF历史抽水折算消耗'],['CR最大Bet','CR $1等值Bet','CF普通最大Bet','CF $1等值Bet'],['CR返还率','CF返还率']][i];
 s.getRange(`W31:${letter(23+seriesCols.length)}31`).values=[['等级',...labels]];
 s.getRange(`W32:W${chartEnd}`).formulas=Array.from({length:chartEnd-31},(_,j)=>[`=""&A${j+32}`]);
 for(let k=0;k<seriesCols.length;k++){
  for(let r=32;r<=chartEnd;r++){
   if(i<2&&k>0&&r>38)continue;
   if(i===3&&k===2&&d.cf[1][r-32][1]==='N/A')continue;
   const val=seriesCols[k]+r;
   // NA仅作为未确认汇率时的绘图缺点，前台为“待汇率”；输入后自动恢复两条线。
   s.getRange(`${letter(24+k)}${r}`).formulas=[[i===0&&k>0?`=IF(ISNUMBER(${val}),${val},NA())`:`=${val}`]];
  }
 }
 const chart=s.charts.add('line',s.getRange(`W31:${letter(23+seriesCols.length)}${chartEnd}`));
 chart.setPosition('A7','N27');chart.title=titles[i]+(i>=2?'（1–300级）':i===0?'（USD；CF需汇率）':'（VIP1=100%）');
 chart.titleTextStyle.fontSize=15;chart.titleTextStyle.typeface='Microsoft YaHei';
 chart.legend={position:'top',textStyle:{typeface:'Microsoft YaHei',fontSize:12}};
 chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Microsoft YaHei',fontSize:11},tickLabelInterval:i<2?1:25};
 chart.yAxis={numberFormatCode:i===1||i===4?'0.0%':i===3?'#,##0.0':'$#,##0',numberFormatSourceLinked:false,textStyle:{typeface:'Microsoft YaHei',fontSize:11}};
 const colors=i===3?['#4472C4','#56A5D8','#D77A22','#A63D40']:['#4472C4','#D77A22','#A63D40'];
 for(const [k,ser]of chart.series.items.entries())ser.line={fill:colors[k],style:i===3&&k%2===1?'dashed':'solid',width:2};
 console.log('Authored '+names[i]);
}
wb.recalculate();await fs.mkdir(dir,{recursive:true});
const out=await SpreadsheetFile.exportXlsx(wb);await out.save(path.join(dir,'CR_vs_CashFrenzy_数值曲线对照.xlsx'));
console.log('5 comparison sheets authored; source models copied as caches, not recalculated.');
