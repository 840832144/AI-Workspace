// TASK-0036：固定dev基线、User决定的Bet目标、逐级反推经验；不输出可提交配置。
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const [dir]=process.argv.slice(2),d=JSON.parse(await fs.readFile(path.join(dir,'comparison-inputs.json'),'utf8'));
const wb=Workbook.create();
const visible=['Bet解锁_概览','升级体验_概览','单Spin经验_概览','Bet档位_明细','逐级_明细','Bet经验_候选','经验约束_明细'];
for(const n of [...visible,'SRC_DEV','SRC_CF','SRC_BET'])wb.worksheets.add(n);
const sheet=n=>wb.worksheets.getItem(n), col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
function mix(s,start,rows){
 const width=rows[0].length,end=start+rows.length-1;
 s.getRange(`A${start}:${col(width)}${end}`).values=rows.map(r=>r.map(v=>typeof v==='string'&&v.startsWith('=')?null:v));
 for(let c=0;c<width;c++){
  let i=0;while(i<rows.length){if(!(typeof rows[i][c]==='string'&&rows[i][c].startsWith('='))){i++;continue;}
   const first=i,f=[];while(i<rows.length&&typeof rows[i][c]==='string'&&rows[i][c].startsWith('='))f.push([rows[i++][c]]);
   s.getRange(`${col(c+1)}${start+first}:${col(c+1)}${start+i-1}`).formulas=f;
  }
 }
}
function title(s,text,note,end=60,width=14){
 s.showGridLines=false;s.freezePanes.unfreeze();s.tabColor='#17365D';
 s.getRange(`A1:${col(width)}${end}`).format={font:{name:'Microsoft YaHei',size:10,color:'#24364B'},rowHeight:22,columnWidth:14,verticalAlignment:'center'};
 s.getRange(`A1:A${end}`).format.columnWidth=9;
 for(const r of [1,2,3])s.mergeCells(`A${r}:N${r}`);
 s.getRange('A1').values=[[text]];s.getRange('A1:N1').format={fill:'#17365D',font:{name:'Microsoft YaHei',size:17,bold:true,color:'#FFFFFF'},rowHeight:37};
 s.getRange('A2').values=[[note]];s.getRange('A2:N2').format={wrapText:true,rowHeight:38,font:{size:11,color:'#855400'}};
 s.getRange('A3').values=[['CR dev r7252 · LevelCfg原样保留｜CF历史正式表｜冲突Bet取较低值｜受控候选，未提交SVN']];
 s.getRange('A3:N3').format={font:{size:10,color:'#667788'},rowHeight:24};
}
function headers(s,labels,end){
 s.getRange(`A4:${col(labels.length)}4`).values=[labels];s.getRange(`A4:${col(labels.length)}4`).format={fill:'#D9EAF7',font:{bold:true},rowHeight:46,wrapText:true,horizontalAlignment:'center'};
 s.getRange(`A5:${col(labels.length)}${end}`).setNumberFormat('#,##0.####');
}
const sd=sheet('SRC_DEV'),sc=sheet('SRC_CF'),sb=sheet('SRC_BET');
sd.getRange('A1').values=[['固定只读导出：CR dev r7252；'+d.read_at_utc]];
sd.getRange('A4:M4').values=[['等级','模式','门槛','Bet ID','Bet金币','EXP/Spin','金币/USD','等级源格','Bet/经验源格','解锁源格','价值源行','CF解锁表最大Bet','User保守Bet']];
sd.getRange('A5:M5004').values=d.cr;
sc.getRange('A1:C2').values=[['基础金币/USD','历史抽水率','CR既定净耗率'],[d.cf_base,d.cf_loss,d.cr_loss]];
sc.getRange('A4:F4').values=[['等级','主表Bet','历史Spin','等级倍率','原始成本缓存','源坐标']];sc.getRange('A5:F304').values=d.cf;
sb.getRange('A4:G4').values=[['CF原解锁级','CF金币Bet','CR现有ID','CR最早解锁','CR现有EXP','CF源坐标','保守后解锁级']];sb.getRange(`A5:G${d.tiers.length+4}`).values=d.tiers;
sb.getRange('I4:L4').values=[['Bet ID','金币Bet','dev EXP','经验源格']];sb.getRange('I5:L42').values=d.candidates.map(c=>[c.id,c.bet,c.current_exp,c.source_cell]);

