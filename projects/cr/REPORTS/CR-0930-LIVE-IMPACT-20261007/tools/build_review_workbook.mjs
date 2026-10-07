import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
const runtimeBase=process.env.CR_REPORT_NODE_MODULES;
const resolveRuntime=createRequire(runtimeBase?path.join(path.dirname(runtimeBase),'package.json'):import.meta.url);
const { Workbook, SpreadsheetFile }=await import(pathToFileURL(resolveRuntime.resolve('@oai/artifact-tool')).href);
process.on('uncaughtException',e=>{console.error(e.stack?.split('\n').slice(0,10).join('\n')||String(e));process.exit(1);});
process.on('unhandledRejection',e=>{console.error(e.stack?.split('\n').slice(0,10).join('\n')||String(e));process.exit(1);});

const [inputFile, outputDir] = process.argv.slice(2);
if (!inputFile || !outputDir) throw new Error('Usage: node build_review_workbook.mjs model.json output-directory');
const model=JSON.parse(await fs.readFile(inputFile,'utf8'));
const wb=Workbook.create();
const font='Microsoft YaHei';
const palette=['#456A8D','#D97732','#668B67','#9575A8'];
const col=i=>String.fromCharCode(65+i);
const layouts=[];
const expected=[];
await fs.mkdir(outputDir,{recursive:true});
for(const p of model.pages)wb.worksheets.add(p.name);
function note(sh,row,text){
  const r=sh.getRange(`A${row}:J${row}`);r.merge();
  sh.getRange(`A${row}`).values=[[text]];
  r.format.wrapText=true;r.format.rowHeight=32;r.format.font={name:font,size:10,color:'#596579'};
}
function ratioFormulas(sh,row,econ=false){
  sh.getRange(`D${row}`).formulas=[[`=IF(C${row}>0,B${row}/C${row},"N/A")`]];
  sh.getRange(`G${row}`).formulas=[[`=IF(F${row}>0,E${row}/F${row},"N/A")`]];
  for(const c of ['D','G']){sh.getRange(`${c}${row}`).setNumberFormat('0.0%');sh.getRange(`${c}${row}`).format.horizontalAlignment='right';}
  if(!econ){
    sh.getRange(`H${row}`).formulas=[[`=IF(AND(ISNUMBER(D${row}),ISNUMBER(G${row})),(G${row}-D${row})*100,"N/A")`]];
    sh.getRange(`I${row}`).formulas=[[`=IF(AND(ISNUMBER(D${row}),ISNUMBER(G${row}),D${row}>0),G${row}/D${row}-1,"N/A")`]];
    sh.getRange(`H${row}`).setNumberFormat('+0.0;-0.0;0.0');sh.getRange(`I${row}`).setNumberFormat('+0.0%;-0.0%;0.0%');
    sh.getRange(`H${row}:I${row}`).format.horizontalAlignment='right';
  }
}
for(const p of model.pages){
  const sh=wb.worksheets.getItem(p.name);sh.showGridLines=false;sh.freezePanes.unfreeze();
  sh.tabColor=p.name.startsWith('00')?'#2D4059':p.name.startsWith('07')?'#9BA6B2':'#547A99';
  const estimated=50+p.sections.reduce((n,s)=>n+s.rows.length*3+10,0);
  sh.getRange(`A1:L${estimated}`).format.font={name:font,size:10,color:'#243247'};
  sh.getRange(`A1:L${estimated}`).format.verticalAlignment='center';
  sh.getRange(`A1:L${estimated}`).format.rowHeight=24;
  const widths=[32,15,15,16,16,16,16,16,16,29,3,12];
  widths.forEach((w,i)=>sh.getRange(`${col(i)}1:${col(i)}${estimated}`).format.columnWidth=w);
  sh.getRange('A2').values=[[p.title]];sh.getRange('A2').format.font={name:font,size:16,bold:true,color:'#263F5B'};
  sh.getRange('A2:J2').format.rowHeight=32;
  sh.getRange('A3:J3').format.borders={bottom:{style:'thin',color:'#9AAEC2'}};
  p.notes.forEach((n,i)=>note(sh,4+i,n));
  let row=p.chart?26:9;const sections=[];
  for(let si=0;si<p.sections.length;si++){
    const s=p.sections[si];
    sh.getRange(`A${row}`).values=[[s.title]];sh.getRange(`A${row}`).format.font={name:font,size:12,bold:true,color:'#263F5B'};
    sh.getRange(`A${row}:J${row}`).format.rowHeight=27;row++;
    const head=row;const count=s.headers.length;
    const spans=count<=6 && s.kind==='plain' && s.rows.every(r=>r.filter(v=>typeof v==='number').length<2);
    const starts=Array.from({length:count},(_,i)=>spans?Math.floor(i*10/count):i);
    const ends=Array.from({length:count},(_,i)=>spans?Math.floor((i+1)*10/count)-1:i);
    const writeRow=(vals,r,isHeader=false)=>{
      vals.forEach((v,i)=>{
        const address=`${col(starts[i])}${r}:${col(ends[i])}${r}`;
        if(starts[i]!==ends[i])sh.getRange(address).merge();
        if(!isHeader && s.formats?.[i]==='date' && typeof v==='string')v=new Date(v+'T12:00:00Z');
        sh.getRange(`${col(starts[i])}${r}`).values=[[v]];
        const cell=sh.getRange(address);
        cell.format.wrapText=isHeader||typeof v==='string';
        cell.format.horizontalAlignment=isHeader?'center':typeof v==='number'?'right':'left';
        if(s.formats?.[i])cell.setNumberFormat(s.formats[i]==='date'?'yyyy-mm-dd':s.formats[i]);
        else if(typeof v==='number')cell.setNumberFormat('#,##0');
      });
      const range=sh.getRange(`A${r}:${col(ends[count-1])}${r}`);
      if(isHeader){range.format.fill='#344E6B';range.format.font={name:font,size:10,bold:true,color:'#FFFFFF'};range.format.rowHeight=38;}
      else{
        if((r-head)%2===0)range.format.fill='#F1F5F9';
        const lens=vals.map((v,i)=>typeof v==='string'?Math.ceil(v.length/Math.max(8,(ends[i]-starts[i]+1)*12)):1);
        range.format.rowHeight=Math.max(28,Math.min(112,Math.max(...lens)*16+8));
      }
    };
    writeRow(s.headers,row,true);row++;
    const begin=row;
    s.rows.forEach((vals,ri)=>{
      writeRow(vals,row);
      for(const [i,format] of Object.entries(s.rowFormats?.[ri]||{}))sh.getRange(`${col(starts[Number(i)])}${row}`).setNumberFormat(format);
      if(s.kind==='ratios'||s.kind==='econratios'){
        ratioFormulas(sh,row,s.kind==='econratios');
        if(vals[2]>0)expected.push({sheet:p.name,cell:`D${row}`,value:vals[1]/vals[2]});
        if(vals[5]>0)expected.push({sheet:p.name,cell:`G${row}`,value:vals[4]/vals[5]});
      }
      if(s.kind==='econratios')for(const c of ['B','C','E','F'])if(typeof vals[c.charCodeAt(0)-65]==='number'&&Math.abs(vals[c.charCodeAt(0)-65])>=1e8)sh.getRange(`${c}${row}`).setNumberFormat('0.0,,"百万"');
      if(s.kind==='percapita'){
        sh.getRange(`D${row}`).formulas=[[`=B${row}/C${row}`]];sh.getRange(`G${row}`).formulas=[[`=E${row}/F${row}`]];
        for(const c of ['B','D','E','G'])sh.getRange(`${c}${row}`).setNumberFormat('0.0,,"百万"');
        sh.getRange(`D${row}`).format.horizontalAlignment='right';sh.getRange(`G${row}`).format.horizontalAlignment='right';
        expected.push({sheet:p.name,cell:`D${row}`,value:vals[1]/vals[2]},{sheet:p.name,cell:`G${row}`,value:vals[4]/vals[5]});
      }
      if(s.kind==='adjusted'){sh.getRange(`F${row}`).formulas=[[`=(E${row}-D${row})*100`]];sh.getRange(`F${row}`).format.horizontalAlignment='right';}
      if(s.kind==='depth'){sh.getRange(`F${row}`).formulas=[[`=IF(D${row}>0,E${row}/D${row},"N/A")`]];sh.getRange(`F${row}`).format.horizontalAlignment='right';}
      if(s.kind==='coverage'){sh.getRange(`F${row}`).formulas=[[`=IF(D${row}>0,E${row}/D${row},"N/A")`]];sh.getRange(`F${row}`).format.horizontalAlignment='right';}
      row++;
    });
    const end=row-1;
    if(s.kind==='heatmap')sh.getRange(`C${begin}:E${end}`).conditionalFormats.add('colorScale',{colors:['#FFF7E8','#B6D3E3','#477795'],thresholds:['min','50%','max']});
    if(s.rows.length>12&&!spans){const t=sh.tables.add(`A${head}:${col(count-1)}${end}`,true,`T${model.pages.indexOf(p)}_${si}`);t.showFilterButton=true;}
    sections.push({title:s.title,head,begin,end,count});
    if(s.note){note(sh,row+1,s.note);row+=3;}else row+=2;
  }
  if(p.chart){
    const cfg=p.chart;const target=sections[cfg.section];const end=cfg.limit?Math.min(target.end,target.begin+cfg.limit-1):target.end;
    const sec=p.sections[cfg.section];let categories=sh.getRange(`${col(cfg.category)}${target.head}:${col(cfg.category)}${end}`);
    if(sec.formats?.[cfg.category]==='date'){
      sh.getRange(`L${target.head}`).values=[['日期标签']];
      sh.getRange(`L${target.begin}:L${end}`).formulas=Array.from({length:end-target.begin+1},(_,i)=>[`=TEXT(A${target.begin+i},"mm/dd")`]);
      categories=sh.getRange(`L${target.head}:L${end}`);
    }
    const ch=sh.charts.add('line',[categories,...cfg.series.map(i=>sh.getRange(`${col(i)}${target.head}:${col(i)}${end}`))]);
    ch.title=cfg.title;ch.titleTextStyle.fontSize=15;ch.titleTextStyle.typeface=font;
    ch.legend={position:'top',textStyle:{typeface:font,fontSize:12}};
    ch.xAxis={axisType:'textAxis',textStyle:{typeface:font,fontSize:12}};
    ch.yAxis={numberFormatCode:cfg.format,numberFormatSourceLinked:false,textStyle:{typeface:font,fontSize:12}};
    ch.series.items.forEach((ser,i)=>{ser.line={fill:palette[i],style:'solid',width:2};ser.fill=palette[i];});
    ch.setPosition('A8','J24');
  }
  layouts.push({sheet:p.name,lastRow:row,sections});
}
wb.recalculate();
for(const check of expected){
  const got=wb.worksheets.getItem(check.sheet).getRange(check.cell).values[0][0];
  if(typeof got!=='number'||Math.abs(got-check.value)>1e-10)throw new Error(`Formula mismatch ${check.sheet}!${check.cell}`);
}
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},maxChars:5000,summary:'Task targeted formula validation'});
await fs.writeFile(path.join(outputDir,'formula-inspection.ndjson'),errors.ndjson);
await fs.writeFile(path.join(outputDir,'layout.local.json'),JSON.stringify(layouts,null,2));
await fs.writeFile(path.join(outputDir,'formula-checks.local.json'),JSON.stringify({count:expected.length,checks:expected,passed:true},null,2));
const xlsx=await SpreadsheetFile.exportXlsx(wb);
const outpath=path.join(outputDir,`CR_0930_线上效果复盘_${model.cutoff}.xlsx`);
await xlsx.save(outpath);
const previews=path.join(outputDir,'visual-review');await fs.mkdir(previews,{recursive:true});
for(const p of model.pages){
  const image=await wb.render({sheetName:p.name,range:'A1:J48',scale:1.2,format:'png'});
  await fs.writeFile(path.join(previews,`${p.name}.png`),new Uint8Array(await image.arrayBuffer()));
}
for(const [sheetName,range,label] of [['02_新增留存','A50:J100','留存明细'],['05_经济与活动','A48:J110','经济明细'],['03_付费留存','A49:J115','付费明细']]){
  const image=await wb.render({sheetName,range,scale:1.2,format:'png'});
  await fs.writeFile(path.join(previews,`${label}.png`),new Uint8Array(await image.arrayBuffer()));
}
for(const [sheetName,title,label] of [['04_成长体验','首日等级分层：机器样本返还','等级分层'],['05_经济与活动','首次余额不足10Bet之后30分钟','低余额后续']]){
  const layout=layouts.find(x=>x.sheet===sheetName),section=layout.sections.find(x=>x.title===title);
  const range=`A${section.head-1}:J${Math.min(layout.lastRow,section.end+15)}`;
  const img=await wb.render({sheetName,range,scale:1.2,format:'png'});
  await fs.writeFile(path.join(previews,`${label}.png`),new Uint8Array(await img.arrayBuffer()));
}
console.log(JSON.stringify({file:outpath,sheets:model.pages.length,charts:model.pages.filter(p=>p.chart).length,formula_checks:expected.length,exported:true,rendered:true}));
