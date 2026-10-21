#!/usr/bin/env bash
# common.sh — shared helpers for 游戏设计 (Game Design) — 设计游戏的规则 / 系统 / 机制 / 体验 的从业者认知操作系统 (以电子游戏为主, 含桌游 / 卡牌 / 棋盘游戏): 决定「玩家做什么、为什么有意义、每一刻的体验如何」的学科 —— 区别于游戏程序 (引擎 / 代码)、游戏美术 (视觉 / 音频)、游戏制作 (排期 / 预算 / 团队)。覆盖 (a) 核心设计理论与框架 (MDA 机制-动态-美学 Hunicke/LeBlanc/Zubek + Schell 的「透镜」+ Koster「乐趣即学习」理论 + Sid Meier「一连串有趣的决策」+ Salen & Zimmerman「有意义的游玩」/「二阶设计」/「魔法圈」+ Costikyan 论不确定性 + Suits/Huizinga 游戏哲学), (b) 系统与机制设计 (核心循环 + 游戏经济 sink/source/产出-消耗 + 正负反馈环 + 资源与成长系统 + 涌现 vs 脚本 Will Wright「可能性空间」+ Machinations 经济建模 Dormans + 支配 / 退化策略 + 正交设计 Garfield), (c) 关卡与遭遇设计 (灰盒 blockout + 节奏与张力 + 预告 telegraphing + 主线 vs 探索 + 环境叙事 + 锁钥 gating + 难度曲线), (d) 游戏手感与「juice」(Steve Swink《Game Feel》+ 即时响应 + 屏震 / 反馈 / 打磨 + 输入与镜头 + 「手感」是设计出来的不是附带的), (e) 玩家心理与 UX (Celia Hodent《The Gamer's Brain》+ 心流通道 挑战 vs 技能 Csikszentmihalyi/陈星汉 Jenova Chen + Bartle 玩家类型 + 动机与奖励节奏 + 新手引导 FTUE / 教学化 + 认知负荷 + 无障碍), (f) 平衡与调优 (Ian Schreiber《Game Balance》+ 对称 / 非对称 + 动态难度 DDA + 传递 / 非传递平衡 + nerf/buff + 消除支配策略 + 测试驱动调优), (g) 叙事与任务设计 (ludonarrative 失调 / 和谐 + 环境与系统叙事 + 分支 vs 线性 + Amy Hennig 角色驱动 + 任务结构), (h) 以玩家为中心的迭代流程 (Tracy Fullerton《Game Design Workshop》playcentric + 纸面原型 + 垂直切片 + 测试协议「看而不说 / 你不是你的玩家」+ 快速迭代 + game jam), (i) 类型与形态工艺 (roguelike/roguelite 与程序生成 Derek Yu + 平台跳跃 + RPG 系统 + 策略 4X + 解谜设计 Jonathan Blow + 多人 / PvP 平衡 + 桌游 / 卡牌设计 Reiner Knizia/Richard Garfield/Brenda Romero), (j) F2P / 长线运营 / 商业化设计 (核心 / 元 / 经济循环 + 抽卡 gacha / 开箱 loot box / 战令 battle pass 机制 + 留存 D1/D7/D30 + 转化 + 鲸鱼 + live ops 内容节奏 —— 并诚实处理掠夺式暗黑模式 / 强迫循环 / 剥削式商业化的伦理), (k) 设计师角色与工艺职业 (系统 / 关卡 / 叙事 / UX 设计师之分 + 通才 vs 专才 + 独立作者 vs 3A 团队 + 设计文档 + 传达设计意图 + GDC 工艺社区)。跨 3A / 独立 / 手游 F2P / 桌游。不含 游戏程序 / 引擎 (Unity/Unreal 编码 / 图形 / 网络同步) / 游戏美术 / 动画 / 音频 / 游戏制作 / 项目管理 / 排期 / QA / 游戏作为生意 / 发行 / 市场 / 电竞运营为终点 / 泛泛「我想做游戏」的 game-dev 教程 —— 本 skill 是「设计」学科: 规则 / 系统 / 机制 / 体验。 master CLI scripts.
# Pure bash 4 + POSIX coreutils. No external deps.

if [[ -t 1 ]]; then
  MS_BOLD=$'\033[1m'; MS_DIM=$'\033[2m'
  MS_RED=$'\033[31m'; MS_GREEN=$'\033[32m'
  MS_YELLOW=$'\033[33m'; MS_BLUE=$'\033[34m'
  MS_RESET=$'\033[0m'
else
  MS_BOLD=""; MS_DIM=""; MS_RED=""; MS_GREEN=""; MS_YELLOW=""; MS_BLUE=""; MS_RESET=""
fi

ms_section() { printf "\n%s━━ %s ━━%s\n" "$MS_BOLD$MS_BLUE" "$1" "$MS_RESET"; }
ms_info()    { printf "%s%s%s\n" "$MS_DIM" "$1" "$MS_RESET"; }
ms_warn()    { printf "%s⚠ %s%s\n" "$MS_YELLOW" "$1" "$MS_RESET"; }
ms_error()   { printf "%s✗ %s%s\n" "$MS_RED" "$1" "$MS_RESET" >&2; }
ms_ok()      { printf "%s✓ %s%s\n" "$MS_GREEN" "$1" "$MS_RESET"; }
ms_prompt()  { printf "%s? %s%s " "$MS_BOLD" "$1" "$MS_RESET"; }

ms_read_multiline() {
  local result=""
  local line
  while IFS= read -r line; do
    [[ -z "$line" ]] && break
    result+="$line"$'\n'
  done
  printf "%s" "$result"
}

ms_confirm() {
  ms_prompt "$1 [y/N]"
  local ans
  read -r ans
  [[ "$ans" =~ ^[Yy] ]]
}

# Markdown buffer (global)
MS_REPORT_BUFFER=""
ms_buffer_append() { MS_REPORT_BUFFER+="$1"$'\n'; }

ms_emit_md_file() {
  local slug="$1"
  local fname="${slug}-$(date +%Y%m%d-%H%M%S).md"
  printf "%s" "$MS_REPORT_BUFFER" > "$fname"
  ms_ok "报告已写到 $fname"
}

ms_emit_md_stdout() { printf "%s" "$MS_REPORT_BUFFER"; }

ms_json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\t'/\\t}"
  s="${s//$'\r'/}"
  printf "%s" "$s"
}

ms_emit_json() {
  local out="{"
  local first=1
  while [[ $# -ge 2 ]]; do
    [[ $first -eq 1 ]] || out+=","
    first=0
    out+="\"$(ms_json_escape "$1")\":\"$(ms_json_escape "$2")\""
    shift 2
  done
  out+="}"
  printf "%s\n" "$out"
}
