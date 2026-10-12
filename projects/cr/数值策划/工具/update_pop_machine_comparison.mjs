// Artifact-authored POP delta only. Python preserves all other User OOXML.
import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const out=process.argv[2],mode=process.argv[3]||'build';
const input=JSON.parse(await fs.readFile(out+'/input.controlled.json','utf8'));
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const pop=[5,8,11,14,17,20,23,26,29,32,36],map=n=>n+pop.filter(x=>x<n).length;
const usd='"$"#,##0.000',P="'结论与参数'!",S="'SRC_POP'!";
if(mode==='render-slices'){
 const views=JSON.parse(await fs.readFile(out+'/layout-preview.controlled.json','utf8'));
 for(const v of views){
  const wb=Workbook.create(),s=wb.worksheets.add(v.source),last=col(v.cells[0].length);
  s.getRange(`A1:${last}${v.cells.length}`).format={font:{name:'Microsoft YaHei',size:11,color:'#273444'},columnWidth:v.width,verticalAlignment:'center'};
  s.getRange(`A1:${last}1`).format={wrapText:true,rowHeight:66};
  v.cells.forEach((row,r)=>row.forEach((c,k)=>{
   const cell=s.getRange(col(k+1)+(r+1));cell.values=[[c.value]];cell.setNumberFormat(c.format);
   cell.format.fill=c.fill||(r===0?'#294C73':r%2?'#DFEFF5':'#FFFFFF');
   if(r===0)cell.format.font={name:'Microsoft YaHei',size:11,bold:true,color:'#FFFFFF'};
  }));
  const im=await wb.render({sheetName:v.source,range:`A1:${last}${v.cells.length}`,scale:1.2,format:'png'});
  await fs.writeFile(out+'/'+v.label+'.png',new Uint8Array(await im.arrayBuffer()));
 }
 console.log('Rendered saved values, number formats and header fills; native WPS not opened');process.exit(0);
}
if(mode==='render-chart'){
 const data=JSON.parse(await fs.readFile(out+'/chart-preview.controlled.json','utf8'));
 const wb=Workbook.create(),s=wb.worksheets.add('保存图表数据复核');
 s.getRange('A:N').format.columnWidth=13;s.getRange('A1:N54').format.font={name:'Microsoft YaHei',size:11};
 for(let k=0;k<data.length;k++){
  const d=data[k],start=17+k*6;
  s.getRange(`${col(start)}1:${col(start+4)}1501`).values=[['等级',...d.labels],...d.rows];
  const c=s.charts.add('line',s.getRange(`${col(start)}1:${col(start+4)}1501`));
  c.setPosition('A'+(2+k*26),'N'+(25+k*26));c.title=d.title+'（含拟合；读取最终文件）';
  c.titleTextStyle.fontSize=14;c.titleTextStyle.typeface='Microsoft YaHei';
  c.legend={position:'top',textStyle:{typeface:'Microsoft YaHei',fontSize:10}};
  c.xAxis={axisType:'textAxis',tickLabelInterval:150,textStyle:{fontSize:9}};
  c.yAxis={numberFormatCode:'0.000',numberFormatSourceLinked:false,textStyle:{fontSize:10}};
  c.series.items.forEach((v,i)=>v.line={fill:['#2864AE','#D57B28','#207760','#9B5AB5'][i],width:2});
 }
 const im=await wb.render({sheetName:s.name,range:'A1:N52',scale:1.2,format:'png'});
 await fs.writeFile(out+'/saved-chart-series.png',new Uint8Array(await im.arrayBuffer()));
 console.log('Rendered actual saved native series in a read-only plotting view');process.exit(0);
}
if(mode==='render'){
 const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(out+'/CR_CF_POP_等级段横向对比_三档Bet_v4_POP普通特殊.xlsx'));
 // Exact saved values are used only in this read-only renderer, not the delivery.
 const caches=JSON.parse(await fs.readFile(out+'/render-caches.controlled.json','utf8'));
 for(const[n,rows]of Object.entries(caches))for(const[area,values]of rows)wb.worksheets.getItem(n).getRange(area).values=values;
 const im=await wb.render({sheetName:process.argv[4],range:process.argv[5],scale:1.2,format:'png'});
 await fs.writeFile(out+'/'+process.argv[6]+'.png',new Uint8Array(await im.arrayBuffer()));
 console.log('Rendered final saved region');process.exit(0);
}
const wb=Workbook.create(),changed={};
for(const name of ['结论与参数','SRC_等级','SRC_POP','SRC_档位','POP明细','等级段对比','Bet曲线','CR明细','CR调整候选']){wb.worksheets.add(name);changed[name]=[];}
function set(name,ref,value,formula=false){
 const r=wb.worksheets.getItem(name).getRange(ref);if(formula)r.formulas=[[value]];else r.values=[[value]];
 changed[name].push(ref);return r;
}
function column(name,letter,values,formula=false){
 const r=wb.worksheets.getItem(name).getRange(`${letter}6:${letter}1505`);
 if(formula)r.formulas=values.map(x=>[x]);else r.values=values.map(x=>[x]);
 for(let n=6;n<=1505;n++)changed[name].push(letter+n);return r;
}
// Unchanged inputs are temporary dependencies only, never grafted back.
for(const[name,cells]of Object.entries(input.seeds)){
 const sh=wb.worksheets.getItem(name);
 for(const[ref,value]of Object.entries(cells))sh.getRange(ref).values=[[value]];
}
if(input.dual_candidates)for(const[n,areas]of Object.entries(input.candidate_seeds))for(const[area,values]of areas)wb.worksheets.getItem(n).getRange(area).values=values;
const src=wb.worksheets.getItem('SRC_POP');src.getRange('U1:AA34').format={font:{name:'Microsoft YaHei',size:11},columnWidth:22};
for(const[ref,value]of Object.entries(input.source))set('SRC_POP',ref,value);
for(const[ref,value]of Object.entries({U1:'普通线数',U2:'特殊线数',U3:'已采机台附加费',U5:'母表索引',V5:'每线Bet',X5:'来源/拟合项',Y5:'等级',Z5:'每线值',AA5:'证据边界',
 X6:'最低档实测',X7:'最低档实测',X8:'最高档实测',X9:'最高档升级包',X10:'最高档实测',X11:'中段最低档拟合',X12:'后段最低档拟合',X13:'高段外推取整',X14:'普通默认档实测',X15:'普通默认档实测',X16:'特殊默认档实测',
 AA6:'PS_LEVEL_BET.json samples[0]；20线',AA7:'samples[1]；20线+五台机器模型',AA8:'samples[0]；完整窗口',AA9:'level_cap_breakpoints_measured；不是完整窗口',AA10:'samples[1]；五台机器模型一致',
 AA11:'owner_hypothesis未验证；本表仅作拟合',AA12:'owner_hypothesis未验证；本表仅作拟合',AA13:'91级后按50/91末段斜率；母表延伸未验证',
 AA14:'samples[0]；特殊机25级默认值缺失',AA15:'machine_Emeralds/FrontierFortune',AA16:'machine_Excalibur/SevenKingdom/Witches'}))set('SRC_POP',ref,value);
