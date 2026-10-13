#!/system/bin/sh
# 把游戏「绕过系统代理」的所有出站 443 直连 REDIRECT 到本地 9443，
# 由宿主 bv_bridge_sni.py 按 SNI 送进 mitmproxy。
# 只劫持 443；去 127.0.0.0/8 的（即系统代理 8099 与 adb reverse）不动。
set -e
BRIDGE_PORT=9443

echo "== 清理旧规则 =="
sh /data/local/tmp/teardown_redirect.sh 2>/dev/null || true

echo "== 添加 REDIRECT（出站 443 -> :$BRIDGE_PORT，排除 127/8）=="
iptables -t nat -A OUTPUT -p tcp --dport 443 ! -d 127.0.0.0/8 \
  -j REDIRECT --to-ports $BRIDGE_PORT

echo "== 当前 nat OUTPUT =="
iptables -t nat -L OUTPUT -n -v --line-numbers
echo "OK  出站 443 已劫持到 :$BRIDGE_PORT"