const dt=sheet('逐级_明细');
title(dt,'逐级数据｜同金币Bet升级体验','保留5000级；两边统一用R列金币Bet。现值按该Bet可用时模拟，实际解锁另见E/AE列；候选只在Excel中，未写配置。',5004,31);
headers(dt,['等级','升级模式\n1=Spin','dev门槛\n不修改','对标Bet ID','dev已解锁\n最大金币Bet','dev同Bet\nEXP/Spin','CR金币\n/USD','dev同Bet\n理论Spin','dev同Bet\n整Spin','dev同Bet\n理论净耗USD','dev同Bet\n整Spin净耗USD','CF历史\n期望Spin','CF主表Bet\n原始金币','CF金币\n/USD','CF保守Bet\n期望成本USD','dev成本\n相对CF','CF解锁表\n原始Bet','CF正式/CR目标\n金币Bet','逐级精确反推\nEXP/Spin','逐级目标\n期望成本USD','期望成本\n相对CF','来源是否\n有冲突','反推适用边界','CF原始\n成本缓存','CF期望向上\n取整Spin','候选同Bet\nEXP/Spin','候选同Bet\n整Spin','候选−CF\n整Spin','候选同Bet\n整Spin净耗USD','候选成本\n相对CF整Spin','dev最大Bet\n是否达目标'],5004);
const rows=d.cr.map((v,i)=>{
 const r=i+5,has=i<300,terminal=i===4999;
 const a=Array.from({length:7},(_,j)=>`='SRC_DEV'!${col(j+1)}${r}`);
 return [...a,terminal?'N/A':`=IF(B${r}=1,C${r},C${r}/F${r})`,terminal?'N/A':`=ROUNDUP(H${r},0)`,terminal?'N/A':`=H${r}*R${r}/G${r}*'SRC_CF'!$C$2`,terminal?'N/A':`=I${r}*R${r}/G${r}*'SRC_CF'!$C$2`,
 has?`='SRC_CF'!C${r}`:'N/A',has?`='SRC_CF'!B${r}`:'N/A',has?`='SRC_CF'!$A$2*'SRC_CF'!D${r}`:'N/A',has?`=R${r}*L${r}*'SRC_CF'!$B$2/N${r}`:'N/A',has?`=K${r}/O${r}-1`:'N/A',
 `='SRC_DEV'!L${r}`,has?`=MIN(M${r},Q${r})`:`=Q${r}`,has&&v[1]===0?`=C${r}/L${r}`:'N/A',has&&v[1]===0?`=L${r}*R${r}/G${r}*'SRC_CF'!$C$2`:'N/A',has&&v[1]===0?`=T${r}/O${r}-1`:'N/A',
 has?`=IF(M${r}=Q${r},"一致","取较低Bet")`:'仅解锁锚点',v[1]===1?'Spin模式：EXP不改变升级次数':has?'反推值；须检查共享档冲突':terminal?'5000级终点':'缺CF同级Spin，不拟造EXP',has?`='SRC_CF'!E${r}`:'N/A',
 has?`=ROUNDUP(L${r},0)`:'N/A',`='Bet经验_候选'!G${v[3]+4}`,terminal?'N/A':`=IF(B${r}=1,C${r},ROUNDUP(C${r}/Z${r},0))`,has?`=AA${r}-Y${r}`:'N/A',terminal?'N/A':`=AA${r}*R${r}/G${r}*'SRC_CF'!$C$2`,has?`=AC${r}/(Y${r}*R${r}/N${r}*'SRC_CF'!$B$2)-1`:'N/A',`=IF(E${r}>=R${r},"达到/超过","未达到")`];
});
mix(dt,5,rows);for(const c of ['P','U','AD'])dt.getRange(`${c}5:${c}5004`).setNumberFormat('0.00%');dt.getRange('W5:W5004').format.columnWidth=36;

const ca=sheet('Bet经验_候选');title(ca,'Bet经验候选｜保持LevelCfg，匹配整Spin模型','候选取可行整数区间内离dev现值最近的经验；17档有来源，其他档保留现值。不是CF原始配置，也未写入SVN表。',45);
headers(ca,['Bet ID','金币Bet','dev EXP','对标等级数','可行EXP下界','可行EXP上界','候选EXP','拟议经验差','候选状态','经验源坐标','全档经验单调性'],42);
mix(ca,5,d.candidates.map((c,i)=>{
 const r=i+5,lo=c.levels.map(l=>`ROUNDUP('逐级_明细'!C${l+4}/'逐级_明细'!Y${l+4},0)`);
 const hi=c.levels.filter(l=>Math.ceil(d.cf[l-1][2])>1).map(l=>`ROUNDUP('逐级_明细'!C${l+4}/('逐级_明细'!Y${l+4}-1),0)-1`);
 return [`='SRC_BET'!I${r}`,`='SRC_BET'!J${r}`,`='SRC_BET'!K${r}`,c.levels.length,c.levels.length?`=MAX(${lo.join(',')})`:'N/A',hi.length?`=MIN(${hi.join(',')})`:'N/A',c.levels.length?(hi.length?`=MIN(MAX(C${r},E${r}),F${r})`:`=MAX(C${r},E${r})`):`=C${r}`,`=G${r}-C${r}`,c.status,c.source_cell,i===0?'初始档':`=IF(G${r}<G${r-1},"经验倒挂：不可落表","未下降")`];
}));ca.getRange('I5:K42').format.columnWidth=32;