src.getRange('U5:AA5').format={fill:'#207760',font:{color:'#FFFFFF',bold:true},wrapText:true};
for(const r of [26,27,28])set('SRC_POP','P'+r,'历史口述锚点，保留供旧CR候选；本轮POP现对比已停用');
const model=wb.worksheets.getItem('POP明细');model.getRange('T1:BD1505').format={font:{name:'Microsoft YaHei',size:11,color:'#273444'},columnWidth:21};
set('POP明细','A2','POP：普通20线／特殊40线；当前对比从T列开始');
set('POP明细','A3','B:S隐藏为旧CR候选依赖；现对比独立计算，不改变CR候选。普通/特殊是本表按线数分类。');
set('POP明细','T2','推荐为100美元余额÷37情景；实测默认Bet另列，不随线数简单翻倍。');
set('POP明细','T3','25/91级窗口为实测；50级仅最高档实测。其余窗口含拟合，特殊低级段不代表已解锁该机台。');
const heads=['普通最小Bet','特殊最小Bet','普通推荐Bet(情景)','特殊推荐Bet(情景)','普通最大Bet','特殊最大Bet',
 '普通最小每转USD','特殊最小每转USD','普通推荐每转USD','特殊推荐每转USD','普通最大每转USD','特殊最大每转USD',
 '普通最小升级Spin','特殊最小升级Spin','普通推荐升级Spin','特殊推荐升级Spin','普通最大升级Spin','特殊最大升级Spin',
 '普通最小升级毛USD','特殊最小升级毛USD','普通推荐升级毛USD','特殊推荐升级毛USD','普通最大升级毛USD','特殊最大升级毛USD',
 '共用coins/USD','共用本级经验','POP证据边界','普通实测默认总Bet','特殊实测默认总Bet'];
