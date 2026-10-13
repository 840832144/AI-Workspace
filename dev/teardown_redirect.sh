#!/system/bin/sh
# 撤销 setup_redirect.sh 的 iptables 规则
iptables -t nat -D OUTPUT -p tcp --dport 443 ! -d 127.0.0.0/8 -j REDIRECT --to-ports 9443 2>/dev/null || true
iptables -t nat -D OUTPUT -p tcp -d 13.248.218.74 --dport 443 -j REDIRECT --to-ports 9443 2>/dev/null || true
iptables -t nat -D OUTPUT -p tcp -d 76.223.79.30  --dport 443 -j REDIRECT --to-ports 9443 2>/dev/null || true
echo "== 剩余 nat OUTPUT =="
iptables -t nat -L OUTPUT -n --line-numbers
echo "redirect rules removed"
