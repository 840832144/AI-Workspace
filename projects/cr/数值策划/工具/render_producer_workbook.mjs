// Artifact Tool 导出适配器。业务、来源和公式由 Python 生成；输入/输出都在受控目录。
// node render_producer_workbook.mjs <workbook-plan.json> <output-dir>
import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const [planPath, outputDir] = process.argv.slice(2);
const previewOnly=process.argv.includes('--preview-only');
if (!planPath || !outputDir) throw new Error('需要计划路径和受控输出目录');
for (let d = path.resolve(outputDir); ; d = path.dirname(d)) {
  try { await fs.stat(path.join(d, '.git')); throw new Error('禁止在Git目录输出商业数值'); }
  catch (e) { if (e.code !== 'ENOENT') throw e; }
  if (path.dirname(d) === d) break;
}
const plan = JSON.parse(await fs.readFile(planPath, 'utf8'));
const wb = Workbook.create();
const letter = (n) => { let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s; };
for (const p of plan.sheets) wb.worksheets.add(p.name);
await fs.mkdir(outputDir, {recursive:true});
// Artifact每次写入会重算依赖；先写计算/输入，最后写汇总，避免样本逐行触发整列聚合。
const writeOrder=[...plan.sheets.filter(p=>p.hidden),...plan.sheets.filter(p=>!p.hidden)];
for (const p of writeOrder) {
  const s=wb.worksheets.getItem(p.name);
  if(plan.preserved_sheets?.includes(p.name)){
    s.getRange(`A1:${letter(p.rows[0].length)}1`).values=[p.rows[0]];
    continue; // 原Accepted工作表由外链适配层原样接回，避免重复构建概率明细。
  }
  const h=p.rows.length,w=Math.max(...p.rows.map(r=>r.length));
  const matrix=p.rows.map(r=>Array.from({length:w},(_,j)=>typeof r[j]==='string'&&r[j].startsWith('=')?null:(r[j]??null)));
  s.getRange(`A1:${letter(w)}${h}`).values=matrix;
  // 按列连续区间写入公式，避免逐格调用和覆盖同一行的文本/原值。
  for(let c=0;c<w;c++){
    for(let r=0;r<h;){
      if(typeof p.rows[r][c]!=='string'||!p.rows[r][c].startsWith('=')){r++;continue;}
      const start=r, formulas=[];
      while(r<h&&typeof p.rows[r][c]==='string'&&p.rows[r][c].startsWith('=')){formulas.push([p.rows[r][c]]);r++;}
      s.getRange(`${letter(c+1)}${start+1}:${letter(c+1)}${r}`).formulas=formulas;
    }
  }
  s.showGridLines=false;
  if(p.hidden){console.log(`built hidden ${p.name}`);continue;} // visibility由适配层补齐
  if(p.dashboard){
    const width=Math.max(w,12),end=letter(width);
    const all=s.getRange(`A1:${end}${h}`);
    all.format={font:{name:'宋体',size:11,color:'#24364B'},rowHeight:25,columnWidth:17,verticalAlignment:'center'};
    all.setNumberFormat('#,##0');
    s.tabColor='#473A78';
    for(const r of [1,2,3,4])s.mergeCells(`A${r}:L${r}`);
    s.getRange('A1:L1').format.font={name:'宋体',size:18,bold:true,color:'#283654'};
    s.getRange('A1:L1').format.rowHeight=36;
    s.getRange('A2:L4').format.font={name:'宋体',size:11,color:'#586575'};
    s.getRange('A3:L3').format.wrapText=true;s.getRange('A3:L3').format.rowHeight=44;
    const colors=['#FBE9DD','#E8F2E9','#EEE8F8','#FFF4D6'];
    for(let i=0;i<4;i++){
      const a=letter(i*3+1),z=letter(i*3+3);
      s.mergeCells(`${a}6:${z}6`);s.mergeCells(`${a}7:${z}8`);
      s.getRange(`${a}6:${z}8`).format.fill=colors[i];
      s.getRange(`${a}7:${z}8`).format.font={name:'宋体',size:17,bold:true,color:'#283654'};
      s.getRange(`${a}7:${z}8`).format.horizontalAlignment='center';
    }
    for(const sec of p.sections){
      const z=letter(sec.columns);
      s.mergeCells(`A${sec.row-1}:${z}${sec.row-1}`);
      s.getRange(`A${sec.row-1}:${z}${sec.row-1}`).format={fill:'#EDEAF4',font:{bold:true},rowHeight:28};
      s.getRange(`A${sec.row}:${z}${sec.row}`).format={fill:'#35405C',font:{name:'宋体',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:42};
      const data=s.getRange(`A${sec.row+1}:${z}${sec.end}`);
      data.format={wrapText:true,rowHeight:p.name==='总览'?65:(['卡包_概览','777_概览','商城_Pass_概览','常驻_概览'].includes(p.name)?80:42),borders:{bottom:{style:'thin',color:'#DAE0E7'}}};
      data.conditionalFormats.add('containsText',{text:'Unknown',format:{fill:'#FFF2C5',font:{color:'#6B571E'}}});
      for(const c of p.cost_columns||[])if(c<=sec.columns)s.getRange(`${letter(c)}${sec.row+1}:${letter(c)}${sec.end}`).format.font.color='#AC4924';
      for(const c of p.reward_columns||[])if(c<=sec.columns)s.getRange(`${letter(c)}${sec.row+1}:${letter(c)}${sec.end}`).format.font.color='#237448';
    }
    for(const [range,fmt] of p.formats)s.getRange(range).setNumberFormat(fmt);
    for(const spec of p.charts){
      const chart=s.charts.add(spec.type,spec.columns.map(c=>s.getRange(`${letter(c)}${spec.start}:${letter(c)}${spec.end}`)));
      chart.title=spec.title;chart.setPosition(...spec.position);
      chart.titleTextStyle.typeface='宋体';chart.titleTextStyle.fontSize=13;
      chart.legend={position:'top',textStyle:{typeface:'宋体',fontSize:10}};
      chart.xAxis={axisType:'textAxis',textStyle:{typeface:'宋体',fontSize:9}};
      chart.yAxis={numberFormatCode:spec.format,numberFormatSourceLinked:false,textStyle:{typeface:'宋体',fontSize:10}};
      for(let i=0;i<chart.series.items.length;i++){
        const color=['#C65C31','#39805C','#6D5B99'][i%3];chart.series.items[i].fill=color;
        if(spec.type==='line')chart.series.items[i].line={fill:color,style:'solid',width:2};
      }
    }
    s.freezePanes.freezeRows(30);
    console.log(`built dashboard ${p.name}`);continue;
  }
  s.tabColor='#284B63';
  const used=s.getRange(`A1:${letter(w)}${h}`);
  used.format.font={name:'宋体',size:11,color:'#192C3A'};
  used.format.rowHeight=23;
  used.format.columnWidth=17;
  used.setNumberFormat('#,##0');
  used.format.verticalAlignment='center';
  s.getRange(`A1:A${h}`).format.columnWidth=26;
  if(p.style_key==='常驻')s.getRange(`B1:B${h}`).format.columnWidth=28;
  const titleEnd=letter(Math.min(w,12));
  for(const r of [1,2,3])s.mergeCells(`A${r}:${titleEnd}${r}`);
  s.getRange(`A1:${titleEnd}1`).format.font={name:'宋体',size:16,bold:true,color:'#17354B'};
  s.getRange(`A1:${titleEnd}1`).format.rowHeight=32;
  s.getRange(`A2:${titleEnd}3`).format.font={name:'宋体',size:11,color:'#526571'};
  s.getRange(`A3:${titleEnd}3`).format.wrapText=true;
  s.getRange(`A3:${titleEnd}3`).format.rowHeight=34;
  for(const sec of p.sections){
    const end=letter(sec.columns);
    s.mergeCells(`A${sec.row-1}:${end}${sec.row-1}`);
    const band=s.getRange(`A${sec.row-1}:${end}${sec.row-1}`);
    band.format.fill='#E8EFF4';band.format.font={bold:true};band.format.rowHeight=27;
    const header=s.getRange(`A${sec.row}:${end}${sec.row}`);
    header.format={fill:'#284B63',font:{name:'宋体',size:11,bold:true,color:'#FFFFFF'},wrapText:true,horizontalAlignment:'center',verticalAlignment:'center',rowHeight:43};
    const data=s.getRange(`A${sec.row+1}:${end}${sec.end}`);
    data.format.borders={bottom:{style:'thin',color:'#B8C7D0'}};
    if(sec.span){
      for(let r=sec.row;r<=sec.end;r++)for(let c=1;c<=sec.columns;c+=sec.span)s.mergeCells(`${letter(c)}${r}:${letter(c+sec.span-1)}${r}`);
      data.format.wrapText=true;data.format.rowHeight=63;
    }
    if(p.name==='Unknown'){
      data.format.wrapText=true;data.format.rowHeight=66;
      s.getRange('A1:B1').format.columnWidth=13;
      s.getRange('C1:E1').format.columnWidth=51;
    }
    if(p.name==='总览'&&sec.columns===4){
      data.format.wrapText=true;data.format.rowHeight=100;
      // 这张宽表沿用同页36组体验的列宽，用跨列文本会扰动数字表，保持四列可滚动。
    }
  }
  const first=p.sections[0];
  const decimals={总览:[5,7,8,9,10],基础金币:[6,7,8,9],BET_RTP:[8,13,14,15],Buff:[3,5],任务福利:[5],商城_Pass:[5,7],卡包卡册:[5],薯片:[7],777:[7]};
  for(const c of decimals[p.style_key||p.name]||[])if(c<=first.columns)s.getRange(`${letter(c)}${first.row+1}:${letter(c)}${first.end}`).setNumberFormat('#,##0.0000');
  if(p.name==='美金金币档位_明细')s.getRange(`E1:T${h}`).format.columnWidth=24;
  if(p.name==='等级_阶段概览'){
    s.getRange(`C1:C${h}`).format.columnWidth=42;
    s.getRange(`H1:H${h}`).format.columnWidth=31;
    s.getRange(`A7:J${h}`).format.wrapText=true;
    s.getRange(`A7:J${h}`).format.rowHeight=44;
  }
  for(const [range,fmt] of p.formats)s.getRange(range).setNumberFormat(fmt);
  s.freezePanes.freezeRows(6);
  console.log(`built ${p.name}`);
}
if(previewOnly){
  for(const p of plan.sheets){
    const width=Math.max(...p.rows.map(r=>r.length));
    const preview=await wb.render({sheetName:p.name,range:p.preview_range||`A1:${letter(width)}${p.rows.length}`,scale:1.2,format:'png'});
    await fs.writeFile(path.join(outputDir,`native-preview-${p.name}.png`),new Uint8Array(await preview.arrayBuffer()));
  }
  process.exit(0);
}
const deferNative=!!plan.preserved_sheets?.length;
console.log(deferNative?'defer full calculation until preserved source sheets are restored':'recalculate');
if(!deferNative)wb.recalculate();
const failures=[];
for(const check of deferNative?[]:plan.checks){
  const m=check.cell.match(/^'?(.+?)'?!([A-Z]+\d+)$/);
  const actual=wb.worksheets.getItem(m[1]).getRange(m[2]).values[0][0];
  const tolerance=Math.max(1e-8,Math.abs(check.expected)*1e-9);
  if(typeof actual!=='number'||Math.abs(actual-check.expected)>tolerance)failures.push({...check,actual});
}
await fs.writeFile(path.join(outputDir,'accepted-comparison.json'),JSON.stringify({count:deferNative?0:plan.checks.length,deferred_to_native:deferNative,failures},null,2));
console.log(deferNative?`${plan.checks.length} current checks deferred to native Excel`:`comparisons ${plan.checks.length}; failed ${failures.length}`);
if(!deferNative){
  const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},maxChars:12000});
  await fs.writeFile(path.join(outputDir,'formula-errors.ndjson'),errors.ndjson);
}
const xlsx=await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(outputDir,plan.title+'.xlsx'));
console.log('exported');
// 每个前台视图一次预览；旧表数值从未作为输入。
for(const p of deferNative?[]:plan.sheets.filter(s=>!s.hidden)){
  const width=p.name==='Unknown'?5:Math.min(10,Math.max(...p.rows.map(r=>r.length)));
  const preview=await wb.render({sheetName:p.name,range:p.preview_range||`A1:${letter(width)}${p.name==='Unknown'?15:20}`,scale:1.2,format:'png'});
  await fs.writeFile(path.join(outputDir,`preview-${p.name}.png`),new Uint8Array(await preview.arrayBuffer()));
}
await fs.writeFile(path.join(outputDir,'render-summary.json'),JSON.stringify({rendered:plan.sheets.filter(s=>!s.hidden).length,comparison_count:plan.checks.length,comparison_failures:failures.length},null,2));
if(failures.length)process.exitCode=1;
