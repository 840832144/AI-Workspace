// Controlled review report only. Configuration copies are written by the native exact-edit script.
import fs from 'node:fs/promises';import path from 'node:path';import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const [input,out]=process.argv.slice(2),d=JSON.parse(await fs.readFile(input,'utf8'));
const wb=Workbook.create();for(const n of ['候选说明','等级_概览','等级_明细','商城档位','SRC','CALC'])wb.worksheets.add(n);
const col=n=>{let x='';for(;n;n=Math.floor((n-1)/26))x=String.fromCharCode(65+(n-1)%26)+x;return x;};
function put(s,start,rows){const m=start.match(/([A-Z]+)(\d+)/);let c=0;for(const x of m[1])c=c*26+x.charCodeAt(0)-64;const r=+m[2];s.getRange(`${col(c)}${r}:${col(c+rows[0].length-1)}${r+rows.length-1}`).values=rows.map(a=>a.map(x=>typeof x==='string'&&x.startsWith('=')?null:x??'N/A'));for(let j=0;j<rows[0].length;j++){let i=0;while(i<rows.length){if(typeof rows[i][j]!=='string'||!rows[i][j].startsWith('=')){i++;continue;}const a=i,f=[];while(i<rows.length&&typeof rows[i][j]==='string'&&rows[i][j].startsWith('='))f.push([rows[i++][j]]);s.getRange(`${col(c+j)}${r+a}:${col(c+j)}${r+i-1}`).formulas=f;}}}
const src=wb.worksheets.getItem('SRC'),calc=wb.worksheets.getItem('CALC');
put(src,'A1',[['CR dev r'+d.revision+' source snapshots; CF 2026-09-22 measured anchors; historical CF is comparison only']]);
put(src,'A3',[['等级','候选最大Bet','候选EXP/Spin','候选门槛','CF原始/拟合门槛','CF标准化Spin','候选理论Spin','候选等级倍率','模式','旧最大Bet','旧Spin','旧coins/USD','旧CF门槛代理','门槛依据','倍率依据','Bet依据']]);put(src,'A4',d.rows);
put(src,'R3',[['money分','User取整USD','旧档位倍数','新档位倍数','基础coins/USD','新SKU金币','源行']]);put(src,'R4',d.tiers);
put(src,'AA3',[['驱动','值']]);put(src,'AA4',[['经验换算分母金币',d.coin_unit],['基础coins/USD',d.base_coins_usd],['CR净耗率',d.cr_loss],['CF净耗率假设',d.cf_loss],['125级后倍率','保留dev原值']]);
put(calc,'A3',[['等级','理论Spin','整Spin','毛下注金币','毛下注USD','CR净耗USD','CF假设净耗USD','理论Spin差','新/旧CF门槛代理','候选经验倍率','cf原始exp/Spin','旧CR净耗USD']]);
put(calc,'A4',d.rows.map((v,i)=>{const r=i+4,l=i+1,has=l<5000;return [l,has?`=IF(SRC!I${r}=1,SRC!D${r},SRC!D${r}/SRC!C${r})`:'N/A',has?`=ROUNDUP(B${r},0)`:'N/A',has?`=B${r}*SRC!B${r}`:'N/A',has?`=D${r}/(SRC!$AB$5*SRC!H${r})`:'N/A',has?`=E${r}*SRC!$AB$6`:'N/A',has?`=E${r}*SRC!$AB$7`:'N/A',l>=6&&has?`=B${r}-P${r}`:'N/A',l>=6&&l<=300?`=SRC!E${r}/SRC!M${r}`:'N/A',l>=6&&has?`=SRC!D${r}/SRC!E${r}`:'N/A',`=SRC!B${r}/3`,has?`=SRC!K${r}*SRC!J${r}/SRC!L${r}*SRC!$AB$6`:'N/A'];}));
put(calc,'M3',[['原dev毛下注USD','上版CF拟合毛下注USD','新减原dev USD','本轮采用目标Spin']]);
put(calc,'M4',d.rows.map((v,i)=>{const r=i+4,l=i+1,has=l<5000;return [has?`=SRC!K${r}*SRC!J${r}/SRC!L${r}`:'N/A',l>=6&&has?`=ROUND(SRC!E${r}*3/SRC!$AB$4,0)*SRC!$AB$4/(SRC!$AB$5*SRC!H${r})`:'N/A',has?`=E${r}-M${r}`:'N/A',has?(l>=d.restore_from_level?`=M${r}*SRC!$AB$5*SRC!H${r}/SRC!B${r}`:`=SRC!F${r}`):'N/A'];}));
function front(name,title,notes,headers,rows,start=8){const s=wb.worksheets.getItem(name),end=start+rows.length-1,w=Math.max(12,headers.length);s.showGridLines=false;s.freezePanes.unfreeze();s.tabColor='#205A72';s.getRange(`A1:${col(w)}${Math.max(end,50)}`).format={font:{name:'Microsoft YaHei',size:11,color:'#263B48'},rowHeight:24,columnWidth:17,verticalAlignment:'center'};s.getRange('A:A').format.columnWidth=11;for(const r of [1,2,3,4])s.mergeCells(`A${r}:L${r}`);put(s,'A1',[[title]]);s.getRange('A1:L1').format={fill:'#205A72',font:{size:18,bold:true,color:'#FFFFFF'},rowHeight:38};for(let i=0;i<3;i++)put(s,`A${i+2}`,[[notes[i]||'']]);s.getRange('A2:L4').format={rowHeight:29,wrapText:true,font:{size:11,color:'#526674'}};put(s,`A${start-1}`,[headers]);s.getRange(`A${start-1}:${col(headers.length)}${start-1}`).format={fill:'#DDECEF',font:{bold:true},rowHeight:52,wrapText:true,horizontalAlignment:'center'};put(s,`A${start}`,rows);s.getRange(`A${start}:${col(headers.length)}${end}`).format.horizontalAlignment='right';s.getRange(`B${start}:${col(headers.length)}${end}`).setNumberFormat('#,##0.00');return s;}
const notes=['固定输入dev r'+d.revision+'；User已批准提交dev检查，实际提交版本以回执为准。VIP配置不动。',`当前${d.restore_from_level}级起恢复原dev美元消耗；前段保留CF标准拟合。经验统一小整数，最小档1点。`,'净耗保留CR 5% / CF 15%历史模型；未调整RTP。125级后等级膨胀保留dev原节点/数值。'];
const headers=['当前等级','最大解锁Bet','理论Spin','毛下注 USD','CR理论净耗 USD','CF假设净耗 USD','等级膨胀','候选EXP/Spin','候选升级门槛','CF原始/旧拟合门槛','采用目标Spin','目标Spin差','依据','原dev毛下注 USD','新减原dev USD'];
function display(levels,start){return levels.map((l,i)=>{const r=l+3;return [l,`=SRC!B${r}`,`=CALC!B${r}`,`=CALC!E${r}`,`=CALC!F${r}`,`=CALC!G${r}`,`=SRC!H${r}`,`=SRC!C${r}`,`=SRC!D${r}`,`=SRC!E${r}`,`=CALC!P${r}`,`=CALC!H${r}`,d.rows[l-1][13],`=CALC!M${r}`,`=CALC!O${r}`];});}
let s=front('候选说明','CR等级对齐CF：5000级受控候选',notes,['项目','当前方案','验收边界'],[
 ['经验单位','CF原始点数×3÷10000','门槛与每Spin经验同比缩放'],
 ['经验差异','102条按1/3规则取整拟合','User已决定，不再阻塞候选；不改原始证据'],
 ['后段难度',`${d.restore_from_level}级起恢复原dev美元消耗`,'用新经验单位/币率反算门槛，保留整数舍入差'],
 ['Bet拟合','L30/35/40/50线性趋势，后段25级节点','按现有Bet档取下界；未知档仅候选'],
 ['等级倍率','已知段随CF；125+保留dev原值','User指定沿用原节点/数值，不冒称最新CF实测'],
 ['基础兑换','最低50万→最高150万金币/USD','全部.99价格向上取整为美元；等级/VIP另乘'],
 ['价格路径','PriceCheatSheet候选','PriceSetting退役路径不修改；钻石保持原值'],
 ['早期缺口','L1–L5无完整当前CF升级门槛','保留现有CR Spin；L1–L4 Bet保持'],
 ['共享影响','4个共用Bet金额及经验字段改变','普通解锁调整；HighRoller解锁行不改，但共用金额/EXP改变'],
 ['验证身份','配置和数学候选','未运行客户端，不代表已验收或已提交'],
 ['下一步','User已批准直接提交dev检查','按正式流程提交；不提交trunk、不冻结/发布、不合并/finalize']]);
