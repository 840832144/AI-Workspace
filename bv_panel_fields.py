"""Decode scoped panel-field observations from an independently bounded reader.

This is a candidate decoder for the locally studied ARM64 build, not a live
transport or a PanelQuote. The caller must bind the binary, process epoch and
read interval. Discounts, free-round state and hotfix dispatch remain unproven.
No business methods, callbacks or inputs are invoked here.
"""
import re
import struct

UI_MANAGER_CLASS_SLOT=0x7e52ae8


def decode_panel_fields(read,il2cpp_base):
    def q(addr):return struct.unpack('<Q',read(addr,8))[0]
    def i(addr):return struct.unpack('<i',read(addr,4))[0]
    def typename(obj):
        klass=q(obj);name=q(klass+16)
        return read(name,64).split(b'\0',1)[0].decode('utf-8'),klass
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
