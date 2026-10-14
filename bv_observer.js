// TASK-0039 scoped passive observation. No game method invocation or return edits.
'use strict';
const types = [
  ['GameLib.Main.Gameplay.Bingo.View', 'BuyCardPanel',
   ['_cardIndex','_betData','_betAddView','_panelModel','_preventClick','_canPlay','_isShowingBuffCost','_multiFastBuffActive','CardAmounts','TicketCost'],
   ['Init','RefreshCards','OnModeChange','OnBetChanged','RefreshTicketText','RefreshDiscountBuff','Close','OnDestroy']],
  ['GameLib.Main.Gameplay.Bingo.View', 'BetAddView',
   ['_index','_usableMaxBetIndex','_betCost','_betListData','_activeSections'],
   ['RefreshBetList','RefreshBet','get_BetCost','OnDestroy']],
  ['GameLib.Main.UI.Model', 'BuyCardPanelModel', ['_currentChooseMode','_buyCardData'], []],
  ['GameLib.Main.Gameplay.Bingo', 'BuyCardContext',
   ['CardCount','BetCost','MissionSaleBubbleVisible','DisableRoundBuffResIDs','HallType','HallConfigID'], []],
  ['GameLib.Main.Gameplay.Bingo.View', 'BaseBingoCardView',
   ['controller','_disableCellClick','canvasGroup','isPlayingBingo','isBingoPlay','MaxLevelBingoMask'],
   ['Initialize','DisableCellClick','ShowMaxLevelBingoMask','CanDaub','TryDaub','ShowManualDaub','OnDestroy']],
  ['GameLib.Main.Gameplay.Bingo.View', 'BingoPlayView',
   ['_isGameOver','_isGamePaused','_bingoCardViews'], ['Initialize','OnRoundStageChanged','OnDestroy']],
  ['GameLib.Main.Gameplay.Bingo.View', 'DaubCellView',
   ['controller','isViewDaubed','isBingo','isAlert','<IsPlayingBingoAnim>k__BackingField'],
   ['SetDaubed','OnDestroy']]
];
let hooks = [], stopped = false, count = 0;
function emit(value) { if (!stopped && count++ < 400) send(value); }
function stop() { stopped = true; hooks.forEach(h => h.detach()); hooks = []; }
rpc.exports = {stop};
setTimeout(stop, 15000); // Independent upper bound even if the host disappears.
try {
  if (Process.arch !== 'arm64') throw Error('arm64_emulated_realm_required');
  const module = Process.getModuleByName('libil2cpp.so');
  function api(name, ret, args) {
    // Only IL2CPP metadata exports, never runtime_invoke or game methods.
    return new NativeFunction(module.getExportByName('il2cpp_' + name), ret, args);
  }
  const domain = api('domain_get','pointer',[])();
  const assemblies = api('domain_get_assemblies','pointer',['pointer','pointer']);
  const image = api('assembly_get_image','pointer',['pointer']);
  const klass = api('class_from_name','pointer',['pointer','pointer','pointer']);
  const field = api('class_get_field_from_name','pointer',['pointer','pointer']);
  const offset = api('field_get_offset','size_t',['pointer']);
  const ftype = api('field_get_type','pointer',['pointer']);
  const tname = api('type_get_name','pointer',['pointer']);
  const free = api('free','void',['pointer']);
  const flags = api('field_get_flags','uint',['pointer']);
  const methods = api('class_get_methods','pointer',['pointer','pointer']);
  const mname = api('method_get_name','pointer',['pointer']);
  const argc = api('method_get_param_count','uint',['pointer']);
  const n = Memory.alloc(Process.pointerSize); n.writeU64(0);
  const aa = assemblies(domain,n), nn = n.readU64().toNumber();
  if (nn < 1 || nn > 1000) throw Error('assembly_count_invalid');
  let schema = [];
  for (const [ns,name,fields,wanted] of types) {
    let cls = ptr(0);
    const nsstr=Memory.allocUtf8String(ns), namestr=Memory.allocUtf8String(name);
    for (let i=0; i<nn && cls.isNull(); i++) cls=klass(image(aa.add(i*Process.pointerSize).readPointer()),nsstr,namestr);
    if (cls.isNull()) throw Error('type_missing:'+name);
    const fs=[];
    for (const fname of fields) {
      const f=field(cls,Memory.allocUtf8String(fname));
      if (f.isNull()) { fs.push({name:fname,missing:true}); continue; }
      const p=tname(ftype(f)); const type=p.readUtf8String(); free(p);
      fs.push({name:fname,type,offset:Number(offset(f)),static:!!(flags(f)&16)});
    }
    const row={name,namespace:ns,fields:fs,methods:[]}; schema.push(row);
    const iter=Memory.alloc(Process.pointerSize); iter.writePointer(ptr(0));
    let m;
    while (!(m=methods(cls,iter)).isNull()) {
      const mn=mname(m).readUtf8String();
      if (!wanted.includes(mn)) continue;
      // MethodInfo starts with methodPointer in the matching IL2CPP ABI.
      // Reject unmapped/non-executable pointers instead of probing calls.
      const target=m.readPointer(), range=Process.findRangeByAddress(target);
      if (!range || !range.protection.includes('x')) throw Error('method_pointer_invalid:'+name+'.'+mn);
      row.methods.push({name:mn,arguments:argc(m),rva:target.sub(module.base).toString()});
      hooks.push(Interceptor.attach(target,{
        onEnter(args) { this.receiver=args[0]; },
        onLeave(retval) {
          if (stopped) return;
          const values={};
          try {
            for (const f of fs) {
              if (f.missing || f.static) continue;
              const a=this.receiver.add(f.offset);
              if (f.type==='System.Boolean') values[f.name]=a.readU8()!==0;
              else if (f.type==='System.Int32') values[f.name]=a.readS32();
              else if (f.type==='System.UInt32') values[f.name]=a.readU32();
              else if (f.type==='System.Int64') values[f.name]=a.readS64().toString();
              // Pointers are identity only; no unbounded heap/object traversal.
              else values[f.name]={unresolved_type:f.type};
            }
            emit({kind:'natural_callback',type:name,method:mn,object:this.receiver.toString(),
                  closed:['Close','OnDestroy'].includes(mn),values,
                  natural_return:mn==='get_BetCost'?retval.toInt32():null});
          } catch(e) { emit({kind:'observation_error',error:String(e)}); stop(); }
        }
      }));
    }
  }
  emit({kind:'observer_ready',arch:Process.arch,schema});
} catch(e) { emit({kind:'observer_error',error:String(e)}); stop(); }
