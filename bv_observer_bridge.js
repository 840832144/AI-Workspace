// Observe only Frida's own ARM64 agent load failure, not game library loads.
'use strict';
const bridge=Process.getModuleByName('libnativebridge.so');
const exports=bridge.enumerateExports();
const listeners=[];
for (const e of exports.filter(e => e.type==='function' && /NativeBridgeLoadLibrary/.test(e.name))) {
  listeners.push(Interceptor.attach(e.address,{
    onEnter(args) {
      this.own=false;
      try { this.own=/\/frida-agent-arm64\.so$/.test(args[0].readUtf8String()); } catch(_) {}
    },
    onLeave(result) {
      if (!this.own) return;
      send({kind:'observer_loader_result',loader:e.name,loaded:!result.isNull()});
    }
  }));
}
rpc.exports={
  status() {
    return {module:bridge.path,
            loaders:exports.filter(e=>e.type==='function' && /NativeBridgeLoadLibrary/.test(e.name)).map(e=>e.name)};
  },
  stop() {listeners.forEach(l=>l.detach());}
};
setTimeout(()=>listeners.forEach(l=>l.detach()),15000);
