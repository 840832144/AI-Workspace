"""Independent source replay. Controller summaries/done sets are never count inputs."""
import datetime as dt
import hashlib
import json
from pathlib import Path

from bv_client_state import ClientTrace, terminal_cells
from bv_evidence import expected_cells, VERSION


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def timestamp(event):
    date=dt.datetime.fromisoformat(event['received_at'])
    if date.tzinfo is None:
        if event.get('legacy_timezone')!='+08:00':raise ValueError('timestamp_timezone_unknown')
        date=date.replace(tzinfo=dt.timezone(dt.timedelta(hours=8)))
    return int(date.timestamp()*1e9)


def content_digest(source,events,files):
    """Only this frozen range and its referenced bodies/local observations."""
    h=hashlib.sha256()
    with Path(source['index']).open('rb') as f:
        f.seek(source['start']);data=f.read(source['end']-source['start'])
    if len(data)!=source['end']-source['start']:raise ValueError('source_truncated')
    h.update(data)
    for e in events:h.update(Path(e['source_ref']['body']).read_bytes())
    for path in files:h.update(Path(path).read_bytes())
    return h.hexdigest()


def replay(frozen_path):
    from bv_live import scan_range,SOURCE
    path=Path(frozen_path).resolve();f=read_json(path);s=f['source']
    if Path(s['index']).resolve()!=(SOURCE/'bv_ws.jsonl').resolve():raise ValueError('source_not_authorized_capture')
    if not all(type(s[k]) is int for k in ('start','end')) or not 0<=s['start']<s['end']:raise ValueError('source_range_invalid')
    files=[(path.parent/f[k]).resolve() for k in ('client_ref','actions_ref','selection_ref','config_ref')]
    if any(p.parent!=path.parent for p in files):raise ValueError('local_observation_outside_session')
    events,quality=scan_range(s['index'],SOURCE/'bv_bodies',s['start'],s['end'])
    if f['source_digest']!=content_digest(s,events,files):raise ValueError('frozen_source_changed')
    errors=list(quality)
    own=[e for e in events if e['type']=='personal_cards']
    if len(own)!=1:raise ValueError('unique_personal_cards_required')
    card=own[0];rid=card['round_id'];cards={c['slot']:c['vals'] for c in card['cards']}
    # Native round-start establishes log ownership; never assign an arbitrary RID to text.
    native=ClientTrace(files[0]).feed(files[0].read_bytes())
    starts=[e for e in native if e['type']=='client_round_start' and e['round_id']==rid and e['cards']==4]
    ends=[e for e in native if e['type']=='client_game_over' and e['round_id']==rid]
    if len(starts)!=1 or len(ends)!=1:raise ValueError('native_round_boundaries_incomplete')
    begin,end=starts[0]['at_ns'],ends[0]['at_ns']
    if not timestamp(card)<=begin<=end:errors.append('card_native_time_mismatch')
    # BallCaller index 0 can precede the layoutFrame log by a few milliseconds.
    # Recover that actual line only within this personal-card source boundary;
    # contiguous 0..last indices and the server union are still required below.
    native=[e for e in native if timestamp(card)<=e['at_ns']<=end and
            (e.get('round_id')==rid and e['at_ns']>=begin or
             e['type']=='client_called' and begin-1_000_000_000<=e['at_ns']<begin)]
    calls=[e for e in native if e['type']=='client_called']
    if not calls or [e['call_index'] for e in calls]!=list(range(len(calls))):errors.append('called_sequence_gap')
    called={e['ball'] for e in calls}
    windows=[e for e in events if e['type']=='balls' and e['round_id']==rid]
    if {n for e in windows for n in e['window']}!=called:errors.append('called_raw_union_mismatch')
    closes=[e for e in events if e['type']=='close_candidate' and e['round_id']==rid]
    if len(closes)!=1 or abs(timestamp(closes[0])-end)>10_000_000_000:errors.append('close_sources_disagree')
    states=[e for e in events if e['type']=='state_observation' and e['round_id']==rid and
            end-2_000_000_000<=timestamp(e)<=end+10_000_000_000]
    if len(states)!=1:raise ValueError('unique_terminal_state_required')
    cells=terminal_cells(states[0]['state'])
    marks=[e for e in native if e['type']=='client_marked']
    marked=set();special=set();call_time={e['ball']:e['at_ns'] for e in calls}
    for e in marks:
        key=e['card_id'],e['cell_index']
        if key not in cells or key[1]==12 or cards.get(key[0],[None]*25)[key[1]]!=e['ball']:
            errors.append('marked_identity_mismatch');continue
        if e['ball'] not in call_time or e['at_ns']<call_time[e['ball']]:
            errors.append('mark_before_call');continue
        if e['daub_type']=='Manual' and not cells[key]['special']:marked.add(key)
        else:special.add(key)
    terminal={k for k,v in cells.items() if k[1]!=12 and v['marked']}
    if not marked<=terminal:errors.append('client_terminal_contradiction')
    targets=expected_cells(card['cards'],called)
    confirmations=marked & terminal & targets
    # Unknown modifiers/effects remain Unknown, including terminal-only marks.
    unknown={k for k in targets if cells[k]['special'] or k in special or k in terminal and k not in confirmations}
    unfilled=targets-confirmations-unknown
    actions=[json.loads(l) for l in files[1].read_text(encoding='utf-8').splitlines()]
    dispatch=[e for e in actions if e.get('kind')=='input_dispatched' and e.get('round_id')==rid]
    manual=[e for e in marks if e['daub_type']=='Manual']
    matched=set()
    for e in manual:
        for i,a in enumerate(dispatch):
            at=a.get('dispatched_ns') or int(dt.datetime.fromisoformat(a['ts']).timestamp()*1e9)
            if (a['slot'],a['cell_index'])==(e['card_id'],e['cell_index']) and at<=e['at_ns']<=at+10_000_000_000:
                matched.add(i);break
    unexplained=len(manual)!=len(matched)
    selection,config=read_json(files[2]),read_json(files[3])
    symbol='BET_NP_SYMBOL_%d'%selection['BetCount']
    costs=[r['cost']*4 for r in config if r['id']==symbol]
    if len(costs)!=1 or selection['CardCount']!=4 or costs[0]!=selection['LastBetTicket'] or not 0<costs[0]<=8:
        raise ValueError('ordinary_quote_mismatch')
    buys=[e for e in events if e['type']=='buy_request']
    if len(buys)!=1 or buys[0]['card_count']!=4 or buys[0]['bet_symbol']!=symbol or card['bet_symbol']!=symbol:
        errors.append('purchase_card_binding_mismatch')
    all_native=ClientTrace(files[0]).feed(files[0].read_bytes())
    # Debit can precede StartGameLogic. Bind it to the same purchase/card boundary.
    buy_time=timestamp(buys[0]) if len(buys)==1 else begin
    changes=[e for e in all_native if e['type']=='ticket_change' and buy_time-2_000_000_000<=e['at_ns']<=end]
    if any(e['before']+e['delta']!=e['after'] for e in changes):errors.append('resource_delta_contradiction')
    gross=sum(-e['delta'] for e in changes if e['delta']<0)
    if gross!=costs[0]:errors.append('actual_spend_mismatch')
    controlled=(not errors and len(dispatch)==len(manual)==len(matched)==1 and terminal==confirmations
                and len(confirmations)==1 and not unexplained)
    return dict(status='observed_semantic_candidate',evidence_valid=False,rate=None,
                round_id=rid,cardset_ref=card['source_ref'],sources_rebuilt=True,errors=sorted(set(errors)),
                source_start=s['start'],source_end=s['end'],ended_ns=f['ended_ns'],
                purchase_ns=buy_time,
                client_begin_ns=begin,client_end_ns=end,called_count=len(called),
                N=len(confirmations),E=len(targets),Unknown=len(unknown),confirmed_unfilled=len(unfilled),
                per_card=[dict(card=i,E=sum(k[0]==i for k in targets),N=sum(k[0]==i for k in confirmations),
                              Unknown=sum(k[0]==i for k in unknown),confirmed_unfilled=sum(k[0]==i for k in unfilled)) for i in range(1,5)],
                manual_takeover=unexplained,controlled_differential=controlled,
                controlled_cell=list(next(iter(confirmations))) if controlled else None,
                dispatches=len(dispatch),native_manual=len(manual),terminal_marks=len(terminal),
                gross_tickets=gross,quote_tickets=costs[0],parser_version=VERSION,
                semantic_scope='ordinary Manual marks; modified cells Unknown; client acceptance, not server ACK')


