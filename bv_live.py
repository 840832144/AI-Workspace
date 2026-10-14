"""TASK-0039 local runtime bindings and controlled diagnostic entry.

Only normal ADB UI inputs. No protocol writes, hooks or collector lifecycle changes.
Raw paths and account identities stay in the controlled directory.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from bv_evidence import RawTail, VERSION, fields, expected_cells, round_id
from bv_ws2 import parse_frame
from bv_client_state import ClientTrace, terminal_cells

SOURCE = Path(r"D:\BingoVoyageProbe\out")
CONTROL = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "AI-Workspace/bingo-voyage-task0039/runtime"
PACKAGE = "com.bingo.cruise.free.best.top.game"
INSTANCE = 'mumu-authorized'
METRIC = "automatic-set-intersection-replan-v1"
RESOURCE_AUTHORIZATION = 'execution-budget-relaxed-20261014'
RESOURCE_POLICIES = {'execution-16t-20261014':
    {"diagnostic_rounds": 3, "acceptance_rounds": 18, "cards": 4,
     "tickets_per_round": 16, "gross_tickets": 96, "round_seconds": 300, "total_seconds": 5400}}
# User relaxed remaining time on 2026-10-14. Use a conservative +600 second
# implementation ceiling for this continuation, preserving every old policy and
# ledger record. No ticket, position, diagnostic or per-round expansion.
RESOURCE_POLICIES['execution-time-relaxed-20261014'] = dict(
    RESOURCE_POLICIES['execution-16t-20261014'], total_seconds=6000)
# Later User ticket relaxation: 52 historical + 10 current 12-ticket rounds.
# User replenishes the wallet; this code never purchases currency.
RESOURCE_POLICIES[RESOURCE_AUTHORIZATION] = dict(
    RESOURCE_POLICIES['execution-time-relaxed-20261014'], gross_tickets=172)
LIMITS = RESOURCE_POLICIES[RESOURCE_AUTHORIZATION]
BATCH_ROUNDS = 10
BATCH_CLEANUP_SECONDS = 30


def frozen_ticket_limit(metadata):
    """New permission is prospective; old captures retain their old 8-ticket cap."""
    version=metadata.get('resource_authorization')
    if version is None:return 8  # Historical TASK-0039 authorization, never current runtime.
    policy=RESOURCE_POLICIES.get(version)
    if policy is None or metadata.get('limits')!=policy:raise ValueError('resource_authorization_mismatch')
    return policy['tickets_per_round']


class PanelQuote(dict):
    """In-memory binding to a live observer, never a serialized verification tag.

    The scoped production observer supports the studied build's ordinary panel
    with inactive price effects. Unsupported or changed state fails closed.
    """
    identity_fields=('instance','epoch','panel_id','revision','config_version','mode','cards',
                     'bet_symbol','tickets','price_effects','available_bets')

    def __init__(self,read_snapshot,config,instance,config_version):
        import copy
        self._read_snapshot=read_snapshot;self._config=copy.deepcopy(config)
        self._instance=instance;self._config_version=config_version
        s=self._snapshot();self._identity={k:copy.deepcopy(s[k]) for k in self.identity_fields}
        self._issued_mono=time.monotonic()
        super().__init__(tickets=s['tickets'],cards=s['cards'],bet_symbol=s['bet_symbol'],
                         source_ref=s['source_ref'],sampled_at=self._issued_mono,
                         panel_id=s['panel_id'],revision=s['revision'],config_version=config_version)

    def _snapshot(self):
        s=self._read_snapshot()
        if (s.get('active') is not True or s.get('instance')!=self._instance or not s.get('epoch')
                or not s.get('panel_id') or type(s.get('revision')) is not int
                or s.get('config_version')!=self._config_version or not s.get('source_ref')
                or type(s.get('observed_mono')) not in (int,float)
                or not 0<=time.monotonic()-s.get('observed_mono',float('-inf'))<=2):
            raise ValueError('panel_snapshot_not_current')
        choices=s.get('available_bets',[])
        costs={c['id']:c['cost'] for c in self._config if c['id'] in choices
               and re.fullmatch(r'BET_NP_SYMBOL_[0-9]+',c['id'])}
        if (s.get('mode')!='ordinary' or s.get('price_effects')!=[] or not costs or len(costs)!=len(choices)
                or type(s.get('cards')) is not int or s['cards']!=4
                or s.get('bet_symbol') not in costs or costs[s['bet_symbol']]!=min(costs.values())
                or type(s.get('tickets')) is not int or s['tickets']!=costs[s['bet_symbol']]*s['cards']
                or not 0<s['tickets']<=LIMITS['tickets_per_round']):
            raise ValueError('current_panel_configuration_or_price_invalid')
        return s

    def recheck(self):
        s=self._snapshot()
        if (any(s[k]!=v for k,v in self._identity.items())
                or any(self.get(k)!=self._identity[k] for k in ('cards','tickets','bet_symbol','panel_id','revision','config_version'))
                or self.get('sampled_at')!=self._issued_mono
                or time.monotonic()<self._issued_mono):
            raise ValueError('panel_quote_changed_or_expired')
        # _snapshot just obtained a fresh bounded observation of the identical
        # state. Renew its timestamp/evidence, never the lifetime of cached data.
        # Otherwise two real ~1.2s reads expired a quote while revalidating it.
        self._issued_mono=time.monotonic()
        self['sampled_at']=self._issued_mono;self['source_ref']=s['source_ref']


def validate_quote(quote):
    if not isinstance(quote,PanelQuote):raise ValueError('current_panel_quote_unavailable')
    quote.recheck()


def nodes(body, path):
    current = [body]
    for key in path:
        current = [c for b in current for k,w,v,c in fields(b) if k == key and w == 2]
    return current


def scalar(body, key, wire=0):
    values = [v if wire == 0 else c for k,w,v,c in fields(body) if k == key and w == wire]
    if len(values) != 1:
        raise ValueError("missing_or_ambiguous_field")
    return values[0]


def body_for(event):
    source = event["source_ref"]
    with Path(source["index"]).open("rb") as f:
        f.seek(source["offset"])
        rec = json.loads(f.readline())
    raw = Path(source["body"]).read_bytes()
    from bv_evidence import decode
    rebuilt = decode(raw, rec, source)
    if rebuilt["source_file"] != event["source_file"]:
        raise ValueError("source_changed")
    return parse_frame(raw)["body"]


def bind(event):
    """Narrow field paths; no recursive card-signature ownership guesses."""
    cmd, direction = event["cmd"], event["direction"]
    allowed={45:301,163:100003,166:100006,167:100007,168:424,174:100014,202:100042,71:327,190:702}
    if event.get("message_id")!=allowed.get(cmd):return event
    if cmd not in (45,163,166,167,168,174,202,71,190):
        return event
    b = body_for(event)
    e = dict(event)
    if cmd == 45 and direction == "S->C":
        account = scalar(scalar(b,1,2),1,2)
        currencies = {}
        for node in nodes(b,[1,3,1,1]):
            name = scalar(node,1,2).decode("ascii")
            currencies[name] = scalar(node,2)
        e.update(type="wallet_snapshot", account=account.decode(), currencies=currencies)
    elif cmd == 163 and direction == "S->C":
        # The personal submessage is distinct from room/other-player seats (1.1.7).
        own = nodes(b,[1,4,1])
        if len(own) == 1:
            # PersonalRound.RoundID is field 10, not the room snapshot's field 1.
            rid = scalar(own[0],10,2).decode()
            if not rid.startswith("BINGO_HALL"):raise ValueError("invalid_personal_round_id")
            cards = []
            for i, card in enumerate(nodes(own[0],[2]),1):
                vals = [scalar(cell,1) for cell in nodes(card,[2])]
                cards.append({"slot":i, "seed":scalar(card,1), "vals":vals})
            expected_cells(cards, [])
            selection = nodes(own[0],[11])
            if rid and len(selection) == 1:
                e.update(type="personal_cards", round_id=rid, cards=cards,
                         bet_symbol=scalar(selection[0],1,2).decode(), card_count=scalar(selection[0],2))
    elif cmd == 174 and direction == "S->C":
        rid = round_id(b)
        if rid:
            e.update(type="close_candidate", round_id=rid)
    elif cmd == 202 and direction == "C->S":
        selected = nodes(b,[2])
        if len(selected) == 1:
            e.update(type="buy_request", bet_symbol=scalar(selected[0],1,2).decode(),
                     card_count=scalar(selected[0],2))
    elif cmd in (168,71,190) and direction == "S->C":
        rewards = []
        for n in nodes(b,[4,2] if cmd == 71 else [1,2]):
            rewards.append({"currency":scalar(n,1,2).decode(),"delta":scalar(n,2),"balance":scalar(n,3)})
        if rewards:
            e.update(type="resource_credit", rewards=rewards)
    return e


def scan_range(index, bodies, start, end):
    tail = RawTail(index, bodies, start=start, end=end)
    events=[]
    while tail.pos < end:
        before=tail.pos
        for e in tail.poll(now=0):
            try: events.append(bind(e))
            except (ValueError, UnicodeError, KeyError) as exc:
                tail.errors["binding_"+str(exc)] += 1
        if tail.pos == before:
            tail.errors["incomplete_index_range"] += 1
            break
    for e in tail.poll(now=3):
        try: events.append(bind(e))
        except (ValueError, UnicodeError, KeyError) as exc:tail.errors["binding_"+str(exc)] += 1
    return events, dict(tail.errors)


def recent_start(index):
    """Last current-account snapshot, exact complete-line position, no historic guessing."""
    offset=0
    with Path(index).open("rb") as stream:
        while line:=stream.readline():
            if not line.endswith(b"\n"):break
            try:
                r=json.loads(line)
                if r.get("dir")=="S->C" and r.get("hdr",{}).get("cmd")==45 and r.get('hdr',{}).get('flags')==256:
                    offset=stream.tell()-len(line)
            except ValueError:pass
    return offset


def cost_proof(raw,symbol,cost):
    spent=re.findall(rb'PrepayCard resId TICKET baseCost (\d+) cardCount (\d+) amount (\d+) betID ([A-Z_0-9]+)',raw)
    if any(int(a)*int(b)==int(c)==cost and b==b'4' and sym.decode()==symbol for a,b,c,sym in spent):return 'current_client_log'
    # App restarts rotate native logs. Reuse bounded, independently replayed cost
    # evidence for this exact ordinary symbol/cost, never a historical balance.
    from bv_verify import replay,read_json
    for p in CONTROL.glob('diagnostic_*/frozen.json'):
        try:
            f=read_json(p);old=read_json(p.parent/f['selection_ref']);config=read_json(p.parent/f['config_ref'])
            if 'BET_NP_SYMBOL_%d'%old['BetCount']!=symbol:continue
            if not any(c['id']==symbol and c['cost']*4==cost for c in config):continue
            audit=replay(p)
            if not audit['errors'] and audit['gross_tickets']==cost:return str(p)
        except (OSError,KeyError,ValueError,TypeError):continue
    raise ValueError('cost_semantics_not_crosschecked')


class Device:
    base = "/sdcard/Android/data/"+PACKAGE+"/files/"

    def __init__(self):
        self.clock_samples=[]
        path=CONTROL/'clock-ready.json'
        if path.exists():
            samples=json.loads(path.read_text(encoding='utf-8'))
            if samples and 0<=time.monotonic_ns()-samples[-1]['mono_after_ns']<=30_000_000_000:
                self.clock_samples=samples[-2:]

    def clock_sample(self):
        from bv_autoplay import ADB,DEV
        from bv_clock import validate
        a=time.time_ns();ma=time.monotonic_ns()
        r=subprocess.run([ADB,'-s',DEV,'exec-out','sh','-c',
                          'date +%s%N; cat /proc/sys/kernel/random/boot_id; cat /proc/uptime'],
                         capture_output=True,timeout=3,check=True)
        b=time.time_ns();mb=time.monotonic_ns();lines=r.stdout.decode().splitlines()
        s=dict(host_before_ns=a,host_after_ns=b,mono_before_ns=ma,mono_after_ns=mb,
               device_ns=int(lines[0]),boot_id=lines[1],uptime_seconds=float(lines[2].split()[0]))
        samples=getattr(self,'clock_samples',[])
        validate(s,samples[-1] if samples else None);samples.append(s);self.clock_samples=samples
        CONTROL.mkdir(parents=True,exist_ok=True)
        (CONTROL/'clock-ready.json').write_text(json.dumps(samples[-2:]),encoding='utf-8')
        return s

    def read_client(self,path,offset):
        from bv_autoplay import ADB,DEV
        if not getattr(self,'clock_samples',[]) or time.monotonic_ns()-self.clock_samples[-1]['mono_after_ns']>10_000_000_000:
            self.clock_sample()
        r=subprocess.run([ADB,'-s',DEV,'exec-out','stat','-c','%i:%s',path],capture_output=True,timeout=3,check=True)
        inode,size=map(int,r.stdout.strip().split(b':'))
        identity=(path,inode)
        if getattr(self,'log_identity',identity)!=identity or size<offset:raise ValueError('client_log_rotated')
        self.log_identity=identity
        return self.read_file(path,offset)

    def stopped(self):
        return (time.monotonic()>=getattr(self,'round_deadline',float('inf'))
                or any(Path(p).exists() for p in getattr(self,'stop_paths',())))

    def send(self,button):
        from bv_autoplay import spawn_tap,finish_tap
        # All possibly slow foreground/quote/sample reads precede this last check.
        if self.stopped():return 'not_executed'
        return finish_tap(spawn_tap(*button))

    def read_file(self,path,offset=0):
        from bv_autoplay import ADB,DEV
        if not path.startswith(self.base):raise ValueError("outside_game_data")
        args=["tail","-c","+%d"%(offset+1),path] if offset else ["cat",path]
        r=subprocess.run([ADB,"-s",DEV,"exec-out",*args],capture_output=True,timeout=5)
        if r.returncode:raise ValueError("game_read_failed")
        return r.stdout

    def context(self,account,folder):
        self.clock_sample()
        if not re.fullmatch(r"[A-Za-z0-9]+",account):raise ValueError("invalid_account_path")
        version=self.read_file(self.base+"gds/gds_version.txt").decode().strip()
        if not re.fullmatch(r"[a-f0-9]{32}",version):raise ValueError("unknown_game_config_version")
        config=self.read_file(self.base+"gds/"+version+"/BaseBetConfig.json")
        (folder/"base_bet_config.json").write_bytes(config)
        from bv_autoplay import ADB,DEV
        r=subprocess.run([ADB,"-s",DEV,"exec-out","ls",self.base+"client_logging_temp"],capture_output=True,timeout=5,check=True)
        names=[n for n in r.stdout.decode().splitlines() if re.fullmatch(r"[0-9_-]+\.txt",n)]
        if len(names)!=1:raise ValueError("client_log_identity_ambiguous")
        logpath=self.base+"client_logging_temp/"+names[0]
        raw=self.read_file(logpath)
        (folder/"client-before.log").write_bytes(raw)
        changes=[e for e in ClientTrace(folder/"client-before.log").feed(raw) if e["type"]=="ticket_change"]
        if any(e["before"]+e["delta"]!=e["after"] for e in changes):raise ValueError("ticket_delta_contradiction")
        reader=self.panel_reader(folder/('panel_'+uuid.uuid4().hex))
        def snapshot():
            if self.read_file(self.base+"gds/gds_version.txt").decode().strip()!=version:
                raise ValueError('panel_config_version_changed')
            return reader.snapshot(version,INSTANCE)
        quote=PanelQuote(snapshot,json.loads(config),INSTANCE,version)
        quote.update(gds_version=version,price_scope='current_panel',
                     config_ref=str(folder/'base_bet_config.json'),
                     log_path=logpath,log_start=len(raw),
                     last_ticket_change=max(changes,key=lambda e:e['at_ns']) if changes else None)
        # Frozen replay consumes this selection. It comes from the real current
        # panel binding, never the old persisted buy_card_data.json.
        (folder/'selection.json').write_text(json.dumps(dict(
            CardCount=quote['cards'],BetCount=int(quote['bet_symbol'].rsplit('_',1)[1]),
            LastBetTicket=quote['tickets'],panel_identity=quote._identity,
            panel_source=quote['source_ref'])),encoding='utf-8')
        return quote

    def panel_reader(self,folder):
        from bv_panel_observer import ScopedPanelReader
        # Preparation must leave the full ten-round envelope and cleanup intact.
        remaining=LIMITS['total_seconds']-Budget().elapsed()
        reserve=0 if hasattr(self,'round_deadline') else BATCH_ROUNDS*LIMITS['round_seconds']+BATCH_CLEANUP_SECONDS
        if remaining-reserve<40:raise ValueError('panel_preparation_budget_insufficient')
        return ScopedPanelReader(self,folder)

    def prepare_panel(self,path):
        sample=self.sample(path)
        if sample['scene']=='lobby':
            if self.open_panel(sample)=='not_executed':raise ValueError('panel_navigation_cancelled')
            time.sleep(1)

    def foreground(self):
        from bv_autoplay import ADB, DEV
        r=subprocess.run([ADB,"-s",DEV,"shell","dumpsys","activity","activities"],
                         capture_output=True, timeout=5, text=True, encoding="utf-8", errors="replace")
        return r.returncode==0 and any(PACKAGE in line for line in r.stdout.splitlines()
                                      if "topResumedActivity=" in line)

    def sample(self, path):
        from bv_autoplay import shot
        from PIL import Image
        import bv_cardgrid
        from bv_autobuy import find_green, near, BLUE, ORANGE
        sampled_at=time.monotonic()
        ok=self.foreground()
        if not ok or not shot(str(path),tries=1):return {"foreground":False,"scene":"unknown","grid":None}
        with Image.open(path) as source:im=source.convert("RGB")
        if im.size!=(900,1600):return {"foreground":True,"scene":"bad_orientation","grid":None}
        raw_det=bv_cardgrid.detect(im)
        for card in raw_det:
            card['cell_geometry']=bv_cardgrid.cell_geometry(im,card)
        det=self.calibrated_grid(raw_det)
        green=find_green(im)
        panel_anchor=near(im.getpixel((100,700)),BLUE,65)
        if panel_anchor:
            # Event ads below the panel also use green. Calibrate the visible
            # panel's action area only; no ticket/card values are read here.
            local=find_green(im.crop((250,1090,650,1260)),yfrac=0)
            green=(local[0]+250,local[1]+1090,local[2]) if local else None
        panel=panel_anchor and green and 400<green[0]<500 and 1100<green[1]<1230
        congrats=near(im.getpixel((150,450)),ORANGE,70) and green and 350<green[0]<550 and 1200<green[1]<1400
        import numpy as np
        pixels=np.asarray(im)
        def yellow_fraction(box):
            x0,y0,x1,y1=box;a=pixels[y0:y1,x0:x1]
            return ((a[:,:,0]>220)&(a[:,:,1]>150)&(a[:,:,2]<130)).mean()
        caption=pixels[980:1060,260:650]
        reward=(yellow_fraction((160,400,800,580))>.12 and
                yellow_fraction((350,610,560,810))>.2 and (caption.min(axis=2)>235).mean()>.05)
        banner=pixels[365:435,300:600];continue_caption=pixels[790:840,280:640]
        level_up=(yellow_fraction((330,80,580,350))>.4 and
                  ((banner[:,:,0]>200)&(banner[:,:,1]<100)&(banner[:,:,2]<100)).mean()>.4 and
                  (continue_caption.min(axis=2)>235).mean()>.05)
        reward=reward or level_up
        rating=(near(im.getpixel((100,600)),BLUE,65) and
                im.getpixel((800,510))[0]>180 and im.getpixel((800,510))[1]<100 and
                min(im.getpixel((812,536)))>220)
        scene="round" if raw_det else "reward" if reward or rating else "betpanel" if panel else "congrats" if congrats else "lobby" if green and 120<green[0]<400 and green[1]>1200 else "unknown"
        if scene=='reward':green=(450,820 if level_up else 1025,0)  # Observed non-consuming dismiss area.
        if rating:green=(812,533,0)  # Close the rating prompt; never select stars.
        return {"foreground":ok,"scene":scene,"grid":det,"button":list(green[:2]) if green else None,
                "sampled_at":sampled_at}

    def calibrated_grid(self,det):
        """Pause and reacquire each card from current cell shapes, not old paint.

        Missing records carry identity only, explicitly unobserved/unusable.
        No cached coordinates may authorize a click. New geometry requires three
        stable independent measurements; a single-card change cannot halt peers.
        """
        import copy
        if not det or len(det)>4:
            self.grid_reference=None;self.grid_tracks={}
            return []
        reference=getattr(self,'grid_reference',None)
        if reference is None:
            if len(det)!=4:return []
            reference=copy.deepcopy(det);self.grid_reference=reference;self.grid_tracks={}
        matches={}
        for current in det:
            # Header is an identity/region anchor only. Coordinates come from
            # independently observed cell shapes, including after an 8px move.
            distances=[max(abs(sum(current['cols'])/5-sum(r['cols'])/5),
                           abs(current['header_bottom']-r['header_bottom'])) for r in reference]
            index=min(range(4),key=lambda i:distances[i])
            if distances[index]>reference[index]['spacing']*.5 or index in matches:
                self.grid_reference=None;self.grid_tracks={};return []
            matches[index]=current
        tracks=getattr(self,'grid_tracks',{});result=[]
        for index,r in enumerate(reference):
            current=matches.get(index);body=current.get('cell_geometry') if current else None
            c=copy.deepcopy(r);c.update(input_ready=False,observed=current is not None,
                                      pause_reason='cell_shapes_unavailable' if current else 'header_missing')
            if body:
                old=tracks.get(index,{});previous=old.get('body')
                stable=previous is not None and max(abs(body[a][k]-previous[a][k])
                           for a in ('cols','rows') for k in range(5))<=2
                count=old.get('count',0)+1 if stable else 1
                tracks[index]=dict(body=copy.deepcopy(body),count=count)
                if count>=3:
                    c=copy.deepcopy(current);c.update(body,input_ready=True,observed=True,
                                 row_mode='current_cell_shapes',pause_reason=None)
                    reference[index]=copy.deepcopy(c)
                else:c['pause_reason']='geometry_stabilizing'
            else:tracks.pop(index,None)
            result.append(c)
        self.grid_tracks=tracks
        return result

    def claim(self,sample):
        from bv_autoplay import spawn_tap,finish_tap
        if sample['scene']!='congrats' or time.monotonic()-sample['sampled_at']>2.5 or not self.foreground():return 'not_executed'
        return self.send(sample['button'])

    def dismiss_reward(self,sample):
        if sample['scene']!='reward' or time.monotonic()-sample['sampled_at']>2.5 or not self.foreground():return 'not_executed'
        return self.send(sample['button'])

    def open_panel(self, sample):
        from bv_autoplay import spawn_tap, finish_tap
        if sample["scene"]!="lobby" or time.monotonic()-sample["sampled_at"]>2.5 or not self.foreground():
            return "not_executed"
        return self.send(sample['button'])

    def buy(self,sample,quote):
        from bv_autoplay import spawn_tap,finish_tap
        if (sample["scene"]!="betpanel" or time.monotonic()-sample["sampled_at"]>2.5
                or not self.foreground()):
            return "not_executed"
        try:validate_quote(quote)
        except (ValueError,KeyError,TypeError):return 'not_executed'
        if time.monotonic()-sample['sampled_at']>2.5:return 'not_executed'
        return self.send(sample['button'])


def ticket_balance(wallet,change,clocks=None):
    from bv_verify import timestamp
    when=timestamp(wallet)
    if clocks and change:
        if change['after']==wallet['currencies']['TICKET']:return change['after']
        from bv_clock import interval
        try:lo,hi=interval(change['at_ns'],clocks)
        except ValueError:
            if when>=clocks[0]['host_after_ns'] and change['at_ns']<clocks[0]['device_ns']:
                return wallet['currencies']['TICKET']  # Fresh server snapshot after this log prefix.
            raise ValueError('resource_clock_not_covered')
        if lo>when+1_000_000_000:return change['after']
        if hi<when:return wallet['currencies']['TICKET']
        if change['after']==wallet['currencies']['TICKET']:return change['after']
        raise ValueError('resource_order_ambiguous')
    return change['after'] if change and change['at_ns']>when else wallet['currencies']['TICKET']


def preflight(source=SOURCE, device=None,remaining_rounds=BATCH_ROUNDS):
    source=Path(source);index=source/"bv_ws.jsonl"
    errors=[];events=[];quality={}
    device=device or Device()
    try:
        start=recent_start(index)
        events,quality=scan_range(index,source/"bv_bodies",start,index.stat().st_size)
        if time.time()-index.stat().st_mtime>20:errors.append("capture_not_fresh")
    except (OSError,ValueError) as exc:errors.append("capture_unavailable_"+type(exc).__name__)
    try:fg=device.foreground()
    except (OSError,subprocess.TimeoutExpired):fg=False
    if not fg:errors.append("game_not_foreground")
    wallets=[e for e in events if e["type"]=="wallet_snapshot"]
    if not wallets or "TICKET" not in wallets[-1]["currencies"]:errors.append("structured_wallet_unavailable")
    quote=None
    if wallets:
        try:
            folder=CONTROL/("check_"+uuid.uuid4().hex);folder.mkdir(parents=True)
            quote=device.context(wallets[-1]["account"],folder)
            quote["balance"]=ticket_balance(wallets[-1],quote.get('last_ticket_change'),getattr(device,'clock_samples',None))
        except (OSError,ValueError,KeyError,subprocess.TimeoutExpired) as exc:
            errors.append("quote_"+str(exc))
    buy_errors=list(errors)
    plan=None
    if quote is None:buy_errors.append("current_ticket_quote_unverified")
    else:
        try:
            validate_quote(quote)
            plan=Budget(CONTROL).batch_plan(quote,remaining_rounds)
            if not plan['fits']:buy_errors.append('batch_budget_insufficient')
        except (ValueError,KeyError,TypeError) as exc:buy_errors.append(str(exc))
    if quality:buy_errors.append("capture_quality_errors")
    from bv_verify import semantic_gate
    gate=semantic_gate()
    clock_ready=bool(getattr(device,'clock_samples',[]))
    if isinstance(device,Device) and not clock_ready:buy_errors.append('clock_not_ready')
    ready=not buy_errors and clean_code()
    result={"status":"Ready" if ready else "Ready for diagnostic navigation" if not errors else "Blocked",
            "diagnostic_navigation_ready":fg and bool(wallets), "live_ready":ready, "purchase_ready":not buy_errors,
            "run_ready":ready,"metric_ready":gate['qualified'],"clock_ready":clock_ready,"semantic_gate":gate,
            "blockers":buy_errors, "capture_errors":quality,"limits":LIMITS,"budget_plan":plan,
            "wallet_source_available":bool(wallets), "quote_source_available":quote is not None,
            "quote":quote}
    return result,events


class Budget:
    """Persistent shared task ledger; credits never offset gross spend/reservation."""
    def __init__(self,root=CONTROL):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
        self.path=self.root/"budget.jsonl"

    def records(self):
        if not self.path.exists():return []
        return [json.loads(l) for l in self.path.read_text(encoding="utf-8").splitlines()]

    def append(self,kind,**kw):
        with self.path.open("a",encoding="utf-8") as f:
            f.write(json.dumps(dict(kind=kind,at_ns=time.time_ns(),**kw))+"\n");f.flush();os.fsync(f.fileno())

    def elapsed(self):
        records=self.records();ends={r['session_id']:r for r in records if r['kind']=='runtime_end'}
        # An interrupted process cannot reset its clock by omitting runtime_end.
        return sum(ends[r['session_id']]['seconds'] if r['session_id'] in ends else
                   max(0,(time.time_ns()-r['at_ns'])/1e9) for r in records if r['kind']=='runtime_start')

    def gross(self):
        records=self.records()
        actual={r['session_id']:r['tickets'] for r in records if r['kind']=='resource_observed'}
        return sum(max(r['reserved_tickets'],actual.get(r['session_id'],0)) for r in records if r['kind']=='purchase_reserved')

    def batch_plan(self,quote,rounds=BATCH_ROUNDS):
        validate_quote(quote)
        if type(rounds) is not int or not 1<=rounds<=BATCH_ROUNDS:raise ValueError('invalid_remaining_batch_rounds')
        required_tickets=quote['tickets']*rounds
        required_seconds=LIMITS['round_seconds']*rounds+BATCH_CLEANUP_SECONDS
        available_tickets=LIMITS['gross_tickets']-self.gross()
        available_seconds=LIMITS['total_seconds']-self.elapsed()
        deficits=dict(positions=max(0,rounds-self.remaining_positions()),
                      tickets=max(0,required_tickets-available_tickets),
                      wallet=max(0,quote['tickets']-quote.get('balance',-1)),
                      seconds=max(0,required_seconds-available_seconds))
        return dict(rounds=rounds,per_round_tickets=quote['tickets'],required_tickets=required_tickets,
                    available_tickets=available_tickets,required_seconds=required_seconds,
                    available_seconds=available_seconds,cleanup_seconds=BATCH_CLEANUP_SECONDS,
                    future_wallet_gap=max(0,required_tickets-quote.get('balance',-1)),
                    wallet_policy='each_purchase_user_replenishes_no_auto_topup',
                    deficits=deficits,fits=not any(deficits.values()))

    def reserve(self,purpose,quote,session,batch_id=None,remaining_rounds=None):
        records=self.records()
        purchases=[r for r in records if r["kind"]=="purchase_reserved"]
        if quote is None or quote.get("source_ref") is None or type(quote.get("tickets")) is not int:
            raise ValueError("verified_quote_required")
        validate_quote(quote)
        elapsed=self.elapsed()  # A real quote refresh is not instantaneous.
        cost=quote["tickets"]
        if not 0<cost<=LIMITS['tickets_per_round'] or quote.get("cards")!=LIMITS['cards'] or quote.get("balance",-1)<cost:
            raise ValueError("per_round_resource_limit")
        limit=LIMITS.get(purpose+'_rounds',0)
        if sum(r["purpose"]==purpose for r in purchases)>=limit:raise ValueError("round_count_limit")
        if self.gross()+cost>LIMITS['gross_tickets'] or elapsed>=LIMITS['total_seconds']:
            raise ValueError("task_resource_limit")
        if purpose=='acceptance' and elapsed+LIMITS['round_seconds']>LIMITS['total_seconds']:
            raise ValueError('insufficient_remaining_time_for_full_round')
        if remaining_rounds is not None and not self.batch_plan(quote,remaining_rounds)['fits']:
            raise ValueError('batch_budget_insufficient')
        self.append("purchase_reserved",purpose=purpose,session_id=session,reserved_tickets=cost,
                    quote_source=quote["source_ref"],quote_identity=quote._identity,batch_id=batch_id,
                    resource_authorization=RESOURCE_AUTHORIZATION,limits=dict(LIMITS))

    def remaining_positions(self):
        return max(0, LIMITS['acceptance_rounds']-sum(
            r['kind']=='purchase_reserved' and r['purpose']=='acceptance' for r in self.records()))


def code_version():
    r=subprocess.run(["git","rev-parse","HEAD"],cwd=Path(__file__).parent,capture_output=True,text=True,check=True)
    return r.stdout.strip()


def clean_code():
    result=subprocess.run(['git','status','--porcelain','--untracked-files=normal'],cwd=Path(__file__).parent,
                          capture_output=True,text=True,check=True)
    return not result.stdout.strip()


def validate_spend(quote_tickets,gross):
    if type(gross) is not int or not 0<gross<=LIMITS['tickets_per_round']:
        raise ValueError('actual_spend_outside_round_limit')
    if gross!=quote_tickets:raise ValueError('actual_spend_mismatch')


def diagnose(seconds=20,open_panel=False,source=SOURCE,root=CONTROL,device=None,play_round=False,
             batch=None,session=None,lock_held=False,prepared=None):
    """Actual bounded source/UI loop. Diagnostic evidence can never pass acceptance."""
    import msvcrt
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    lock=None
    try:
        if not lock_held:
            lock=(root/'controller.lock').open('a+b')
            lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
            msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:
        if lock:lock.close()
        return {"status":"Blocked","errors":["controller_already_running"],"acceptance_pass":False}
    purpose='acceptance' if batch else 'diagnostic'
    session=Path(session) if session else root/(purpose+"_"+uuid.uuid4().hex)
    session.mkdir(exist_ok=bool(batch))
    ledger=Budget(root);t0=time.monotonic();device=device or Device()
    device.round_deadline=min(t0+min(seconds,LIMITS['round_seconds']),getattr(device,'round_deadline',float('inf'))) if batch else t0+min(seconds,LIMITS['round_seconds'])
    # Reference geometry belongs to this one round, never a previous purchase.
    device.grid_reference=None;device.grid_candidate=None;device.grid_count=0
    stop_paths=(session/'STOP',Path(batch['folder'])/'STOP') if batch else (session/'STOP',)
    device.stop_paths=stop_paths
    stopped=lambda:any(p.exists() for p in stop_paths)
    source=Path(source);index=source/"bv_ws.jsonl"
    result={"status":"Insufficient evidence","purpose":purpose,"acceptance_pass":False,
            "session_id":session.name,"session_path":str(session),"rounds_started":0,"gross_tickets":0}
    pool=ThreadPoolExecutor(max_workers=1);future=None
    events=[];samples=[];opened=False;controller=None;paid=False;closed_at=None;client_offset=None
    client_chunks=[];client_future=None;client_pool=ThreadPoolExecutor(max_workers=1)
    quote=None;buy_at=None;round_id_bound=None;trace=None;native_events=[];history=[];tail=None;start=None
    registration={};processed_calls=set();processed_marks=set();progress_at=0;prepurchase_dismissals=0
    ledger.append('runtime_start',session_id=session.name)
    try:
        if play_round and not clean_code():raise ValueError('candidate_not_frozen')
        check,history=prepared if prepared is not None else preflight(source,device,
            remaining_rounds=batch['planned_rounds']-batch['ordinal']+1 if batch else 1)
        if batch and not check.get('run_ready',check.get('purchase_ready')):raise ValueError('run_not_ready:'+','.join(check['blockers']))
        start=index.stat().st_size
        registration={"purpose":purpose,"registered_ns":time.time_ns(),"code_version":code_version(),
                      "parser_version":VERSION,"metric_version":METRIC,"source_start":start,
                      "instance":INSTANCE,"limits":dict(LIMITS),"resource_authorization":RESOURCE_AUTHORIZATION,"session_id":session.name,
                      "mode":"full_autoplay" if batch else "single_target_diagnostic",
                      "target_dispatch_limit":288 if batch else 1,"user_should_intervene":False}
        if batch:
            registration.update({k:batch[k] for k in ('batch_id','code_version','parser_version','metric_version','instance')})
            with (Path(batch['folder'])/'starts.jsonl').open('a',encoding='utf-8') as f:
                row=dict(registration,ordinal=batch['ordinal'],started_ns=time.time_ns(),frozen_ref=str(session.relative_to(Path(batch['folder']))/'frozen.json'))
                f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
            ledger.append('batch_round_start',**row)
        (session/"registration.json").write_text(json.dumps(registration),encoding="utf-8")
        tail=RawTail(index,source/"bv_bodies",start=start)
        if play_round:
            from bv_autoplay import AutoPlay
            from types import SimpleNamespace
            controller=AutoPlay(SimpleNamespace(map=None,settle=1.8,retries=2,ack_wait=1.5,dry=False,
                         max_dispatches=288 if batch else 1,round_deadline=device.round_deadline,
                         batch_stop_path=str(stop_paths[1]) if batch else None,
                         diagnostic_slot=None if batch else 2,
                         session_path=str(session),capture_index=str(index),bodies=source/"bv_bodies"))
        while time.monotonic()<device.round_deadline and ledger.elapsed()<LIMITS['total_seconds'] and not (session/"STOP").exists() and not (batch and (Path(batch['folder'])/'STOP').exists()):
            newly=[]
            for event in tail.poll():
                try:
                    e=bind(event);events.append(e);newly.append(e)
                except (ValueError,KeyError,UnicodeError) as exc:tail.errors["binding_"+str(exc)]+=1
            if paid and controller:
                if tail.errors:controller.revoke('capture_quality_error',halt=True)
                for e in newly:
                    if e["type"]=="personal_cards":
                        if round_id_bound and e["round_id"]!=round_id_bound:
                            controller.revoke("unexpected_round_switch",halt=True)
                        elif not round_id_bound:
                            round_id_bound=e["round_id"];controller.rid=round_id_bound;controller.cards=e["cards"]
                            (session/"card-source.json").write_text(json.dumps(e),encoding="utf-8")
                    # cmd100009 carries a look-ahead queue, up to ~20s ahead of BallCaller.
                    # Keep every member as raw evidence, but only ClientTrace permits dispatch.
                    if e["type"]=="close_candidate" and e["round_id"]==round_id_bound:
                        controller.revoke("structured_close_candidate",halt=True)
                        closed_at=closed_at or time.monotonic()
                # Exactly one dispatched ordinary target per diagnostic. No repetition/auto-powerup input.
                controller.tick([e for e in newly if e["type"]=="cell_observation"])
                if closed_at and time.monotonic()-closed_at>=10:break
                if buy_at and time.monotonic()-buy_at>=LIMITS['round_seconds']:break
            if future is None:
                future=pool.submit(device.sample,session/("navigation_%d.png"%len(samples)))
            elif future.done():
                sample=future.result();samples.append(sample);future=None
                if controller:
                    with controller.state_lock:
                        controller.foreground_ok=sample["foreground"] and sample["scene"]=="round"
                        controller.foreground_at=sample.get("sampled_at",0)
                    if sample["scene"]=="round" and round_id_bound and (batch or controller.n_tap==0):
                        controller.setup_grid(4,sample["grid"])
                        if controller.grid:
                            controller.layout_at=sample['sampled_at'];controller.backfill()
                    elif not paid or sample["scene"]!="round":controller.revoke("not_visible_round")
                if (open_panel and not paid and sample['scene']=='reward' and prepurchase_dismissals<2
                        and any(e['type']=='close_candidate' for e in history)):
                    prepurchase_dismissals+=1
                    outcome=device.dismiss_reward(sample)
                    events.append(dict(type='reward_navigation',outcome=outcome,at_ns=time.time_ns()))
                    time.sleep(1)
                elif open_panel and not paid and not opened and check["diagnostic_navigation_ready"] and sample["scene"]=="lobby":
                    # Only a non-consuming navigation action. No fall-through to PLAY on the panel.
                    opened=True
                    outcome=device.open_panel(sample)
                    events.append({"type":"navigation_input","outcome":outcome,"at_ns":time.time_ns()})
                elif play_round and not paid and sample["scene"]=="betpanel" and check["purchase_ready"]:
                    account=next(e["account"] for e in reversed(history) if e["type"]=="wallet_snapshot")
                    quote=device.context(account,session)
                    wallet=next(e for e in reversed(history) if e['type']=='wallet_snapshot')
                    quote['balance']=ticket_balance(wallet,quote.get('last_ticket_change'),getattr(device,'clock_samples',None))
                    if stopped():break
                    if batch and (code_version()!=batch['code_version'] or not clean_code()):raise ValueError('code_changed_during_batch')
                    ledger.reserve(purpose,quote,session.name,batch['batch_id'] if batch else None,
                                   remaining_rounds=batch['planned_rounds']-batch['ordinal']+1 if batch else None)
                    paid=True;buy_at=time.monotonic();client_offset=quote["log_start"]
                    trace=ClientTrace(str(session/"client-during.log"))
                    result.update(rounds_started=1,reserved_tickets=quote["tickets"],gross_tickets=None)
                    # Reservation includes real quote IO. Calibrate afterward so
                    # that final quote recheck does not use a pre-reservation image.
                    fresh=device.sample(session/"before-buy.png")
                    outcome=device.buy(fresh,quote)
                    events.append({"type":"purchase_input","outcome":outcome,"at_ns":time.time_ns(),"quote":quote})
                    if outcome=="not_executed":raise ValueError("purchase_cancelled_before_dispatch")
            if paid and quote:
                if client_future is None:
                    client_future=client_pool.submit(getattr(device,'read_client',device.read_file),quote["log_path"],client_offset)
                elif client_future.done():
                    chunk=client_future.result();client_future=None;client_offset+=len(chunk);client_chunks.append(chunk)
                    for event in trace.feed(chunk):
                        if getattr(device,'clock_samples',None):
                            from bv_clock import observe
                            event=observe(event,device.clock_samples)
                        native_events.append(event)
                        if event['type']=='client_game_over' and event.get('round_id')==round_id_bound:
                            controller.close_round(round_id_bound,verified=True)
                            closed_at=closed_at or time.monotonic()
                    # Replay only already-observed native calls after personal-card binding.
                    for event in native_events:
                        ref=event['source_ref']['offset']
                        if event['type']=='client_called' and round_id_bound and ref not in processed_calls:
                            if event.get('round_id')!=round_id_bound:
                                from bv_verify import timestamp
                                starts=[e for e in native_events if e['type']=='client_round_start' and e['round_id']==round_id_bound]
                                own=[e for e in events if e['type']=='personal_cards' and e['round_id']==round_id_bound]
                                if not starts or not own or not starts[0]['at_ns']-1_000_000_000<=event['at_ns']<starts[0]['at_ns']:continue
                            processed_calls.add(ref)
                            candidates={n for e in events if e.get("type")=="balls" and e.get("round_id")==round_id_bound for n in e["window"]}
                            if event["ball"] not in candidates:
                                controller.revoke("called_source_mismatch",halt=True)
                            else:controller.on_ball(event["at_ns"],round_id_bound,event["ball"])
                        elif batch and event['type']=='client_marked' and round_id_bound and ref not in processed_marks:
                            if event['round_id']!=round_id_bound:continue
                            processed_marks.add(ref)
                            if not controller.accept_client_mark(event):
                                controller.observe_unmatched(event)
                    deltas=re.findall(rb"NotifyResources TICKET current=(\d+) next=(\d+) delta=(-?\d+)",b"".join(client_chunks))
                    gross=sum(-int(d) for a,b,d in deltas if int(d)<0)
                    if deltas:result["gross_tickets"]=gross
                    if gross:
                        try:validate_spend(quote['tickets'],gross)
                        except ValueError:
                            controller.revoke('actual_spend_mismatch',halt=True)
                            raise
            if controller and batch and time.monotonic()-progress_at>=2:
                progress_at=time.monotonic()
                (session/'progress.json').write_text(json.dumps(dict(mode='full_autoplay',ordinal=batch['ordinal'],
                    dispatched=controller.n_tap,confirmed=len(controller.done),pending=len(controller.pending),
                    awaiting=len(controller.awaiting),unknown=len(controller.giveup),closed=closed_at is not None,
                    halted=controller.halted,stop_path=str(stop_paths[-1]))),encoding='utf-8')
            time.sleep(.05)
        result.update(blockers=check["blockers"], capture_errors=dict(tail.errors),
                      observed_commands=dict(Counter(str(e.get("cmd")) for e in events if "cmd" in e)),
                      scene=samples[-1]["scene"] if samples else "unknown", navigation_sent=opened,
                      source_start=start, source_end=tail.pos,
                      stopped_confirmed=True, stop_requested=stopped())
        if controller:
            result['control_summary']=controller.summary()
            result.update(input_dispatched=controller.n_tap,round_bound=bool(round_id_bound),
                          close_candidate_observed=closed_at is not None)
    except (OSError,ValueError,subprocess.TimeoutExpired) as exc:
        result.update(errors=[type(exc).__name__,str(exc)],stopped_confirmed=True)
    finally:
        if controller:
            controller.revoke("diagnostic_exit",halt=True)
            controller.input_pool.shutdown(wait=True,cancel_futures=True)
            controller.act.close()
        client_pool.shutdown(wait=True,cancel_futures=True)
        if quote:
            try:
                client_chunks.append(device.read_file(quote["log_path"],client_offset))
            except (OSError,ValueError,subprocess.TimeoutExpired):result.setdefault("errors",[]).append("client_log_final_read_failed")
            (session/"client-during.log").write_bytes(b"".join(client_chunks))
            deltas=re.findall(rb'NotifyResources TICKET current=(\d+) next=(\d+) delta=(-?\d+)',b''.join(client_chunks))
            result['gross_tickets']=sum(-int(d) for a,b,d in deltas if int(d)<0) if deltas else None
            if paid:
                try:validate_spend(quote['tickets'],result['gross_tickets'])
                except ValueError as exc:result.setdefault('errors',[]).append(str(exc))
        pool.shutdown(wait=True,cancel_futures=True)
        for name,data in (("history.json",history),("events.json",events),("samples.json",samples),("native-events.json",native_events)):
            (session/name).write_text(json.dumps(data),encoding='utf-8')
        if tail is not None:
            # Expire unresolved bodies into explicit quality failures before freezing.
            for e in tail.poll(now=time.monotonic()+tail.body_wait):
                try:events.append(bind(e))
                except (ValueError,KeyError,UnicodeError) as exc:tail.errors['binding_'+str(exc)]+=1
            result.update(source_start=start,source_end=tail.pos,capture_errors=dict(tail.errors))
            (session/'events.json').write_text(json.dumps(events),encoding='utf-8')
        if paid and tail is not None:
            try:
                from bv_verify import freeze
                if getattr(device,'clock_samples',None):
                    (session/'clock.json').write_text(json.dumps(dict(samples=device.clock_samples,log_identity=getattr(device,'log_identity',None))),encoding='utf-8')
                # A frozen failure is retained too; the verifier determines completeness.
                freeze(session,start,tail.pos,source_root=source,**{k:v for k,v in registration.items() if k!='source_start'},ended_ns=time.time_ns())
            except (OSError,ValueError,KeyError) as exc:result.setdefault('errors',[]).append('freeze_'+str(exc))
        result['stopped_confirmed']=True
        if type(result.get('gross_tickets')) is int:
            ledger.append('resource_observed',session_id=session.name,tickets=result['gross_tickets'])
        ledger.append("runtime_end",session_id=session.name,seconds=time.monotonic()-t0)
        (session/"result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        if lock:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
            lock.close()
    return result


def verify_round(path):
    from bv_verify import verify_round as verify
    return verify(path)


def resume_registration(batch, ledger):
    """Only an authenticated pre-purchase wallet pause can resume the same candidate."""
    from bv_batch import verify_batch
    reg=json.loads((batch/'registration.json').read_text(encoding='utf-8'))
    previous=json.loads((batch/'result.json').read_text(encoding='utf-8'))
    starts=[json.loads(x) for x in (batch/'starts.jsonl').read_text(encoding='utf-8').splitlines()]
    if ((batch/'STOP').exists() or previous.get('status')!='Paused for wallet'
            or previous.get('next_ordinal')!=len(starts)+1 or len(starts)>=BATCH_ROUNDS):
        raise ValueError('resume_requires_unstarted_wallet_pause')
    expected=dict(code_version=code_version(),parser_version=VERSION,metric_version=METRIC,
                  instance=INSTANCE,resource_authorization=RESOURCE_AUTHORIZATION,limits=dict(LIMITS))
    if any(reg.get(k)!=v for k,v in expected.items()):raise ValueError('resume_candidate_changed')
    records=ledger.records()
    pauses=[r for r in records if r['kind']=='batch_wallet_pause' and r.get('batch_id')==batch.name]
    if not pauses or pauses[-1]['next_ordinal']!=len(starts)+1:
        raise ValueError('resume_pause_not_in_ledger')
    purchases=[r for r in records if r['kind']=='purchase_reserved' and r.get('batch_id')==batch.name]
    if len(purchases)!=len(starts) or {p['session_id'] for p in purchases}!={r['session_id'] for r in starts}:
        raise ValueError('resume_purchase_history_mismatch')
    verified=verify_batch(batch)
    allowed={'all_ten_started_rounds_required','live_source_verification_failed'}
    if set(verified.get('errors',[]))-allowed or len(verified.get('rounds',[]))!=len(starts):
        raise ValueError('resume_history_invalid')
    if any(not r.get('evidence_valid') or r.get('source_errors') for r in verified.get('rounds',[])):
        raise ValueError('resume_history_sources_incomplete')
    return reg,len(starts)+1


def start_batch(device=None,resume=None):
    """One registered candidate, at most ten consecutive starts; no replacement rounds."""
    import msvcrt
    from bv_verify import semantic_gate
    from bv_batch import verify_batch
    if not clean_code():return dict(status='Blocked',acceptance_pass=False,errors=['candidate_not_frozen'])
    if resume:
        target=Path(resume).resolve()
        if target.parent!=CONTROL.resolve() or not target.name.startswith('batch_') or not target.is_dir():
            return dict(status='Blocked',acceptance_pass=False,errors=['resume_path_outside_control'])
    CONTROL.mkdir(parents=True,exist_ok=True)
    lock=(CONTROL/'controller.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:
        lock.close();return dict(status='Blocked',acceptance_pass=False,errors=['controller_already_running'])
    batch=Path(resume).resolve() if resume else CONTROL/('batch_'+uuid.uuid4().hex)
    if not resume:batch.mkdir()
    ledger=Budget();device=device or Device();result={};run_errors=[];t0=time.monotonic()
    try:
        if resume:
            registration,first_ordinal=resume_registration(batch,ledger)
            used=registration['positions'][0]-1
            prepared=None
        else:
            remaining=ledger.remaining_positions()
            if remaining<BATCH_ROUNDS:raise ValueError('insufficient_positions_for_new_ten_round_batch')
            prep_sid=batch.name+'_preflight';prep0=time.monotonic()
            ledger.append('runtime_start',session_id=prep_sid)
            try:prepared=preflight(SOURCE,device,remaining_rounds=BATCH_ROUNDS)
            finally:ledger.append('runtime_end',session_id=prep_sid,seconds=time.monotonic()-prep0)
            check,_=prepared
            if not check.get('run_ready',check.get('purchase_ready')):
                result=dict(status='Blocked',acceptance_pass=False,started_rounds=0,
                            errors=check['blockers'],run_errors=check['blockers'],budget_plan=check.get('budget_plan'))
                return result
            plan=ledger.batch_plan(check['quote'])
            if not plan['fits']:
                result=dict(status='Blocked',acceptance_pass=False,started_rounds=0,
                            errors=['batch_budget_insufficient'],budget_plan=plan)
                return result
            used=LIMITS['acceptance_rounds']-remaining
            registration=dict(batch_id=batch.name,instance=INSTANCE,code_version=code_version(),
                              parser_version=VERSION,metric_version=METRIC,purpose='acceptance',planned_rounds=BATCH_ROUNDS,
                              registered_ns=time.time_ns(),source_start=(SOURCE/'bv_ws.jsonl').stat().st_size,
                              mode='full_autoplay',positions=list(range(used+1,used+BATCH_ROUNDS+1)),
                              available_rounds=remaining,budget_plan=plan,limits=dict(LIMITS),resource_authorization=RESOURCE_AUTHORIZATION,
                              semantic_rule='two_source_bound_rounds_distinct_targets_v1')
            (batch/'registration.json').write_text(json.dumps(registration),encoding='utf-8')
            (batch/'starts.jsonl').touch()
            ledger.append('batch_registered',**registration)
            first_ordinal=1
        for ordinal in range(first_ordinal,BATCH_ROUNDS+1):
            if (batch/'STOP').exists() or ledger.elapsed()>=LIMITS['total_seconds']:break
            if prepared is None:
                # Settlement may return to the lobby. Open only its known,
                # non-consuming panel before reading the next real quote.
                prep_sid=batch.name+'_prepare_'+uuid.uuid4().hex;prep0=time.monotonic()
                ledger.append('runtime_start',session_id=prep_sid)
                try:
                    device.stop_paths=(batch/'STOP',)
                    device.round_deadline=time.monotonic()+LIMITS['round_seconds']
                    prepare_panel=getattr(device,'prepare_panel',None)
                    if prepare_panel:prepare_panel(batch/f'prepare-{ordinal}.png')
                    prepared=preflight(SOURCE,device,remaining_rounds=BATCH_ROUNDS-ordinal+1)
                finally:ledger.append('runtime_end',session_id=prep_sid,seconds=time.monotonic()-prep0)
                check,_=prepared
                if not check.get('run_ready',check.get('purchase_ready')):
                    plan=check.get('budget_plan') or {};deficits=plan.get('deficits',{})
                    if (check.get('blockers')==['batch_budget_insufficient'] and deficits.get('wallet',0)>0
                            and not any(v for k,v in deficits.items() if k!='wallet')):
                        ledger.append('batch_wallet_pause',batch_id=batch.name,next_ordinal=ordinal,budget_plan=plan)
                        result=verify_batch(batch)
                        result.update(status='Paused for wallet',next_ordinal=ordinal,budget_plan=plan,
                                      acceptance_pass=False,run_errors=['wallet_insufficient_before_purchase'])
                        return result
                    run_errors=check.get('blockers') or ['run_not_ready'];break
            print(json.dumps(dict(mode='full_autoplay',round=ordinal,planned=BATCH_ROUNDS,
                  task_position=used+ordinal,status='starting',
                  notice='持续填充四卡全部合法目标，User无需补点',stop_path=str(batch/'STOP')),ensure_ascii=False),flush=True)
            session=batch/('acceptance_'+uuid.uuid4().hex)
            device.stop_paths=(session/'STOP',batch/'STOP')
            # Purchase, play and settlement share the same per-round input cap.
            device.round_deadline=time.monotonic()+LIMITS['round_seconds']
            run=diagnose(LIMITS['round_seconds'],True,source=SOURCE,root=CONTROL,device=device,play_round=True,batch=dict(registration,folder=str(batch),ordinal=ordinal),
                         session=session,lock_held=True,prepared=prepared)
            prepared=None
            if run.get('errors') or run.get('rounds_started')!=1:
                run_errors=run.get('errors') or ['round_not_started']
                break
            checked=verify_round(session/'frozen.json')
            (session/'verification.json').write_text(json.dumps(checked,indent=2),encoding='utf-8')
            if not checked.get('sources_rebuilt') or checked.get('source_errors'):break
            # A verified low rate stays in the batch; it is never replaced with a success.
            # Settlement navigation requires independently rebuilt close/terminal sources.
            nav0=time.monotonic();claimed=False;ready=False;rewards_dismissed=0
            ledger.append('runtime_start',session_id=session.name+'_settlement')
            while (time.monotonic()-nav0<20 and time.monotonic()<device.round_deadline
                   and ledger.elapsed()<LIMITS['total_seconds'] and not (batch/'STOP').exists()):
                sample=device.sample(session/'settlement.png')
                if time.monotonic()>=device.round_deadline or any(p.exists() for p in device.stop_paths):break
                if sample['scene'] in ('lobby','betpanel'):
                    ready=True;break
                if sample['scene']=='congrats' and not claimed:
                    claimed=True
                    if device.claim(sample)=='not_executed':break
                if sample['scene']=='reward' and rewards_dismissed<2:
                    rewards_dismissed+=1
                    if device.dismiss_reward(sample)=='not_executed':break
                    time.sleep(1)
                time.sleep(.5)
            ledger.append('runtime_end',session_id=session.name+'_settlement',seconds=time.monotonic()-nav0)
            (session/'settlement.json').write_text(json.dumps(dict(claimed=claimed,navigation_ready=ready,rewards_dismissed=rewards_dismissed)),encoding='utf-8')
            if not ready:break
        result=verify_batch(batch)
        if run_errors:
            result['run_errors']=run_errors
            result['errors']=sorted(set(result.get('errors',[])+run_errors))
    except (OSError,ValueError,KeyError,subprocess.TimeoutExpired) as exc:
        result=dict(status='Insufficient evidence',acceptance_pass=False,errors=[str(exc)])
    finally:
        result.update(batch_path=str(batch),stopped_confirmed=True)
        (batch/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        ledger.append('batch_end',batch_id=batch.name,wall_seconds=time.monotonic()-t0)
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
    return result
