# frps 服务端搭建（VPS 中继）

> 本文是 `cloudphone-adb-tunnel` skill 的服务端参考。所有 `<占位符>` 换成你自己的值；**真实 token 永远不要提交进任何仓库**。

frps 是"盲中继"：只转发 frp 的加密流量，不解密、不落盘、不暴露 ADB。STCP 模式下，手机端 frpc 与电脑端 frpc visitor 必须持同一 token（登录服务端）+ 同一 secretKey（互相配对），服务端无法单独建立连接。

## 1. frps.toml 模板

```toml
bindAddr = "0.0.0.0"
bindPort = 48721

auth.method = "token"
auth.token = "<生成一个 64 位随机十六进制：openssl rand -hex 32>"

# 强制 TLS：拒绝一切非 TLS 登录（frpc 0.50+ 默认开启 TLS，两端一致即可）
transport.tls.force = true

# 只允许客户端占用中继侧端口段（收紧暴露面；stcp 模式实际不占用公网端口，防呆用）
allowPorts = [{ start = 48000, end = 48999 }]

# Dashboard 只绑环回，用 SSH 隧道查看；不要开公网
webServer.addr = "127.0.0.1"
webServer.port = 7500
webServer.user = "admin"
webServer.password = "<openssl rand -hex 16>"

log.level = "info"
log.maxDays = 7
```

要点：

- `transport.tls.force = true` 是底线，防止手滑用裸 TCP 注册。
- STCP 的流量发生在两个 frpc 之间经服务端撮合，`allowPorts` 里的端口并不会真正对外监听——它限制的是万一有人建了 tcp/udp 代理时能占用的范围。
- token 用 `openssl rand -hex 32` 生成；它是唯一防线，泄露 = 别人可把任意设备接入你的中继。

## 2. systemd 托管（推荐）

```ini
# /etc/systemd/system/frps.service
[Unit]
Description=frp server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=frp
Restart=on-failure
RestartSec=5
ExecStart=/usr/local/bin/frps -c /etc/frp/frps.toml

[Install]
WantedBy=multi-user.target
```

```bash
useradd -r -s /usr/sbin/nologin frp || true
mkdir -p /etc/frp && chown -R frp:frp /etc/frp
systemctl daemon-reload && systemctl enable --now frps
systemctl is-active frps
```

无 systemd 的环境（容器沙箱等）用 supervisord 同理：`command=/usr/local/bin/frps -c /etc/frp/frps.toml`，`autorestart=true`。

## 3. 云防火墙 / 安全组

- 只放行 `frps bindPort`（TCP，如 48721）。ADB 端口 5555、visitor 端口 55556 永远不出现在任何防火墙规则里。
- 腾讯云轻量服务器可在控制台放行，也可用 API 管理（项目 `tc-firewall.py` 的做法：TC3 签名直调 Lighthouse `ModifyFirewallRules`，注意空 `CidrBlock` 必须省略键）。
- 排障经验：**本机 `nc` 通不代表公网通**——Clash TUN 会替你完成 TCP 握手造成假阳性；判定放行与否要看应用层字节或从外部主机实测。

## 4. 域名接入（可选但推荐）

- 中继是纯 TCP，**不能用 Cloudflare 橙云代理**（那会破坏 frp 协议），DNS 必须灰云/DNS-only 直指 VPS IP。
- 域名包装的价值：脚本/文档里不出现裸 IP；换 VPS 只改 DNS。
- frps 层面的 TLS 与域名无关（token 派生自签名），填 IP 或域名都能连。

## 5. 健康检查（v0.71 实测）

```bash
curl -su <user>:<password> http://127.0.0.1:7500/api/serverinfo
# 健康判据: clientCounts=2(两端 frpc)、proxyTypeCount.stcp=1、curConns>=1
```

- **坑**：`/api/proxy`（不带类型）在 v0.71 返回 404 "no proxy info found"，即使代理在线——不要用它做健康判断。
- 日志：`journalctl -u frps -n 50`，看 `login to server success` / `start proxy success` 字样。

## 6. 客户端计数语义

`clientCounts` 统计的是登录到 frps 的 frpc 进程数。一套最小链路 = 2（手机 proxy 端 + 电脑 visitor 端）。只有 1 时说明有一端掉线；0 时服务端空转。
