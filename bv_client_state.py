"""Read existing client logs and terminal state; never generate game messages."""
import datetime as dt
import re

STAMP=re.compile(rb"^[A-Z]:\d+:-?\d+:(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d+) ([+-]\d{2}:\d{2}) ")
CALL=re.compile(rb"\[BallCaller\].* index (\d+), num (\d+)")
DAUB=re.compile(rb"BingoLog: Daub Type (\w+), Index: (\d+), (\d+), \((\d+),(\d+)\)")
TICKET=re.compile(rb"NotifyResources TICKET current=(\d+) next=(\d+) delta=(-?\d+)")


class ClientTrace:
    def __init__(self,source,round_id=None,offset=0):
        self.source=str(source);self.round_id=round_id;self.offset=offset;self.pending=b''

    def feed(self,chunk):
        self.pending+=chunk;out=[]
        lines=self.pending.split(b'\n');self.pending=lines.pop()
        for line in lines:
            at=self.offset;self.offset+=len(line)+1
            call=CALL.search(line);daub=DAUB.search(line);ticket=TICKET.search(line)
            start=re.search(rb'StartGameLogic:layoutFrame round=(\S+) .*cards=(\d+)',line)
            if not (call or daub or ticket or start or b'BingoPlayView GameOver' in line):continue
            stamp=STAMP.search(line)
            if not stamp:continue
            date=dt.datetime.strptime((stamp[1]+b' '+stamp[2]).decode(),'%y/%m/%d %H:%M:%S.%f %z')
            base=dict(at_ns=int(date.timestamp()*1e9),round_id=self.round_id,
                      source_ref={"client_log":self.source,"offset":at},evidence_level="client_observation")
            if start:
                self.round_id=start[1].decode();base['round_id']=self.round_id
                out.append(dict(base,type='client_round_start',cards=int(start[2])))
            elif call:
                out.append(dict(base,type='client_called',call_index=int(call[1]),ball=int(call[2])))
            elif daub:
                out.append(dict(base,type='client_marked',daub_type=daub[1].decode(),card_id=int(daub[2])+1,
                                ball=int(daub[3]),cell_index=int(daub[5])*5+int(daub[4])))
            elif ticket:
                out.append(dict(base,type='ticket_change',before=int(ticket[1]),after=int(ticket[2]),delta=int(ticket[3])))
            elif b'BingoPlayView GameOver' in line:
                out.append(dict(base,type='client_game_over'))
        return out


def terminal_cells(state):
    """Four 25-cell blocks, including FREE. '@...#' is between cards, not a cell.

    Splitting all '|' first produces 97 tokens because adjacent card endpoints merge.
    Each cell has three colon fields; only the first field denotes the mark candidate.
    Qualification of that meaning is separate from this parser.
    """
    parts=state.split('@')
    if len(parts)!=5 or parts[-1] not in ('','Z'):
        raise ValueError('state_card_boundaries')
    cards=[]
    for i,part in enumerate(parts[:4]):
        if i:
            if part.count('#')!=1:raise ValueError('state_wrapper_missing')
            wrapper,part=part.split('#',1)
            if not re.fullmatch(r'[0-9.,:-]*',wrapper):raise ValueError('state_wrapper_unknown')
        tokens=part.split('|')
        if len(tokens)!=25:raise ValueError('state_card_size')
        parsed=[]
        for t in tokens:
            if t=='':parsed.append(dict(marked=False,special=False));continue
            if not re.fullmatch(r'[01]?:[0-9]*:[0-9]*',t):
                raise ValueError('state_cell_semantics_unknown')
            flag,modifier,extra=t.split(':')
            parsed.append(dict(marked=flag=='1',special=bool(modifier or extra)))
        if not parsed[12]['marked']:raise ValueError('free_cell_mapping_inconsistent')
        cards.append(parsed)
    return {(slot+1,index):cell for slot,card in enumerate(cards) for index,cell in enumerate(card)}
