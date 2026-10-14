"""Scoped original-instance read-only panel binding for the studied ARM64 build.

No attach, agent, method invocation, heap scan, device writes or input. The
caller owns runtime accounting. Address plans and initialized metadata names
survive between snapshots; every business value, object class pointer, method
slot, dispatch flag and callee is obtained twice within one bounded window.
"""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

from bv_panel_fields import decode_panel_price

BUILD_ID_ADDRESS=0x8454098
BUILD_ID=bytes.fromhex('040000001400000003000000474e55007f687ebac8e6fc17d74a9eea2749859fd4d9b29d')
LOADS=((0,0),(48221268,48204884),(124504368,124471600),
       (130639280,130590128),(138690560,138625024),(138723328,138641408),
       (138756096,138657792),(138870784,138756096))


def merge_ranges(ranges):
    """Merge overlapping/adjacent requested bytes, never gaps or extra pages."""
    result=[]
    for address,size in sorted(set(ranges)):
        if result and address<=result[-1][0]+result[-1][1]:
            start,length=result[-1]
            result[-1]=(start,max(start+length,address+size)-start)
        else:result.append((address,size))
    return result


def saved_reader(values):
    def read(address,size):
        for (start,length),data in values.items():
            if start<=address and address+size<=start+length:
                return data[address-start:address-start+size]
        raise ValueError('panel_address_plan_changed')
    return read


