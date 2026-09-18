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
for (const p of plan.sheets) {
  const s=wb.worksheets.getItem(p.name);
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
  if(p.hidden) continue; // 导出后以标准OOXML sheet state隐藏；当前API未公开visibility设置。
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
    const preview=await wb.render({sheetName:p.name,range:`A1:${letter(width)}${p.rows.length}`,scale:1.5,format:'png'});
    await fs.writeFile(path.join(outputDir,`native-preview-${p.name}.png`),new Uint8Array(await preview.arrayBuffer()));
  }
  process.exit(0);
}
console.log('recalculate');wb.recalculate();
const failures=[];
for(const check of plan.checks){
  const m=check.cell.match(/^'?(.+?)'?!([A-Z]+\d+)$/);
  const actual=wb.worksheets.getItem(m[1]).getRange(m[2]).values[0][0];
  const tolerance=Math.max(1e-8,Math.abs(check.expected)*1e-9);
  if(typeof actual!=='number'||Math.abs(actual-check.expected)>tolerance)failures.push({...check,actual});
}
await fs.writeFile(path.join(outputDir,'accepted-comparison.json'),JSON.stringify({count:plan.checks.length,failures},null,2));
console.log(`accepted comparisons ${plan.checks.length}; failed ${failures.length}`);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},maxChars:12000});
await fs.writeFile(path.join(outputDir,'formula-errors.ndjson'),errors.ndjson);
const xlsx=await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(outputDir,plan.title+'.xlsx'));
console.log('exported');
// 每个前台视图一次预览；旧表数值从未作为输入。
for(const p of plan.sheets.filter(s=>!s.hidden)){
  const width=p.name==='Unknown'?5:Math.min(10,Math.max(...p.rows.map(r=>r.length)));
  const preview=await wb.render({sheetName:p.name,range:`A1:${letter(width)}${p.name==='Unknown'?15:20}`,scale:1.5,format:'png'});
  await fs.writeFile(path.join(outputDir,`preview-${p.name}.png`),new Uint8Array(await preview.arrayBuffer()));
}
await fs.writeFile(path.join(outputDir,'render-summary.json'),JSON.stringify({rendered:plan.sheets.filter(s=>!s.hidden).length,comparison_count:plan.checks.length,comparison_failures:failures.length},null,2));
if(failures.length)process.exitCode=1;
