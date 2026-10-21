#!/data/data/com.termux/files/usr/bin/bash
# ══════════════════════════════════════════════════════════
#  云手机 ADB 隧道一键部署 · Termux v10 (FRP STCP)
#
#  用法: bash install-termux.sh   (或整块粘贴进 Termux 回车)
#  幂等: 可重复执行, 失败重跑即可
#  下载源: GitHub 官方/镜像优先, 全部失败时回落自建 CDN (CF 边缘缓存兜底)
#
#  【DNS 方案】frpc 为 Go 静态二进制, 只认 /etc/resolv.conf;
#  Android 无此文件会回退查 [::1]:53 被拒。本脚本把 nameserver
#  写入 $PREFIX/etc/resolv.conf, 并经 termux-chroot(proot) 拉起
#  frpc —— chroot 内 /etc 即 $PREFIX/etc, Go 解析器因此读得到。
#  【临时目录】Termux 无根目录 /tmp, 统一用 ~/frp/tmp
#  【入口格式】支持 域名 / IP / IP:端口 / http://IP:端口/ (IPv6 字面量暂不支持)
#  【分享版】连接信息三项 (入口/token/secretKey) 运行时手动输入,
#  脚本本体不含任何私人信息; frpc 二进制官方源优先, 全失败时回落公共 CDN。
#  分享方式: 把连接信息单独发给对方, 脚本本体可直接给下载链接:
#  https://download.mangoqwq.com/pub/install-termux.sh
# ══════════════════════════════════════════════════════════

# ──────────── 配置区 (分享前清空下面的值!) ────────────
SERVER_URL="${SERVER_URL:-}"
FRPS_TOKEN="${FRPS_TOKEN:-}"
STCP_SK="${STCP_SK:-}"
# 自建下载源 (官方源全失败时的兜底; CF 边缘缓存直发 frpc 二进制)
PUB_MIRROR="${PUB_MIRROR:-https://download.mangoqwq.com/pub/frpc-0.71.0-linux-arm64}"
# 电脑端 visitor 本地绑定端口 (单一定义源: 下方模板与连接命令都引用它)
# 默认 55556: 部分 Mac 上 55555 被隐形 root 进程占用(报 bind in use); 新机器空闲可改回 55555
VISITOR_BIND_PORT="${VISITOR_BIND_PORT:-55556}"
# frps 通信端口默认值 (SERVER_URL 未带端口时使用)
SERVER_PORT_DEFAULT=48721
# ─────────────────────────────────────────────────────

set -o pipefail
if [ -z "$SERVER_URL" ]; then read -r -p "frps 服务器地址(域名/IP[:端口]): " SERVER_URL; fi
if [ -z "$FRPS_TOKEN" ]; then read -r -p "frps auth token: " FRPS_TOKEN; fi
if [ -z "$STCP_SK" ]; then read -r -p "STCP secretKey: " STCP_SK; fi

# 0. 智能解析入口: 剥离协议头与路径, 识别自定义端口
PARSED_ADDR="${SERVER_URL#*://}"; PARSED_ADDR="${PARSED_ADDR%%/*}"
if [[ "$PARSED_ADDR" == *:* ]]; then
  SERVER_PORT="${PARSED_ADDR##*:}"; SERVER_ADDR="${PARSED_ADDR%:*}"
else
  SERVER_PORT="$SERVER_PORT_DEFAULT"; SERVER_ADDR="$PARSED_ADDR"
fi
[ -z "$SERVER_PORT" ] && SERVER_PORT="$SERVER_PORT_DEFAULT"

G='\033[32m'; R='\033[31m'; Y='\033[33m'; C='\033[36m'; B='\033[1m'; D='\033[2m'; N='\033[0m'
SPINNER='|/-\'; _s=0; STEP=0; TOTAL=5

step()  { STEP=$((STEP+1)); printf "\n${B}${C}[%d/%d]${N} ${B}%s${N}\n" "$STEP" "$TOTAL" "$1"; }
ok()    { printf "  ${G}✔${N} %s\n" "$1"; }
warn()  { printf "  ${Y}!${N} %s\n" "$1"; }
die()   { printf "\n${R}${B}==== [FAIL] %s ====${N}\n" "$1"; [ -n "$2" ] && tail -12 "$2" 2>/dev/null; exit 1; }
human() { local b=$1; if [ "$b" -ge 1048576 ]; then printf "%d.%dMB" $((b/1048576)) $(( (b%1048576)*10/1048576 )); elif [ "$b" -ge 1024 ]; then printf "%dKB" $((b/1024)); else printf "%dB" "$b"; fi; }
bar()   { local f=$(( $1 * ${2:-26} / 100 )) s="" i; for ((i=0;i<${2:-26};i++)); do if (( i<f )); then s+="█"; else s+="░"; fi; done; printf "%s" "$s"; }

