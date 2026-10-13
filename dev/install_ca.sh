#!/system/bin/sh
# 在 /system/etc/security/cacerts 上做 bind-mount，装入 mitmproxy 系统级 CA。
# 需要 root。可逆：sh uninstall_ca.sh
set -e

MNT=/data/local/tmp/cacerts
REAL=/system/etc/security/cacerts
CA=/data/local/tmp/c8750f0d.0

echo "== 1. 准备目录 =="
umount "$REAL" 2>/dev/null || true
rm -rf "$MNT"
mkdir -p "$MNT"
cp "$REAL"/* "$MNT"/ 2>/dev/null || true
echo "copied: $(ls "$MNT" | wc -l) certs"

echo "== 2. 放入 mitmproxy CA =="
cp "$CA" "$MNT/c8750f0d.0"
chmod 644 "$MNT"/*.0
chown 0:0 "$MNT"/*.0
chcon u:object_r:system_security_cacerts_file:s0 "$MNT"/*.0 2>/dev/null || echo "(chcon skipped)"
echo "total now: $(ls "$MNT" | wc -l)"

echo "== 3. bind-mount 覆盖 =="
mount --bind "$MNT" "$REAL"
ls -la "$REAL/c8750f0d.0"
echo "certs visible in system store: $(ls "$REAL" | wc -l)"

echo "== 4. 验证 =="
if [ -f "$REAL/c8750f0d.0" ]; then echo "OK: mitmproxy CA is in system store"; else echo "FAIL"; exit 1; fi
