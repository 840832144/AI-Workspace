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
METRIC = "set-intersection-r1-v2"
LIMITS = {"diagnostic_rounds": 3, "acceptance_rounds": 10, "cards": 4,
          "tickets_per_round": 8, "gross_tickets": 96, "round_seconds": 300, "total_seconds": 2700}


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

    def stopped(self):
        return any(Path(p).exists() for p in getattr(self,'stop_paths',()))

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
        if not re.fullmatch(r"[A-Za-z0-9]+",account):raise ValueError("invalid_account_path")
        version=self.read_file(self.base+"gds/gds_version.txt").decode().strip()
        if not re.fullmatch(r"[a-f0-9]{32}",version):raise ValueError("unknown_game_config_version")
        path=self.base+"save/"+account+"/"
        selection=self.read_file(path+"buy_card_data.json")
        discount=self.read_file(path+"discount_buff_local_data.json")
        config=self.read_file(self.base+"gds/"+version+"/BaseBetConfig.json")
        s=json.loads(selection);d=json.loads(discount)
        symbol="BET_NP_SYMBOL_%d"%s["BetCount"]
        matches=[r for r in json.loads(config) if r["id"]==symbol]
        if len(matches)!=1 or s["CardCount"]!=4 or s["BetCount"] not in (1,2) or d["IsActivated"]:
            raise ValueError("ordinary_four_card_configuration_required")
        cost=matches[0]["cost"]*s["CardCount"]
        if type(cost) is not int or not 0<cost<=8 or s["LastBetTicket"]!=cost:
            raise ValueError("current_selection_cost_mismatch")
        # Original bytes retained locally so the selected quote can be rebuilt.
        for name,b in (("selection.json",selection),("discount.json",discount),("base_bet_config.json",config)):
            (folder/name).write_bytes(b)
        from bv_autoplay import ADB,DEV
        r=subprocess.run([ADB,"-s",DEV,"exec-out","ls",self.base+"client_logging_temp"],capture_output=True,timeout=5,check=True)
        names=[n for n in r.stdout.decode().splitlines() if re.fullmatch(r"[0-9_-]+\.txt",n)]
        if len(names)!=1:raise ValueError("client_log_identity_ambiguous")
        logpath=self.base+"client_logging_temp/"+names[0]
        raw=self.read_file(logpath)
        (folder/"client-before.log").write_bytes(raw)
        proof=cost_proof(raw,symbol,cost)
        changes=[e for e in ClientTrace(folder/"client-before.log").feed(raw) if e["type"]=="ticket_change"]
        if any(e["before"]+e["delta"]!=e["after"] for e in changes):raise ValueError("ticket_delta_contradiction")
        return {"tickets":cost,"cards":4,"bet_symbol":symbol,"gds_version":version,
                "source_ref":str(folder/"selection.json"),"config_ref":str(folder/"base_bet_config.json"),"cost_semantics_ref":proof,
                "log_path":logpath,"log_start":len(raw),"sampled_at":time.monotonic(),
                "last_ticket_change":max(changes,key=lambda e:e['at_ns']) if changes else None}

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
        det=bv_cardgrid.detect(im)
        green=find_green(im)
        panel=near(im.getpixel((100,700)),BLUE,65) and green and 400<green[0]<500 and 1100<green[1]<1230
        congrats=near(im.getpixel((150,450)),ORANGE,70) and green and 350<green[0]<550 and 1200<green[1]<1400
        scene="round" if len(det or [])==4 else "betpanel" if panel else "congrats" if congrats else "lobby" if green and 120<green[0]<400 and green[1]>1200 else "unknown"
        return {"foreground":ok,"scene":scene,"grid":det,"button":list(green[:2]) if green else None,
                "sampled_at":sampled_at}

    def claim(self,sample):
        from bv_autoplay import spawn_tap,finish_tap
        if sample['scene']!='congrats' or time.monotonic()-sample['sampled_at']>2.5 or not self.foreground():return 'not_executed'
        return self.send(sample['button'])

    def open_panel(self, sample):
        from bv_autoplay import spawn_tap, finish_tap
        if sample["scene"]!="lobby" or time.monotonic()-sample["sampled_at"]>2.5 or not self.foreground():
            return "not_executed"
        return self.send(sample['button'])

    def buy(self,sample,quote):
        from bv_autoplay import spawn_tap,finish_tap
        if (sample["scene"]!="betpanel" or time.monotonic()-sample["sampled_at"]>2.5
                or time.monotonic()-quote["sampled_at"]>10 or not self.foreground()):
            return "not_executed"
        return self.send(sample['button'])


