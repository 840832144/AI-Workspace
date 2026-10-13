#!/system/bin/sh
# 撤销 install_ca.sh 的 bind-mount，恢复原始 cacerts
REAL=/system/etc/security/cacerts
MNT=/data/local/tmp/cacerts
umount "$REAL" 2>/dev/null && echo "unmounted $REAL" || echo "not mounted"
rm -rf "$MNT"
echo "restored: $(ls "$REAL" | wc -l) certs"
ls "$REAL/c8750f0d.0" 2>/dev/null && echo "WARN: CA still present" || echo "OK: mitmproxy CA removed"
