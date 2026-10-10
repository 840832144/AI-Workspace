// Controlled workbook only; never writes game configurations or source files.
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const out=process.argv[2],d=JSON.parse(await fs.readFile(path.join(out,'inputs.controlled.json'),'utf8'));
if(process.argv[3]==='render-cf'){
 const imported=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(out,d.book)));
 const im=await imported.render({sheetName:'CF明细',range:'A5:O13',scale:1.2,format:'png'});
 await fs.writeFile(path.join(out,'cf-readback.png'),new Uint8Array(await im.arrayBuffer()));
 console.log('CF final file readback rendered');process.exit(0);
}
const wb=Workbook.create(),names=['结论与参数','等级段对比','Bet曲线','VIP对比','CR调整候选','CR明细','CF明细','POP明细','SRC_等级','SRC_档位','SRC_VIP','SRC_POP'];
names.forEach(n=>wb.worksheets.add(n));
const sheet=n=>wb.worksheets.getItem(n),col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
function write(s,start,rows){
 const r0=+start.match(/\d+/)[0];let c0=0;for(const c of start.match(/[A-Z]+/)[0])c0=c0*26+c.charCodeAt(0)-64;
 s.getRange(`${col(c0)}${r0}:${col(c0+rows[0].length-1)}${r0+rows.length-1}`).values=rows.map(r=>r.map(v=>typeof v==='string'&&v.startsWith('=')?null:v??'N/A'));
 for(let j=0;j<rows[0].length;j++){let i=0;while(i<rows.length){if(typeof rows[i][j]!=='string'||!rows[i][j].startsWith('=')){i++;continue;}const a=i,f=[];while(i<rows.length&&typeof rows[i][j]==='string'&&rows[i][j].startsWith('='))f.push([rows[i++][j]]);s.getRange(`${col(c0+j)}${r0+a}:${col(c0+j)}${r0+i-1}`).formulas=f;}}
}
function base(n,title,note,rows=50,cols=12){const s=sheet(n);s.showGridLines=false;s.freezePanes.unfreeze();s.getRange(`A1:${col(cols)}${rows}`).format={font:{name:'Microsoft YaHei',size:11,color:'#273444'},rowHeight:25,columnWidth:16,verticalAlignment:'center'};s.getRange('A:A').format.columnWidth=10;s.getRange('A2').values=[[title]];s.getRange('A2:L2').format={font:{bold:true,size:18,color:'#183654'},rowHeight:37};s.getRange('A3').values=[[note]];s.getRange('A3:L3').format={font:{size:10,color:'#64748B'},rowHeight:29};s.tabColor=n.startsWith('SRC')?'#BCC5D0':'#294C73';return s;}
function table(s,heads,rows,name){write(s,'A5',[heads]);write(s,'A6',rows);s.getRange(`A5:${col(heads.length)}5`).format={fill:'#294C73',font:{bold:true,color:'#FFFFFF'},rowHeight:58,wrapText:true};s.tables.add(`A5:${col(heads.length)}${rows.length+5}`,true,name);}
function num(s,r,f='#,##0'){s.getRange(r).setNumberFormat(f);s.getRange(r).format.horizontalAlignment='right';}
function note(s,r,t,last='L'){s.getRange(`A${r}:${last}${r}`).merge();write(s,`A${r}`,[[t]]);s.getRange(`A${r}:${last}${r}`).format={wrapText:true,rowHeight:43,font:{size:11,color:'#43566A'}};}
const P="'结论与参数'!",I="'SRC_等级'!",usd='"$"#,##0.0000';
let s=base('结论与参数','CR / CF / POP：三档Bet与升级消耗',`CR trunk r${d.revision}；POP 10/10 L88包；CF沿用已确认底稿。完整逐级到1500；只作方案比较。`,57,12);
note(s,5,'结论：POP最低Bet的美元成本并非全程更高。等级兑换能力、商城档位与Bet必须放在一起比较。');
note(s,6,'提高CR最低Bet会提高每转消耗；5级起EXP也随Bet同比增加，升一级总毛下注基本不变。1–4级按转数升级，暂保留。');
note(s,7,'POP在50级、75级分别出现11倍、18倍兑换基数；不是只在50级变化一次。89级以后用末档延续情景。');
note(s,8,'推荐Bet统一用“名义100美元余额÷37”试算并限制在上下界；不是已证实的三款游戏默认推荐算法，也未取整到实际档。');
write(s,'A10',[['可调情景','输入值','说明']]);s.getRange('A10:C10').format={fill:'#294C73',font:{bold:true,color:'#FFFFFF'}};
write(s,'A11',[
 ['名义余额 USD',100,'User确认；B11可修改'],['推荐除数',37,'两次样本的近似研究情景，非精确代码'],
 ['POP低档实际标价',1.99,'不套用CR .99名义取整'],['POP低档k',10,'标准低档；活动/VIP另列'],['POP基础M',200000,'最早观测L20；L1–19按同基准假设'],
 ['POP活动额外加成',0,'主对比无促销'],['POP VIP额外加成',0,'主对比VIP0'],['CF基础coins/USD',500000,'沿用已确认基准'],
 ['POP最大Bet线数情景',20,'字段单位未完全闭合；可改50看敏感性'],['POP尾段锚点等级',88,'已知段1–88保留'],
 ['POP锚点升级EXP','=SRC_POP!D93','当前88升89的门槛'],['POP每级趋势增量','=SUMPRODUCT(SRC_POP!F80:F93,SRC_POP!G80:G93)/SUMPRODUCT(SRC_POP!F80:F93,SRC_POP!F80:F93)','75–88固定88锚点一次拟合'],
 ['POP经验取整单位',1000000,'89–1500为长距离估算'],['POP底档Bet参考',50000,'早期20线机台；高等级真实下限未验证'],['CF底档Bet参考',30000,'已有最低档；高等级下限未验证'],
 ['CR EXP/Bet',0.0001,'bet2普通金币机；本轮现值定向验证'],['CF EXP/Bet',1/3,'复用当前底稿，不重新拟合已知段'],['POP EXP/Bet',1,'交接标准付费Spin模型，免费转除外'],
 ['POP历史TP/USD',80,'VIP纯购等值；免费TP不在此分母']
 ]);
 s.getRange('A:A').format.columnWidth=29;s.getRange('B:B').format.columnWidth=20;s.getRange('C:C').format.columnWidth=51;s.getRange('C11:C29').format.wrapText=true;s.getRange('A11:C29').format.rowHeight=36;num(s,'B11:B29','#,##0.0000');num(s,'B16:B17','0%');num(s,'B26:B28','0.000000');
 s.getRange('B11:B12').format={fill:'#FFF2CC',font:{color:'#1D4ED8'}};
 const notes=[
 '口径：每转美元＝Bet÷coins/USD；升级毛下注美元＝本级门槛÷每转经验×Bet÷coins/USD。不是净亏、付费金额或补币需求。',
 'CR 5级起、CF、POP的经验与Bet成比例时，三档理论升级美元相等；向上取整一局的结果另列，假定单级独立、不带入余量。',
 'POP最早商城倍率观测在20级，50级和75级变化有时间线支持。1–19级回推基准、89+延续末档均为情景。',
 'POP最大Bet按包内“每线”字段×20列条件结果；旧20线早段可对照。新机台50线不等于推荐Bet必须达到其上限。',
 'POP/CF最低Bet只用已知底档延续，不把实际玩过的最小投注冒充可选下限；缺少高等级下限页面确认。',
 'POP 1级门槛为交接方按早段规律回填；2–88用已知跨度，包括87级下降。89–1500不代表实测。',
 'CF已知/历史/拟合边界保留在明细来源列；不使用旧促销折扣或将SGD当USD。CR采用已确认名义美元。',
 '建议先审最低Bet候选；只筛普通机台可选档，不改EXP、最大Bet、VIP或其他机台换算。推荐倍率36号参数语义仍需另核。',
 'CR候选提供“美元对齐取现档”和“最低Bet不回退”两列；后者跨50/75级不降档，但会高于POP对齐值，需User选定。',
 '如果目标是升一级更贵，单独改Bet且保持EXP/Bet不变达不到；需另审Bet/EXP关系。本轮不写源配置、不提交SVN。'
 ];notes.forEach((t,i)=>note(s,32+i,t));

 s=base('SRC_等级','三方基础输入与原来源','固定来源仅内嵌数值；CR r7502导出经相关路径核对适用于r7529；CF模型直接复用。',1505,17);
 table(s,['等级','CR门槛类型','CR门槛','CR最小Bet','CR最大Bet','CR coins/USD','CF最大Bet','CF等值升级EXP','CF金币倍率','POP升级EXP','POP上限每线','POP商城M','CR解锁阶段','CF升级来源','CF Bet来源','CF倍率来源','CR来源'],d.level_inputs.map((r,i)=>[...r,...d.cf[i].slice(5,8),`LevelCfg level=${i+1}; SlotsCasinoBetUnlock level=${r[12]}; PriceCheatSheet priceType9/money99/VIP0`]),'SourceLevels');num(s,'B6:M1505');s.getRange('N:Q').format.columnWidth=35;
 s=base('SRC_档位','CR普通机台当前可选池','SlotsCasinoBetUnlock 普通highroller=0；SlotsCasinoBetList bet2与levelExp；未修改源表。',d.bet_pool.length+5,4);
 table(s,['阶段等级','Bet档ID','bet2金币','EXP/Spin'],d.bet_pool,'SourcePools');num(s,`A6:D${d.bet_pool.length+5}`);
 const poolRanges={};d.bet_pool.forEach((r,i)=>{if(!poolRanges[r[0]])poolRanges[r[0]]=[i+6,i+6];else poolRanges[r[0]][1]=i+6;});
 s=base('SRC_POP','POP等级、商城与推荐证据','等级来自ps_levels_full.csv；商城来自ps_store_history.csv并与三段原始级别事件对齐；不修改原文件。',100,17);
 table(s,['等级','到达累计EXP','下一级累计EXP','本级跨度','来源','等级距88','跨度距锚点'],d.pop88.map((r,i)=>[...r,i===0?'交接方规律回填':'L88交接已知',`=A${i+6}-${P}$B$20`,`=D${i+6}-${P}$B$21`]),'SourcePOP');num(s,'B6:D93');num(s,'F6:G93');s.getRange('E:E').format.columnWidth=22;
 write(s,'I5',[['商城观测等级','M','同档99.99金币']]);write(s,'I6',d.store_timeline.map(r=>r.slice(0,3)));num(s,'I6:K10');
 write(s,'I14',[['真实余额','真实推荐Bet','余额/推荐Bet']]);write(s,'I15',d.observed_recommended.map((r,i)=>[r.balance,r.shown_bet,`=I${i+15}/J${i+15}`]));num(s,'I15:J16');num(s,'K15:K16','0.000');
 write(s,'I19',[['最早M观测级','说明'],[20,'L1–19是向前延续情景'],[50,'M由200000到2200000'],[75,'M由2200000到3600000']]);
 s.getRange('J:J').format.columnWidth=32;

 const heads=['等级','最小Bet','推荐Bet情景','最大Bet情景','最小档每转USD','推荐档每转USD','最大档每转USD','最小档升级Spin','推荐档升级Spin','最大档升级Spin','最小档升级USD','推荐档升级USD','最大档升级USD','coins/USD','本级门槛','最小档整局USD','推荐档整局USD','最大档整局USD','适用与证据'];
 for(const [g,n] of ['CR明细','CF明细','POP明细'].entries()){
  s=base(n,`${n.slice(0,-2)}：三档Bet逐级至1500`,`升级美元为本级到下级理论毛下注；推荐统一POP式余额情景。${g===2?'L89+拟合；最低/最高档有条件，见首页。':g===1?'底档延续情景，来源边界见末列。':'普通金币机bet2；1–4级按转数。'}`,1505,19);
  const rows=d.level_inputs.map((v,i)=>{const r=i+6,l=i+1;
   const min=g===0?`=${I}D${r}`:`=${P}$B$${g===1?25:24}`;
   const max=g===0?`=${I}E${r}`:g===1?`=${I}G${r}`:`=${I}K${r}*${P}$B$19`;
   const rate=g===0?`=${I}F${r}`:g===1?`=${I}I${r}*${P}$B$18`:`=${I}L${r}*${P}$B$14/${P}$B$13*(1+${P}$B$16)*(1+${P}$B$17)`;
   const need=g===0?`=${I}C${r}`:g===1?`=${I}H${r}`:l<=88?`=${I}J${r}`:`=ROUND((${P}$B$21+${P}$B$22*(A${r}-${P}$B$20))/${P}$B$23,0)*${P}$B$23`;
   const spin=['B','C','D'].map(c=>g===0?`=IF(${I}B${r}=1,O${r},O${r}/(${c}${r}*${P}$B$26))`:`=O${r}/(${c}${r}*${P}$B$${g+26})`);
   return [l,min,`=MAX(B${r},MIN(D${r},N${r}*${P}$B$11/${P}$B$12))`,max,...['B','C','D'].map(c=>`=${c}${r}/N${r}`),...spin,...['H','I','J'].map((c,k)=>`=${c}${r}*${col(k+2)}${r}/N${r}`),rate,need,...['H','I','J'].map((c,k)=>`=ROUNDUP(${c}${r},0)*${col(k+2)}${r}/N${r}`),g===0?'当前trunk；1–4计数；5+EXP':g===1?`${d.cf[i][5]}；${d.cf[i][7]}；底档未逐级验证`:l<=88?(l===1?'门槛回填；底档延续；最大20线条件':'已知门槛；底档延续；最大20线条件'):'升级拟合；Bet/M末档延续；非实际解锁'];
  });
  table(s,heads,rows,`Model${g}`);num(s,'B6:D1505');num(s,'E6:G1505',usd);num(s,'H6:J1505','#,##0.00');num(s,'K6:M1505',usd);num(s,'N6:O1505');num(s,'P6:R1505',usd);s.getRange('S:S').format.columnWidth=43;
 }

 s=base('等级段对比','相同等级段：最低 / 推荐 / 最高Bet','一段三行；Bet/每转/升级值均取段首等级；段内完成全部升级的毛下注单列，不把段首当整段。',d.stages.length*3+5,15);
 const overview=[];for(const [a,b] of d.stages)for(const [g,n]of['CR明细','CF明细','POP明细'].entries()){const r=a+5;overview.push([a,b,n.slice(0,-2),...['B','C','D','E','F','G','K','L','M'].map(c=>`='${n}'!${c}${r}`),`=SUM('${n}'!K${r}:K${b+5})`,`='${n}'!N${r}`,g===2?'POP上下限/推荐均有情景边界':g===1?'CF底档/推荐情景；已知+历史+拟合':'CR现值；推荐为对比情景']);}
 table(s,['起始级','结束级','游戏','最小Bet','推荐Bet情景','最大Bet情景','最小每转USD','推荐每转USD','最大每转USD','段首最小升级USD','段首推荐升级USD','段首最大升级USD','全段升级毛USD','coins/USD','说明'],overview,'StageComparison');num(s,`D6:F${overview.length+5}`);num(s,`G6:M${overview.length+5}`,usd);num(s,`N6:N${overview.length+5}`);s.getRange('O:O').format.columnWidth=37;

 s=base('CR调整候选','CR最低Bet：先把美元目标落到当前可选档','E为价值对齐取档；N为不回退候选。L1–4保留。其余EXP/最大Bet/机台系数不动；没有写入配置。',1505,16);
 table(s,['等级','当前最低Bet','当前coins/USD','POP对齐金币目标','对齐后的现档Bet','候选每转USD','POP底档每转USD','候选/POP','候选升级Spin','候选升级毛USD','原升级毛USD','总成本倍率','当前解锁阶段','不回退最低Bet','不回退每转USD','不回退/POP'],d.level_inputs.map((v,i)=>{const r=i+6,[a,b]=poolRanges[v[12]],rng=`'SRC_档位'!$C$${a}:$C$${b}`;return [i+1,`='CR明细'!B${r}`,`='CR明细'!N${r}`,`='POP明细'!E${r}*C${r}`,`=IF(A${r}<5,B${r},IF(COUNTIF(${rng},">="&D${r})>0,_xlfn.MINIFS(${rng},${rng},">="&D${r}),MAX(${rng})))`,`=E${r}/C${r}`,`='POP明细'!E${r}`,`=F${r}/G${r}`,`=IF(${I}B${r}=1,${I}C${r},${I}C${r}/(E${r}*${P}$B$26))`,`=I${r}*F${r}`,`='CR明细'!K${r}`,`=J${r}/K${r}`,v[12],i===0?`=E${r}`:`=MIN('CR明细'!D${r},MAX(N${r-1},E${r}))`,`=N${r}/C${r}`,`=O${r}/G${r}`];}),'Candidate');num(s,'B6:E1505');num(s,'F6:G1505',usd);num(s,'H6:I1505','0.00');num(s,'J6:K1505',usd);num(s,'L6:L1505','0.0000"倍"');num(s,'N6:N1505');num(s,'O6:O1505',usd);num(s,'P6:P1505','0.00"倍"');

 s=base('SRC_VIP','VIP原输入','CR当前配置；CF既有当前口径；POP1–7当前截图、8–10历史门槛。',35,21);
 s.getRange('U:U').format.columnWidth=32;
 write(s,'A5',[['CR VIP','门槛']]);write(s,'A6',d.vip);write(s,'D5',[['CR VIP','金币包','VIP0包']]);write(s,'D6',d.cr_packages);write(s,'H5',[['CF VIP','门槛']]);write(s,'H6',d.cf_vip);write(s,'K5',[['CF VIP','Coin Packages']]);write(s,'K6',d.cf_packages);write(s,'N5',[['USD价格','VIP点','点/USD']]);write(s,'N6',d.shops.map((r,i)=>[...r,`=O${i+6}/N${i+6}`]));write(s,'A25',[['CR points/USD',d.cr_vip_points_usd]]);write(s,'R5',[['POP Tier','门槛TP','加成','来源']]);write(s,'R6',d.pop_vip);num(s,'T6:T15','0%');
 s=base('VIP对比','VIP：消费门槛与金币包权益','同编号不代表同权益。纯购等值非实际付款；POP 8–10门槛为历史，金币加成为趋势估算。',77,10);
 table(s,['VIP序号','CR门槛USD','CF门槛最低USD','CF门槛最高USD','POP门槛USD','CR金币倍率','CF金币倍率','POP金币倍率'],Array.from({length:15},(_,i)=>{const r=i+6,t=i+1;return[t,`=SRC_VIP!B${r}/SRC_VIP!$B$25`,i<d.cf_vip.length?`=SRC_VIP!I${r}/MAX(SRC_VIP!P6:P${5+d.shops.length})`:'N/A',i<d.cf_vip.length?`=SRC_VIP!I${r}/MIN(SRC_VIP!P6:P${5+d.shops.length})`:'N/A',i<10?`=SRC_VIP!S${r}/${P}$B$29`:'N/A',`=SRC_VIP!E${r+1}/SRC_VIP!F${r+1}`,i<d.cf_packages.length?`=SRC_VIP!L${r}/SRC_VIP!$L$6`:'N/A',i<7?`=1+SRC_VIP!T${r}`:i<10?`=1+SRC_VIP!$T$12+(A${r}-SRC_VIP!$R$12)*(SRC_VIP!$T$12-SRC_VIP!$T$11)`:'N/A'];}),'VIPComparison');num(s,'B6:E20','"$"#,##0');num(s,'F6:H20','0.00"倍"');
 function chart(s,title,series,a,b,fmt){const c0=27+s.charts.items.length*6;write(s,`${col(c0)}5`,[['等级',...series.map(v=>v.label)]]);const max=Math.max(...series.map(v=>v.end));write(s,`${col(c0)}6`,Array.from({length:max},(_,i)=>[i+1,...series.map(v=>i<v.end?`='${v.sheet}'!${v.column}${i+6}`:null)]));const c=s.charts.add('line',s.getRange(`${col(c0)}5:${col(c0+series.length)}${max+5}`));c.setPosition(a,b);c.title=title;c.titleTextStyle.fontSize=14;c.titleTextStyle.typeface='Microsoft YaHei';c.legend={position:'top',textStyle:{typeface:'Microsoft YaHei',fontSize:10}};c.xAxis={axisType:'textAxis',tickLabelInterval:max>100?150:1,textStyle:{fontSize:9}};c.yAxis={numberFormatCode:fmt,numberFormatSourceLinked:false,textStyle:{fontSize:10}};c.series.items.forEach((v,i)=>{v.formula=`'${series[i].sheet}'!${series[i].column}6:${series[i].column}${series[i].end+5}`;v.categoryFormula=`'${series[i].sheet}'!A6:A${series[i].end+5}`;v.line={fill:series[i].color??['#2864AE','#D57B28','#279581'][i],width:2,style:series[i].dash?'dashed':'solid'};});}
 chart(s,'VIP消费门槛（USD；POP高阶含历史）',[{sheet:'VIP对比',column:'B',end:15,label:'CR当前'},{sheet:'VIP对比',column:'C',end:d.cf_vip.length,label:'CF低',color:'#D57B28'},{sheet:'VIP对比',column:'D',end:d.cf_vip.length,label:'CF高',color:'#D9B381',dash:true},{sheet:'VIP对比',column:'E',end:10,label:'POP标称',color:'#279581'}],'A23','L46','$#,##0');
 chart(s,'金币包倍率（POP8–10为估算）',[{sheet:'VIP对比',column:'F',end:15,label:'CR当前'},{sheet:'VIP对比',column:'G',end:d.cf_packages.length,label:'CF参考'},{sheet:'VIP对比',column:'H',end:10,label:'POP含拟合'}],'A49','L73','0.0"倍"');
 s=base('Bet曲线','美元成本与等级兑换能力','全1500逐级点；尾段依赖拟合与末档延续。POP底档/最大档为条件情景，不能当作完整服务器配置。',139,12);
 const chartdefs=[['最低档：每转USD','E',6],['推荐情景：每转USD（100美元余额）','F',32],['最大档：每转USD（POP20线条件）','G',58],['升一级：理论毛下注USD（最低档）','K',84]];
 for(const[t,c,r]of chartdefs)chart(s,t,['CR明细','CF明细','POP明细'].map((n,i)=>({sheet:n,column:c,end:1500,label:(c==='F'?['CR统一情景','CF统一情景','POP近似情景']:['CR现值','CF底稿/情景','POP已知/拟合/情景'])[i]})),`A${r}`,`L${r+23}`,'$#,##0.00');
 write(s,'AA1510',[['等级','CR倍率','CF倍率','POP商城基数倍数']]);write(s,'AA1511',d.level_inputs.map((v,i)=>[i+1,`='SRC_等级'!F${i+6}/'SRC_等级'!$F$6`,`='SRC_等级'!I${i+6}`,`='SRC_等级'!L${i+6}/${P}$B$15`]));
 // Reuse chart helper's native line setup, then bind the multiplier ranges.
 chart(s,'等级兑换倍数：POP50级与75级两次观测',['CR明细','CF明细','POP明细'].map((n,i)=>({sheet:n,column:'N',end:1500,label:['CR','CF含拟合','POP89+末档延续'][i]})),'A110','L133','0"倍"');
 s.charts.items[4].series.items.forEach((v,i)=>{v.formula=`'Bet曲线'!${col(28+i)}1511:${col(28+i)}3010`;v.categoryFormula="'Bet曲线'!AA1511:AA3010";});

 wb.recalculate();
 const ctl=sheet('结论与参数'),model=sheet('CR明细'),r=55;
 const before=model.getRange(`C${r}`).values[0][0],cost=model.getRange(`L${r}`).values[0][0],floor=model.getRange(`B${r}`).values[0][0];
 ctl.getRange('B11').values=[[1]];wb.recalculate();
 if(model.getRange(`C${r}`).values[0][0]===before||Math.abs(model.getRange(`L${r}`).values[0][0]-cost)>1e-7||model.getRange(`B${r}`).values[0][0]!==floor)throw Error('Balance scenario dependency check failed '+JSON.stringify({before,after:model.getRange(`C${r}`).values,cost,costAfter:model.getRange(`L${r}`).values,floor,floorAfter:model.getRange(`B${r}`).values}));
 ctl.getRange('B11').values=[[100]];wb.recalculate();
 if(model.getRange(`C${r}`).values[0][0]!==before)throw Error('Balance restore failed');
 await fs.writeFile(path.join(out,'recalculation.json'),JSON.stringify({balance_input_responded:true,level_gross_unchanged_in_EXP_mode:true,minimum_unchanged:true,restored:true}));
 await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,d.book));
 const views=[['结论与参数','A2:L8','summary'],['结论与参数','A10:C29','inputs'],['等级段对比','A5:O14','stages'],['CR调整候选','A5:P16','candidate'],['CR明细','A5:O12','cr'],['CF明细','A5:O12','cf'],['POP明细','A50:O58','pop50'],['SRC_等级','A5:M9','source'],['SRC_档位','A5:D13','pool'],['SRC_POP','I5:K22','pop-source'],['SRC_VIP','R5:U15','vip-source'],['VIP对比','A5:H15','vip'],['VIP对比','A23:L73','vip-charts'],['Bet曲线','A6:L29','minimum-chart'],['Bet曲线','A32:L55','recommended-chart'],['Bet曲线','A58:L81','maximum-chart'],['Bet曲线','A84:L107','upgrade-chart'],['Bet曲线','A110:L133','inflation-chart']];
 const selected=process.argv[3]==='labels-only'?views.filter(v=>['recommended-chart','vip-source'].includes(v[2])):views;
 for(const[n,range,name]of selected){const im=await wb.render({sheetName:n,range,scale:1.2,format:'png'});await fs.writeFile(path.join(out,`${name}.png`),new Uint8Array(await im.arrayBuffer()));}
 console.log(JSON.stringify({book:d.book,sheets:names.length,charts:7,rendered:selected.length}));
