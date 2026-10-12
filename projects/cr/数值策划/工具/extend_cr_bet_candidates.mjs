// Author additions with Artifact. Python grafts only Q:AM back into the User file.
// Existing formulas/styles/charts never come from this temporary calculation copy.
import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const out=process.argv[2];
const renderFinal=process.argv[3]==='render-final';
const filename=renderFinal?'CR_CF_POP_等级段横向对比_三档Bet_v3_用户修订加方案.xlsx':'user-edited-v2.xlsx';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(out+'/'+filename));
const seeds=JSON.parse(await fs.readFile(out+'/artifact-seeds.controlled.json','utf8'));
const controls=JSON.parse(await fs.readFile(out+'/candidate-controls.json','utf8'));
// WPS unquoted Chinese references are valid in WPS, but this engine yields NAME.
// Use the User-saved, error-free caches only for unchanged input dependencies here.
// The delivered ZIP retains every original cell, including its formula and cache.
for(const[name,areas]of Object.entries(seeds))for(const[area,values]of areas)wb.worksheets.getItem(name).getRange(area).values=values;
if(renderFinal){
 const im=await wb.render({sheetName:'CR调整候选',range:process.argv[4],scale:1.2,format:'png'});
 await fs.writeFile(out+'/'+process.argv[5]+'.png',new Uint8Array(await im.arrayBuffer()));
 console.log('Final candidate region rendered using preserved User input values');process.exit(0);
}
const s=wb.worksheets.getItem('CR调整候选'),P="'结论与参数'!",I="'SRC_等级'!",usd='"$"#,##0.000';
const col=n=>{let x='';for(;n;n=Math.floor((n-1)/26))x=String.fromCharCode(65+(n-1)%26)+x;return x;};
s.getRange('Q1:AM1505').format={font:{name:'Microsoft YaHei',size:11,color:'#273444'},columnWidth:18,verticalAlignment:'center'};
s.getRange('Q1:X1').values=[['推荐除数',controls.divisor,'新档取整单位',controls.new_bet_rounding,'开始调整等级',controls.first_adjusted_level,'名义余额USD',null]];
s.getRange('X1').formulas=[[`=${P}B11`]];
s.getRange('R1').format={fill:'#FFF2CC',font:{color:'#1D4ED8'}};
s.getRange('T1').format={fill:'#FFF2CC',font:{color:'#1D4ED8'}};
s.getRange('Q2:AM2').merge();s.getRange('Q2').values=[['新增方案：推荐余额÷30，最大Bet按POP同级美元上限对标']];
s.getRange('Q2:AM2').format.font={name:'Microsoft YaHei',size:18,bold:true,color:'#183654'};
s.getRange('Q3:AM3').merge();s.getRange('Q3').values=[['保留User原表；新方案独立算CR美元，不沿用概览中的CF引用。前4级推荐/上限不变，先取已有Bet档；超出全池才拟新档。仅候选，不写配置。']];
const heads=['继承User最低Bet','原推荐Bet','推荐原始目标','推荐候选Bet','推荐提升','推荐每转USD','推荐升级Spin','推荐升级毛USD','原最大Bet','POP最大每转USD','最大Bet对标目标','最大Bet候选','最大提升','最大每转USD','最大升级Spin','最大升级毛USD','推荐落表类型','上限落表类型','推荐理论EXP','上限理论EXP','推荐升级成本倍数','上限升级成本倍数','说明'];
s.getRange('Q5:AM5').values=[heads];
s.getRange('Q5:X5').format={fill:'#294C73',font:{bold:true,color:'#FFFFFF'},wrapText:true};
s.getRange('Y5:AF5').format={fill:'#A66023',font:{bold:true,color:'#FFFFFF'},wrapText:true};
s.getRange('AG5:AM5').format={fill:'#207760',font:{bold:true,color:'#FFFFFF'},wrapText:true};
s.getRange('AG:AH').format.columnWidth=24;s.getRange('AM:AM').format.columnWidth=42;
const pool="'SRC_档位'!$C$6:$C$798",stages="'SRC_档位'!$A$6:$A$798";
const up=cell=>`IF(COUNTIF(${pool},">="&${cell})>0,_xlfn.MINIFS(${pool},${pool},">="&${cell}),ROUNDUP(${cell}/$T$1,0)*$T$1)`;
const type=(cell,r)=>`=IF(COUNTIF(${pool},${cell})=0,"需新增Bet/EXP",IF(COUNTIFS(${stages},M${r},${pool},${cell})>0,"当前已解锁档","已有档需提前解锁"))`;
const rows=Array.from({length:1500},(_,i)=>{const r=i+6;return[
 `=VLOOKUP(A${r},'等级段对比'!$A$6:$C$104,3,TRUE)`,
 `='CR明细'!C${r}`,`=MAX(Q${r},C${r}*$X$1/$R$1)`,
 `=IF(A${r}<$V$1,R${r},MAX(Q${r},MIN(AB${r},${up('S'+r)})))`,
 `=T${r}/R${r}-1`,`=T${r}/C${r}`,
 `=IF(${I}B${r}=1,${I}C${r},${I}C${r}/AI${r})`,`=W${r}*V${r}`,
 `='CR明细'!D${r}`,`='POP明细'!G${r}`,`=MAX(Y${r},Z${r}*C${r})`,
 `=IF(A${r}<$V$1,Y${r},MAX(Y${r},${i?`AB${r-1},`:''}${up('AA'+r)}))`,
 `=AB${r}/Y${r}-1`,`=AB${r}/C${r}`,
 `=IF(${I}B${r}=1,${I}C${r},${I}C${r}/AJ${r})`,`=AE${r}*AD${r}`,
 type('T'+r,r),type('AB'+r,r),`=T${r}*${P}$B$26`,`=AB${r}*${P}$B$26`,
 `=X${r}/'CR明细'!L${r}`,`=AF${r}/'CR明细'!M${r}`,
 `=IF(A${r}<$V$1,"推荐和上限保持；最低档继承User",IF(AH${r}="需新增Bet/EXP","新档经验仅按比例试算，待落表验证","推荐受上限与取档影响；POP含拟合"))`
 ];});
