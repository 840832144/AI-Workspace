// Optional POP extension to the existing CR/CF author; no source or config writes.
import fs from 'node:fs/promises';
import path from 'node:path';

export async function addPopComparison(ctx){
 const {wb,d,base,write,header,table,num,chart,col,sheet,out}=ctx,p=d.pop;
 let s=base('SRC_POP','POP交接包输入','10/09提供的等级/商城/VIP；高阶VIP门槛另用历史正式截图，不改原始文件。',48,16);
 table(s,5,['等级','到达累计EXP','升下一级累计EXP','本级EXP跨度','已知最大Bet'],p.levels,'POPLevels');
 write(s,'H5',[['Tier','累计TP','金币包加成','来源']]);write(s,'H6',p.vip);
 write(s,'M5',[['标价USD','金币','coins/USD']]);
 write(s,'M6',p.store.map((r,i)=>[...r,`=N${i+6}/M${i+6}`]));
 num(s,'B6:E46','#,##0');num(s,'J6:J15','0.0%');num(s,'M6:O11','#,##0.00');
 s.getRange('K:K').format.columnWidth=24;
 s.getRange('B:C').format.columnWidth=22;s.getRange('D:E').format.columnWidth=18;

 s=base('POP拟合说明','POP：已知段保留，缺失段单独估算','升级、Bet、商城兑换是不同口径；尾段只供横向研究，不能当作真实配置。',44,12);
 s.getRange('A:A').format.columnWidth=29;s.getRange('B:B').format.columnWidth=21;
 write(s,'A6',[
  ['拟合衔接等级',41],
  ['衔接升级EXP','=SRC_POP!D46'],
  ['每级增加EXP','=SUMPRODUCT(F22:F33,G22:G33)/SUMPRODUCT(F22:F33,F22:F33)'],
  ['EXP取整单位',p.xp_rounding],
  ['衔接最大Bet','=SRC_POP!E46'],
  ['每级Bet趋势增量','=SUMPRODUCT(I22:I48,J22:J48)/SUMPRODUCT(I22:I48,I22:I48)'],
  ['估算Bet取整步长',p.bet_step],
  ['VIP历史标称TP/USD',p.historical_tp_usd],
  ['VIP金币加成每Tier增量','=SRC_POP!J9-SRC_POP!J8'],
  ['商城低档coins/USD','=SRC_POP!O6'],
  ['商城高档coins/USD','=SRC_POP!O11'],
  ['商城档位倍率','=B16/B15'],
  ['普通付费Spin EXP/Bet',1]
 ]);num(s,'B6:B18','#,##0.0000');
 const notes=[
  'L1–41直接保留交接包。L41是当前等级，跨度指41升42，不是已跑完41级。',
  '早段指数、过渡整数档、后段增长分别保留；不把早段指数外推到1500级。',
  'L42+以L41为锚，按L30–41固定锚点的一次趋势估算，并按输入单位取整。',
  'Bet L1–3沿用包内基础档；L4/15/25是已知解锁；L25–41保留观测上限。',
  'Bet L42+按L15–41上限趋势估算，含已知平台期；不是实际解锁节点。',
  '升级Spin＝本级EXP跨度÷每Spin EXP；标准付费Spin暂沿用交接方EXP=Bet模型。',
  '逐局导出的Bet由EXP差反推，不能用它独立证明EXP=Bet；免费转不纳入。',
  '主美元列＝毛下注÷低档商城coins/USD；高档兑换另列，不等于实付或净耗。',
  '商城是采样时报价，等级/VIP影响未拆清；不再额外乘未知倍率。',
  '等级金币倍率无跨等级商城证据，保留N/A；经验跨度增长另画，不混用。',
  'VIP1–4来自本轮界面；5–10门槛沿用历史正式截图，当前有效性待确认。',
  'VIP5–10金币加成按3→4的增量外推；只作候选趋势，非已验证权益。',
  'VIP纯购美元用历史80TP/USD；免费TP和跨游戏积分可降低真实支出。',
  '新包商城gems字段命名存疑；本表不用该字段推导VIP点或额外货币价值。',
  '升级经验累计：到达41级用start_xp；next_xp是到达42级，避免错一档。',
  '不使用充值过滤假设估计RTP；未启动采集、购买或修改任何配置。'
 ];
 for(let i=0;i<notes.length;i++){
  const r=i+22;s.getRange(`A${r}:E${r}`).merge();write(s,`A${r}`,[[notes[i]]]);
  s.getRange(`A${r}:E${r}`).format={wrapText:true,rowHeight:41,font:{size:10,color:'#43566A'}};
 }
 write(s,'F20',[['等级差','经验差']]);
 write(s,'F22',Array.from({length:12},(_,i)=>{const r=35+i;return [`=SRC_POP!A${r}-$B$6`,`=SRC_POP!D${r}-$B$7`];}));
 write(s,'I20',[['等级差','Bet差']]);
 write(s,'I22',Array.from({length:27},(_,i)=>{const r=20+i;return [`=SRC_POP!A${r}-$B$6`,`=SRC_POP!E${r}-$B$10`];}));

 s=base('POP模型','POP逐级计算 至1500','L1–41原表；L42+经验与Bet分别估算；不含免费Spin、经验Buff或实际付款。',1505,13);
 const popRows=Array.from({length:1500},(_,i)=>{
  const l=i+1,r=l+5,control="'POP拟合说明'!";
  return [l,l<=41?`=SRC_POP!E${r}`:`=ROUNDDOWN((${control}$B$10+${control}$B$11*(A${r}-${control}$B$6))/${control}$B$12,0)*${control}$B$12`,
   l<=41?`=SRC_POP!D${r}`:`=ROUND((${control}$B$7+${control}$B$8*(A${r}-${control}$B$6))/${control}$B$9,0)*${control}$B$9`,
   `=C${r}/(B${r}*${control}$B$18)`,`=D${r}*B${r}/${control}$B$15`,`=D${r}*B${r}/${control}$B$16`,
   `=C${r}/SRC_POP!$D$6`,l<=41?`=SRC_POP!B${r}`:`=I${r-1}`,`=H${r}+C${r}`,
   l<=41?`=D${r}`:`=C${r}/(${control}$B$10*${control}$B$18)`,l<=41?'交接原表跨度＋标准Spin模型':'经验和Bet均为拟合',
   l<=3?'初始基础档参考':l<=41?'已知解锁/上限延续':'Bet趋势估算，非真实解锁',
   l<=41?`PS_DATASET.level_table[level=${l}]`:'L30–41经验趋势 / L15–41 Bet趋势'];
 });
 table(s,5,['等级','最大Bet','升级EXP跨度','升级Spin','毛下注USD低档','毛下注USD高档','经验跨度倍数','到达累计EXP','下一级累计EXP','仅尾段固定Bet Spin','升级依据','Bet依据','来源'],popRows,'POPModel');
 num(s,'B6:C1505','#,##0');num(s,'D6:F1505','#,##0.00');num(s,'G6:I1505','#,##0');num(s,'J6:J1505','#,##0.0');s.getRange('K:M').format.columnWidth=29;
 s.getRange('C6:C46').format.font.color='#1B7467';s.getRange('B47:C1505').format.font.color='#B16A16';

 const heads=['等级','CR最大Bet','CF最大Bet','POP最大Bet','CR升级Spin','CF升级Spin','POP升级Spin','CR毛下注USD','CF毛下注USD','POP毛下注USD','CR等级金币倍数','CF等级金币倍数','POP等级金币倍数','POP依据','同CR Bet POP Spin','POP升级EXP','POP经验跨度倍数'];
 s=base('等级明细','CR / CF / POP 逐级体验','当前等级升下一级；POP第42级起为拟合；美元为各自报价/基准下的毛下注价值。',1505,17);
 const detail=Array.from({length:1500},(_,i)=>{const r=i+6;return [
  `=CALC_CR_CF!A${r}`,`=CALC_CR_CF!B${r}`,`=CALC_CR_CF!C${r}`,`='POP模型'!B${r}`,
  `=CALC_CR_CF!D${r}`,`=CALC_CR_CF!E${r}`,`='POP模型'!D${r}`,
  `=CALC_CR_CF!F${r}`,`=CALC_CR_CF!G${r}`,`='POP模型'!E${r}`,
  `=CALC_CR_CF!H${r}`,`=CALC_CR_CF!I${r}`,'N/A',`='POP模型'!K${r}`,
  `='POP模型'!C${r}/(B${r}*'POP拟合说明'!$B$18)`,`='POP模型'!C${r}`,`='POP模型'!G${r}`];});
 table(s,5,heads,detail,'ThreeWayDetail');
 num(s,'B6:D1505','#,##0');num(s,'E6:G1505','#,##0.0');num(s,'H6:J1505','"$"#,##0.00');num(s,'K6:M1505','#,##0');
 num(s,'O6:O1505');num(s,'P6:Q1505','#,##0');s.getRange('N:N').format.columnWidth=32;
 s=base('等级概览','三方已知Bet变化点','仅列已知变化点和1500级终点；POP拟合Bet不视作真实解锁；金币倍率缺证据写N/A。',d.overview.length+5,14);
 table(s,5,heads.slice(0,14),d.overview.map(l=>Array.from({length:14},(_,i)=>`='等级明细'!${col(i+1)}${l+5}`)),'ThreeWayOverview');
 num(s,`B6:D${d.overview.length+5}`,'#,##0');num(s,`E6:G${d.overview.length+5}`,'#,##0.0');num(s,`H6:J${d.overview.length+5}`,'"$"#,##0.00');num(s,`K6:M${d.overview.length+5}`,'#,##0');s.getRange('N:N').format.columnWidth=32;

 s=sheet('VIP门槛');write(s,'G5',[['POP累计TP','POP标称USD','POP门槛依据']]);
 s.getRange('G5:I5').format={fill:'#294C73',font:{bold:true,color:'#FFFFFF'},wrapText:true};
 write(s,'G6',d.vip.map((v,i)=>i<10?[`=SRC_POP!I${i+6}`,`=G${i+6}/'POP拟合说明'!$B$13`,`=SRC_POP!K${i+6}`]:['N/A','N/A','无该Tier来源']));
 num(s,'G6:H20','#,##0');s.getRange('I:I').format.columnWidth=27;
 write(s,'A3',[['纯购买等值，非真实付款；POP1–4当前界面、5–10历史；同编号VIP不代表权益相同。']]);
 chart(s,'VIP门槛：CR / CF / POP（USD）','VIP门槛',['C','E','F','H'],['CR名义','CF最低','CF最高','POP历史换算'],1,8,'A23','L43','$#,##0');
 // Each game stops at its last sourced tier. Missing tiers are not zero points.
 const vc=s.charts.items[0];
 vc.series.items[0].formula="'VIP门槛'!C6:C20";vc.series.items[0].categoryFormula="'VIP门槛'!A6:A20";
 vc.series.items[3].formula="'VIP门槛'!H6:H15";vc.series.items[3].categoryFormula="'VIP门槛'!A6:A15";

 s=sheet('VIP倍率');write(s,'E5',[['POP金币倍率','POP依据']]);
 s.getRange('E5:F5').format={fill:'#294C73',font:{bold:true,color:'#FFFFFF'},wrapText:true};
 write(s,'E6',d.cr_packages.map((v,i)=>i>=1&&i<=10?[
  i<=4?`=1+SRC_POP!J${i+5}`:`=1+SRC_POP!$J$9+(A${i+6}-SRC_POP!$H$9)*'POP拟合说明'!$B$14`,
  i<=4?'10/09金币包加成':'按Tier3→4增量估算']:['N/A','无该Tier来源']));
 num(s,'E6:E21','0.00"倍"');s.getRange('F:F').format.columnWidth=31;
 write(s,'A3',[['POP倍率＝1＋金币包加成；1–4实测界面，5–10趋势估算；不反套到商城采样报价。']]);
 chart(s,'金币包倍率：CR / CF / POP','VIP倍率',['B','C','E'],['CR现值','CF现有参考','POP含拟合'],2,10,'A23','L43','0"倍"');
 const mc=s.charts.items[0];
 mc.series.items[0].formula="'VIP倍率'!B7:B21";mc.series.items[0].categoryFormula="'VIP倍率'!A7:A21";
 mc.series.items[2].formula="'VIP倍率'!E7:E16";mc.series.items[2].categoryFormula="'VIP倍率'!A7:A16";

 s=base('等级曲线','CR / CF / POP 至1500级','蓝CR、橙CF、绿POP；CR r7502，CF含历史/拟合，POP L42+为估算。',116,12);
 chart(s,'最大Bet及1美元等值Bet（金币）','等级明细',['B','C','D'],['CR最大Bet','CF最大Bet','POP估算Bet'],1,1500,'A6','L25','0.0,,"百万"');
 write(s,'AE5',[['CR 1美元金币','CF 1美元金币','POP采样低档1美元金币']]);
 write(s,'AE6',Array.from({length:1500},(_,i)=>[`=SRC_CR!F${i+6}`,`=CALC_CR_CF!I${i+6}*'拟合说明'!$B$12`,`='POP拟合说明'!$B$15`]));
 s.charts.items[0].setData(s.getRange('AA5:AG1505'));
 chart(s,'最大Bet下升级Spin（理论次数）','等级明细',['E','F','G'],['CR现值','CF参考及拟合','POP参考及拟合'],1,1500,'A28','L47','#,##0');
 chart(s,'升级毛下注（各自币率的名义USD）','等级明细',['H','I','J'],['CR现值','CF基础500k','POP采样低档'],1,1500,'A50','L69','$#,##0');
 chart(s,'等级金币倍率：POP缺同口径来源，暂不画线','等级明细',['K','L'],['CR现值','CF参考及拟合'],1,1500,'A72','L91','0"倍"');
 chart(s,'POP升级EXP跨度增长（L1=1倍，非金币倍率）','POP模型',['G'],['POP含尾段拟合'],1,1500,'A95','L114','#,##0"倍"');
 for(const n of ['等级曲线','VIP门槛','VIP倍率'])for(const c of sheet(n).charts.items)c.series.items.forEach((v,i)=>{
  const colors=n==='VIP门槛'?['#2864AE','#D57B28','#D9B381','#279581']:['#2864AE','#D57B28','#279581','#7395AD','#D9B381','#93BFB0'];
  v.line={fill:colors[i],width:2,style:i>=3||i===1?'dashed':'solid'};
 });
 s.charts.items[4].series.items[0].line={fill:'#279581',width:2,style:'dashed'};

 wb.recalculate();
 const control=sheet('POP拟合说明'),model=sheet('POP模型');
 const before=model.getRange('C1505').values[0][0],known=model.getRange('C46').values[0][0];
 const formula='=SUMPRODUCT(F22:F33,G22:G33)/SUMPRODUCT(F22:F33,F22:F33)';
 control.getRange('B8').formulas=[['=2*'+formula.slice(1)]];wb.recalculate();
 if(!(model.getRange('C1505').values[0][0]>before)||model.getRange('C46').values[0][0]!==known)throw Error('POP fit dependency failed');
 control.getRange('B8').formulas=[[formula]];wb.recalculate();
 if(model.getRange('C1505').values[0][0]!==before)throw Error('POP restore failed');
 await fs.writeFile(path.join(out,'recalculation.json'),JSON.stringify({pop_tail_responded:true,known_levels_preserved:true,restored:true}));
}
