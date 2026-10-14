"""Prospective host/device brackets shared by control and independent replay."""
import time

TTL_NS = 45_000_000_000
MAX_ERROR_NS = 500_000_000


def validate(sample, previous=None):
    a,b=sample['host_before_ns'],sample['host_after_ns']
    ma,mb=sample['mono_before_ns'],sample['mono_after_ns']
    if not 0 <= b-a <= MAX_ERROR_NS or abs((b-a)-(mb-ma))>50_000_000:
        raise ValueError('host_clock_jump_or_slow_sample')
    if not sample.get('boot_id') or sample['device_ns']<=0:raise ValueError('device_epoch_missing')
    if previous:
        if sample['boot_id']!=previous['boot_id']:raise ValueError('device_epoch_changed')
        host_delta=a-previous['host_before_ns'];mono_delta=ma-previous['mono_before_ns']
        if abs(host_delta-mono_delta)>50_000_000:raise ValueError('host_clock_jump')
        device_delta=sample['device_ns']-previous['device_ns']
        if abs(device_delta-mono_delta)>MAX_ERROR_NS:raise ValueError('device_clock_jump')
    return sample


def interval(event_ns, samples):
    # No extrapolation to historical rounds: only prospective samples within TTL.
    choices=[s for s in samples if 0<=event_ns-s['device_ns']<=TTL_NS]
    if not choices:raise ValueError('clock_evidence_not_current')
    brackets=[]
    for s in choices:
        validate(s)
        # Intersect only already-taken brackets, with each bracket's full error.
        # No future sample, midpoint guess, or widening of the match window.
        error=1_000_000+int((event_ns-s['device_ns'])*.00005)
        brackets.append((event_ns+s['host_before_ns']-s['device_ns']-error,
                         event_ns+s['host_after_ns']-s['device_ns']+error))
    lo=max(a for a,b in brackets);hi=min(b for a,b in brackets)
    if lo>hi:raise ValueError('clock_brackets_disagree')
    return [lo,hi]


def matched(event, sent_ns, window_ns=10_000_000_000):
    lo,hi=event.get('host_interval_ns',[event['at_ns'],event['at_ns']])
    return sent_ns<=lo<=hi<=sent_ns+window_ns


def observe(event, samples):
    result=dict(event)
    result['host_interval_ns']=interval(event['at_ns'],samples)
    return result