for(let c=0;c<23;c++)s.getRange(`${col(c+17)}6:${col(c+17)}1505`).formulas=rows.map(r=>[r[c]]);
for(let r=6;r<=1505;r+=2)s.getRange(`Q${r}:AM${r}`).format.fill='#DFEFF5';
s.getRange('Q6:AM1505').setNumberFormat('#,##0');
for(const c of ['V','X','Z','AD','AF'])s.getRange(`${c}6:${c}1505`).setNumberFormat(usd);
for(const c of ['U','AC'])s.getRange(`${c}6:${c}1505`).setNumberFormat('0.0%');
for(const c of ['W','AE'])s.getRange(`${c}6:${c}1505`).setNumberFormat('#,##0.00');
for(const c of ['AK','AL'])s.getRange(`${c}6:${c}1505`).setNumberFormat('0.000"倍"');
s.getRange('X1').setNumberFormat(usd);
wb.recalculate();
const before=s.getRange('T305').values[0][0];
s.getRange('R1').values=[[controls.divisor*2]];wb.recalculate();
if(s.getRange('T305').values[0][0]===before)throw Error('Recommendation divisor did not update candidate');
s.getRange('R1').values=[[controls.divisor]];wb.recalculate();
if(s.getRange('T305').values[0][0]!==before)throw Error('Divisor restore failed');
await fs.writeFile(out+'/candidate-recalculation.json',JSON.stringify({divisor_responded:true,restored:true,source_formula_caches_used_only_in_temporary_calculation:true}));
await(await SpreadsheetFile.exportXlsx(wb)).save(out+'/additions.xlsx');
for(const[range,name]of [['Q1:AF8','candidate-controls'],['Q50:X61','recommended-plan'],['Y50:AF61','maximum-plan'],['AG5:AM12','implementation-notes']]){
 const im=await wb.render({sheetName:'CR调整候选',range,scale:1.2,format:'png'});
 await fs.writeFile(out+'/'+name+'.png',new Uint8Array(await im.arrayBuffer()));
}
console.log(JSON.stringify({authored:'Q:AM only; await preservation graft',levels:1500,scenario:'balance / 30'}));
