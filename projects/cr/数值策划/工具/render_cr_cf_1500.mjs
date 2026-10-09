// Artifact Tool author: node render_cr_cf_1500.mjs <controlled output directory>
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const out=process.argv[2], d=JSON.parse(await fs.readFile(path.join(out,'inputs.controlled.json'),'utf8'));
const wb=Workbook.create();
const names=['VIP门槛','VIP倍率','等级曲线','等级概览','等级明细','拟合说明','SRC_CR','SRC_CF','SRC_VIP'];
for(const n of names)wb.worksheets.add(n);
const sheet=n=>wb.worksheets.getItem(n);
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const q=n=>`'${n}'`;
function write(s,start,rows){
 const first=Number(start.match(/\d+/)[0]);const letters=start.match(/[A-Z]+/)[0];
 let c=0;for(const a of letters)c=c*26+a.charCodeAt(0)-64;
 s.getRange(`${letters}${first}:${col(c+rows[0].length-1)}${first+rows.length-1}`).values=rows.map(r=>r.map(v=>typeof v==='string'&&v.startsWith('=')?null:v??'N/A'));
 for(let j=0;j<rows[0].length;j++){let i=0;while(i<rows.length){if(typeof rows[i][j]!=='string'||!rows[i][j].startsWith('=')){i++;continue;}
  const a=i,f=[];while(i<rows.length&&typeof rows[i][j]==='string'&&rows[i][j].startsWith('='))f.push([rows[i++][j]]);
  s.getRange(`${col(c+j)}${first+a}:${col(c+j)}${first+i-1}`).formulas=f;
 }}
}
function base(n,title,note,endRow=45,endCol=12){
 const s=sheet(n);s.showGridLines=false;s.freezePanes.unfreeze();
 s.getRange(`A1:${col(endCol)}${endRow}`).format={font:{name:'Microsoft YaHei',size:11,color:'#273444'},rowHeight:24,columnWidth:15,verticalAlignment:'center'};
 s.getRange('A:A').format.columnWidth=10;
 s.getRange('A2').values=[[title]];s.getRange('A2:L2').format={font:{bold:true,size:17,color:'#183654'},rowHeight:34};
 s.getRange('A3').values=[[note]];s.getRange('A3:L3').format={font:{size:10,color:'#657487'},rowHeight:27};
 s.getRange('A4:L4').format.borders={bottom:{style:'thin',color:'#BAC9D8'}};
 s.tabColor=n.startsWith('SRC')?'#BCC5D0':'#294C73';return s;
}
function header(s,row,heads){
 write(s,`A${row}`,[heads]);s.getRange(`A${row}:${col(heads.length)}${row}`).format={fill:'#294C73',font:{bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:46,horizontalAlignment:'center'};
}
function num(s,range,format='#,##0.0'){s.getRange(range).setNumberFormat(format);s.getRange(range).format.horizontalAlignment='right';}
function table(s,row,heads,rows,name){header(s,row,heads);write(s,`A${row+1}`,rows);s.tables.add(`A${row}:${col(heads.length)}${row+rows.length}`,true,name);}
function chart(s,title,source,columns,labels,from,to,position1,position2,format){
 // Compact helpers reshape nonadjacent metrics; data remains formula linked.
 const c0=27+s.charts.items.length*7;
 write(s,`${col(c0)}5`,[['等级',...labels]]);
 write(s,`${col(c0)}6`,Array.from({length:to-from+1},(_,i)=>{
  const r=i+from+5;return [`=${q(source)}!A${r}`,...columns.map(c=>`=${q(source)}!${c}${r}`)];
 }));
 const c=s.charts.add('line',s.getRange(`${col(c0)}5:${col(c0+columns.length)}${to-from+6}`));
 c.setPosition(position1,position2);c.title=title;c.titleTextStyle.fontSize=14;c.titleTextStyle.typeface='Microsoft YaHei';
 c.legend={position:'top',textStyle:{typeface:'Microsoft YaHei',fontSize:11}};
 c.xAxis={axisType:'textAxis',tickLabelInterval:to>100?150:1,textStyle:{typeface:'Microsoft YaHei',fontSize:10}};
 c.yAxis={numberFormatCode:format,numberFormatSourceLinked:false,textStyle:{typeface:'Microsoft YaHei',fontSize:10}};
 c.series.items.forEach((v,i)=>v.line={fill:['#2864AE','#D57B28','#7395AD','#D9B381'][i],width:2,style:i%2?'dashed':'solid'});
}

let s=base('SRC_CR','CR配置输入','公司 trunk r7502；普通金币机台 bet2；源表只读。',1505,10);
table(s,5,['等级','升级类型','本级门槛','最大Bet','EXP/Spin','coins/USD','L0币率','等级来源','Bet来源','兑换来源'],d.cr,'CRInputs');
num(s,'B6:G1505','#,##0');s.getRange('H:J').format.columnWidth=42;
s=base('SRC_CF','CF输入及来源','9/22数据优先；旧正式表为历史参考；缺失项保留N/A。',1505,10);
table(s,5,['等级','最大Bet','历史Spin','实测区间EXP','等级倍率','升级依据','Bet依据','倍率依据','历史坐标','实测坐标'],d.cf,'CFInputs');
num(s,'B6:E1505','#,##0.0');s.getRange('F:J').format.columnWidth=32;
s=base('SRC_VIP','VIP输入及来源','CR取trunk现值；CF取9/22门槛、Coin Packages与六档美元SKU。',35,20);
write(s,'A5',[['CR VIP','累计点']]);write(s,'A6',d.vip);
write(s,'D5',[['CR VIP','金币包','VIP0金币包']]);write(s,'D6',d.cr_packages);
write(s,'H5',[['CF VIP','累计点']]);write(s,'H6',d.cf_vip);
write(s,'K5',[['CF VIP','Coin Packages']]);write(s,'K6',d.cf_packages);
write(s,'N5',[['USD标价','VIP点','点/USD']]);write(s,'N6',d.shops.map((r,i)=>[...r,`=O${i+6}/N${i+6}`]));
write(s,'A25',[
 ['CR points/USD',d.cr_vip_points_usd,'PriceCheatSheet priceType2, money99, level0；.99取整名义美元'],
 ['CR VIP门槛来源','VipCfg!A5:B19','累计门槛沿用原Accepted解释；不是每档相加'],
 ['CR商城倍率来源','PriceCheatSheet priceType9, money99, level0','各VIP金币包/同档VIP0；本轮直接读trunk'],
 ['CF来源','9/22 VIP规则及商城SKU','免费VIP点会降低实际付款；此处只算纯购买等值']]);

s=base('拟合说明','CF1500级拟合口径','实测、历史参考和拟合分列；本表不代表1500级服务器配置已验证。',74,12);
write(s,'A6',[
 ['外推锚点等级',300],
 ['锚点经验','=SRC_CF!B305*SRC_CF!C305/3'],
 ['每级增加经验','=SUMPRODUCT(F20:F69,G20:G69)/SUMPRODUCT(F20:F69,F20:F69)'],
 ['倍率锚点','=SRC_CF!E305'],
 ['倍率每级增量','=(SRC_CF!E305-SRC_CF!E155)/(300-150)'],
 ['CR名义基础coins/USD','=SRC_CR!G6'],
 ['CF基础coins/USD',500000],
 ['CF另一场景coins/USD',150000],
 ['CF EXP/Bet基准',1/3]
]);s.getRange('A:A').format.columnWidth=28;s.getRange('B:B').format.columnWidth=22;num(s,'B6:B14','#,##0.0000');
write(s,'D6',[
 ['当前L6–49升下一级：沿用9/22实测区间经验，按Bet/3计算标准Spin。'],
 ['当前L1–5及L50–300：沿用旧表Spin，使用本轮优先级确定的Bet，反推等值EXP。'],
 ['L301–1500：锚定L300，用L251–300拟合正向经验增量；不拉伸或改写已有点。'],
 ['Bet：沿用已知历史档位；L70旧解锁改用当前确认L75，未虚构高阶新档。'],
 ['倍率：L2–124用9/22，125–300用旧表，301+按历史末两次变化趋势取整数。'],
 ['倍率拟合值不表示实际解锁级；高等级美元消耗也随此假设变化。'],
 ['美元为最大Bet下升级毛下注的名义价值，含等级倍率，VIP0和最低商城档。'],
 ['不使用旧1/6或×5.5折扣，也不把毛下注当实付金额或净亏损。'],
 ['原始EXP单位不同，不直接比较高低；重点看同Bet或最大Bet的标准Spin。'],
 ['L49与L50附近有来源切换，保留接续差异，不强行平滑。'],
 ['免费Spin、经验加倍、首转特殊规则不混入标准升级曲线。'],
 ['POP Slots新资料待补，本轮只交CR与CF；不改配置。']]);
write(s,'F18',[['拟合自变量','拟合因变量']]);
write(s,'F20',Array.from({length:50},(_,i)=>{const l=251+i,r=l+5;return [`=SRC_CF!A${r}-$B$6`,`=SRC_CF!B${r}*SRC_CF!C${r}*$B$14-$B$7`];}));

const detailHeads=['等级','CR最大Bet','CF最大Bet','CR升级Spin','CF升级Spin','CR毛下注 USD','CF毛下注 USD','CR等级倍率','CF等级倍率','CF等值EXP门槛','CR门槛原值','CR EXP/Spin','CF EXP/Spin','CF毛下注 150k场景','CF升级依据','CF Bet依据','CF倍率依据','CR升级类型','同CR Bet的CF Spin'];
const rows=[];
for(let level=1;level<=1500;level++){
 const r=level+5,measured=level>=6&&level<=49;
 rows.push([`=SRC_CR!A${r}`,`=SRC_CR!D${r}`,`=SRC_CF!B${r}`,
  `=IF(SRC_CR!B${r}=1,SRC_CR!C${r},SRC_CR!C${r}/SRC_CR!E${r})`,
  `=J${r}/M${r}`,`=D${r}*B${r}/SRC_CR!F${r}`,`=E${r}*C${r}/('拟合说明'!$B$12*I${r})`,
  `=SRC_CR!F${r}/SRC_CR!G${r}`,
  level<=300?`=SRC_CF!E${r}`:`=ROUND('拟合说明'!$B$9+'拟合说明'!$B$10*(A${r}-'拟合说明'!$B$6),0)`,
  measured?`=SRC_CF!D${r}`:level<=300?`=SRC_CF!B${r}*SRC_CF!C${r}*'拟合说明'!$B$14`:`='拟合说明'!$B$7+'拟合说明'!$B$8*(A${r}-'拟合说明'!$B$6)`,
  `=SRC_CR!C${r}`,`=SRC_CR!E${r}`,`=C${r}*'拟合说明'!$B$14`,
  `=E${r}*C${r}/('拟合说明'!$B$13*I${r})`,
  `=SRC_CF!F${r}`,`=SRC_CF!G${r}`,`=SRC_CF!H${r}`,level<=4?'Spin次数':'经验',
  `=J${r}/(B${r}*'拟合说明'!$B$14)`]);
}
s=base('等级明细','逐级体验对比 1–1500','当前等级升到下一级；无经验加倍。美元主列按CF 500k基础场景。',1505,19);
table(s,5,detailHeads,rows,'LevelDetail');
num(s,'B6:C1505','#,##0');num(s,'D6:G1505');num(s,'H6:L1505','#,##0');num(s,'M6:N1505');num(s,'S6:S1505');
s.getRange('O:Q').format.columnWidth=28;s.getRange('J:J').format.columnWidth=21;
s.getRange('F6:G1505').setNumberFormat('"$"#,##0.00');s.getRange('N6:N1505').setNumberFormat('"$"#,##0.00');
s=base('等级概览','最大Bet解锁点概览','仅展示任一游戏最大Bet变化的等级，另保留1500级终点；完整逐级曲线见明细。',d.overview.length+5,10);
table(s,5,[...detailHeads.slice(0,9),'CF升级依据'],d.overview.map(l=>[...Array.from({length:9},(_,i)=>`='等级明细'!${col(i+1)}${l+5}`),`='等级明细'!O${l+5}`]),'LevelOverview');
num(s,`B6:C${d.overview.length+5}`,'#,##0');num(s,`D6:G${d.overview.length+5}`);num(s,`H6:I${d.overview.length+5}`,'#,##0');s.getRange('J:J').format.columnWidth=34;
num(s,`F6:G${d.overview.length+5}`,'"$"#,##0.00');
s=base('等级曲线','CR与CF等级曲线 至1500级','CR trunk r7502；CF含历史参考与尾段拟合。蓝色CR，橙色CF。',93,12);
chart(s,'最大Bet与1美元等值Bet（金币）','等级明细',['B','C'],['CR最大Bet','CF最大Bet'],1,1500,'A6','L25','0.0,,"百万"');
// Add the currency-equivalent curves to the same chart with a contiguous helper rebuild.
write(s,'AD5',[['CR 1美元等值Bet','CF 1美元等值Bet']]);
write(s,'AD6',Array.from({length:1500},(_,i)=>[`=SRC_CR!F${i+6}`,`='等级明细'!I${i+6}*'拟合说明'!$B$12`]));
s.charts.items[0].setData(s.getRange('AA5:AE1505'));
s.charts.items[0].series.items.forEach((v,i)=>v.line={fill:['#2864AE','#D57B28','#7395AD','#D9B381'][i],width:2,style:i%2?'dashed':'solid'});
chart(s,'最大Bet下升级Spin（理论次数）','等级明细',['D','E'],['CR现值','CF参考及拟合'],1,1500,'A28','L47','0.0');
chart(s,'升级毛下注（名义USD，CF基础500k）','等级明细',['F','G'],['CR现值','CF参考及拟合'],1,1500,'A50','L69','$#,##0');
chart(s,'等级金币倍率（整数倍）','等级明细',['H','I'],['CR现值','CF参考及拟合'],1,1500,'A72','L91','0"倍"');

s=base('VIP门槛','VIP消费门槛（纯购买等值USD）','CF含免费VIP点来源，实际付费可更低；同编号VIP不代表权益相同。',45,10);
header(s,5,['VIP','CR累计点','CR名义USD','CF累计点','CF最低USD','CF最高USD']);
const vipRows=d.vip.map((v,i)=>{const r=i+6;return [v[0],`=SRC_VIP!B${r}`,`=B${r}/SRC_VIP!$B$25`,i<8?`=SRC_VIP!I${r}`:'N/A',i<8?`=D${r}/MAX(SRC_VIP!$P$6:$P$11)`:'N/A',i<8?`=D${r}/MIN(SRC_VIP!$P$6:$P$11)`:'N/A'];});
write(s,'A6',vipRows);num(s,'B6:F20','#,##0');
chart(s,'VIP1–8 累计消费等值（USD）','VIP门槛',['C','E','F'],['CR名义','CF纯购最低','CF纯购最高'],1,8,'A23','L43','$#,##0');
s=base('VIP倍率','商城金币倍率','CR按当前trunk同档VIP0作分母；CF为Coin Packages，VIP9无独立新门槛。',45,10);
header(s,5,['VIP','CR金币倍率','CF金币倍率','CF说明']);
write(s,'A6',d.cr_packages.map((v,i)=>[v[0],`=SRC_VIP!E${i+6}/SRC_VIP!F${i+6}`,i>=1&&i<=9?`=SRC_VIP!L${i+5}`:'N/A',i===9?'上限权益档，无独立新门槛':'']));
num(s,'B6:C21','0.00"倍"');s.getRange('D:D').format.columnWidth=35;
// VIP0 row6, VIP1 row7. chart helper uses positional indices2–10.
chart(s,'同编号VIP金币倍率','VIP倍率',['B','C'],['CR现值','CF Coin Packages'],2,10,'A23','L43','0"倍"');

wb.recalculate();
// Exercise the new tail dependency, then restore before export.
const levelCheck=sheet('等级明细'),control=sheet('拟合说明');
const before=levelCheck.getRange('J1505').values[0][0];
control.getRange('B8').formulas=[['=2*SUMPRODUCT(F20:F69,G20:G69)/SUMPRODUCT(F20:F69,F20:F69)']];wb.recalculate();
const changed=levelCheck.getRange('J1505').values[0][0];
if(!(changed>before))throw new Error('Tail formula did not respond to fit slope');
control.getRange('B8').formulas=[['=SUMPRODUCT(F20:F69,G20:G69)/SUMPRODUCT(F20:F69,F20:F69)']];wb.recalculate();
if(Math.abs(levelCheck.getRange('J1505').values[0][0]-before)>1e-6)throw new Error('Fit slope restore failed');
await fs.writeFile(path.join(out,'recalculation.json'),JSON.stringify({slope_input_changed:true,tail_responded:true,restored:true}));
const inspect=await wb.inspect({kind:'table',range:"'等级明细'!A1503:J1505",include:'values,formulas',tableMaxRows:3,tableMaxCols:10});
await fs.writeFile(path.join(out,'inspect.local.ndjson'),inspect.ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,'CR_vs_CF_数值对比_1500级_trunk_r7502.xlsx'));
await fs.mkdir(path.join(out,'previews'),{recursive:true});
for(const name of names){
 const ranges=name==='等级曲线'?['A1:L26','A27:L48','A49:L70','A71:L92']:name.startsWith('VIP')?['A1:L44']:name==='拟合说明'?['A1:L18']:['A1:J15'];
 for(let i=0;i<ranges.length;i++){
  const img=await wb.render({sheetName:name,range:ranges[i],scale:1.3,format:'png'});
  await fs.writeFile(path.join(out,'previews',`${name}-${i+1}.png`),new Uint8Array(await img.arrayBuffer()));
 }
}
console.log(JSON.stringify({book:'CR_vs_CF_数值对比_1500级_trunk_r7502.xlsx',sheets:names.length,charts:6,levels:1500}));
