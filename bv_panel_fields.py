"""Decode scoped panel-field observations from an independently bounded reader.

This is a candidate decoder for the locally studied ARM64 build, not a live
transport or a PanelQuote. The caller must bind the binary, process epoch and
read interval. decode_panel_price covers only the observed ordinary path with
inactive free/discount effects; every unsupported state remains blocked.
No business methods, callbacks or inputs are invoked here.
"""
import re
import struct

UI_MANAGER_CLASS_SLOT=0x7e52ae8


def decode_panel_fields(read,il2cpp_base,type_names=None):
    type_names={} if type_names is None else type_names
    def q(addr):return struct.unpack('<Q',read(addr,8))[0]
    def i(addr):return struct.unpack('<i',read(addr,4))[0]
    def typename(obj):
        klass=q(obj)
        if klass not in type_names:
            type_names[klass]=read(q(klass+16),64).split(b'\0',1)[0].decode('utf-8')
        return type_names[klass],klass
    def expect(obj,name):
        actual,klass=typename(obj)
        if actual!=name:raise ValueError('unexpected_scoped_type')
        return klass
    def managed_id(addr):
        length=i(addr+16)
        if not 1<=length<=64:raise ValueError('identifier_length')
        value=read(addr+20,length*2).decode('utf-16-le')
        if not re.fullmatch(r'BET_[A-Z0-9_]+',value):raise ValueError('not_bet_config_id')
        return value

    ui_class=q(il2cpp_base+UI_MANAGER_CLASS_SLOT)
    static=q(ui_class+0xb8);manager=q(static)
    if expect(manager,'UIManager')!=ui_class:raise ValueError('manager_class_mismatch')
    panels=q(manager+0x50)
    header=read(panels+0x10,16);head,count,version=struct.unpack('<Qii',header)
    if not 0<=count<=8:raise ValueError('panel_count_out_of_bound')
    node=head;found=[];seen=set()
    for _ in range(count):
        if node in seen:raise ValueError('panel_list_cycle')
        seen.add(node);owner,next_node,prev_node,item=struct.unpack('<4Q',read(node+0x10,32))
        if owner!=panels:raise ValueError('panel_list_owner_changed')
        name,klass=typename(item)
        if name=='BuyCardPanel':found.append(item)
        node=next_node
    if len(found)!=1:raise ValueError('active_buy_panel_not_unique')
    panel=found[0]
    if read(panel+0x38,1)!=b'\0':raise ValueError('buy_panel_closed')
    cards_array=q(panel+0x90);index=i(panel+0x10c);length=i(cards_array+0x18)
    if not 0<=index<length<=8:raise ValueError('card_index_invalid')
    cards=i(cards_array+0x20+index*4)
    bet=q(panel+0xb0);expect(bet,'BetAddView')
    if q(bet+0xa0)!=panel:raise ValueError('bet_panel_backref_mismatch')
    data=q(panel+0x98);expect(data,'BetData')
    config=q(data+0x18);expect(config,'BaseBetConfig')
    symbol=managed_id(q(config+0x10));cost=i(config+0x18)
    model=q(panel+0x160);expect(model,'BuyCardPanelModel')
    fields=dict(panel_id=hex(panel),cards=cards,card_index=index,bet_index=i(bet+0x60),
                usable_max_bet_index=i(bet+0x64),cached_bet_cost=i(bet+0xb8),
                bet_symbol=symbol,base_per_card_cost=cost,unadjusted_product=cost*cards,
                mode_raw=i(model+0x18),can_play=bool(read(panel+0x111,1)[0]),
                showing_buff_cost=bool(read(panel+0x168,1)[0]),multi_fast_active=bool(read(panel+0x1d0,1)[0]))
    if read(panels+0x10,16)!=header or q(manager+0x50)!=panels or q(panel+0xb0)!=bet:
        raise ValueError('panel_lifecycle_changed')
    return dict(fields=fields,kind='observed_field_candidates_only',
                quote_source_available=False,run_ready=False)