def freeze(session,source_start,source_end,source_root=None,**metadata):
    from bv_live import SOURCE,scan_range
    source_root=Path(source_root or SOURCE)
    session=Path(session);source=dict(index=str(source_root/'bv_ws.jsonl'),start=source_start,end=source_end)
    events,quality=scan_range(source['index'],source_root/'bv_bodies',source_start,source_end)
    f=dict(source=source,client_ref='client-during.log',actions_ref='actions.jsonl',
           selection_ref='selection.json',config_ref='base_bet_config.json')
    f.update(metadata)
    f['source_digest']=content_digest(source,events,[session/f[k] for k in ('client_ref','actions_ref','selection_ref','config_ref')])
    path=session/'frozen.json'
    with path.open('x',encoding='utf-8') as stream:json.dump(f,stream,indent=2)
    return path


def semantic_gate(root=None):
    from bv_live import Budget,CONTROL
    root=Path(root or CONTROL);proofs=[];errors=[];seen=set()
    for row in Budget(root).records():
        if row['kind']!='purchase_reserved' or row['purpose']!='diagnostic':continue
        path=root/row['session_id']/'frozen.json'
        try:
            f=read_json(path)
            if f.get('purpose')!='diagnostic' or f.get('session_id')!=row['session_id']:raise ValueError('diagnostic_registration_mismatch')
            r=replay(path)
            if r['round_id'] in seen:raise ValueError('duplicate_diagnostic_round')
            seen.add(r['round_id'])
            proofs.append(dict(session_id=row['session_id'],controlled=r['controlled_differential'],
                               cell=r['controlled_cell'],errors=r['errors']))
        except (OSError,ValueError,KeyError,TypeError) as exc:
            errors.append(row['session_id']+':'+str(exc))
    count=sum(p['controlled'] for p in proofs)
    varied=len({tuple(p['cell']) for p in proofs if p['controlled']})>=2
    return dict(qualified=count>=2 and varied and not errors,controlled_rounds=count,required_rounds=2,
                distinct_targets_proven=varied,
                errors=errors,proofs=proofs,scope='ordinary_manual_only')