heads.forEach((h,i)=>set('POP明细',col(20+i)+'5',h));
model.getRange('T5:AV5').format={fill:'#207760',font:{color:'#FFFFFF',bold:true},wrapText:true,rowHeight:58};
set('POP明细','BB5','拟合每线下限');set('POP明细','BC5','拟合每线上限');set('POP明细','BD5','每线上限连续目标');
const rowforms=Array.from({length:1500},(_,i)=>{const r=i+6;return {
 BB:`=IF(A${r}<${S}$Y$11,${S}$Z$6,IF(A${r}<${S}$Y$12,${S}$Z$11,${S}$Z$7))`,
 BD:`=${S}$Z$9+(${S}$Z$10-${S}$Z$9)*(A${r}-${S}$Y$9)/(${S}$Y$10-${S}$Y$9)`,
 BC:`=IF(A${r}<=${S}$Y$9,'SRC_等级'!K${r},IF(A${r}<=${S}$Y$10,LOOKUP(BD${r},${S}$V$6:$V$34),ROUND(BD${r}/${S}$Z$13,0)*${S}$Z$13))`,
 T:`=BB${r}*${S}$V$1+${S}$V$3`,U:`=BB${r}*${S}$V$2+${S}$V$3`,
 V:`=MAX(T${r},MIN(X${r},N${r}*${P}$B$11/${P}$B$12))`,W:`=MAX(U${r},MIN(Y${r},N${r}*${P}$B$11/${P}$B$12))`,
 X:`=BC${r}*${S}$V$1+${S}$V$3`,Y:`=BC${r}*${S}$V$2+${S}$V$3`,
 AR:`=N${r}`,AS:`=O${r}`,
 AU:`=IF(A${r}=${S}$Y$14,${S}$Z$14*${S}$V$1,IF(A${r}=${S}$Y$15,${S}$Z$15*${S}$V$1,"N/A"))`,
 AV:`=IF(A${r}=${S}$Y$16,${S}$Z$16*${S}$V$2,"N/A")`,
 };});
