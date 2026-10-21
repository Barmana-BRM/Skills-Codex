# 全量踩坑手册（Termux / 电脑端 / 网络 / 分发）

> 本文是 `cloudphone-adb-tunnel` skill 的深度参考。每一条都在真机上踩到过；SKILL.md 里的速查表是它的摘要。

## 1. Termux 环境

### 1.1 没有根目录 /tmp

- **症状**：脚本把下载产物写到 `/tmp/frpc-dl`，所有下载源全部"失败"，进度条根本不动。
- **根因**：Android 应用没有 `/` 的写权限，真实根文件系统上不存在 `/tmp`。Termux 的临时目录是 `$TMPDIR` = `$PREFIX/tmp` = `/data/data/com.termux/files/usr/tmp`。
- **正确做法**：脚本内统一用 `~/frp/tmp`（自己 mkdir、自己清理，配 `trap 'rm -rf ...' EXIT`）。打包脚本已如此。
- **教训**：这个 bug 曾被误诊为"DNS 污染"——所有源以完全相同的方式失败时，先怀疑本地文件路径而不是网络。

### 1.2 Go 静态二进制的 DNS：`[::1]:53 connection refused`

- **症状**：curl 能下载（bionic 链接，走 Android netd 解析），但 frpc 报 `dial tcp: lookup <域名> on [::1]:53: read udp ... connection refused`。
- **根因**：frpc 是 CGO_ENABLED=0 的 Go 静态二进制，自带纯 Go 解析器，**只认 `/etc/resolv.conf`**。Android 应用没有这个文件，Go 解析器回退查询环回 DNS（127.0.0.1/[::1]:53），无人监听即被拒。
- **解法（两层配合）**：
  1. 把 `nameserver 223.5.5.5` / `119.29.29.29` 写入 `$PREFIX/etc/resolv.conf`（Termux 可写）；
  2. 用 `termux-chroot`（proot 包）拉起 frpc——proot 把 `$PREFIX/etc` 映射成 chroot 内的 `/etc`，Go 解析器于是能读到。
- **为什么不用"先解析成 IP 再连"**：chroot 方案让域名保留在配置里、无需运行时解析逻辑，且被实机长期验证。备选方案（ping/curl 探测解析后写 IP）在 proot 不可用时可用，但要自己维护重解析。
- **注意**：frps 的 TLS 是 token 派生的自签名握手，不校验主机名，所以连 IP 也可行——这是最后的兜底。

### 1.3 curl 动态库错配

- **症状**：`CANNOT LINK EXECUTABLE "curl": cannot locate symbol "SSL_set_quic_tls_early_data_enabled" referenced by .../libcurl.so`。
- **根因**：libcurl 是新版、libssl 是旧版（长期只升级部分包的 Termux 常见）。动态链接器拒载，curl 及一切链接 libcurl 的程序全灭。
- **解法**：换清华源（备份 sources.list 后注释原行、追加 tuna 行）→ `apt update && apt install -y openssl libcurl curl`。安装脚本已内置：仅在 `curl --version` 失败时触发，且输出全程可见。

### 1.4 pkg install 静默黑屏

- **症状**：跑脚本时在依赖安装步骤"没动静"，像死机。
- **根因**：`pkg install ... >/dev/null 2>&1` 吞掉全部输出 + 默认软件源未配置（Termux 新装未跑 `termux-change-repo`）或不通。
- **正确做法**：依赖用 `command -v` 逐个检测（curl/procps/proot 分开判），缺啥装啥；安装输出实时可见；默认源 `apt update` 失败自动切清华镜像；装完回读验证。
- **连带教训**：依赖检测绝不能放进"仅当 curl 损坏"的分支——curl 健康的新设备会静默缺 proot/procps，chroot 拉不起、keepalive 空转。

### 1.5 长脚本粘贴

- **症状 A**：整块粘贴后回车"没动静"——粘贴缓冲 + 末尾换行问题。
- **症状 B（更隐蔽）**：外层 `cat << 'EOF' > install.sh` 会在脚本内 frpc.toml heredoc 的 `EOF` 行**提前终止**，只有前半段写进文件，后半段直接漏进交互 shell 执行。
- **正确做法**：外层定界符必须与脚本内所有 heredoc 不同名（如 `INSTALL_EOF`）；或者干脆 `curl -O` 下载脚本再 `bash` 执行，绕过粘贴。

### 1.6 procps 与 keepalive 堆积

- **症状**：frpc 进程越积越多、日志疯狂滚动"重启 frpc"。
- **根因**：keepalive 用 `pgrep` 探活；procps 未装时 pgrep 不存在，`if ! pgrep ...` 恒真 → 每个循环周期拉起一个新 frpc。frp 同名 proxy 会互踢，表现为隧道反复闪断。
- **正确做法**：keepalive 双路径探活（有 pgrep 用 pgrep，没有用 `ps -A | grep '[f]rpc'`）；拉起写 `frpc.pid`；spawn 前先按 pid 精确杀旧进程。

### 1.7 Android 13 幽灵进程查杀

