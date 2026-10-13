"""已知卡面号码，在所有帧里搜包含该 varint 子序列的帧 —— 定位卡面下发路径。"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\BingoVoyageProbe")
import bv_ws2
from bv_proto import parse  # noqa

# s61 屏幕卡 A 的 B 列（cmd 166 的下发顺序 = 列序 B5 开头）
NEEDLE = [12, 23, 33, 54, 72]


def all_varints(b, depth=0, out=None):
    if out is None:
        out = []
    if depth > 8:
        return out
    for fld, wt, val, ch in parse(b):
        if fld is None:
            continue
        if wt == 0:
            out.append(val)
        elif wt == 2 and ch is not None:
            all_varints(ch, depth + 1, out)
    return out


def find_subseq(seq, needle):
    n, m = len(seq), len(needle)
    for i in range(n - m + 1):
        if seq[i:i + m] == needle:
            return i
    # 放宽：只要 needle 前 3 个按序出现
    idx = []
    j = 0
    for k, v in enumerate(seq):
        if j < 3 and v == needle[j]:
            idx.append(k); j += 1
    return idx[0] if j == 3 else None


def main():
    recs = bv_ws2.load()
    print("扫描 %d 帧，needle=%s" % (len(recs), NEEDLE))
    n = 0
    for r in recs:
        f = r["f"]
        if not f.get("ok") or not f["body"]:
            continue
        vs = all_varints(f["body"])
        pos = find_subseq(vs, NEEDLE)
        if pos is None:
            continue
        n += 1
        print("  %s %s cmd=%-4d %6dB  pos=%s  %s" % (
            r["ts"], r["dir"], f["cmd"], len(f["body"]), pos,
            vs[max(0, pos):pos + 30]))
    print("\n命中 %d 帧" % n)


if __name__ == "__main__":
    main()
