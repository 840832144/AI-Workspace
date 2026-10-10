// TASK-0036 only: controlled candidates and scenario curves, never edit the r7013 source.
import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile,Workbook} from '@oai/artifact-tool';
const [input,dir]=process.argv.slice(2),d=JSON.parse(await fs.readFile(input,'utf8'));
const names=['候选总览','VIP_消费门槛','VIP_商城金币','等级_升级消耗','等级_Bet曲线','等级_消耗返还','档位_膨胀','等级_膨胀'];
const wb=Workbook.create();for(const n of [...names,'CALC_等级','SRC'])wb.worksheets.add(n);
const L=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const src=wb.worksheets.getItem('SRC'),calc=wb.worksheets.getItem('CALC_等级');
function block(col,headers,rows){src.getRange(`${L(col)}3:${L(col+headers.length-1)}3`).values=[headers];src.getRange(`${L(col)}4:${L(col+headers.length-1)}${rows.length+3}`).values=rows;}
src.getRange('A1').values=[['来源：trunk固定r7013配置、前轮已验证曲线缓存、CashRoyal历史正式表、CR_TUNING_POP_CF/User后续VIP拟合选择；未独立重读App截图。']];
block(1,['VIP','旧needExp','目标/拟合needExp','POP累计TP','VipCfg源行'],d.vip);
block(9,['CF等级','历史消耗USD','历史奖励USD','等级倍率'],d.cf);
block(14,['等级','原模式','原门槛','EXP/Spin','原BetUSD','旧净耗USD','原奖励USD','最大Bet金币','1USD等值Bet金币','CR等级倍率','CF等级倍率'],d.levels);
block(27,['序号','money','旧形状','旧VIP0金币','保形方案倍率','方案VIP0金币','同档金币行数','PriceSetting源行'],d.tiers);
block(36,['VIP','商店倍率'],d.shop_vip);
src.getRange('AN3:AO10').values=[['口径','值'],['POP TP/USD',80],['CR VIP点/USD',100],['POP高阶对数斜率',d.tail_slope],['VIP10锚点',2500000],['等级净耗率',.05],['旧最低档',d.tiers[0][2]],['旧最高档',d.tiers.at(-1)[2]]];
src.getRange('AN12:AO17').values=[['固定来源','字段/坐标'],['VipCfg.xlsx/Sheet1','B5:B19'],['LevelCfg.fresh.xlsx/Sheet1','levelUpType/levelUpExp；r7013'],['PriceSetting.xlsx/Sheet1','currencyType=1；money/vip0–15；仅分析不写表'],['CashRoyal数值.xlsx','档位膨胀!A2:B31；cashFrenzy等级!I2:I301'],['前轮合并曲线','等级_升级消耗/等级_Bet曲线；第32行起已验证缓存']];
calc.getRange('A1:R1').values=[['等级','映射A_CF级','A目标净耗USD','A整Spin','A拟议门槛','A实现净耗USD','A返还率','映射B_CF级','B目标净耗USD','B整Spin','B拟议门槛','B实现净耗USD','B返还率','CR旧净耗USD','CR奖励USD','CR等级倍率','CF等级倍率','原BetUSD']];
function writeRows(s,first,rows){for(let c=0;c<rows[0].length;c++){const col=L(c+1);s.getRange(`${col}${first}:${col}${first+rows.length-1}`).values=rows.map(r=>typeof r[c]==='string'&&r[c].startsWith('=')? [null]:[r[c]]);let j=0;while(j<rows.length){if(typeof rows[j][c]!=='string'||!rows[j][c].startsWith('=')){j++;continue;}const start=j,forms=[];while(j<rows.length&&typeof rows[j][c]==='string'&&rows[j][c].startsWith('='))forms.push([rows[j++][c]]);s.getRange(`${col}${first+start}:${col}${first+j-1}`).formulas=forms;}}}
const lr=d.levels.map((v,j)=>{const r=j+2,t=j+4,cap=j===4999;return [`=SRC!N${t}`,cap?'N/A':`=1+INT((A${r}-1)*299/4998)`,cap?'N/A':`=INDEX(SRC!$J$4:$J$303,B${r})`,cap?'N/A':`=MAX(1,ROUNDUP(ROUND(C${r}/(R${r}*SRC!$AO$8),10),0))`,cap?'N/A':`=IF(SRC!O${t}=1,D${r},ROUNDUP(ROUND(D${r}*SRC!Q${t},10),0))`,cap?'N/A':`=IF(SRC!O${t}=1,E${r},ROUNDUP(ROUND(E${r}/SRC!Q${t},10),0))*R${r}*SRC!$AO$8`,cap?'N/A':`=O${r}/F${r}`,cap?'N/A':`=IF(A${r}<=100,A${r},101+INT((A${r}-101)*199/4898))`,cap?'N/A':`=INDEX(SRC!$J$4:$J$303,H${r})`,cap?'N/A':`=MAX(1,ROUNDUP(ROUND(I${r}/(R${r}*SRC!$AO$8),10),0))`,cap?'N/A':`=IF(SRC!O${t}=1,J${r},ROUNDUP(ROUND(J${r}*SRC!Q${t},10),0))`,cap?'N/A':`=IF(SRC!O${t}=1,K${r},ROUNDUP(ROUND(K${r}/SRC!Q${t},10),0))*R${r}*SRC!$AO$8`,cap?'N/A':`=O${r}/L${r}`,`=SRC!S${t}`,`=SRC!T${t}`,`=SRC!W${t}`,`=SRC!X${t}`,`=SRC!R${t}`];});
writeRows(calc,2,lr);console.log('Built 5000 level rows / 2 unselected mapping scenarios');
const usd='"$"#,##0.0000;[Red]("$"#,##0.0000);"$"0.0000';
function front(name,title,note,heads,rows,series,chartEnd,format='usd'){
 const s=wb.worksheets.getItem(name),end=31+rows.length,width=heads.length;s.showGridLines=false;s.freezePanes.unfreeze();s.tabColor='#1F4E78';
 s.getRange(`A1:N${Math.max(end,48)}`).format={font:{name:'Microsoft YaHei',size:10,color:'#24364B'},rowHeight:21,columnWidth:15,verticalAlignment:'center'};s.getRange(`A1:A${end}`).format.columnWidth=10;
 for(const r of [1,2,3,5,29])s.mergeCells(`A${r}:N${r}`);
 s.getRange('A1').values=[[title]];s.getRange('A1:N1').format={fill:'#1F4E78',font:{color:'#FFFFFF',bold:true,size:16},rowHeight:34};
 s.getRange('A2').values=[[note]];s.getRange('A2:N2').format={font:{bold:true,color:'#9C6500'},rowHeight:28};
 s.getRange('A3').values=[['固定r7013；仅候选/比较。全部阶段保留，下方明细可筛选；5000级为终点，不虚构5000→5001。']];
 s.getRange('A5').values=[['未提交SVN、未冻结、未发布。CF仅1–300级有来源；图中映射曲线是待选方案，不是CF实测5000级。']];s.getRange('A5:N5').format={font:{size:10,color:'#667788'}};
 s.getRange('A29').values=[['明细与口径（配置写入状态见候选总览）']];s.getRange('A29:N29').format={fill:'#EDF3F8',font:{bold:true},rowHeight:28};
 s.getRange(`A31:${L(width)}31`).values=[heads];s.getRange(`A31:${L(width)}31`).format={fill:'#D9EAF7',font:{bold:true},rowHeight:52,wrapText:true,horizontalAlignment:'center'};
 writeRows(s,32,rows);s.getRange(`A32:${L(width)}${end}`).format.horizontalAlignment='right';s.getRange(`B32:${L(width)}${end}`).setNumberFormat(usd);s.getRange(`A32:A${end}`).setNumberFormat('0');
 const chartFormat=format==='pct'?'0%':format==='mult'?'0.0"x"':format==='coins'?'#,##0.0':'$#,##0';
 s.getRange(`AZ31:${L(52+series.length)}31`).values=[['阶段',...series.map(x=>x.label)]];
 s.getRange(`AZ32:AZ${chartEnd}`).formulas=Array.from({length:chartEnd-31},(_,j)=>[`=""&A${j+32}`]);
 series.forEach((x,k)=>{for(let r=32;r<=chartEnd;r++){if(x.until&&r>x.until)continue;s.getRange(`${L(53+k)}${r}`).formulas=[[`=${x.col}${r}`]];}});
 const c=s.charts.add('line',s.getRange(`AZ31:${L(52+series.length)}${chartEnd}`));c.setPosition('A7','N27');c.title=title;c.titleTextStyle.fontSize=14;c.legend={position:'top',textStyle:{typeface:'Microsoft YaHei',fontSize:11}};
 c.xAxis={axisType:'textAxis',tickLabelInterval:chartEnd>1000?250:chartEnd>100?25:1};c.yAxis={numberFormatCode:chartFormat,numberFormatSourceLinked:false};
 const colors=['#4472C4','#D77A22','#548235','#A63D40'];c.series.items.forEach((ser,k)=>{ser.line={fill:colors[k],style:k===2?'dashed':'solid',width:2};});
 console.log('Authored '+name);return s;
}
let s=front(names[1],'VIP消费门槛：POP目标 / CR原值 / 候选','主图VIP1–10；11–15按POP高阶趋势外推，列于明细；VIP1=0安全Gate未通过。',['VIP','CR原值USD','CR候选USD','POP目标USD','候选needExp','与原值差USD','来源/状态'],d.vip.map((v,j)=>{const r=j+32,t=j+4;return [v[0],`=SRC!B${t}/SRC!$AO$5`,`=E${r}/SRC!$AO$5`,j<10?`=SRC!D${t}/SRC!$AO$4`:'N/A',j<10?`=SRC!C${t}`:`=ROUND(SRC!$AO$7*EXP(SRC!$AO$6*(A${r}-10)),0)`,`=C${r}-B${r}`,j<10?'User固定门槛':'POP高阶外推候选'];}),[{col:'B',label:'CR原值'},{col:'C',label:'CR候选'},{col:'D',label:'POP Tier1–10',until:41}],41);
s.getRange('E32:E46').setNumberFormat('#,##0');s.getRange('B32:D46').setNumberFormat('"$"#,##0.00');
s=front(names[2],'VIP商城金币倍率：保持原配置','CR原值与候选应完全重合；权益不调整，最高2.5x。',['VIP','CR原值x','CR候选x','原值%','候选%'],d.shop_vip.map((v,j)=>{const r=32+j,t=4+j;return [v[0],`=SRC!AK${t}`,`=B${r}`,`=B${r}`,`=C${r}`];}),[{col:'B',label:'CR原值'},{col:'C',label:'CR候选（未改）'}],47,'mult');s.getRange('B32:C47').setNumberFormat('0.00"x"');s.getRange('D32:E47').setNumberFormat('0%');
s=front(names[3],'升级消耗：未选定的两种CF映射候选','A全段拉伸；B保留前100级再拉伸余段。按整Spin反推门槛，两方案均未写LevelCfg。',['CR等级','CR旧净耗USD','A目标USD','A实现净耗USD','B目标USD','B实现净耗USD','CF同级历史USD','A映射CF级','B映射CF级','A拟议门槛','B拟议门槛'],d.levels.map((v,j)=>{const r=2+j,t=4+j;return [v[0],`=CALC_等级!N${r}`,`=CALC_等级!C${r}`,`=CALC_等级!F${r}`,`=CALC_等级!I${r}`,`=CALC_等级!L${r}`,j<300?`=SRC!J${t}`:'N/A',`=CALC_等级!B${r}`,`=CALC_等级!H${r}`,`=CALC_等级!E${r}`,`=CALC_等级!K${r}`];}),[{col:'B',label:'CR原值'},{col:'D',label:'方案A实现'},{col:'F',label:'方案B实现'},{col:'G',label:'CF历史1–300',until:331}],5030);s.getRange('H32:K5031').setNumberFormat('#,##0');
s=front(names[4],'最大Bet / $1等值Bet：本轮不调整','两方案仅调整拟议升级门槛；Bet与金币价值基准均沿用r7013。',['CR等级','最大Bet百万金币','1USD等值Bet百万金币','最大Bet美元','原levelUpType','原levelUpExp','EXP/Spin'],d.levels.map((v,j)=>{const t=4+j;return [v[0],`=SRC!U${t}/1000000`,`=SRC!V${t}/1000000`,`=SRC!R${t}`,`=SRC!O${t}`,`=SRC!P${t}`,`=SRC!Q${t}`];}),[{col:'B',label:'最大Bet'},{col:'C',label:'$1等值Bet'}],5031,'coins');s.getRange('B32:C5031').setNumberFormat('#,##0.00');s.getRange('E32:G5031').setNumberFormat('#,##0.00');
s=front(names[5],'升级消耗返还：奖励不变，分母随候选成本变化','返还率=原升级奖励USD / 候选机器理论净耗USD；不是RTP，低成本可能产生高返还。',['CR等级','CR原返还率','方案A返还率','方案B返还率','原奖励USD','CR旧净耗USD','A实现净耗USD','B实现净耗USD'],d.levels.map((v,j)=>{const r=2+j;return [v[0],j<4999?`=CALC_等级!O${r}/CALC_等级!N${r}`:'N/A',`=CALC_等级!G${r}`,`=CALC_等级!M${r}`,`=CALC_等级!O${r}`,`=CALC_等级!N${r}`,`=CALC_等级!F${r}`,`=CALC_等级!L${r}`];}),[{col:'B',label:'CR原值'},{col:'C',label:'方案A'},{col:'D',label:'方案B'}],5030,'pct');s.getRange('B32:D5031').setNumberFormat('0.0%');
s=front(names[6],'档位膨胀：保形归一到100%→500%','30档现有形状唯一匹配；PriceSetting真相源Gate未通过，本页方案未写任何价格配置。',['档位序号','标价USD','原相对最低档','保形候选','旧基准金币','新基准金币_方案','相邻档倍率','关联金币行数','实际修改行数'],d.tiers.map((v,j)=>{const r=32+j,t=4+j;return [v[0],`=SRC!AB${t}/100`,`=SRC!AC${t}`,`=1+4*(C${r}-SRC!$AO$9)/(SRC!$AO$10-SRC!$AO$9)`,`=SRC!AD${t}`,`=E${r}*D${r}/C${r}`,j?`=D${r}/D${r-1}`:'N/A',`=SRC!AG${t}`,0];}),[{col:'C',label:'原形状'},{col:'D',label:'保形归一方案'}],61,'pct');s.getRange('B32:B61').setNumberFormat('"$"0.00');s.getRange('C32:D61').setNumberFormat('0%');s.getRange('E32:F61').setNumberFormat('#,##0');s.getRange('G32:G61').setNumberFormat('0.0000"x"');s.getRange('H32:I61').setNumberFormat('0');
s=front(names[7],'等级膨胀：CR / CF共同1–300级一致','共同区间No Change；301–5000保留CR现值，缺少CF证据，不能宣称全5000级验证通过。',['CR等级','CR等级倍率','CF等级倍率','相对差','验证状态'],d.levels.map((v,j)=>{const r=j+32,t=j+2;return [v[0],`=CALC_等级!P${t}`,`=CALC_等级!Q${t}`,j<300?`=B${r}/C${r}-1`:'N/A',j<300?'一致 No Change':'CF无来源；保留CR现值'];}),[{col:'B',label:'CR等级膨胀'},{col:'C',label:'CF等级膨胀',until:331}],331,'mult');s.getRange('B32:C5031').setNumberFormat('0.00"x"');s.getRange('D32:D5031').setNumberFormat('0.0%');
const o=wb.worksheets.getItem(names[0]);o.showGridLines=false;o.getRange('A1:L27').format={font:{name:'Microsoft YaHei',size:12,color:'#24364B'},columnWidth:16,rowHeight:30,wrapText:true};
o.mergeCells('A1:L2');o.getRange('A1').values=[['CR调优候选：POP VIP + CF体验 + 档位保形归一']];o.getRange('A1:L2').format={fill:'#1F4E78',font:{size:20,bold:true,color:'#FFFFFF'}};
for(const [r,text] of [[4,'结论：本轮是可复核候选包，配置发布条件尚未满足。'],[6,'VIP：前10档照指定值；11–15按POP高阶趋势外推，全部门槛单调。'],[8,'VIP1=0：登录校正会进入VIP1；加0经验直接返回，跨入口一致性及客户端未运行验证。'],[10,'LevelCfg：正式历史表无唯一300→5000映射。A全段拉伸 / B前100保留，两套待选。'],[12,'PriceSetting：查询服务已标废弃；当前价格服务读PriceCheatSheet，未确认制作生成链。'],[14,'档位：旧30档形状已匹配，只展示保形100%→500%方案；同档比例和VIP倍率保留。'],[16,'等级膨胀：1–300全部一致，No Change；300级以后CF无证据，不外推确认。'],[18,'配置文件：candidate/VipCfg为有安全Gate的候选；withheld中两表是未修改基线。'],[20,'拟合：以VIP10锚点，对Tier6–10的对数门槛作最小二乘；11–15为外推假设。'],[22,'本包未提交SVN、未冻结、未发布。r7013源表、VIP权益、Bet、奖励均未改。'],[24,'Review重点：VIP零门槛升级行为、等级映射选择、正确价格制作表及生成链。']]){o.mergeCells(`A${r}:L${r+1}`);o.getRange(`A${r}`).values=[[text]];o.getRange(`A${r}:L${r+1}`).format.fill=r===4?'#FFF2CC':r%4===0?'#EDF3F8':'#FFFFFF';}
wb.recalculate();await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(dir,'CR_调优候选_vs_CF_POP_数值曲线.xlsx'));
// Preserve the original configuration workbook and its schema; edit only needExp in the controlled copy.
const vipBook=await SpreadsheetFile.importXlsx(await FileBlob.load(d.source_vip));
vipBook.worksheets.getItem('Sheet1').getRange('B5:B19').values=d.vip.map(r=>[r[2]]);
await (await SpreadsheetFile.exportXlsx(vipBook)).save(path.join(dir,'candidate','VipCfg.xlsx'));
console.log('Exported curve workbook and gated VipCfg candidate; withheld baseline copies are unchanged.');