- **背景**：Android 13 对每个 app 限制最多 32 个子进程，超限的子进程被静默 SIGKILL（"phantom process killer"）。Termux 里 frpc/keepalive 属于 app 子进程，长时间运行或子 shell 累积会被杀。
- **解法**（adb shell 即可，无需 root）：`device_config set_sync_disabled_for_tests persistent` + `device_config put activity_manager max_phantom_processes 2147483647`；配合电池白名单 `dumpsys deviceidle whitelist +com.termux` 与 appops（RUN_IN_BACKGROUND / START_FOREGROUND allow）。
- **验证**：每一条都要 `device_config get` / `appops get` 回读；重启设备后部分设置可能复位，`persistent` 声明能挡住云同步覆盖，但大版本升级后建议复跑一遍。

## 2. 电脑端

### 2.1 端口 55555 被隐形占用

- **症状**：visitor 报 `bind: address already in use`，但 `lsof -nP -iTCP:55555` 和 `netstat -an` 都看不到持有者；adb 侧表现为 `connection refused`（bind 失败 + accept 拒绝并存）。
- **根因**：root 权限进程持有端口，非 sudo 的 lsof/netstat 不可见（本机实测存在）。
- **解法**：visitor `bindPort` 换 55556 即通。打包脚本与文档默认 55556；新机器上 55555 空闲可改回。
- **通用教训**：「bind in use + connect refused 并存」= 有持有者但不在 accept，换端口比深挖快。

### 2.2 adb 假死 / offline

- 先 `adb disconnect 127.0.0.1:55556 && adb connect 127.0.0.1:55556`；
- 仍不行按顺序重启：电脑端 visitor → 手机端 frpc（kill 后 keepalive 15 秒自动拉起）；
- `adb devices` 里若有 `127.0.0.1:16384 offline` 之类的条目，那是云手机厂商客户端自己的本地中继，与本隧道无关，`adb disconnect` 清掉即可。

### 2.3 Clash TUN 假握手

- **症状**：`nc -zv host port` 显示成功，但真实业务连不上；frpc 日志 `session shutdown` 而服务端毫无登录记录。
- **根因**：Clash TUN 接管后由它代替目标完成 TCP 三次握手，"端口通"只说明 TUN 活着。
- **判定方法**：必须看应用层数据（TLS 首字节、HTTP 状态码），或从另一台外部主机（不同网络出口）实测。
- **配套**：给 VPS IP 加 Clash DIRECT 规则，且要与订阅更新共存（脚本规则 + 静态 IP 列表双写）。

## 3. 分发与发布

### 3.1 无密钥断言（发布前必跑）

```bash
grep -rn "<token前8位>\|<secretKey前8位>\|<frps域名>" install-termux-share.sh && echo LEAK || echo clean
grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' install-termux-share.sh | grep -vE '^(127\.0\.0\.1|0\.0\.0\.0|223\.5\.5\.5|119\.29\.29\.29)$'
```

白名单只放行环回与公共 DNS。自用版（预填密钥）与分享版（交互输入）严格分文件管理。

### 3.2 下载源链路

- 顺序：**GitHub 官方 → ghfast.top → ghproxy.net → gh-proxy.com → 自建 CDN（兜底）**；官方源可用时不消耗自建站带宽。
- 固定 sha256 校验（`sha256sum -c`），防镜像劫持；校验失败视为源损坏直接换下一个。
- 单源 15 秒均速 <1KB/s 判定卡死（`curl --speed-limit 1024 --speed-time 15`），避免假死干等。

### 3.3 下载站 CDN 边缘缓存

- `/pub/` 走 Cloudflare 边缘缓存（zone cache rule：`starts_with(http.request.uri.path, "/pub/")` → cache=true + edge_ttl override_origin 86400；源站 nginx `Cache-Control: public, max-age=86400`；Smart Tiered Cache on）。
- **同名覆盖文件后必须 CF purge 该 URL**（purge_cache API 实测可用），否则边缘 24 小时内仍是旧版——真机吃过亏。
- 二进制升级用新版本号文件名，天然免 purge。
- 注意 zone cache rule 的 API 坑：`POST /zones/{id}/rulesets` 创建成功，但 `PUT/GET …/phases/…/entry` 可能报/返回 not_found——规则实际在生效，用「源站临时 no-store 仍判可缓存」的隔离实验验证，别只信 GET。
- frps 中继同理：纯 TCP 不能过 CF 橙云，DNS 必须灰云。

## 4. 快速对照索引

| 症状关键词 | 查本文件 | 一句话方向 |
|---|---|---|
| 所有源下载失败 | §1.1 | /tmp 不存在 |
| [::1]:53 refused | §1.2 | chroot + resolv.conf |
| curl SSL symbol | §1.3 | 换源重装 openssl/libcurl |
| pkg 黑屏 | §1.4 | 可见输出 + 换镜像 |
| 粘贴跑一半崩 | §1.5 | 定界符改名 |
| frpc 越积越多 | §1.6 | 探活双路径 |
| 后台被杀 | §1.7 | 幽灵进程 + 白名单 |
| bind in use + refused | §2.1 | 换 55556 |
| nc 通但业务不通 | §2.3 | TUN 假握手 |
| 发布后还是旧版 | §3.3 | CF purge |
