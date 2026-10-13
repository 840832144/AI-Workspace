// Values-only presentation of an existing controlled comparison. No source-model edit.
import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const out=process.argv[2],renderName=process.argv[3];
const d=JSON.parse(await fs.readFile(out+'/display-input.controlled.json','utf8'));
const wb=Workbook.create();
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const style=(s,last,n)=>{
 s.showGridLines=false;s.getRange(`A1:${col(last)}${n}`).format={font:{name:'Microsoft YaHei',size:10,color:'#243447'},rowHeight:22,columnWidth:20,verticalAlignment:'center'};
 s.getRange(`A2:${col(Math.min(8,Math.max(3,last)))}2`).merge();s.getRange('A2').format.font={size:16,bold:true,color:'#183654'};
 s.getRange(`A3:${col(Math.min(8,Math.max(3,last)))}3`).merge();s.getRange('A3').format={wrapText:true,rowHeight:46};
};
const a=wb.worksheets.add('本轮核对');style(a,4,20);
a.getRange('A2').values=[['DSH更新核对及对比表展示']];
a.getRange('A3').values=[['数据表是v6展示快照；本轮新增证据另列，尚未改写数值模型。先查看以下待修订项。']];
a.getRange('A5:D5').values=[['项目','新资料','对原表的影响','处理边界']];
a.getRange(`A6:D${5+d.notes.findings.length}`).values=d.notes.findings;
a.getRange('A5:D5').format={fill:'#183654',font:{color:'#FFFFFF',bold:true},rowHeight:32};
a.getRange('A6:D11').format={wrapText:true,rowHeight:68,verticalAlignment:'center'};
a.getRange('A:A').format.columnWidth=20;a.getRange('B:D').format.columnWidth=43;
a.getRange('A14:D14').merge();a.getRange('A14').values=[[d.notes.basis]];a.getRange('A14').format={wrapText:true,rowHeight:52};
for(const t of d.tabs){
 const s=wb.worksheets.add(t.name),nr=t.rows.length+4,nc=t.rows[0].length;
 style(s,nc,nr);s.getRange('A2').values=[[t.name+'（v6审阅快照）']];
 s.getRange('A3').values=[['DSH新增差异见“本轮核对”；USD三位。40线机型不代表全部特殊机台；100级后是User指定拟合。']];
 s.getRange(`A5:${col(nc)}${nr}`).values=t.rows;
 s.getRange(`A5:${col(nc)}5`).format={fill:'#183654',font:{color:'#FFFFFF',bold:true},wrapText:true,rowHeight:64};
 for(let j=0;j<nc;j++){
   s.getRange(`${col(j+1)}6:${col(j+1)}${nr}`).setNumberFormat(t.formats[j]||'General');
   if(/说明|边界|依据|来源/.test(String(t.rows[0][j])))s.getRange(`${col(j+1)}:${col(j+1)}`).format.columnWidth=50;
 }
 if(/明细|候选/.test(t.name)){s.freezePanes.freezeRows(5);s.freezePanes.freezeColumns(1);}
}
const cs=wb.worksheets.add('对比曲线');style(cs,24,150);
cs.getRange('A2').values=[['原对比曲线（v6快照）']];cs.getRange('A3').values=[['曲线保留原模型全部点；新实测差异列在“本轮核对”，本轮没有重新拟合。']];
let dataRow=170;
const colors=['#2871B5','#EC8847','#207760','#9553A5'];
for(let i=0;i<d.charts.length;i++){
 const x=d.charts[i],n=x.series[0].values.length;
 const rows=[['等级或VIP',...x.series.map(s=>s.name)],...Array.from({length:n},(_,k)=>[x.series[0].categories[k]??String(k+1),...x.series.map(s=>s.values[k]??null)])];
 const rg=cs.getRange(`A${dataRow}:${col(rows[0].length)}${dataRow+n}`);rg.values=rows;rg.setNumberFormat(i<4?'0.000':'0.###');
 const ch=cs.charts.add('line',rg);ch.title=x.title||`对比曲线${i+1}`;
 const r=5+Math.floor(i/2)*29,c=i%2?13:1;ch.setPosition(col(c)+r,col(c+10)+(r+25));
 ch.legend={position:'top',textStyle:{typeface:'Microsoft YaHei',fontSize:10}};
 ch.titleTextStyle.typeface='Microsoft YaHei';ch.titleTextStyle.fontSize=12;
 ch.yAxis={numberFormatCode:i<4?'0.000':'0.###',numberFormatSourceLinked:false};
 for(let j=0;j<ch.series.items.length;j++)ch.series.items[j].line={fill:colors[j%colors.length],width:2,style:'solid'};
 dataRow+=n+3;
}
wb.recalculate();
if(renderName){
 const range=renderName==='本轮核对'?'A2:D11':renderName==='对比曲线'?'A2:K30':'A2:H10';
 const blob=await wb.render({sheetName:renderName,range,scale:1.3});await fs.writeFile(out+'/preview-'+renderName+'.png',new Uint8Array(await blob.arrayBuffer()));
}else{
 console.log((await wb.inspect({kind:'table',range:'本轮核对!A5:D10',tableMaxRows:6,tableMaxCols:4,maxChars:1400})).ndjson);
 await(await SpreadsheetFile.exportXlsx(wb)).save(out+'/CR_CF_POP_对比表_飞书展示审阅版.xlsx');
 console.log(JSON.stringify({exported:true,charts:d.charts.length,numeric_model_changed:false}));
}