# ── 输入校验: 空值/非法字符尽早失败, 不拖到 40s 健康检查之后 ──
case "$SERVER_ADDR" in
  ""|*[!A-Za-z0-9._-]*) die "服务器入口无效: \"${SERVER_ADDR}\" (仅支持 域名/IP[:端口], IPv6 字面量暂不支持)" ;;
esac
case "$SERVER_PORT" in
  ""|*[!0-9]*) die "端口无效: \"${SERVER_PORT}\"" ;;
esac
for pair in "token:$FRPS_TOKEN" "secretKey:$STCP_SK"; do
  label="${pair%%:*}"; val="${pair#*:}"
  case "$val" in
    ""|*'"'*|*"\\"*|*' '*|*$'\t'*|*$'\n'*) die "$label 不能为空, 且不得含引号/反斜杠/空白 (将写入 TOML)" ;;
  esac
done

TMPD="$HOME/frp/tmp"
trap 'rm -rf "$TMPD" 2>/dev/null' EXIT

FRPC_SHA="6e8e45fd0c7514b636fd8d049212f8a5715e8b33c412cf968988252e7a8a00f2"
BASE="https://github.com/fatedier/frp/releases/download/v0.71.0/frp_0.71.0_linux_arm64.tar.gz"
# 源格式: 名称|URL|模式(bin=裸二进制 / tar=官方压缩包)
# 顺序: GitHub 官方/镜像优先, 自建 CDN 放最后兜底 (被 DNS 污染/墙困住时才动用)
SOURCES+=(
  "GitHub 官方|${BASE}|tar"
  "镜像 ghfast.top|https://ghfast.top/${BASE}|tar"
  "镜像 ghproxy.net|https://ghproxy.net/${BASE}|tar"
  "镜像 gh-proxy.com|https://gh-proxy.com/${BASE}|tar"
)
[ -n "$PUB_MIRROR" ] && SOURCES+=("下载站 CDN(兜底)|${PUB_MIRROR}|bin")

download() { # $1=url $2=dest
  local len rc cur pct; rm -f "$2"
  len=$(curl -sIL --connect-timeout 8 "$1" | tr -d '\r' | awk 'tolower($1)=="content-length:"{s=$2} END{print s}')
  # --speed-limit/-time: 15s 内均速 <1KB/s 判定卡死, 中止后换下一个源
  curl -fsSL --connect-timeout 8 --retry 1 --speed-limit 1024 --speed-time 15 -o "$2" "$1" & local pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    cur=$(wc -c < "$2" 2>/dev/null); cur=${cur:-0}
    if [ -n "$len" ] && [ "$len" -gt 0 ] 2>/dev/null; then
      pct=$(( cur>len ? 100 : cur*100/len ))
      printf "\r  ${C}%s${N} ${B}%3d%%${N}  %s / %s   " "$(bar $pct)" "$pct" "$(human $cur)" "$(human $len)"
    else
      _s=$(( (_s+1)%4 )); printf "\r  ${C}%s${N} 已下载 %s   " "${SPINNER:_s:1}" "$(human $cur)"
    fi
    sleep 0.3
  done
  wait "$pid" 2>/dev/null; rc=$?
  [ "$rc" -eq 0 ] && [ -s "$2" ] || { printf "\r  ${R}✗ 下载失败，切换下一个源…%s\n" "            "; return 1; }
  return 0
}