def ticket_balance(wallet,change):
    from bv_verify import timestamp
    when=timestamp(wallet)
    return change['after'] if change and change['at_ns']>when else wallet['currencies']['TICKET']


def preflight(source=SOURCE, device=None):
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
            quote["balance"]=ticket_balance(wallets[-1],quote.get('last_ticket_change'))
        except (OSError,ValueError,KeyError,subprocess.TimeoutExpired) as exc:
            errors.append("quote_"+str(exc))
    buy_errors=list(errors)
    if quote is None:buy_errors.append("current_ticket_quote_unverified")
    if quality:buy_errors.append("capture_quality_errors")
    from bv_verify import semantic_gate
    gate=semantic_gate()
    ready=not buy_errors and gate['qualified'] and clean_code()
    result={"status":"Ready" if ready else "Ready for diagnostic navigation" if not errors else "Blocked",
            "diagnostic_navigation_ready":fg and bool(wallets), "live_ready":ready, "purchase_ready":not buy_errors,
            "semantic_gate":gate,
            "blockers":buy_errors, "capture_errors":quality,"limits":LIMITS,
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

    def reserve(self,purpose,quote,session,batch_id=None):
        records=self.records()
        purchases=[r for r in records if r["kind"]=="purchase_reserved"]
        elapsed=self.elapsed()
        if quote is None or quote.get("source_ref") is None or type(quote.get("tickets")) is not int:
            raise ValueError("verified_quote_required")
        cost=quote["tickets"]
        if not 0<cost<=8 or quote.get("cards")!=4 or quote.get("balance",-1)<cost:
            raise ValueError("per_round_resource_limit")
        limit=LIMITS.get(purpose+'_rounds',0)
        if sum(r["purpose"]==purpose for r in purchases)>=limit:raise ValueError("round_count_limit")
        actual={r['session_id']:r['tickets'] for r in records if r['kind']=='resource_observed'}
        if sum(max(r['reserved_tickets'],actual.get(r['session_id'],0)) for r in purchases)+cost>96 or elapsed>=2700:
            raise ValueError("task_resource_limit")
        self.append("purchase_reserved",purpose=purpose,session_id=session,reserved_tickets=cost,
                    quote_source=quote["source_ref"],batch_id=batch_id)


def code_version():
    r=subprocess.run(["git","rev-parse","HEAD"],cwd=Path(__file__).parent,capture_output=True,text=True,check=True)
    return r.stdout.strip()


def clean_code():
    result=subprocess.run(['git','status','--porcelain','--untracked-files=normal'],cwd=Path(__file__).parent,
                          capture_output=True,text=True,check=True)
    return not result.stdout.strip()


def diagnose(seconds=20,open_panel=False,source=SOURCE,root=CONTROL,device=None,play_round=False,
             batch=None,session=None,lock_held=False):
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
    registration={};processed_calls=set();processed_marks=set()
    ledger.append('runtime_start',session_id=session.name)
    try:
        if play_round and not clean_code():raise ValueError('candidate_not_frozen')
        if batch:
            from bv_verify import semantic_gate
            if not semantic_gate(root)['qualified']:raise ValueError('two_controlled_diagnostics_not_proven')
        check,history=preflight(source,device)
        start=index.stat().st_size
        registration={"purpose":purpose,"registered_ns":time.time_ns(),"code_version":code_version(),
                      "parser_version":VERSION,"metric_version":METRIC,"source_start":start,
                      "instance":INSTANCE,"limits":LIMITS,"session_id":session.name}
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
                         max_dispatches=96 if batch else 1,
                         batch_stop_path=str(stop_paths[1]) if batch else None,
                         diagnostic_slot=None if batch else 2,
                         session_path=str(session),capture_index=str(index),bodies=source/"bv_bodies"))
        while time.monotonic()-t0 < min(seconds,300) and ledger.elapsed()<2700 and not (session/"STOP").exists() and not (batch and (Path(batch['folder'])/'STOP').exists()):
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
                if buy_at and time.monotonic()-buy_at>=300:break
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
                        if controller.grid:controller.layout_at=sample['sampled_at']
                    elif not paid or sample["scene"]!="round":controller.revoke("not_visible_round")
                if open_panel and not opened and check["diagnostic_navigation_ready"] and sample["scene"]=="lobby":
                    # Only a non-consuming navigation action. No fall-through to PLAY on the panel.
                    opened=True
                    outcome=device.open_panel(sample)
                    events.append({"type":"navigation_input","outcome":outcome,"at_ns":time.time_ns()})
                elif play_round and not paid and sample["scene"]=="betpanel" and check["purchase_ready"]:
                    account=next(e["account"] for e in reversed(history) if e["type"]=="wallet_snapshot")
                    quote=device.context(account,session)
                    wallet=next(e for e in reversed(history) if e['type']=='wallet_snapshot')
                    quote['balance']=ticket_balance(wallet,quote.get('last_ticket_change'))
                    # Re-sample after context IO, then re-check the just-read quote before dispatch.
                    fresh=device.sample(session/"before-buy.png")
                    if stopped():break
                    if batch and (code_version()!=batch['code_version'] or not clean_code()):raise ValueError('code_changed_during_batch')
                    ledger.reserve(purpose,quote,session.name,batch['batch_id'] if batch else None)
                    paid=True;buy_at=time.monotonic();client_offset=quote["log_start"]
                    trace=ClientTrace(str(session/"client-during.log"))
                    result.update(rounds_started=1,reserved_tickets=quote["tickets"],gross_tickets=None)
                    outcome=device.buy(fresh,quote)
                    events.append({"type":"purchase_input","outcome":outcome,"at_ns":time.time_ns(),"quote":quote})
                    if outcome=="not_executed":raise ValueError("purchase_cancelled_before_dispatch")
            if paid and quote:
                if client_future is None:
                    client_future=client_pool.submit(device.read_file,quote["log_path"],client_offset)
                elif client_future.done():
                    chunk=client_future.result();client_future=None;client_offset+=len(chunk);client_chunks.append(chunk)
                    for event in trace.feed(chunk):
                        native_events.append(event)
                    # Replay only already-observed native calls after personal-card binding.
                    for event in native_events:
                        ref=event['source_ref']['offset']
                        if event['type']=='client_called' and round_id_bound and ref not in processed_calls:
                            if event.get('round_id')!=round_id_bound:
                                from bv_verify import timestamp
                                starts=[e for e in native_events if e['type']=='client_round_start' and e['round_id']==round_id_bound]
                                own=[e for e in events if e['type']=='personal_cards' and e['round_id']==round_id_bound]
                                if not starts or not own or not max(timestamp(own[0]),starts[0]['at_ns']-1_000_000_000)<=event['at_ns']<starts[0]['at_ns']:continue
                            processed_calls.add(ref)
                            candidates={n for e in events if e.get("type")=="balls" and e.get("round_id")==round_id_bound for n in e["window"]}
                            if event["ball"] not in candidates:
                                controller.revoke("called_source_mismatch",halt=True)
                            else:controller.on_ball(event["at_ns"],round_id_bound,event["ball"])
                        elif batch and event['type']=='client_marked' and round_id_bound and ref not in processed_marks:
                            if event['round_id']!=round_id_bound:continue
                            processed_marks.add(ref)
                            if not controller.accept_client_mark(event):
                                controller.revoke('unmatched_client_mark',halt=True)
                                result.setdefault('errors',[]).append('unmatched_client_mark')
                    deltas=re.findall(rb"NotifyResources TICKET current=(\d+) next=(\d+) delta=(-?\d+)",b"".join(client_chunks))
                    gross=sum(-int(d) for a,b,d in deltas if int(d)<0)
                    if deltas:result["gross_tickets"]=gross
                    if gross>quote["tickets"]:
                        controller.revoke("unexpected_ticket_consumption",halt=True)
                        raise ValueError("unexpected_ticket_consumption")
            time.sleep(.05)
        result.update(blockers=check["blockers"], capture_errors=dict(tail.errors),
                      observed_commands=dict(Counter(str(e.get("cmd")) for e in events if "cmd" in e)),
                      scene=samples[-1]["scene"] if samples else "unknown", navigation_sent=opened,
                      source_start=start, source_end=tail.pos,
                      stopped_confirmed=True, stop_requested=stopped())
        if controller:
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


