// node render_cf_live_rebase.mjs <controlled live-inputs.json> <controlled output>
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const [input,out]=process.argv.slice(2),d=JSON.parse(await fs.readFile(input,'utf8'));
const names=['VIP_消费门槛','VIP_膨胀系数','等级_升级消耗','等级_Bet曲线','等级_升级消耗返还'];
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const usd='"$"#,##0.00;[Red]("$"#,##0.00);"$"0.00', integer='#,##0';
const val=x=>x===null?'N/A':x;
function write(s,cell,rows){
 const match=cell.match(/([A-Z]+)(\d+)/),start=Number(match[2]);let c=0;for(const ch of match[1])c=c*26+ch.charCodeAt(0)-64;
 s.getRange(`${col(c)}${start}:${col(c+rows[0].length-1)}${start+rows.length-1}`).values=rows.map(r=>r.map(x=>typeof x==='string'&&x.startsWith('=')?null:val(x)));
 for(let j=0;j<rows[0].length;j++){let i=0;while(i<rows.length){if(typeof rows[i][j]!=='string'||!rows[i][j].startsWith('=')){i++;continue;}const a=i,forms=[];while(i<rows.length&&typeof rows[i][j]==='string'&&rows[i][j].startsWith('='))forms.push([rows[i++][j]]);s.getRange(`${col(c+j)}${start+a}:${col(c+j)}${start+i-1}`).formulas=forms;}}
}
function sources(wb,limit){
 const cr=wb.worksheets.getItem('SRC_CR'),cf=wb.worksheets.getItem('SRC_CF'),calc=wb.worksheets.getItem('CALC');
 write(cr,'A1',[['CR dev r7258 readback inputs; reward USD reused from Accepted r7013, unchanged by r7258']]);
 write(cr,'A3',[['等级','门槛类型','门槛','最大Bet','EXP/Spin','coins/USD','升到下一级奖励USD','LevelCfg坐标','EXP坐标','解锁坐标','兑换坐标']]);write(cr,'A4',d.cr.slice(0,limit));
 write(cr,'N3',[['VIP','当前needExp','暂存候选needExp']]);write(cr,'N4',d.vip);
 write(cr,'R3',[['VIP','商城金币倍率']]);write(cr,'R4',d.cr_packages);
 write(cf,'A1',[['2026-09-22 current evidence only; level=arrival; no historical CF fallback']]);
 write(cf,'A3',[['到达等级','到达后最大Bet','到达后等级倍率','到达本级ΔEXP','到达本级奖励金币','实际段Spin','实测来源','倍率来源','服务器Bet变化点']]);write(cf,'A4',d.cf);
 write(cf,'M3',[['模型参数','固定值']]);write(cf,'M4',[
 ['场景A基础coins/USD',d.drivers.base_a],['场景B约coins/USD',d.drivers.base_b],
 ['CF净耗率 Estimate 历史假设',d.drivers.cf_loss],['CR既有净耗率',d.drivers.cr_loss],
 ['折扣仅CALC',d.drivers.discount],['CR VIP点/USD',d.drivers.cr_vip_points_usd]]);
 write(cf,'Q1',[['CF_VIP_RULES.md current client VIP_POINTS_THRESHOLD / status_boost_data; 2026-09-22']]);
 write(cf,'Q3',[['VIP','累计点']]);write(cf,'Q4',d.cf_vip);write(cf,'T3',[['VIP','Coin Packages']]);write(cf,'T4',d.cf_packages);
 write(cf,'W3',[['USD标价','VIP点','点/USD']]);write(cf,'W4',d.shops.map((r,i)=>[...r,`=X${i+4}/W${i+4}`]));
 write(cf,'M11',[['最高点/USD','=MAX(Y4:Y9)'],['最低点/USD','=MIN(Y4:Y9)']]);
 write(calc,'A1',[['升级到L的ΔEXP，使用L-1最大Bet及L-1兑换率；奖励、成本同分母；理论Spin非实际对局次数']]);
 write(calc,'A3',[['到达等级','出发等级','CF出发Bet','CFΔEXP','CF出发倍率','CF理论Spin','CF向上取整Spin','CF毛下注金币','CF理论净耗金币','CF成本A USD','CF成本B USD','CF奖励A USD','CF奖励B USD','CF返还率A','CF返还率B','CR出发Bet','CR EXP/Spin','CR理论Spin','CR理论净耗USD','CR升级奖励USD','CR返还率','CR出发coins/USD','CF实际段Spin','CR整Spin','CF折扣成本A','CF折扣成本B']]);
 const rows=[];
 for(let l=1;l<=limit;l++){
  const r=l+3,p=r-1,known=l>=7&&l<=50,has=l>=2;
  rows.push([l,l-1,known?`=SRC_CF!B${p}`:'N/A',known?`=SRC_CF!D${r}`:'N/A',known?`=SRC_CF!C${p}`:'N/A',
   known?`=3*D${r}/C${r}`:'N/A',known?`=ROUNDUP(F${r},0)`:'N/A',known?`=F${r}*C${r}`:'N/A',
   known?`=H${r}*SRC_CF!$N$6`:'N/A',known?`=I${r}/(SRC_CF!$N$4*E${r})`:'N/A',known?`=I${r}/(SRC_CF!$N$5*E${r})`:'N/A',
   known?`=SRC_CF!E${r}/(SRC_CF!$N$4*E${r})`:'N/A',known?`=SRC_CF!E${r}/(SRC_CF!$N$5*E${r})`:'N/A',
   known?`=L${r}/J${r}`:'N/A',known?`=M${r}/K${r}`:'N/A',has?`=SRC_CR!D${p}`:'N/A',has?`=SRC_CR!E${p}`:'N/A',
   has?`=IF(SRC_CR!B${p}=1,SRC_CR!C${p},SRC_CR!C${p}/Q${r})`:'N/A',has?`=R${r}*P${r}/V${r}*SRC_CF!$N$7`:'N/A',
   has?`=SRC_CR!G${p}`:'N/A',has?`=T${r}/S${r}`:'N/A',has?`=SRC_CR!F${p}`:'N/A',known?`=SRC_CF!F${r}`:'N/A',
   has?`=ROUNDUP(R${r},0)`:'N/A',known?`=J${r}/SRC_CF!$N$8`:'N/A',known?`=K${r}/SRC_CF!$N$8`:'N/A']);
 }
 write(calc,'A4',rows);
}
function front(wb,name,title,notes,headers,rows){
 const s=wb.worksheets.getItem(name),end=31+rows.length,width=headers.length;
 s.showGridLines=false;s.freezePanes.unfreeze();s.tabColor='#205A72';
 s.getRange(`A1:${col(Math.max(12,width))}${Math.max(end,47)}`).format={font:{name:'Microsoft YaHei',size:11,color:'#263B48'},rowHeight:24,columnWidth:17,verticalAlignment:'center'};
 s.getRange('A:A').format.columnWidth=11;
 for(const r of [1,2,3,4,29])s.mergeCells(`A${r}:L${r}`);
 s.getRange('A1').values=[[title]];s.getRange('A1:L1').format={fill:'#205A72',font:{name:'Microsoft YaHei',size:18,bold:true,color:'#FFFFFF'},rowHeight:40};
 for(let j=0;j<3;j++)s.getRange(`A${j+2}`).values=[[notes[j]||'']];
 s.getRange('A2:L4').format={rowHeight:29,font:{size:11,color:'#526674'},wrapText:true};
 s.getRange('A29').values=[['完整数据（筛选阅读；图表缺值不连线）']];s.getRange('A29:L29').format={fill:'#EDF3F5',font:{bold:true},rowHeight:30};
 write(s,'A31',[headers]);s.getRange(`A31:${col(width)}31`).format={fill:'#DDECEF',font:{bold:true},rowHeight:48,wrapText:true,horizontalAlignment:'center'};
 write(s,'A32',rows);s.getRange(`A32:${col(width)}${end}`).format.horizontalAlignment='right';s.getRange(`B32:${col(width)}${end}`).setNumberFormat('#,##0.00');
 return s;
}
function chart(s,title,columns,labels,from,to,format){
 write(s,'AA31',[['等级',...labels]]);
 for(let l=from;l<=to;l++){
  const r=l+31,t=l-from+32;
  s.getRange(`AA${t}`).formulas=[[`=A${r}`]];
  for(let k=0;k<columns.length;k++){
   // Blanks outside evidence ranges, never text-as-zero chart points.
   if((s.name===names[0]&&k>=2&&l>8)||(s.name===names[1]&&k===1&&(l<2||l>10))||(s.name===names[3]&&k===1&&l>50))continue;
   s.getRange(`${col(28+k)}${t}`).formulas=[[`=${columns[k]}${r}`]];
  }
 }
 const c=s.charts.add('line',s.getRange(`AA31:${col(27+columns.length)}${to-from+32}`));
 c.setPosition('A6','L27');c.title=title;c.titleTextStyle.fontSize=14;c.titleTextStyle.typeface='Microsoft YaHei';
 c.legend={position:'top',textStyle:{typeface:'Microsoft YaHei',fontSize:11}};
 c.xAxis={axisType:'textAxis',tickLabelInterval:to-from>20?5:1};
 c.yAxis={numberFormatCode:format,numberFormatSourceLinked:false};
 for(const [k,ser]of c.series.items.entries())ser.line={fill:['#2864AE','#D47620','#438B79','#A34C64','#8064A2'][k],width:2,style:k===2?'dashed':'solid'};
}