s.getRange('B:B').format.columnWidth=47;s.getRange('C:C').format.columnWidth=75;s.getRange('A8:C18').format={wrapText:true,rowHeight:43,horizontalAlignment:'left'};
s=front('等级_概览','等级概览：仅最大Bet解锁等级',notes,headers,display(d.overview,8));
const ovEnd=d.overview.length+7;
const detail=front('等级_明细','等级明细：1–5000逐级',notes,headers,display(d.rows.map(r=>r[0]),8));
for(const [sheet,end]of [[s,ovEnd],[detail,5007]]){sheet.getRange(`B8:B${end}`).setNumberFormat('#,##0');sheet.getRange(`D8:F${end}`).setNumberFormat('"$"#,##0.00');sheet.getRange(`G8:J${end}`).setNumberFormat('#,##0');sheet.getRange(`N8:N${end}`).setNumberFormat('"$"#,##0.00');sheet.getRange(`O8:O${end}`).setNumberFormat('0.000000');sheet.getRange('M:M').format.columnWidth=58;}
function line(sheet,title,labels,rows,from,to,fmt,first='AA'){const c=27;put(sheet,`${first}${from}`,[['等级',...labels],...rows]);const chart=sheet.charts.add('line',sheet.getRange(`${first}${from}:${col(c+labels.length)}${from+rows.length}`));chart.setPosition(`A${to}`,`L${to+20}`);chart.title=title;chart.titleTextStyle.fontSize=14;chart.titleTextStyle.typeface='Microsoft YaHei';chart.legend={position:'top',textStyle:{typeface:'Microsoft YaHei',fontSize:11}};chart.xAxis={axisType:'textAxis',tickLabelInterval:rows.length>50?25:5};chart.yAxis={numberFormatCode:fmt,numberFormatSourceLinked:false};for(const [i,se]of chart.series.items.entries())se.line={fill:['#2864AE','#D47620','#438B79'][i],width:2,style:i===1?'dashed':'solid'};}
line(s,'L6–L299升级Spin：候选与本轮目标',['CR候选','采用目标（272+原dev成本）'],Array.from({length:294},(_,i)=>{const r=i+9;return [i+6,`=CALC!B${r}`,`=CALC!P${r}`];}),1,ovEnd+4,'0.0');
line(s,'最大Bet：dev现值与候选（1–300级）',['dev现值','CF对齐候选'],Array.from({length:300},(_,i)=>[i+1,`=SRC!J${i+4}`,`=SRC!B${i+4}`]),320,ovEnd+28,'#,##0');
for(const [count,from,to,title]of [[300,650,ovEnd+52,'升级美元消耗：1–300级衔接'],[4999,1000,ovEnd+76,'升级美元消耗：完整1–4999级']])line(s,title,['原dev','上版CF拟合','本轮修订'],Array.from({length:count},(_,i)=>[i+1,`=CALC!M${i+4}`,i>=5?`=CALC!N${i+4}`:null,`=CALC!E${i+4}`]),from,to,'$0.00');
s=front('商城档位','基础商城兑换：50万→150万金币/USD',[
 '中间30档按当前正式形状保形归一到1→3倍；不默认线性。等级与VIP倍率另乘。',
 'User口径：所有.99档位按取整美元计算，例如$0.99→$1、$4.99→$5、$99.99→$100。',
 'PriceCheatSheet priceType=9调整SKU；priceType=17保持线性基础兑值50万。非金币不变。'],
 ['原标价（分）','取整 USD','原档位倍数','候选档位倍数','基础金币/USD','候选SKU金币','最低档比例'],d.tiers.map((v,i)=>{const r=i+4,t=i+8;return [`=SRC!R${r}`,`=SRC!S${r}`,`=SRC!T${r}`,`=SRC!U${r}`,`=SRC!V${r}`,`=SRC!W${r}`,`=E${t}/SRC!$AB$5`];}));
s.getRange('B8:B37').setNumberFormat('"$"0.00');s.getRange('E8:F37').setNumberFormat('#,##0');
line(s,'商城档位基础coins/USD（等级/VIP另乘）',['候选'],d.tiers.map((v,i)=>[v[1],`=E${i+8}`]),1,41,'#,##0');
wb.recalculate();await fs.writeFile(path.join(out,'report-inspect.local.ndjson'),(await wb.inspect({kind:'table',range:"'等级_明细'!A13:L17",include:'values,formulas',tableMaxRows:5,tableMaxCols:12})).ndjson);
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,'CR_CF_等级对齐候选_5000级.xlsx'));console.log('Candidate report authored');