fetch() { # $1="名称|URL|模式"
  local pair="$1" name url mode u dest
  name="${pair%%|*}"; u="${pair#*|}"; mode="${u##*|}"; url="${u%|*}"
  rm -rf "$TMPD"; mkdir -p "$TMPD"
  dest="$TMPD/frpc-dl"; [ "$mode" = "tar" ] && dest="$TMPD/frp.tgz"
  download "$url" "$dest" || return 1
  if [ "$mode" = "tar" ]; then
    tar xzf "$TMPD/frp.tgz" -C "$TMPD" 2>/dev/null && cp "$TMPD"/frp_*_linux_arm64/frpc "$TMPD/frpc-dl" \
      || { printf "\r  ${R}✗ %s 解压失败%s\n" "$name" "            "; return 1; }
  fi
  echo "${FRPC_SHA}  $TMPD/frpc-dl" | sha256sum -c - >/dev/null 2>&1 \
    || { printf "\r  ${R}✗ %s 文件校验不符（疑似劫持/损坏），换源…%s\n" "$name" "        "; return 1; }
  printf "\r  ${G}✔ ${name} 校验通过 (%s)%s\n" "$(human $(wc -c < "$TMPD/frpc-dl"))" "                    "
  return 0
}

printf "${B}${C}══════════════════════════════════════${N}\n"
printf "${B}   云手机 ADB 隧道一键部署 · frpc v0.71.0${N}\n"
printf "${B}${C}══════════════════════════════════════${N}\n"
echo -e "目标节点: ${Y}${SERVER_ADDR}${N}  通信端口: ${Y}${SERVER_PORT}${N}"

step "环境准备与动态库修复"
mkdir -p ~/frp/logs "$TMPD"
NEED=""
command -v curl >/dev/null 2>&1 && curl --version >/dev/null 2>&1 || NEED="$NEED openssl libcurl curl"
command -v pgrep >/dev/null 2>&1 || NEED="$NEED procps"
command -v termux-chroot >/dev/null 2>&1 || NEED="$NEED proot"
if [ -n "$NEED" ]; then
  warn "缺依赖:$NEED → 安装（实时输出；长时间卡住多为软件源不通，Ctrl+C 后重跑）"
  if ! apt update 2>&1 | tail -2; then
    warn "apt update 失败 → 自动换清华镜像后重试"
    SL="$PREFIX/etc/apt/sources.list"
    [ -f "$SL" ] && cp "$SL" "$SL.bak.frp" 2>/dev/null
    if ! grep -q "mirrors.tuna.tsinghua.edu.cn/termux" "$SL" 2>/dev/null; then
      sed -i 's@^deb@#deb@' "$SL" 2>/dev/null
      echo "deb https://mirrors.tuna.tsinghua.edu.cn/termux/apt/termux-main stable main" >> "$SL"
    fi
    apt update 2>&1 | tail -2
  fi
  apt install -y $NEED 2>&1 | tail -6
fi
curl --version >/dev/null 2>&1 && ok "curl 就绪 ($(curl --version 2>/dev/null | head -1 | awk '{print $1,$2}'))" || die "curl 仍损坏：手动 apt update && apt full-upgrade 后重跑"
command -v termux-chroot >/dev/null 2>&1 && ok "proot/termux-chroot 就绪 (DNS 映射层)" || die "proot 安装失败：手动 pkg install proot 后重跑"
command -v pgrep >/dev/null 2>&1 && ok "procps 就绪 (pgrep/pkill)" || warn "procps 缺失：keepalive 将用 ps 探活兜底"

# Go 静态二进制只认 /etc/resolv.conf; chroot 内 /etc = $PREFIX/etc
RES="$PREFIX/etc/resolv.conf"
[ -f "$RES" ] && [ ! -f "$RES.bak.frp" ] && cp "$RES" "$RES.bak.frp" 2>/dev/null
cat > "$RES.tmp.frp" <<'DNS_EOF'
nameserver 223.5.5.5
nameserver 119.29.29.29
DNS_EOF
mv -f "$RES.tmp.frp" "$RES"
ok "虚拟 DNS 就绪 ($RES → chroot 内映射为 /etc/resolv.conf)"
termux-wake-lock >/dev/null 2>&1 && ok "CPU wake-lock 已持有" || warn "wake-lock 不可用（不阻塞；ADB 通后做加固可长期常驻）"

step "下载 frpc (linux-arm64) · 多源自动切换"
got=""
for s in "${SOURCES[@]}"; do fetch "$s" && { got=1; break; }; done
if [ -z "$got" ]; then
  echo ""
  warn "全部下载源均失败：检查云手机出站网络/DNS 后重跑本脚本"
  die "所有下载源均失败"
fi
cp "$TMPD/frpc-dl" ~/frp/frpc && chmod 755 ~/frp/frpc \
  && ok "frpc 就绪 (版本 $(~/frp/frpc -v 2>/dev/null | head -1))" || die "安装 frpc 失败"

