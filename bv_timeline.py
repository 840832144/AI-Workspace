"""按时间轴列出客户端动作（C->S）与服务端关键回应，用于与手动操作对齐。"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
import bv_ws2
from bv_proto import parse, try_str  # noqa

# 服务端推送里值得看的命令
SERVER_INTEREST = {2, 167, 168, 169, 171, 202, 203, 227, 78, 146, 158}


def brief(b, depth=0):
    out = []
    for fld, wt, val, ch in parse(b):
        if fld is None:
            continue
        if wt == 0:
            out.append("%d=%s" % (fld, val))
        elif wt == 2:
            s = try_str(ch) if ch is not None else None
            if s is not None:
                out.append('%d="%s"' % (fld, s[:60]))
            else:
                inner = []
                if isinstance(val, int) and val > 1 and ch and depth < 2:
                    inner = brief(ch, depth + 1)
                out.append("%d={%s}" % (fld, ",".join(inner[:7])))
        elif wt == 5:
            out.append("%d=f32" % fld)
        elif wt == 1:
            out.append("%d=f64" % fld)
    return out


def main():
    since = sys.argv[1] if len(sys.argv) > 1 else "2026-10-13 00:44"
    side = sys.argv[2] if len(sys.argv) > 2 else "both"
    recs = bv_ws2.load()
    for r in recs:
        f = r["f"]
        if not f.get("ok") or r["ts"] < since:
            continue
        cs = r["dir"] == "C->S"
        if side == "cs" and not cs:
            continue
        if side == "sc" and cs:
            continue
        if not cs and f["cmd"] not in SERVER_INTEREST:
            continue
        body = " ; ".join(brief(f["body"]))[:150]
        print("%s %s cmd=%-4d topic=%-40s %4dB  %s" % (
            r["ts"], "C->S" if cs else "S->C", f["cmd"],
            f["topic"][:40], len(f["body"]), body))


if __name__ == "__main__":
    main()