def start_batch(device=None):
    """One registered candidate, at most ten consecutive starts; no replacement rounds."""
    import msvcrt
    from bv_verify import semantic_gate
    from bv_batch import verify_batch
    gate=semantic_gate()
    if not gate['qualified']:
        return dict(status='Blocked',acceptance_pass=False,started_rounds=0,gate=gate,
                    errors=['two_controlled_diagnostics_not_proven'])
    if not clean_code():return dict(status='Blocked',acceptance_pass=False,errors=['candidate_not_frozen'])
    CONTROL.mkdir(parents=True,exist_ok=True)
    lock=(CONTROL/'controller.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:
        lock.close();return dict(status='Blocked',acceptance_pass=False,errors=['controller_already_running'])
    batch=CONTROL/('batch_'+uuid.uuid4().hex);batch.mkdir()
    ledger=Budget();device=device or Device();result={};t0=time.monotonic()
    try:
        registration=dict(batch_id=batch.name,instance=INSTANCE,code_version=code_version(),
                          parser_version=VERSION,metric_version=METRIC,purpose='acceptance',planned_rounds=10,
                          registered_ns=time.time_ns(),source_start=(SOURCE/'bv_ws.jsonl').stat().st_size)
        (batch/'registration.json').write_text(json.dumps(registration),encoding='utf-8')
        (batch/'starts.jsonl').touch()
        ledger.append('batch_registered',**registration)
        for ordinal in range(1,11):
            if (batch/'STOP').exists() or ledger.elapsed()>=2700:break
            session=batch/('acceptance_'+uuid.uuid4().hex)
            device.stop_paths=(session/'STOP',batch/'STOP')
            run=diagnose(300,True,source=SOURCE,root=CONTROL,device=device,play_round=True,batch=dict(registration,folder=str(batch),ordinal=ordinal),
                         session=session,lock_held=True)
            if run.get('errors') or run.get('rounds_started')!=1:break
            checked=verify_round(session/'frozen.json')
            (session/'verification.json').write_text(json.dumps(checked,indent=2),encoding='utf-8')
            if not checked.get('evidence_valid'):break
            # A verified low rate stays in the batch; it is never replaced with a success.
            # Settlement navigation requires independently rebuilt close/terminal sources.
            nav0=time.monotonic();claimed=False;ready=False
            ledger.append('runtime_start',session_id=session.name+'_settlement')
            while time.monotonic()-nav0<20 and ledger.elapsed()<2700 and not (batch/'STOP').exists():
                sample=device.sample(session/'settlement.png')
                if any(p.exists() for p in device.stop_paths):break
                if sample['scene'] in ('lobby','betpanel'):
                    ready=True;break
                if sample['scene']=='congrats' and not claimed:
                    claimed=True
                    if device.claim(sample)=='not_executed':break
                time.sleep(.5)
            ledger.append('runtime_end',session_id=session.name+'_settlement',seconds=time.monotonic()-nav0)
            (session/'settlement.json').write_text(json.dumps(dict(claimed=claimed,navigation_ready=ready)),encoding='utf-8')
            if not ready:break
        result=verify_batch(batch)
    except (OSError,ValueError,KeyError,subprocess.TimeoutExpired) as exc:
        result=dict(status='Insufficient evidence',acceptance_pass=False,errors=[str(exc)])
    finally:
        result.update(batch_path=str(batch),stopped_confirmed=True)
        (batch/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        ledger.append('batch_end',batch_id=batch.name,wall_seconds=time.monotonic()-t0)
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
    return result