step "写入穿透配置与自愈常驻脚本"
cat > ~/frp/frpc.toml <<EOF
serverAddr = "${SERVER_ADDR}"
serverPort = ${SERVER_PORT}
auth.method = "token"
auth.token = "${FRPS_TOKEN}"
loginFailExit = false

[transport]
tcpMux = true
heartbeatInterval = 10
heartbeatTimeout = 30

[[proxies]]
name = "cloudphone-adb"
type = "stcp"
secretKey = "${STCP_SK}"
localIP = "127.0.0.1"
localPort = 5555
EOF
ok "frpc.toml 已写入 (server: ${SERVER_ADDR}:${SERVER_PORT})"
cat > ~/frp/spawn.sh <<'SEOF'
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
SEOF
chmod +x ~/frp/spawn.sh
cat > ~/frp/keepalive.sh <<'KEOF'
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
KEOF
chmod +x ~/frp/keepalive.sh
ok "spawn.sh / keepalive.sh 已写入 (每 15s 自愈; pgrep 缺失时 ps 探活兜底)"

step "启动隧道服务"
[ -f ~/frp/keepalive.pid ] && kill "$(cat ~/frp/keepalive.pid 2>/dev/null)" 2>/dev/null
if command -v pkill >/dev/null 2>&1; then
  pkill -f "frp/frpc" 2>/dev/null; pkill -f "keepalive.sh" 2>/dev/null
else
  for p in $(ps -A 2>/dev/null | awk '/[k]eepalive\.sh|[f]rpc/{print $1}'); do kill "$p" 2>/dev/null; done
fi
sleep 1
: > ~/frp/logs/frpc.log
: > ~/frp/logs/keepalive.log
nohup ~/frp/keepalive.sh >/dev/null 2>&1 &
echo $! > ~/frp/keepalive.pid
sleep 4
pgrep -f "frp/frpc" >/dev/null 2>&1 && ok "frpc 进程已运行 (PID $(pgrep -f 'frp/frpc' | head -1))" || warn "frpc 暂未拉起，保活循环将自动重试"

step "握手检测（等待服务器确认）"
res=""
for i in $(seq 1 40); do
  grep -q "start proxy success" ~/frp/logs/frpc.log 2>/dev/null && { res=1; break; }
  _s=$(( (_s+1)%4 ))
  printf "\r  ${C}%s${N} 等待注册确认 ... %2ds" "${SPINNER:_s:1}" "$i"
  sleep 1
done

if [ -n "$res" ]; then
  printf "\r  ${G}✔ 隧道已注册成功 (start proxy success)%s\n" "                    "
  echo ""
  printf "${G}${B}══════════════════════════════════════════${N}\n"
  printf "${G}${B}  ✅ 部署完成！ADB 隧道已打通并常驻后台${N}\n"
  printf "${G}${B}══════════════════════════════════════════${N}\n"
  echo ""
  echo -e "${B}💻 电脑端 visitor 配置 (已存在 ~/project/cloudphone-frp/pc/frpc-visitor.toml，自用无需再配)：${N}"
  echo -e "${C}──────────────────────────────────────────${N}"
  cat << PC_EOF
serverAddr = "${SERVER_ADDR}"
serverPort = ${SERVER_PORT}
auth.method = "token"
auth.token = "${FRPS_TOKEN}"

[[visitors]]
name = "cloudphone-adb-visitor"
type = "stcp"
serverName = "cloudphone-adb"
secretKey = "${STCP_SK}"
bindAddr = "127.0.0.1"
bindPort = ${VISITOR_BIND_PORT}
PC_EOF
  echo -e "${C}──────────────────────────────────────────${N}"
  echo ""
  echo -e "电脑终端启动 visitor 后连接: ${Y}adb connect 127.0.0.1:${VISITOR_BIND_PORT}${N}"
else
  printf "\r  ${R}✘%s\n" "                        "
  warn "frpc.log 末尾:"; tail -6 ~/frp/logs/frpc.log 2>/dev/null | sed 's/^/    /'
  warn "keepalive.log 末尾:"; tail -6 ~/frp/logs/keepalive.log 2>/dev/null | sed 's/^/    /'
  die "40 秒内未注册成功（常见: 域名解析失败 / 端口不通 / token 或 secretKey 错误）"
fi