def verify_round(path):
    from bv_live import CONTROL,METRIC,Budget,INSTANCE
    path=Path(path).resolve()
    try:
        f=read_json(path)
        if f.get('purpose')!='acceptance' or f.get('evidence_kind')=='synthetic':raise ValueError('production_acceptance_sources_required')
        if CONTROL.resolve() not in path.parents or not path.parent.name.startswith('acceptance_'):raise ValueError('unregistered_session_path')
        r=replay(path);gate=semantic_gate()
        identity={k:f.get(k) for k in ('batch_id','instance','session_id','code_version','parser_version','metric_version')}
        if not all(identity.values()) or f['parser_version']!=VERSION or f['metric_version']!=METRIC:raise ValueError('version_identity_missing_or_mismatched')
        if f['instance']!=INSTANCE or f['session_id']!=path.parent.name:raise ValueError('runtime_identity_mismatch')
        reservations=[x for x in Budget().records() if x['kind']=='purchase_reserved' and x['purpose']=='acceptance' and
                      x['session_id']==f['session_id'] and x.get('batch_id')==f['batch_id']]
        if len(reservations)!=1 or reservations[0]['reserved_tickets']!=r['gross_tickets']:raise ValueError('live_budget_registration_missing')
        if not (f['registered_ns']<=reservations[0]['at_ns']<=r['purchase_ns']+2_000_000_000 and
                f['registered_ns']<=r['purchase_ns'] and f['ended_ns']>=r['client_end_ns']):
            raise ValueError('registration_not_before_live_sources')
        errors=r['errors']+([] if gate['qualified'] else ['two_controlled_diagnostics_not_proven'])
        if r['manual_takeover']:errors.append('unmatched_manual_input')
        valid=not errors
        return {**r,**identity,'frozen_ref':str(path),'evidence_valid':valid,'errors':errors,
                'status':('verified_lower_bound' if r['Unknown'] else 'exact') if valid else 'Insufficient evidence',
                'rate':r['N']/r['E'] if valid and r['E'] else None,
                'acceptance_pass':valid and 10*r['N']>9*r['E'],
                'hard_pass':valid and 10*r['N']>9*r['E']}
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return dict(status='Invalid',evidence_valid=False,acceptance_pass=False,hard_pass=False,rate=None,
                    frozen_ref=str(path),errors=[str(exc)])
