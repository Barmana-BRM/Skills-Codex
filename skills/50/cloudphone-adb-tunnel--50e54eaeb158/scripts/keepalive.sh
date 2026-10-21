#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock 2>/dev/null
mkdir -p "$HOME/frp/logs"
while true; do
    KL="$HOME/frp/logs/keepalive.log"
    [ -f "$KL" ] && [ "$(wc -c < "$KL" 2>/dev/null || echo 0)" -gt 1048576 ] && mv -f "$KL" "$KL.1"
    if command -v pgrep >/dev/null 2>&1; then
        pgrep -f "frp/frpc" >/dev/null 2>&1 || "$HOME/frp/spawn.sh" >> "$HOME/frp/logs/keepalive.log" 2>&1
    elif ! ps -A 2>/dev/null | grep -q "[f]rpc"; then
        "$HOME/frp/spawn.sh" >> "$HOME/frp/logs/keepalive.log" 2>&1
    fi
    sleep 15
done
