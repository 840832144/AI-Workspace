"""Synthetic geometry/dispatch integration. No ADB, spending or real scores."""
import copy
from concurrent.futures import Future
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image,ImageDraw
import bv_autoplay as ap
import bv_live as live
from bv_cardgrid import cell_geometry
from test_reliability import controller,grid


def measured():
    cards=grid()
    for c in cards:
        c.update(header_top=c['rows'][0]-75,header_bottom=c['rows'][0]-40,
                 spacing=78,header_x0=c['cols'][0]-38,header_x1=c['cols'][-1]+38,
                 cell_geometry=dict(cols=list(c['cols']),rows=list(c['rows']),reachable_cells=list(range(25))))
    return cards


class Recovery(unittest.TestCase):
    def test_vectorized_runs_preserve_component_merging(self):
        import numpy as np
        from bv_cardgrid import components,row_runs
        def previous(mask):
            result=[]
            for y in range(mask.shape[0]):
                for left,right in row_runs(mask[y]):
                    for c in result:
                        overlap=min(c[1],right)-max(c[0],left)+1
                        if y-c[3]<=2 and overlap>.5*min(c[1]-c[0]+1,right-left+1):
                            c[0],c[1]=min(c[0],left),max(c[1],right)
                            c[3]=y;c[4]+=right-left+1;break
                    else:result.append([left,right,y,y,right-left+1])
            return [tuple(c) for c in result if c[4]>=1]
        rng=np.random.default_rng(39)
        for _ in range(10):
            mask=np.zeros((45,120),bool)
            for j in range(12):
                x,y=rng.integers(0,90),rng.integers(0,30)
                mask[y:y+8,x:x+25]=True
            self.assertEqual(components(mask,min_area=1),previous(mask))

    def test_round_input_deadline_also_cancels_settlement_after_slow_foreground(self):
        d=live.Device();d.round_deadline=300
        # Sampling starts before the deadline; the final send is after it.
        with patch.object(live.time,'monotonic',side_effect=[299,301]),patch.object(d,'foreground',return_value=True),patch.object(ap,'spawn_tap') as send:
            self.assertEqual(d.claim(dict(scene='congrats',sampled_at=298,button=[1,1])),'not_executed')
            send.assert_not_called()
        from test_review_r1 import Dispatch
        c=Dispatch().queued();c.a.round_deadline=12
        with patch.object(ap.time,'monotonic',return_value=12),patch.object(ap,'spawn_tap') as send:
            self.assertEqual(c.input_pool.fn(),'cancelled');send.assert_not_called()

    def test_real_cell_shapes_not_header_or_bright_extent(self):
        c=measured()[0];im=Image.new('RGB',(900,1600),'#38719e');draw=ImageDraw.Draw(im)
        for i,x in enumerate(c['cols']):
            for j,y in enumerate(c['rows']):
                draw.rounded_rectangle((x-34,y-34,x+34,y+34),radius=16,
                                       fill=(245,210,50) if (i,j)==(2,1) else
                                            (245,40,50) if (i+j)%2 else (250,247,233))
        x,y=c['cols'][0],c['rows'][4]
        draw.rectangle((x-26,y-26,x+26,y+26),fill='black')
        body=cell_geometry(im,c);self.assertIsNotNone(body)
        self.assertLess(max(abs(a-b) for a,b in zip(body['rows'],c['rows'])),2)
        self.assertEqual(len(body['reachable_cells']),25)
        draw.rectangle((c['cols'][0]-38,c['rows'][0]-38,c['cols'][-1]+38,c['rows'][-1]+38),fill='#38719e')
        self.assertIsNone(cell_geometry(im,c)) # Header/old coordinates alone cannot open input.

    def test_three_actual_shape_measurements_do_not_need_three_extra_frames(self):
        d=live.Device();c=controller();base=measured()
        for t in [10,11,12]:
            with patch.object(live.time,'monotonic',return_value=t):det=d.calibrated_grid(base)
        with patch.object(ap.time,'monotonic',return_value=12):
            c.setup_grid(4,det)
        self.assertTrue(all(g['input_ready'] for g in c.grid.values()))
        for history in [[],[dict(at=12,cols=base[0]['cols'],rows=base[0]['rows'])]*3,
                        [dict(at=t,cols=base[0]['cols'],rows=base[0]['rows']) for t in [1,2,3]]]:
            fresh=controller();bad=copy.deepcopy(det)
            for card in bad:card['shape_history']=history
            with patch.object(ap.time,'monotonic',return_value=12):fresh.setup_grid(4,bad)
            self.assertFalse(any(g['input_ready'] for g in fresh.grid.values()))

    def test_partial_header_new_layout_backlog_last_ball_and_close(self):
        d=live.Device();c=controller();c.special_observed=set();c.a.dry=False
        base=measured();attempts=[]
        def submit(fn):
            f=Future();f.set_result(fn());return f
        c.input_pool=SimpleNamespace(submit=submit)
        process=SimpleNamespace(communicate=lambda **kw:None,returncode=0)
        def sample(now,det):
            with patch.object(ap.time,'monotonic',return_value=now):
                c.foreground_at=now;c.setup_grid(4,d.calibrated_grid(det));c.backfill()
        def drain(now):
            for step in range(12):
                with patch.object(ap.time,'monotonic',return_value=now+step*.02),patch.object(ap,'spawn_tap',return_value=process):
                    c.tick([])
                    q=c.input_target
                    if q and (q['slot'],q['c']*5+q['r']) not in attempts:
                        attempts.append((q['slot'],q['c']*5+q['r']))
                        sent=c.dispatch_times[(q['slot'],q['r'],q['c'])]
                        self.assertTrue(c.accept_client_mark(dict(round_id=c.rid,card_id=q['slot'],
                          cell_index=q['c']*5+q['r'],ball=q['ball'],daub_type='Manual',
                          at_ns=sent+1,host_interval_ns=[sent+1,sent+2],source_ref={'synthetic':True})))
        for t in range(10,16):sample(t,base)
        # One missing header pauses only that card. A called target stays pending.
        sample(16,base[1:])
        self.assertFalse(c.grid[1]['input_ready']);self.assertTrue(all(c.grid[i]['input_ready'] for i in (2,3,4)))
        with patch.object(ap.time,'monotonic',return_value=14):c.on_ball('',c.rid,1)
        drain(16);self.assertEqual({s for s,k in attempts},{2,3,4})
        changed=copy.deepcopy(base)
        for key in ('header_top','header_bottom'):changed[0][key]+=8
        changed[0]['rows']=[v+8 for v in changed[0]['rows']]
        changed[0]['cell_geometry']['rows']=[v+8 for v in changed[0]['cell_geometry']['rows']]
        for t in range(17,23):sample(t,changed)
        self.assertTrue(c.grid[1]['input_ready']);self.assertEqual(c.grid[1]['rows'][0],508)
        drain(22);self.assertIn((1,0),attempts) # Original unattempted target recovered.
        with patch.object(ap.time,'monotonic',return_value=22):c.on_ball('',c.rid,2)
        sample(24,changed);drain(24)
        self.assertEqual(len(c.done),8);self.assertEqual(len(attempts),8)
        with patch.object(ap.time,'monotonic',return_value=25):
            c.close_round(c.rid,verified=True);c.on_ball('',c.rid,3)
            with patch.object(ap,'spawn_tap') as send:c.tick([]);send.assert_not_called()
        self.assertTrue(c.closed);self.assertFalse(c.pending)

    def test_hidden_cell_and_peer_revision_cancel_only_affected_input(self):
        from test_review_r1 import Dispatch
        c=Dispatch().queued();slot=c.input_target['slot'];peer=2 if slot!=2 else 3
        c.grid[peer]['version']+=1
        p=SimpleNamespace(communicate=lambda **kw:None,returncode=0)
        with patch.object(ap.time,'monotonic',return_value=12),patch.object(ap,'spawn_tap',return_value=p) as send:
            self.assertEqual(c.input_pool.fn(),'executed');send.assert_called_once()
        c=Dispatch().queued();slot=c.input_target['slot'];c.grid[slot]['reachable_cells']=[]
        with patch.object(ap.time,'monotonic',return_value=12),patch.object(ap,'spawn_tap') as send:
            self.assertEqual(c.input_pool.fn(),'cancelled');send.assert_not_called()