for(const k of Object.keys(rowforms[0]))column('POP明细',k,rowforms.map(x=>x[k]),true);
for(let j=0;j<6;j++){
 const b=col(20+j),u=col(26+j),s=col(32+j),cost=col(38+j);
 column('POP明细',u,rowforms.map((_,i)=>`=${b}${i+6}/N${i+6}`),true).setNumberFormat(usd);
 column('POP明细',s,rowforms.map((_,i)=>`=O${i+6}/((${b}${i+6}-${S}$V$3)*${P}$B$28)`),true).setNumberFormat('#,##0.00');
 column('POP明细',cost,rowforms.map((_,i)=>`=${s}${i+6}*${u}${i+6}`),true).setNumberFormat(usd);
}
column('POP明细','AT',rowforms.map((_,i)=>i+1===25?'普通完整窗口实测；特殊同窗40线换算，默认值缺失':i+1===91?'普通/特殊完整窗口及默认Bet实测':i+1===50?'最高每线档升级包实测；最低档拟合':i+1<25?'早段沿旧资料；特殊为40线条件情景':i+1<50?'25级窗口延续情景；未逐级采样':i+1<91?'最低50/75断点是假设；最高按母表取档拟合':'92+最低延续，最高末段拟合；非服务器配置'));
model.getRange('T6:Y1505').setNumberFormat('#,##0');model.getRange('AR6:AS1505').setNumberFormat('#,##0');model.getRange('AU6:AV1505').setNumberFormat('#,##0');
const st=wb.worksheets.getItem('等级段对比');st.getRange('A5:AU111').format={font:{name:'Microsoft YaHei',size:11,color:'#273444'},columnWidth:20};
st.getRange('A5:AU5').format={fill:'#294C73',font:{color:'#FFFFFF',bold:true},wrapText:true,rowHeight:64};
set('等级段对比','A2','相同等级段：CR / CF / POP普通20线 / POP特殊40线');
set('等级段对比','A3','保留User等级段和CR/CF；POP按段首列示，25/91级实测另列。推荐是余额情景；其余窗口见来源边界。');
const modelcols=['T','V','X','Z','AB','AD','AL','AN','AP','AR',null];
for(let i=0;i<pop.length;i++){
 const old=pop[i],normal=col(map(old)),special=col(map(old)+1);
 for(const[letter,j]of [[normal,0],[special,1]]){
  set('等级段对比',letter+'5',input.heads[old-1]+(j?'\n特殊40线':'\n普通20线'));
  st.getRange(`${letter}5`).format={fill:j?'#75438F':'#207760',font:{color:'#FFFFFF',bold:true},wrapText:true};
  for(let r=6;r<=104;r++){
   const m=modelcols[i];const mc=m==='AR'?'AR':m?col((({T:20,V:22,X:24,Z:26,AB:28,AD:30,AL:38,AN:40,AP:42})[m])+j):col(38+j);
   set('等级段对比',letter+r,m?`=INDEX('POP明细'!${mc}:${mc},A${r}+5)`:`=SUMIFS('POP明细'!$${mc}$6:$${mc}$1505,'POP明细'!$A$6:$A$1505,">="&A${r},'POP明细'!$A$6:$A$1505,"<="&B${r})`,true);
  }
  st.getRange(`${letter}6:${letter}104`).setNumberFormat(i>=3&&i!==9?usd:'#,##0');
 }
}
const note=col(map(33));set('等级段对比',note+'5','POP证据边界；CR/CF原值保留');
for(let r=6;r<=104;r++)set('等级段对比',note+r,`=INDEX('POP明细'!AT:AT,A${r}+5)`,true);
st.getRange(note+':'+note).format.columnWidth=55;
set('等级段对比','A107','实测窗口核对（不改变上方User原等级段）');
const sampleheads=['等级','普通线数','特殊线数','普通最小Bet','特殊最小Bet','普通最大Bet','特殊最大Bet','普通实际默认Bet','特殊实际默认Bet','证据边界'];
sampleheads.forEach((x,i)=>set('等级段对比',col(i+1)+'108',x));
for(const[r,lv]of [[109,25],[110,91]]){
 set('等级段对比','A'+r,lv);set('等级段对比','B'+r,`=${S}$V$1`,true);set('等级段对比','C'+r,`=${S}$V$2`,true);
 ['T','U','X','Y','AU','AV'].forEach((mc,i)=>set('等级段对比',col(i+4)+r,`='POP明细'!${mc}${lv+5}`,true));
 set('等级段对比','J'+r,lv===25?'特殊按共同阶梯换算，默认值未采':'两类实测，实际默认总Bet相同');
}
st.getRange('A108:J108').format={fill:'#207760',font:{bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:55};st.getRange('A109:I110').setNumberFormat('#,##0');
for(const[ref,text]of Object.entries({
 A3:'CR/CF及User修改沿用v3；POP新增10/12等级窗口包。普通20线、特殊40线；完整逐级1500，非配置实施。',
 A7:'POP已确认25级与91级窗口；普通20线、特殊40线。最小/最大总Bet按线数换算，50/75最低档断点尚未实测。',
 A8:'推荐仍为名义100美元余额÷37并限制上下界；不是默认Bet算法，未取实际档。91级两类实际默认总Bet相同，详见实测核对。',
 A36:'POP 50级最高每线档有升级包依据；51–91按50/91锚点在已知母表上取档拟合；92+按末段斜率外推并取整，不代表真实解锁。',
 A37:'POP最低50/75级变更仅作假设拟合；92+延续91级最低每线档。旧50万等总Bet口述缺同机台/线数证据，不再当作普通机当前事实。CF不变。',
 A43:'本轮只更新POP；CR调整候选继续引用隐藏的旧POP基线，数值不随本轮POP修订重算。VIP/等级经验/币率与线数无关，继续共用原底稿。',
 A44:'本包已验证特殊机为40线；未取得50线完整窗口。低等级特殊栏为同窗口40线条件换算，不表示当时已解锁该机台。',
 A45:'普通/特殊升级毛USD可相同：经验随金币Bet同比增加，线数改变每转下注和升级Spin，不能把毛下注当净亏或实付。',
 }))set('结论与参数',ref,text);
const curve=wb.worksheets.getItem('Bet曲线');
set('Bet曲线','A3','全1500逐级点；POP普通20线/特殊40线分列，25/91级窗口实测，其他含拟合；CR/CF沿用User比较底稿。');
for(const[c,mc,label]of [['AD','Z','POP普通20线'],['AE','AA','POP特殊40线'],['AJ','AB','POP普通20线'],['AK','AC','POP特殊40线'],['AP','AD','POP普通20线'],['AQ','AE','POP特殊40线'],['AV','AL','POP普通20线'],['AW','AM','POP特殊40线']]){
 set('Bet曲线',c+'5',label);column('Bet曲线',c,rowforms.map((_,i)=>`='POP明细'!${mc}${i+6}`),true).setNumberFormat(usd);
}
if(input.dual_candidates){
 const n='CR调整候选',s=wb.worksheets.getItem(n),pool="'SRC_档位'!$C$6:$C$798",I="'SRC_等级'!";
 const up=t=>`IF(COUNTIF(${pool},">="&${t})>0,_xlfn.MINIFS(${pool},${pool},">="&${t}),ROUNDUP(${t}/$AU$1,0)*$AU$1)`;
 s.getRange('AN1:BS1505').format={font:{name:'Microsoft YaHei',size:11,color:'#273444'},columnWidth:23};
 set(n,'A2','CR调整候选');set(n,'A3','普通／特殊');
 set(n,'AN1','推荐除数');set(n,'AO1',30);set(n,'AQ1','名义余额USD');set(n,'AR1',`=${P}$B$11`,true);set(n,'AT1','新增档取整');set(n,'AU1',input.candidate_seeds[n][0][1][0][19]);
 set(n,'AN2','本轮两套候选：对标POP普通20线／特殊40线，推荐均用余额÷30');
 set(n,'AN3','B:AM保留v3历史供主对比基线引用。新候选从AN列开始；不写配置，前4级继承User最低档及原推荐/上限。');
 const hs=['最低Bet候选','推荐Bet候选','最大Bet候选','最低每转USD','推荐每转USD','最大每转USD',
 '最低升级Spin','推荐升级Spin','最大升级Spin','最低升级毛USD','推荐升级毛USD','最大升级毛USD','最低较v3候选','推荐较原情景','最大较原配置','落表说明'];
 hs.forEach((h,i)=>{for(let j=0;j<2;j++)set(n,col(40+i*2+j)+'5',h+'\n'+(j?'对标特殊40线':'对标普通20线'));});
 s.getRange('AN5:BS5').format={font:{bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:66};
 for(let c=40;c<=71;c++)s.getRange(`${col(c)}5`).format.fill=c%2===0?'#207760':'#75438F';
 for(let j=0;j<2;j++){
  const mn=col(40+j),rc=col(42+j),mx=col(44+j),pm=col(26+j),px=col(30+j);
  const formulas=Array.from({length:1500},(_,i)=>{
   const r=i+6,[lo,hi]=input.candidate_pool_ranges[i],local=`'SRC_档位'!$C$${lo}:$C$${hi}`,target=`'POP明细'!${pm}${r}*C${r}`;
   const take=`IF(COUNTIF(${local},">="&${target})>0,_xlfn.MINIFS(${local},${local},">="&${target}),MAX(${local}))`;
   return [
    `=IF(A${r}<$V$1,Q${r},MIN(Y${r},MAX(${i?mn+(r-1)+',':''}${take})))`,
    `=IF(A${r}<$V$1,R${r},MAX(${mn}${r},MIN(${mx}${r},${up(`C${r}*$AR$1/$AO$1`)})))`,
    `=IF(A${r}<$V$1,Y${r},MAX(Y${r},${i?mx+(r-1)+',':''}${up(`'POP明细'!${px}${r}*C${r}`)}))`,
    ...[mn,rc,mx].map(c=>`=${c}${r}/C${r}`),
    ...[mn,rc,mx].map(c=>`=IF(${I}B${r}=1,${I}C${r},${I}C${r}/(${c}${r}*${P}$B$26))`),
    ...[0,1,2].map(k=>`=${col(52+2*k+j)}${r}*${col(46+2*k+j)}${r}`),
    `=${mn}${r}/Q${r}-1`,`=${rc}${r}/R${r}-1`,`=${mx}${r}/Y${r}-1`,
    `=IF(COUNTIF(${pool},${mx}${r})=0,"上限需新增Bet/EXP",IF(COUNTIF(${local},${mx}${r})=0,"上限需提前解锁","上限已有档"))&IF(${col(46+j)}${r}<'POP明细'!${pm}${r},"；底档受旧上限限制","")&"；后段含拟合"`
   ];
  });
  for(let k=0;k<16;k++)column(n,col(40+2*k+j),formulas.map(r=>r[k]),true);
 }
 s.getRange('AN6:BS1505').setNumberFormat('#,##0');
 for(let c=46;c<=51;c++)s.getRange(`${col(c)}6:${col(c)}1505`).setNumberFormat(usd);
 for(let c=52;c<=57;c++)s.getRange(`${col(c)}6:${col(c)}1505`).setNumberFormat('#,##0.00');
 for(let c=58;c<=63;c++)s.getRange(`${col(c)}6:${col(c)}1505`).setNumberFormat(usd);
 for(let c=64;c<=69;c++)s.getRange(`${col(c)}6:${col(c)}1505`).setNumberFormat('0.0%');
 s.getRange('AN2:AW2').format.font={size:16,bold:true,color:'#183654'};
 set('结论与参数','A43','本轮增加CR双列候选：普通20线／特殊40线，推荐均余额÷30。原CR/CF主比较及User修改保持，v3候选隐藏作历史；新方案见候选页AN列后。');
 set('POP明细','A3','B:S隐藏保留旧POP历史；现对比从T列开始。CR本轮两套新候选引用新POP普通/特殊列。');
}
wb.recalculate();
const before=model.getRange('U96').values[0][0];src.getRange('V2').values=[[input.controls.special_lines/2]];wb.recalculate();
if(model.getRange('U96').values[0][0]!==before/2)throw Error('Special line count input did not recalculate');
src.getRange('V2').values=[[input.controls.special_lines]];wb.recalculate();
if(model.getRange('U96').values[0][0]!==before)throw Error('Line count restore failed');
await fs.writeFile(out+'/changed-cells.json',JSON.stringify(Object.fromEntries(Object.entries(changed).filter(([,r])=>r.length))));
await fs.writeFile(out+'/recalculation.json',JSON.stringify({special_lines_changed_and_restored:true}));
await(await SpreadsheetFile.exportXlsx(wb)).save(out+'/delta.xlsx');
console.log(JSON.stringify({authored_POP_delta:true,levels:1500,await_preservation_graft:true}));