# Version-specific MethodInfo slots and normal ARM64 implementations. The
# translated ARM64 mapping need not have the host executable permission bit.
PRICE_METHODS = (
    ('BuyCardPanel.RefreshTicketText',0x7ea5808,0x3d93b14),
    ('BuyCardPanel.get_CardAmount',0x7ea58d0,0x3d90d30),
    ('BetData.get_Cost',0x7e97ce0,0x3c91d9c),
    ('BetData.get_BaseBetConfig',0x7e97cc8,0x3c91a64),
    ('RoundBuffManager.Get',0x7effea0,0x3c1451c),
    ('RoundBuffManager.HasFreeRoundBuff',0x7effed0,0x3c1459c),
    ('BaseBuffModel.get_RemainTime',0x7e95720,0x412a530),
    ('NowTime.get_Seconds',0x7eee2d0,0x42215c0),
    ('NowTime.get_Milliseconds',0x7eee2c8,0x42213ac),
    ('DiscountRoundBuffManager.Get',0x7ebb408,0x3c3a6bc),
    ('DiscountRoundBuffManager.IsDiscountApplicable',0x7ebb458,0x3c3b4d8),
    ('DiscountRoundBuffManager.IsActive',0x7ebb440,0x3c3ae58),
    ('DiscountRoundBuffManager.ShouldShowBuyCardAnimation',0x7ebb4c8,0x3c3bc9c),
    ('BuyCardPanel.PlayTicketCostAnimation',0x7ea5750,0x3d94618),
    ('BuyCardPanel.PlaySelectCard',0x7ea5748,0x3d9ccd0),
    ('RuntimeBetListData.get_BetDataList',0x7f00390,0x3c93964),
    ('RuntimeBetListData.get_Source',0x7f003c0,0x3c936ac),
    ('RuntimeBetListData.get_CardCount',0x7f003a0,0x3c93710),
    ('RuntimeBetListData.get_Item',0x7f003b0,0x3c93ae8),
    ('BetListData.GetRuntimeBetDataList',0x7e97e28,0x3c93290),
)


