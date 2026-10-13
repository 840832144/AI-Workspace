#!/system/bin/sh
# 修 Android 14+ 的 CA：应用命名空间里的 apex 挂载可能残留成空目录，
# 必须先在该命名空间内 umount 再重新 bind，否则 mount 会 "skip" 且应用看到 0 个证书。
MNT=/data/local/tmp/cacerts
PKG=com.bingo.cruise.free.best.top.game

# 1) 重建全局的 CA 目录（从真实 cacerts 拷贝 + 我们的 CA）
if [ ! -f "$MNT/bv_ca.0" ] || [ "$(ls $MNT | wc -l)" -lt 100 ]; then
  umount /apex/com.android.conscrypt/cacerts 2>/dev/null
  rm -rf "$MNT"; mkdir -p "$MNT"
  cp /apex/com.android.conscrypt/cacerts/* "$MNT"/ 2>/dev/null
  cp /data/local/tmp/bv_ca.0 "$MNT"/ 2>/dev/null
  chmod 644 "$MNT"/*.0; chown 0:0 "$MNT"/*.0
  chcon u:object_r:system_security_cacerts_file:s0 "$MNT"/*.0 2>/dev/null
  mount --bind "$MNT" /apex/com.android.conscrypt/cacerts 2>/dev/null
fi
echo "全局 MNT 证书数: $(ls $MNT | wc -l)"

# 2) 逐进程命名空间修复：先 umount 再 bind
PIDS=""
for n in zygote64 zygote; do
  for p in $(pidof $n 2>/dev/null); do PIDS="$PIDS $p"; done
done
for p in $(pidof $PKG 2>/dev/null); do PIDS="$PIDS $p"; done

for p in $PIDS; do
  nsenter --mount=/proc/$p/ns/mnt -- umount -l /apex/com.android.conscrypt/cacerts 2>/dev/null
  nsenter --mount=/proc/$p/ns/mnt -- umount -l /system/etc/security/cacerts 2>/dev/null
  nsenter --mount=/proc/$p/ns/mnt -- mount --bind "$MNT" /apex/com.android.conscrypt/cacerts 2>/dev/null \
    && echo "OK pid=$p" || echo "FAIL pid=$p"
done

echo "== 验证 =="
for p in $(pidof $PKG 2>/dev/null); do
  echo "游戏 pid=$p apex certs: $(nsenter --mount=/proc/$p/ns/mnt -- ls /apex/com.android.conscrypt/cacerts 2>/dev/null | wc -l)"
done
