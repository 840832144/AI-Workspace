"""Bounded, approved passive observer preparation. Never authorizes a purchase.

Only the original game PID is attached. Metadata and natural callback fields are
controlled evidence, not a validated PanelQuote. No root/policy/collector changes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

HELPER_SHA256='d27e9eba721e623e6b39186f98cf9f03f77be5ac0e3870edb158db62e24318eb'
EMULATED_BINDING_STOP='emulated_binding_stopped_load_failure_and_unload_unavailable'


def require_emulated_binding():
    """This binding is stopped after three load failures and the unload audit.

    Frida 16.7.19 leaves a successfully loaded emulated agent resident. Script
    unload/detach is not library unload. No runtime flag re-enables this binding;
    a compatible implementation with a reviewed lifecycle must replace it.
    """
    raise RuntimeError(EMULATED_BINDING_STOP)


def prepare_helper(source, destination):
    """Disable Frida 16.7.19's automatic Android SELinux policy patch.

    Upstream patch.c returns before policy reads/writes when system_policy does
    not exist. /dev/null is verified to be a character device before execution,
    so a child path cannot exist. This changes only the local helper's constant,
    not the game, kernel, SELinux policy, authentication, or enforcement state.
    The official original remains intact. Other helper versions are unsupported.
    """
    data=Path(source).read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    old=b'/sys/fs/selinux/policy\0'
    new=b'/dev/null/'+b'x'*(len(old)-11)+b'\0'
    if (data[:4]!=b'\x7fELF' or data[4:6]!=b'\x02\x01'
            or data[18:20]!=b'\x3e\x00' or data.count(old)!=1
            or b'16.7.19' not in data or digest!=HELPER_SHA256):
        raise ValueError('unsupported_helper_image')
    assert len(old)==len(new)
    at=data.index(old);patched=data[:at]+new+data[at+len(old):]
    Path(destination).write_bytes(patched)
    return dict(version='16.7.19',changed_offset=at,changed_size=len(old),
                before_sha256=digest,
                after_sha256=hashlib.sha256(patched).hexdigest(),
                policy_patch_disabled=True)


def worker(address,pid,output,seconds,bridge_diagnostic=False):
    require_emulated_binding()
    import frida
    import threading
    events=Path(output)/'observations.jsonl'
    session=None;script=None;native_session=None;bridge_script=None
    failed=threading.Event();ready_at=[]
    def write(row):
        with events.open('a',encoding='utf-8') as f:
            f.write(json.dumps(dict(row,received_mono=time.monotonic(),received_ns=time.time_ns()))+'\n')
            f.flush()
    try:
        write(dict(type='worker_phase',phase='connecting'))
        device=frida.get_device_manager().add_remote_device(address)
        if bridge_diagnostic:
            native_session=device.attach(pid,persist_timeout=0)
            bridge_script=native_session.create_script(Path(__file__).with_name('bv_observer_bridge.js').read_text(encoding='utf-8'))
            bridge_script.on('message',lambda message,data:write(message))
            bridge_script.load()
        write(dict(type='worker_phase',phase='attaching_emulated'))
        session=device.attach(pid,realm='emulated',persist_timeout=0)
        write(dict(type='worker_phase',phase='attached'))
        script=session.create_script(Path(__file__).with_suffix('.js').read_text(encoding='utf-8'))
        def message_received(message,data):
            write(message)
            payload=message.get('payload',{})
            if message.get('type')=='error' or payload.get('kind') in ('observer_error','observation_error'):failed.set()
            if payload.get('kind')=='observer_ready':ready_at.append(time.monotonic())
        script.on('message',message_received)
        session.on('detached',lambda reason,crash:write(dict(type='detached',reason=reason)))
        script.load()
        end=time.monotonic()+seconds
        while time.monotonic()<end and not failed.is_set() and not (Path(output)/'STOP').exists():
            if ready_at and time.monotonic()-ready_at[0]>=1:break
            time.sleep(.05)
    except Exception as exc:
        write(dict(type='worker_error',error=type(exc).__name__+':'+str(exc)))
        if bridge_script:
            try:write(dict(type='bridge_status',status=bridge_script.exports_sync.status()))
            except Exception as detail:write(dict(type='bridge_status_error',error=str(detail)))
    finally:
        if script:
            try:script.exports_sync.stop();script.unload()
            except Exception as exc:write(dict(type='unload_error',error=type(exc).__name__))
        if session:
            try:session.detach()
            except Exception as exc:write(dict(type='detach_error',error=type(exc).__name__))
        if bridge_script:
            try:bridge_script.exports_sync.stop();bridge_script.unload()
            except Exception as exc:write(dict(type='bridge_unload_error',error=type(exc).__name__))
        if native_session:
            try:native_session.detach()
            except Exception as exc:write(dict(type='native_detach_error',error=type(exc).__name__))


def inspect(helper,output,seconds=12,bridge_diagnostic=False):
    require_emulated_binding()
    from bv_live import Budget,LIMITS,BATCH_ROUNDS,BATCH_CLEANUP_SECONDS,PACKAGE
    from bv_autoplay import ADB,DEV
    if not 1<=seconds<=15:raise ValueError('bounded_inspection_required')
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    # Bind future observations to the exact observer source, including WIP code.
    for name in ('bv_observer.py','bv_observer.js','bv_observer_bridge.js'):
        (out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    prepared=out/'observer-helper'
    manifest=prepare_helper(helper,prepared)
    (out/'helper.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    ledger=Budget();margin=LIMITS['total_seconds']-ledger.elapsed()-BATCH_ROUNDS*LIMITS['round_seconds']-BATCH_CLEANUP_SECONDS
    if margin<seconds+5:raise ValueError('insufficient_preparation_margin')
    adb=[ADB,'-s',DEV];token='task0039_'+uuid.uuid4().hex
    remote='/data/local/tmp/'+token
    started=time.monotonic();deadline=started+seconds;port=None;proc=None
    result=dict(status='Insufficient evidence',purchase_inputs=0,policy_patch_disabled=True)
    ledger.append('runtime_start',session_id=token)
    def run(args,timeout=2,check=True):
        return subprocess.run(adb+args,capture_output=True,text=True,timeout=timeout,check=check)
    def remaining():return max(.05,deadline-time.monotonic())
    try:
        before=run(['shell',f'test -c /dev/null && id -u && getenforce && sha256sum /sys/fs/selinux/policy && pidof {PACKAGE}'])
        lines=before.stdout.strip().splitlines()
        if len(lines)!=4 or lines[0]!='0' or not re.fullmatch(r'\d+',lines[3]):raise ValueError('original_environment_unavailable')
        pid=int(lines[3]);result['game_pid']=pid;result['environment_before']=lines[:3]
        stat=run(['shell','cat',f'/proc/{pid}/stat'],timeout=min(2,remaining())).stdout
        result['process_start_ticks']=int(stat.rsplit(')',1)[1].split()[19])
        run(['push',str(prepared),remote],timeout=min(4,remaining()))
        # Unix abstract socket only. No device TCP listener or network policy change.
        # Android's shell may retain the ADB channel for a background job. Use
        # the helper's own daemon readiness handshake, not shell job control.
        run(['shell',f'chmod 700 {remote} && {remote} -D -P -C -l unix:{token} >{remote}.log 2>&1'],timeout=min(3,remaining()))
        port=int(run(['forward','tcp:0','localabstract:'+token],timeout=min(2,remaining())).stdout.strip())
        proc=subprocess.Popen([sys.executable,'-X','utf8',str(out/'bv_observer.py'),
                               '--worker','127.0.0.1:'+str(port),'--pid',str(pid),'--output',str(out),
                               '--seconds',str(max(1,remaining()-1))]+(['--bridge-diagnostic'] if bridge_diagnostic else []),
                              stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                              creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        while proc.poll() is None and time.monotonic()<deadline and not (out/'STOP').exists():time.sleep(.05)
        if proc.poll() is None:
            (out/'STOP').touch()
            try:proc.wait(timeout=.3)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=1)
        result['worker_exit']=proc.returncode
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        result['error']=type(exc).__name__+':'+str(exc)
    finally:
        if proc is not None and proc.poll() is None:proc.terminate();proc.wait(timeout=1)
        # Kill only our exact helper executable; never a game or existing collector.
        try:
            cleanup=run(['shell',f'for p in $(pidof {token}); do test "$(readlink /proc/$p/exe)" = "{remote}" && kill "$p"; done; '
                         'sleep 0.1; '
                         f'cat {remote}.log 2>/dev/null; rm -f {remote} {remote}.log; '
                         f'getenforce; sha256sum /sys/fs/selinux/policy; pidof {PACKAGE}; '
                         f'if pidof {token}; then echo HELPER_STILL_RUNNING; else echo HELPER_STOPPED; fi'],check=False)
            (out/'cleanup.txt').write_text(cleanup.stdout+cleanup.stderr,encoding='utf-8')
            after=cleanup.stdout.strip().splitlines()
            result['environment_after']=after
            result['helper_stopped']=bool(after and after[-1]=='HELPER_STOPPED')
            result['policy_unchanged']=result['helper_stopped'] and result.get('environment_before',[None]*3)[1:]==after[-4:-2]
            result['game_alive']=result['helper_stopped'] and after[-2]==str(result.get('game_pid'))
        except (OSError,subprocess.SubprocessError) as exc:result['cleanup_error']=str(exc)
        if port:
            try:run(['forward','--remove','tcp:'+str(port)])
            except (OSError,subprocess.SubprocessError) as exc:result['forward_cleanup_error']=str(exc)
        elapsed=time.monotonic()-started
        if result.get('helper_stopped'):
            ledger.append('runtime_end',session_id=token,seconds=elapsed)
        else:
            # Never stop billing an observer whose termination is unconfirmed.
            result['cleanup_error']=result.get('cleanup_error','helper_stop_unconfirmed')
            result['runtime_session_open']=token
        result.update(seconds=elapsed,task_seconds=ledger.elapsed(),gross_tickets=ledger.gross())
        result.update(summarize_observations(out))
        (out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def summarize_observations(folder):
    path=Path(folder)/'observations.jsonl'
    rows=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()] if path.exists() else []
    payloads=[row.get('payload',{}) for row in rows]
    ready=any(row.get('kind')=='observer_ready' for row in payloads)
    callbacks=sum(row.get('kind')=='natural_callback' for row in payloads)
    errors=[row['error'] for row in rows if row.get('error')]
    errors += [row['error'] for row in payloads if row.get('error')]
    return dict(observer_ready=ready,natural_callbacks=callbacks,observer_errors=errors,
                run_ready=False,quote_source_available=False,
                status='Observed candidates only' if ready and callbacks and not errors else 'Insufficient evidence')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--helper');p.add_argument('--output',required=True)
    p.add_argument('--seconds',type=float,default=12);p.add_argument('--worker');p.add_argument('--pid',type=int)
    p.add_argument('--bridge-diagnostic',action='store_true')
    a=p.parse_args()
    try:require_emulated_binding()
    except RuntimeError as exc:
        print(json.dumps(dict(status='Stopped binding',error=str(exc),run_ready=False,
                              quote_source_available=False,purchase_inputs=0)))
        sys.exit(2)
    if a.worker:worker(a.worker,a.pid,a.output,a.seconds,a.bridge_diagnostic)
    elif a.helper:
        print(json.dumps(inspect(a.helper,a.output,a.seconds,a.bridge_diagnostic),indent=2))
        sys.exit(2) # Candidate observation never implies purchase readiness.
    else:p.error('--helper is required')
