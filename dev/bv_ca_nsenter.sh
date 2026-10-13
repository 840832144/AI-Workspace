#!/system/bin/sh
# Android 14+ 系统 CA：apex 里的信任库在 zygote/应用进程各自的 mount namespace，
# 必须 nsenter 进去逐个 bind-mount，只挂全局命名空间应用看不到。
MNT=/data/local/tmp/cacerts
PKG=com.bingo.cruise.free.best.top.game
echo "== 目标目录内容 =="
ls "$MNT" | wc -l

PIDS=""
for n in zygote64 zygote zygote_secondary; do
  for p in $(pidof $n 2>/dev/null); do PIDS="$PIDS $p"; done
done
for p in $(pidof $PKG 2>/dev/null); do PIDS="$PIDS $p"; done
echo "== 进程 ==" $PIDS

for p in $PIDS; do
  for REAL in /apex/com.android.conscrypt/cacerts /system/etc/security/cacerts; do
    nsenter --mount=/proc/$p/ns/mnt -- mount --bind "$MNT" "$REAL" 2>/dev/null \
      && echo "OK   pid=$p $REAL" || echo "skip pid=$p $REAL"
  done
done

echo "== 验证（游戏进程视角）=="
for p in $(pidof $PKG 2>/dev/null); do
  echo -n "pid=$p apex certs: "
  nsenter --mount=/proc/$p/ns/mnt -- ls /apex/com.android.conscrypt/cacerts 2>/dev/null | wc -l
done
