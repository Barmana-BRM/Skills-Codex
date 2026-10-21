# wechat-exporter

一个 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) / [Codex](https://openai.com/index/introducing-codex/) 技能（Skill），用于将 macOS 微信桌面端的本地聊天记录全量导出为明文 SQLite 数据库。

## 它能做什么

- 自动安装所需依赖（sqlcipher、Python 虚拟环境等）
- 对微信客户端进行重签名，从内存中提取数据库加密密钥
- 解密全部聊天记录数据库（联系人、消息、会话等）
- 输出为标准 SQLite 明文数据库，可直接用任何 SQL 工具查询
- 注册为 MCP Server，解密后可在 Claude Code 中直接查询聊天记录

## 前置条件

| 条件 | 说明 |
|------|------|
| macOS | 仅支持 macOS 系统 |
| 微信桌面端 | 需要已安装并登录微信 Mac 版 |
| 聊天记录已备份到电脑 | 在手机微信中将聊天记录迁移/备份到 Mac 端 |
| Claude Code 或 Codex | 用于运行本技能 |
| 终端完全磁盘访问权限 | 系统设置 → 隐私与安全性 → 完全磁盘访问权限 → 添加你的终端 |

## 快速开始

### 1. 安装技能

将技能添加到你的 Claude Code 技能目录。以下两种方式任选其一：

```bash
# 方式一：直接复制文件
cp SKILL.md ~/.claude/skills/wechat-exporter.md

# 方式二：创建目录（适合后续扩展）
mkdir -p ~/.claude/skills/wechat-exporter
cp SKILL.md ~/.claude/skills/wechat-exporter/skill.md
```

> 以上示例为全局安装（所有项目可用）。如需项目级安装，将 `~/.claude/skills/` 替换为 `<你的项目>/.claude/skills/`。

### 2. 运行

在 Claude Code 中输入：

```
导出微信聊天记录
```

或直接调用技能名：

```
/wechat-exporter
```

技能会一步步引导你完成整个过程，包括：

1. 安装系统依赖（`brew install sqlcipher`）
2. 下载并编译密钥扫描工具
3. 对微信进行重签名（需要 `sudo`）
4. 提取数据库加密密钥（需要 `sudo`，需手动在终端执行）
5. 解密所有聊天数据库
6. 输出导出摘要

### 3. 导出结果

解密后的数据库存放在 `~/wechat-decrypt-macos/decrypted/`：

```
decrypted/
├── contact/
│   └── contact.db          # 联系人
├── message/
│   ├── message_0.db        # 消息分片（按时间段切割）
│   ├── message_1.db
│   └── ...
├── session/
│   └── session.db          # 会话列表
└── ...
```

所有数据库均为标准 SQLite 格式，可以用 `sqlite3`、DB Browser for SQLite 等任何工具直接查询。

## 数据库结构

### 联系人（contact.db）

`contact` 表中 `local_type` 字段含义：

| local_type | 含义 |
|------------|------|
| 1 | 真实好友（双向添加） |
| 3 | 有过消息往来但未必是好友 |
| 0 | 服务号、系统通知 |

### 消息分片（message_*.db）

消息按**时间段**分片存储，`message_0.db` 通常是最近一年的主力库。每个联系人的消息存储在独立的 `Msg_<md5>` 表中，`<md5>` 为联系人 `username` 的 MD5 哈希值。

可通过 `Name2Id` 表建立 username 到表名的映射：

```python
import hashlib, sqlite3

conn = sqlite3.connect("message_0.db")
for (username,) in conn.execute("SELECT user_name FROM Name2Id"):
    table = "Msg_" + hashlib.md5(username.encode()).hexdigest()
    print(f"{username} → {table}")
```

## 工作原理

```
手机微信 ──备份──→ Mac 微信桌面端（加密 SQLCipher 数据库）
                         │
                    重签名微信 App
                         │
                    内存扫描提取密钥
                         │
                    SQLCipher 解密
                         │
                         ▼
                   明文 SQLite 数据库 ──→ 自由查询 / MCP Server
```

核心依赖了以下两个开源项目：

- [cocohahaha/wechat-decrypt-macos](https://github.com/cocohahaha/wechat-decrypt-macos) — MCP Server
- [ylytdeng/wechat-decrypt](https://github.com/ylytdeng/wechat-decrypt) — 密钥扫描与数据库解密

## 常见问题

| 问题 | 处理方式 |
|------|---------|
| HMAC 验证失败 | config.json 指向了错误的账号目录，重新确认当前登录账号 |
| 0/N keys found | 微信版本更新后需重签名 + 重新扫描密钥 |
| lldb attach 失败 | 微信未重签名，执行 `sudo codesign --force --deep --sign - /Applications/WeChat.app` |
| 解密后消息为空 | 检查 server.py 是否已按技能说明修改为读取明文数据库 |

## 注意事项

- 提取密钥需要 `sudo` 权限，技能会提示你手动在终端执行
- 微信每次更新版本后需要重新签名并重新提取密钥
- 导出的数据仅保存在本地，请妥善保管

## 致谢

- [cocohahaha/wechat-decrypt-macos](https://github.com/cocohahaha/wechat-decrypt-macos)
- [ylytdeng/wechat-decrypt](https://github.com/ylytdeng/wechat-decrypt)

## License

[MIT](LICENSE)