const bt=sheet('Bet档位_明细');title(bt,'Bet档位｜正式目标与dev差异','目标按同等级、同金币；原解锁表0级视为初始可用。CF不含的CR额外档不自动处理，完整配置落表待验收。',42,14);
headers(bt,['CF金币Bet','CF原始解锁级','保守后目标级','dev当前首开级','dev现有Bet ID','首开级差\ndev−目标','dev EXP/Spin','CF源坐标'],d.tiers.length+4);bt.getRange('A:A').format.columnWidth=20;
mix(bt,5,d.tiers.map((v,i)=>{const r=i+5;return [`='SRC_BET'!B${r}`,`='SRC_BET'!A${r}`,`=IF(B${r}=0,0,COUNTIF('逐级_明细'!$R$5:$R$5004,"<"&A${r})+1)`,`='SRC_BET'!D${r}`,`='SRC_BET'!C${r}`,`=D${r}-MAX(1,C${r})`,`='SRC_BET'!E${r}`,v[5]];}));bt.getRange(`H5:H${d.tiers.length+4}`).format.columnWidth=45;

const ex=sheet('经验约束_明细');title(ex,'共享Bet经验｜逐级反推能否落到一个值','同一Bet只配置一个levelExp；最小与最大反推值不同即存在冲突，不取平均掩盖。301级后无CF同级Spin。',36,14);
headers(ex,['Bet金币','起始等级','结束等级','覆盖等级数','最小所需EXP','最大所需EXP','共用一个值','最大/最小−1'],d.groups.length+4);
ex.getRange('A:A').format.columnWidth=21;ex.getRange('E:F').format.columnWidth=20;
mix(ex,5,d.groups.map((g,i)=>{const r=i+5,refs=g.levels.map(l=>`'逐级_明细'!S${l+4}`).join(',');return [g.bet,Math.min(...g.levels),Math.max(...g.levels),g.levels.length,`=MIN(${refs})`,`=MAX(${refs})`,`=IF(ABS(F${r}-E${r})<0.0000001,"唯一","冲突")`,`=F${r}/E${r}-1`];}));ex.getRange(`H5:H${d.groups.length+4}`).setNumberFormat('0.00%');

