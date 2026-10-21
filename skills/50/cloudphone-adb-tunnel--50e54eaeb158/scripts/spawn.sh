#!/data/data/com.termux/files/usr/bin/bash
# 经 termux-chroot 拉起 frpc: chroot 内 /etc/resolv.conf = $PREFIX/etc/resolv.conf
cd "$HOME/frp" || exit 1
if ! command -v termux-chroot >/dev/null 2>&1; then
  echo "[$(date '+%F %T')] termux-chroot 缺失 (pkg install proot)，本轮跳过"
  exit 1
fi
[ -f frpc.pid ] && kill "$(cat frpc.pid 2>/dev/null)" 2>/dev/null
if command -v pkill >/dev/null 2>&1; then
  pkill -f "frp/frpc" 2>/dev/null
else
  for p in $(ps -A 2>/dev/null | awk '/[f]rpc/{print $1}'); do kill "$p" 2>/dev/null; done
fi
sleep 1
[ -f logs/frpc.log ] && mv -f logs/frpc.log logs/frpc.log.1
termux-chroot "$HOME/frp/frpc" -c "$HOME/frp/frpc.toml" >> logs/frpc.log 2>&1 &
sleep 1
# frpc.pid 取真实 frpc 进程 (proot exec 后 pgrep 可见); pgrep 缺失/未捕获时退回包装进程 PID
echo "$(pgrep -nf "frp/frpc" 2>/dev/null || echo $!)" > frpc.pid
echo "[$(date '+%F %T')] frpc 已拉起 (termux-chroot)"