class ScopedPanelReader:
    def __init__(self,device,folder):
        self.device=device;self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True)
        self.calls=0;self.bytes=0;self.sequence=0;self.plan=None
        self.deadline=time.monotonic()+40;self.maps=[];self.discovered={}

    def adb(self,args):
        from bv_autoplay import ADB,DEV
        if self.device.stopped() or (self.folder/'STOP').exists():raise ValueError('panel_read_stopped')
        remaining=self.deadline-time.monotonic()
        if remaining<=0:raise ValueError('panel_read_deadline')
        self.calls+=1
        result=subprocess.run([ADB,'-s',DEV,'exec-out',*args],capture_output=True,
                              timeout=min(2,remaining))
        if result.returncode:raise ValueError('scoped_panel_transport_failed')
        if self.device.stopped():raise ValueError('panel_read_stopped')
        return result.stdout

    @staticmethod
    def epoch(stat):
        text=stat.decode();pid=int(text.split(' ',1)[0])
        return (pid,int(text.rsplit(')',1)[1].split()[19]))

    def check_epoch(self):
        raw=self.adb(['cat',f'/proc/{self.pid}/stat','/proc/sys/kernel/random/boot_id'])
        if self.epoch(raw)!=self.process or raw.decode().splitlines()[-1]!=self.boot:
            raise ValueError('panel_process_epoch_changed')

    def read_ranges(self,ranges):
        if sum(n for _,n in ranges)>32768:raise ValueError('panel_read_total_bound')
        values={};parts=[]
        # At most 32 numeric, bounded dd operations per exec; no user shell text.
        for start in range(0,len(ranges),32):
            part=ranges[start:start+32]
            for address,size in part:
                if (type(address) is not int or type(size) is not int or not 1<=size<=4096
                        or not any(lo<=address and address+size<=hi and 'r' in perm for lo,hi,perm in self.maps)):
                    raise ValueError('panel_read_unmapped_or_unbounded')
            parts.append(part)
        def fetch(part):
            commands=[f'dd if=/proc/{self.pid}/mem bs=1 skip={a} count={n} status=none' for a,n in part]
            return self.adb(['sh','-c',' && '.join(commands)])
        # Disjoint reads in a pass are independent. The two complete passes stay
        # sequential; any failed/cancelled chunk rejects the entire observation.
        if len(parts)>1:
            with ThreadPoolExecutor(max_workers=4) as pool:raws=list(pool.map(fetch,parts))
        else:raws=[fetch(part) for part in parts]
        for part,raw in zip(parts,raws):
            if len(raw)!=sum(n for _,n in part):raise ValueError('panel_partial_read')
            offset=0
            for address,size in part:
                data=raw[offset:offset+size];offset+=size
                values[address,size]=data;self.bytes+=size
        received=time.time_ns()
        with (self.folder/'panel-reads.jsonl').open('a',encoding='utf-8') as f:
            for (address,size),data in values.items():
                f.write(json.dumps(dict(sequence=self.sequence,address=hex(address),size=size,
                                       data=data.hex(),received_ns=received))+'\n')
        return values

    def discover_read(self,address,size):
        if not 1<=size<=1024 or self.bytes+size>32768:raise ValueError('panel_discovery_bound')
        value=self.read_ranges([(address,size)])[address,size]
        self.discovered[address,size]=value
        return value

    def prepare(self):
        from bv_live import PACKAGE
        clock=self.device.clock_sample()
        if clock['device_ns']<2*86400*1_000_000_000:raise ValueError('price_clock_epoch_unsupported')
        self.boot=clock['boot_id']
        raw=self.adb(['sh','-c',f'p=$(pidof {PACKAGE}); test -n "$p" && cat /proc/$p/stat /proc/$p/maps'])
        lines=raw.decode().splitlines();self.process=self.epoch(lines[0].encode());self.pid=self.process[0]
        libraries=[]
        for line in lines[1:]:
            columns=line.split(maxsplit=5)
            lo,hi=(int(v,16) for v in columns[0].split('-'))
            self.maps.append((lo,hi,columns[1]))
            if len(columns)==6 and columns[5].endswith('/libil2cpp.so'):
                libraries.append((lo,hi,int(columns[2],16)))
        candidates=[lo for lo,_,offset in libraries if offset==0 and all(
            any(a<=lo+(va&~4095)<b and off+lo+(va&~4095)-a==(fileoff&~4095)
                for a,b,off in libraries) for va,fileoff in LOADS)]
        if len(candidates)!=1:raise ValueError('panel_binary_mapping_ambiguous')
        self.base=candidates[0]
        if self.discover_read(self.base+BUILD_ID_ADDRESS,len(BUILD_ID))!=BUILD_ID:
            raise ValueError('panel_binary_build_changed')
        self.metadata_names={'classes':{},'methods':{}}
        result=decode_panel_price(self.discover_read,self.base,metadata_names=self.metadata_names)
        self.components=result['component_slots']
        # Rebuild the address plan using only the two relevant dictionary entries.
        requested=[];read=saved_reader(self.discovered)
        def planned(address,size):
            requested.append((address,size));return read(address,size)
        decode_panel_price(planned,self.base,self.components,self.metadata_names)
        requested.append((self.base+BUILD_ID_ADDRESS,len(BUILD_ID)))
        self.plan=merge_ranges(requested)
        self.discovered.clear()  # No observation values are a live cache.
        self.check_epoch()

    def snapshot(self,config_version,instance):
        if self.plan is None:self.prepare()
        start=time.monotonic();self.deadline=start+2;self.sequence+=1
        self.check_epoch()
        observations=[]
        for _ in range(2):
            values=self.read_ranges(self.plan);read=saved_reader(values)
            if read(self.base+BUILD_ID_ADDRESS,len(BUILD_ID))!=BUILD_ID:
                raise ValueError('panel_binary_build_changed')
            observations.append(decode_panel_price(read,self.base,self.components,self.metadata_names))
        self.check_epoch()
        end=time.monotonic()
        if observations[0]!=observations[1]:raise ValueError('panel_observation_changed')
        if end-start>2:raise ValueError('panel_snapshot_too_slow')
        result=observations[-1];fields=result['fields']
        # A content revision binds the entire freshly observed state, including
        # effect inputs, selected data and collection identity; bools alone don't.
        revision=int.from_bytes(hashlib.sha256(json.dumps(result,sort_keys=True).encode()).digest()[:8],'big')
        path=self.folder/f'panel-{self.sequence}.json'
        snapshot=dict(instance=instance,epoch=f'{self.boot}:{self.pid}:{self.process[1]}',panel_id=fields['panel_id'],
                      revision=revision,config_version=config_version,mode='ordinary',cards=fields['cards'],
                      bet_symbol=fields['bet_symbol'],tickets=result['tickets'],price_effects=[],
                      available_bets=[v['id'] for v in result['available_bets']],active=True,
                      observed_mono=end,source_ref=str(path))
        path.write_text(json.dumps(dict(snapshot=snapshot,observation=result,
                        read_seconds=end-start,read_started_mono=start,read_ended_mono=end,
                        matching_observations=2),indent=2),encoding='utf-8')
        return snapshot