function chart(s,helper,start,stop,columns,labels,titleText,position,fmt,tick){
 s.getRange(`${helper}4:${col(helper.charCodeAt(0)-64+columns.length)}4`).values=[['等级',...labels]];
 const x=helper.charCodeAt(0)-64;
 s.getRange(`${helper}5:${helper}${stop-start+5}`).formulas=Array.from({length:stop-start+1},(_,j)=>[`=""&'逐级_明细'!A${start+j+4}`]);
 for(let k=0;k<columns.length;k++){
  const [source,divisor=1]=columns[k];
  const vals=Array.from({length:stop-start+1},(_,j)=>{const l=start+j;return [`='逐级_明细'!${source}${l+4}/${divisor}`];});
  s.getRange(`${col(x+k+1)}5:${col(x+k+1)}${stop-start+5}`).formulas=vals;
 }
 const c=s.charts.add('line',s.getRange(`${helper}4:${col(x+columns.length)}${stop-start+5}`));c.setPosition(...position);c.title=titleText;
 c.titleTextStyle.fontSize=15;c.titleTextStyle.typeface='Microsoft YaHei';
 c.legend={position:'top',textStyle:{typeface:'Microsoft YaHei',fontSize:11}};
 c.xAxis={axisType:'textAxis',tickLabelInterval:tick,textStyle:{typeface:'Microsoft YaHei',fontSize:10}};
 c.yAxis={numberFormatCode:fmt,numberFormatSourceLinked:false,textStyle:{typeface:'Microsoft YaHei',fontSize:10}};
 for(const [i,ser]of c.series.items.entries())ser.line={fill:['#D97706','#2563EB','#059669'][i],style:i?'dashed':'solid',width:2};
}
const bo=sheet(visible[0]);title(bo,'CR × Cash Frenzy｜Bet解锁对比','金币原值对标；CF冲突已按较低Bet统一。目标线为待验收方案，未写入dev；下钻到Bet档位/逐级明细。',55);
chart(bo,'P',1,300,[['E',1e6],['R',1e6]],['CR dev r7252','CF正式 / CR候选目标'],'普通最大Bet · 1–300级（百万金币）',['A5','N25'],'#,##0.0',25);
chart(bo,'U',1,5000,[['E',1e6],['R',1e6]],['CR dev r7252','CF解锁表目标'],'普通最大Bet · 1–5000级（百万金币）',['A29','N49'],'#,##0',250);
bo.mergeCells('A26:N27');bo.getRange('A26').values=[['15–19级与250–300级保留双来源，正式目标取较低值；CF301级后仅有Bet解锁锚点，不代表有同级经验或成本数据。']];bo.getRange('A26:N27').format.wrapText=true;
bo.mergeCells('A51:N53');bo.getRange('A51').values=[['本轮已完成解锁目标与数据对比；未生成可提交配置。共享Bet经验冲突、额外Bet档处理及活动字段耦合须在验收后定向落表。LevelCfg不修改。']];bo.getRange('A51:N53').format.wrapText=true;
const co=sheet(visible[1]);title(co,'同Bet升级体验｜次数与美元门槛','同等级、同金币Bet比较；CF小数是历史期望，整Spin线是向上取整的模拟基准，不是CF客户端实测。',55);
chart(co,'P',1,300,[['I'],['Y'],['AA']],['CR dev同Bet','CF期望向上取整','CR经验候选'],'同Bet升一级所需整Spin · 1–300级',['A5','N25'],'#,##0',25);
chart(co,'U',1,300,[['K'],['O'],['AC']],['CR dev同Bet','CF历史期望成本','CR经验候选整Spin成本'],'同Bet美元消耗门槛 · 1–300级（USD）',['A29','N49'],'$#,##0.00',25);
co.mergeCells('A26:N27');co.getRange('A26').values=[['候选5–300级匹配整Spin模型；1–4级遵从User要求保留dev Spin门槛，仍不一致。小数期望差异在S列保留，不宣称全部游戏体验已一致。']];co.getRange('A26:N27').format.wrapText=true;
co.mergeCells('A51:N54');co.getRange('A51').values=[['美元仍有差异：CR等级专项沿用95% RTP、CF历史表85%；两边金币/USD不同。明细G/N列列出换算分母，AD列按两边同一整Spin口径计算成本偏差，未改RTP或价值配置。']];co.getRange('A51:N54').format.wrapText=true;
const eo=sheet(visible[2]);title(eo,'单次Spin经验｜逐级反推与落表限制','反推EXP=固定dev升级门槛÷CF同级历史Spin。它是CR对齐候选，不是CF原始经验配置。',44);
chart(eo,'P',5,300,[['F'],['S'],['Z']],['CR dev同Bet EXP','小数期望精确反推','整Spin模型候选EXP'],'每Spin经验 · 5–300级（点）',['A5','N25'],'#,##0',25);
eo.mergeCells('A27:N29');eo.getRange('A27').values=[['小数期望有7组共享Bet冲突；整Spin模拟存在17档可行经验区间，可覆盖5–300级。候选按最小改动选值，精确期望与整数模拟分别展示。']];eo.getRange('A27:N29').format={wrapText:true,fill:'#FFF2CC',font:{bold:true},rowHeight:24};
eo.mergeCells('A31:N33');eo.getRange('A31').values=[['1–4级是Spin门槛模式，调整levelExp不改变升级次数，遵从User要求保留门槛。301级以后缺CF同级Spin，本轮不外推所谓“CF原始EXP”。']];eo.getRange('A31:N33').format.wrapText=true;
eo.mergeCells('A35:N38');eo.getRange('A35').values=[['CF历史Spin有分数，作为体验期望参与反推；dev实际升级有整Spin取整。两者单列，不能用取整后的差异伪称逐级经验完全一致。所有结果均为配置推导，未执行游戏采集。']];eo.getRange('A35:N38').format.wrapText=true;
eo.mergeCells('A40:N43');eo.getRange('A40').values=[['不可直接落表：缺来源档暂留旧值时，整张Bet表有9处经验倒挂；参考档的逐级匹配不代表所有Bet体验一致。经验候选页K列逐处标红，待完整规则明确后处理。']];eo.getRange('A40:N43').format={wrapText:true,fill:'#FCE4D6',font:{bold:true,color:'#9C0006'}};
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:"'逐级_明细'!A5:F8",include:'values,formulas',tableMaxRows:4,tableMaxCols:6})).ndjson);
await fs.mkdir(path.join(dir,'previews'),{recursive:true});
const preview=await wb.render({sheetName:visible[2],range:'A27:N38',scale:1,format:'png'});await fs.writeFile(path.join(dir,'previews/artifact-notes.png'),new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(dir,'CR_vs_CF_Bet解锁与经验对照_r7252.xlsx'));
console.log('Authored 7 visible sheets, 3 source sheets, 5 formula-bound line charts.');