for(const diff of [false,true]){
 const wb=Workbook.create();for(const n of [...(diff?['r7258差异']:names),'CALC','SRC_CR','SRC_CF'])wb.worksheets.add(n);sources(wb,diff?50:5000);
 if(!diff){
 let s=front(wb,names[0],'VIP消费门槛（USD）',[
  'CF仅VIP1–8有独立门槛；曲线比较同编号VIP，完整CR15档见明细。',
  'CF为纯购买取点上下界，升级/活动赠点可降低实付；六档SKU点/USD复算，未作SGD换算。',
  'CR现值沿用Accepted底稿；POP候选仍暂存，未提交。CF来源为2026-09-22客户端/商城规则。'],
  ['VIP','CR现值 USD','CR暂存候选 USD','CF纯购买最低 USD','CF纯购买最高 USD','CF累计点','CF最高点/USD','CF最低点/USD'],
  d.vip.map((v,i)=>{const r=i+4;return [v[0],`=SRC_CR!O${r}/SRC_CF!$N$9`,`=SRC_CR!P${r}/SRC_CF!$N$9`,i<8?`=SRC_CF!R${r}/SRC_CF!$N$11`:'N/A',i<8?`=SRC_CF!R${r}/SRC_CF!$N$12`:'N/A',i<8?`=SRC_CF!R${r}`:'N/A',i<8?'=SRC_CF!$N$11':'N/A',i<8?'=SRC_CF!$N$12':'N/A'];}));
 s.getRange('B32:E46').setNumberFormat(usd);s.getRange('F32:F46').setNumberFormat(integer);chart(s,'VIP1–8 纯购买累计成本（USD）',['B','C','D','E'],['CR现值','CR暂存候选','CF最低','CF最高'],1,8,'$#,##0');
 s=front(wb,names[1],'VIP金币包倍率',[
  'CF按Coin Packages：最高50倍；Store Bonus是另一种权益，不混入。',
  'CF VIP9为上限权益档，没有独立新门槛；CR含VIP0基准，权益未调整。',
  'CR现值r7013 Accepted底稿；CF当前status_boost_data（2026-09-22）。'],
  ['VIP','CR商城金币 倍','CF Coin Packages 倍','说明'],d.cr_packages.map((v,i)=>[v[0],`=SRC_CR!S${i+4}`,i>=1&&i<=9?`=SRC_CF!U${i+3}`:'N/A',i===9?'CF无独立新门槛':'']));
 s.getRange('B32:C47').setNumberFormat('0.0"x"');s.getRange('D:D').format.columnWidth=30;
 // VIP0 starts at row32; chart() uses level+31, so explicitly shifted chart indices.
 chart(s,'商城金币倍率（同一倍数轴）',['B','C'],['CR商城金币','CF Coin Packages'],1,16,'0.0"x"');
 s=front(wb,names[2],'等级升级消耗（到达等级）',[
  '实测闭合L7–L50；51+ CF成本N/A。标准化Spin按出发等级最大Bet，保留理论小数。',
  'Estimate：CF净耗率15%为历史假设；CR沿用5%。场景币率=基础coins/USD×出发等级倍率。',
  'Bet÷3按Task规则计算；逐手102条非零比例冲突待Review。L6缺锚点；CR r7258保留5000级。'],
  ['到达等级','CR净耗 USD','CF 500k基础 USD','CF约150k基础 USD','CR理论Spin','CF理论Spin','CF取整Spin','CF实际段Spin','CF状态'],
  d.cr.map((v,i)=>{const r=i+4,l=i+1;return [l,`=CALC!S${r}`,`=CALC!J${r}`,`=CALC!K${r}`,`=CALC!R${r}`,`=CALC!F${r}`,`=CALC!G${r}`,`=CALC!W${r}`,l>=7&&l<=50?'实测门槛/模型成本':'N/A 未实测'];}));
 s.getRange('B32:D5031').setNumberFormat(usd);chart(s,'L7–L50 升级理论净耗（USD，Estimate）',['B','C','D'],['CR r7258','CF 500k基础','CF约150k基础'],7,50,'$0.00');
 s=front(wb,names[3],'等级Bet与$1等值Bet',[
  'CF最大Bet仅填实测L6–L50；51+不延填，L75/L100只确认变化点，金额N/A。',
  '$1等值Bet=基础coins/USD×当前等级倍率；两种无折扣场景与最大Bet共用金币轴。',
  '等级倍率仅取当前服务器L2–L124八段；125+ N/A。CR为r7258现值，膨胀列显示整数倍。'],
  ['当前等级','CR最大Bet','CF最大Bet','CR $1等值Bet','CF $1 500k基础','CF $1 约150k基础','CR等级膨胀','CF等级膨胀','CF解锁说明'],
  d.cr.map((v,i)=>{const r=i+4,l=i+1,known=l>=2&&l<=124;return [l,`=SRC_CR!D${r}`,l>=6&&l<=50?`=SRC_CF!B${r}`:'N/A',`=SRC_CR!F${r}`,known?`=SRC_CF!$N$4*SRC_CF!C${r}`:'N/A',known?`=SRC_CF!$N$5*SRC_CF!C${r}`:'N/A',`=SRC_CR!F${r}/SRC_CR!$F$4`,known?`=SRC_CF!C${r}`:'N/A',[75,100].includes(l)?'服务器变化点，金额缺失':l>50?'未实测金额':''];}));
 s.getRange('B32:H5031').setNumberFormat(integer);chart(s,'最大Bet与$1等值Bet（金币，L6–L124）',['B','C','D','E','F'],['CR最大Bet','CF最大Bet','CR $1','CF $1 500k','CF $1 约150k'],6,124,'#,##0');
 s=front(wb,names[4],'等级升级消耗返还',[
  '返还率=本次升级奖励USD÷机器理论净耗USD；分子分母使用同一出发等级兑币效率。',
  'Estimate：CF净耗率15%为历史假设。两个兑币场景返还率相同，主图只画一条CF线。',
  'L50保留实测11.5m奖励尖峰；51+奖励/成本不推测。CR奖励复用Accepted r7013结果。'],
  ['到达等级','CR返还率','CF返还率 500k','CF返还率 约150k','CR奖励 USD','CF奖励 500k USD','CF奖励 约150k USD','CR净耗 USD','CF净耗 500k USD','CF净耗 约150k USD'],
  d.cr.map((v,i)=>{const r=i+4;return [i+1,`=CALC!U${r}`,`=CALC!N${r}`,`=CALC!O${r}`,`=CALC!T${r}`,`=CALC!L${r}`,`=CALC!M${r}`,`=CALC!S${r}`,`=CALC!J${r}`,`=CALC!K${r}`];}));
 s.getRange('B32:D5031').setNumberFormat('0.0%');s.getRange('E32:J5031').setNumberFormat(usd);chart(s,'L7–L50 升级奖励返还率（Estimate）',['B','C'],['CR r7258','CF 两场景一致'],7,50,'0.0%');
 }else{
 const headers=['等级','CR最大Bet','CF最大Bet','Bet差 CR-CF','CR EXP/Spin','CF EXP/Spin','EXP差 CR-CF','CR到本级Spin','CF到本级Spin','Spin差 CR-CF','CR到本级成本USD','CF成本500k USD','CF成本约150k USD','成本差500k USD','成本差约150k USD','CR等级膨胀','CF等级膨胀','膨胀差 CR-CF','升级段'];
 const s=front(wb,'r7258差异','r7258 vs CF最新实测 L6–L50',[
  'Bet / EXP / 膨胀按当前等级；Spin / 成本按上一等级升到本级，避免解锁点错一档。',
  '差值统一CR−CF。CF L6升级段缺锚点；其余44段按最大Bet标准化，非实际逐手次数。',
  'CF净耗率15%为历史假设；Bet÷3按Task规则，逐手102条非零比例冲突待Review；本轮无SVN写入。'],headers,
  Array.from({length:45},(_,i)=>{const l=i+6,r=l+3,t=i+32,closed=l>=7;return [l,`=SRC_CR!D${r}`,`=SRC_CF!B${r}`,`=B${t}-C${t}`,`=SRC_CR!E${r}`,`=C${t}/3`,`=E${t}-F${t}`,`=CALC!R${r}`,`=CALC!F${r}`,closed?`=H${t}-I${t}`:'N/A',`=CALC!S${r}`,`=CALC!J${r}`,`=CALC!K${r}`,closed?`=K${t}-L${t}`:'N/A',closed?`=K${t}-M${t}`:'N/A',`=SRC_CR!F${r}/SRC_CR!$F$4`,`=SRC_CF!C${r}`,`=P${t}-Q${t}`,`${l-1}→${l}`];}));
 s.getRange('B32:G76').setNumberFormat(integer);s.getRange('K32:O76').setNumberFormat(usd);s.getRange('P32:R76').setNumberFormat(integer);
 s.mergeCells('A7:L9');s.getRange('A7').values=[['L6–L50 共45个同等级对照点；升级过程44段闭合。\n旧CF目标不再作为当前验收依据，r7258保留现状，等待Review后由User决定。']];s.getRange('A7:L9').format={fill:'#EDF3F5',wrapText:true,font:{size:14}};
 }
 wb.recalculate();
 const inspection=await wb.inspect({kind:'table',range:`'${diff?'r7258差异':names[2]}'!A38:F42`,include:'values,formulas',tableMaxRows:5,tableMaxCols:6});
 await fs.writeFile(path.join(out,diff?'diff-inspect.local.ndjson':'curve-inspect.local.ndjson'),inspection.ndjson);
 await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,diff?'r7258_vs_CF_最新实测_差异.xlsx':'CR_vs_CF_最新实测_数值曲线.xlsx'));
 console.log(diff?'Difference workbook authored':'Five-sheet curve workbook authored');
}