def decode_panel_price(read,base,component_slots=None,metadata_names=None):
    """Pure decoder; no IO, calls, labels from saved files, or purchase permission.

    component_slots retains only dictionary indices plus its identity/version.
    Values and all followed pointers are reread. A changed table needs discovery.
    The transport must obtain two complete fresh matching observations.
    """
    metadata_names={'classes':{},'methods':{}} if metadata_names is None else metadata_names
    q=lambda a:struct.unpack('<Q',read(a,8))[0]
    i=lambda a:struct.unpack('<i',read(a,4))[0]
    def boolean(a):
        value=read(a,1)[0]
        if value not in (0,1):raise ValueError('invalid_boolean')
        return bool(value)
    def cname(klass):
        if klass not in metadata_names['classes']:
            metadata_names['classes'][klass]=read(q(klass+16),64).split(b'\0',1)[0].decode()
        return metadata_names['classes'][klass]
    def expect(obj,name):
        klass=q(obj)
        if cname(klass)!=name:raise ValueError('unexpected_price_type')
        return klass
    def string(obj,pattern,limit=64):
        n=i(obj+16)
        if not 1<=n<=limit:raise ValueError('price_string_length')
        value=read(obj+20,2*n).decode('utf-16-le')
        if not re.fullmatch(pattern,value):raise ValueError('price_string_format')
        return value
    def method(slot,expected,name=None):
        obj=q(base+slot)
        if not obj or obj&1:raise ValueError('price_method_not_initialized')
        raw=read(obj,104)
        if raw[0x53]&32 or struct.unpack_from('<Q',raw,0x60)[0]!=base+expected:
            raise ValueError('price_method_dispatch_changed')
        if name:
            np,klass=struct.unpack_from('<QQ',raw,24)
            if np not in metadata_names['methods']:
                metadata_names['methods'][np]=read(np,96).split(b'\0',1)[0].decode()
            actual=cname(klass)+'.'+metadata_names['methods'][np]
            if actual!=name:raise ValueError('price_method_identity')
        return obj

    fields=decode_panel_fields(read,base,metadata_names['classes'])['fields']
    panel=int(fields['panel_id'],16)
    fields.update(discount_anim_played=boolean(panel+0x169),
                  prevent_click=boolean(panel+0x108))
    for name,slot,rva in PRICE_METHODS:method(slot,rva,name)
    klass=q(base+0x7e48580);root=q(q(klass+0xb8))
    if expect(root,'GameComponentRoot')!=klass or boolean(root+0x20):
        raise ValueError('component_root_invalid')
    table=q(root+0x28);expect(table,'Dictionary`2')
    header=read(table+0x10,32)
    _,entries,count,version,_,free=struct.unpack('<QQiiii',header)
    if not 0<=free<=count<=i(entries+0x18)<=512:raise ValueError('component_table_bound')
    identity=(root,table,header.hex())
    if component_slots is not None and component_slots['identity']!=identity:
        raise ValueError('component_table_changed')
    targets={}
    for name,slot in [('RoundBuffManager',0x7ecfd48),('DiscountRoundBuffManager',0x7ecfbb8)]:
        obj=method(slot,0x4fa5498)
        _,target=struct.unpack('<QQ',read(q(obj+0x38),16))
        if cname(target)!=name:raise ValueError('component_generic_type')
        targets[target+0x20]=(name,target)
    matches={};indices=[]
    for index in component_slots['indices'] if component_slots is not None else range(count):
        if not 0<=index<count:raise ValueError('component_index_bound')
        code,_,key,value=struct.unpack('<iiQQ',read(entries+0x20+24*index,24))
        if code<0 or not key:continue
        target=targets.get(q(key+0x10))
        if target is None:continue
        name,klass=target
        if name in matches:raise ValueError('duplicate_price_component')
        expect(value,'List`1');items=q(value+0x10);n=i(value+0x18)
        if not 1<=n<=8 or i(items+0x18)<n:raise ValueError('component_list_bound')
        obj=q(items+0x20)
        if expect(obj,name)!=klass or q(obj+0x18)!=root or boolean(obj+0x20):
            raise ValueError('price_component_identity')
        matches[name]=obj;indices.append(index)
    if len(matches)!=2:raise ValueError('price_component_missing')
    rb=matches['RoundBuffManager'];dr=matches['DiscountRoundBuffManager']
    buff=q(rb+0x38);expect(buff,'FreeRoundBuff')
    # A zero/negative end time cannot be active at a positive game epoch.
    # Other expiration/discount cases require their own proven path.
    effect_state=dict(free_end=i(buff+0x18),free_temp_ended=boolean(rb+0x58),
                      discount_state=q(dr+0x38),discount_config=q(dr+0x40))
    time_class=q(base+0x7e4d120);now=q(q(time_class+0xb8))
    if expect(now,'NowTime')!=time_class:raise ValueError('price_clock_identity')
    effect_state['server_time_diff_ms']=struct.unpack('<q',read(now+0x38,8))[0]
    if abs(effect_state['server_time_diff_ms'])>=86400000:raise ValueError('price_clock_offset_unsupported')
    if effect_state['free_end']>0 or effect_state['discount_state'] or effect_state['discount_config']:
        raise ValueError('unsupported_price_effect_state')
    if (fields['mode_raw']!=1 or fields['cards']!=4 or not fields['can_play']
            or fields['multi_fast_active'] or fields['showing_buff_cost'] or fields['prevent_click']):
        raise ValueError('ordinary_panel_not_ready')
    bet=q(panel+0xb0)
    if not boolean(bet+0x6c) or boolean(bet+0xc8):raise ValueError('bet_selection_in_transition')
    runtime=q(bet+0x48);expect(runtime,'RuntimeBetListData')
    if i(runtime+0x18)!=fields['cards']:raise ValueError('bet_card_count_mismatch')
    source=q(runtime+0x10);expect(source,'BetListData')
    listing=q(source+0x20);expect(listing,'List`1')
    items=q(listing+0x10);count=i(listing+0x18);list_version=i(listing+0x1c)
    index=fields['bet_index'];maximum=fields['usable_max_bet_index']
    if not 0<=index<=maximum<count<=i(items+0x18)<=64:raise ValueError('bet_choices_bound')
    choices=[]
    for idx in range(maximum+1):
        data=q(items+0x20+idx*8);expect(data,'BetData')
        if i(data+0x10)!=idx:raise ValueError('bet_index_mismatch')
        config=q(data+0x18);expect(config,'BaseBetConfig')
        choices.append(dict(id=string(q(config+0x10),r'BET_NP_SYMBOL_[0-9]+'),cost=i(config+0x18)))
        if idx==index and data!=q(panel+0x98):raise ValueError('panel_bet_list_mismatch')
    if len({v['id'] for v in choices})!=len(choices):raise ValueError('duplicate_available_bet')
    chosen=choices[index]
    if (chosen['id']!=fields['bet_symbol'] or chosen['cost']!=fields['base_per_card_cost']
            or chosen['cost']!=min(v['cost'] for v in choices)):
        raise ValueError('current_bet_not_minimum')
    agent=q(panel+0x280);expect(agent,'TextAgent')
    tmp=boolean(agent+0x48);text=q(agent+(0x38 if tmp else 0x40))
    expect(text,'TextMeshProUGUI' if tmp else 'Text')
    text_pointer=q(text+(0xd8 if tmp else 0xe0))
    displayed=int(string(text_pointer,r'[0-9]{1,2}',2))
    if displayed!=fields['unadjusted_product']:raise ValueError('displayed_price_mismatch')
    if read(table+0x10,32)!=header or i(listing+0x1c)!=list_version:
        raise ValueError('price_collection_changed')
    return dict(fields=fields,available_bets=choices,tickets=displayed,effect_state=effect_state,
                text_source='TextCostNum.TextTMP.m_text' if tmp else 'TextCostNum.TextUGUI.m_Text',
                component_slots=dict(identity=identity,indices=indices))
