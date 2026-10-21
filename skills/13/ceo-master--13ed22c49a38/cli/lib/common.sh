#!/usr/bin/env bash
# common.sh — shared helpers for CEO (Chief Executive Officer) — 一家公司「最高操作员」的工艺, 与泛泛「领导力 / 管理学」不同: (a) 设定战略与凝结愿景 (Drucker 的「企业的经营理论」+ Porter 论定位 + Hamilton Helmer 的「七力」+ Andy Grove 的「战略转折点」+ Roger Martin 《Playing to Win》); (b) 资本配置是 CEO 单一最高杠杆的工作 (Buffett/Munger Berkshire 致股东信 + William Thorndike 《The Outsiders 商界局外人》论 8 位非常规 CEO + Michael Mauboussin 论 hurdle rate + Bezos 年度致股东信「invariants vs bets」+ Mark Leonard Constellation Software); (c) 组建与领导高管班子 (Patrick Lencioni 《团队的五大障碍》+ Ben Horowitz 《艰难的事》+ Reed Hastings 《No Rules Rules》人才密度 + Andy Grove HOP《高产出管理》+ Lou Gerstner IBM 转型 + Marshall Goldsmith); (d) 董事会与投资人关系 (Larcker & Tayan 《公司治理重要》+ Bill George 《True North》+ 正式 CEO-董事长 / CEO-独立董事 protocol + 维权投资人 playbook + 资本市场沟通); (e) 企业文化与价值观作为操作系统 (Netflix 文化手册 + Amazon Leadership Principles + Bridgewater 《Principles》Ray Dalio + Schein 论组织文化 + 任正非 灰度 + 张瑞敏 人单合一 + 稻盛和夫 阿米巴); (f) 高不确定下的高风险决策 (Bezos Type 1/Type 2 决策 + premortem Klein + Kahneman 论 executive bias + RAPID/DACI + base rates + 情景规划 + 反思 premortem); (g) 对内对外沟通 (创始人 / CEO 致股东信作为机构构建工具: Bezos / Buffett / Reed Hastings 备忘录 / 任正非 内部讲话 + Town Hall + 危机沟通 Tylenol/Boeing/Wells Fargo + 应对维权投资人); (h) 跨阶段规模化 (创业 0→1 / 扩张 1→100 / 成熟期掌舵 / 危机转型): Steve Blank + Brian Chesky founder-mode + Marc Andreessen + Pierre Lassonde + Lou Gerstner 转型; (i) 创始人 CEO vs 职业经理人 CEO 的差异 (Paul Graham 「Founder Mode」2024 + Brian Chesky + Reed Hastings (创始人→职业过渡) + BCG/McKinsey 的「manager mode」+ 两者各自代价 + 什么时候切换)。诚实处理: 幸存者偏差 (单个 CEO 的打法 ≠ 普适规律, 学术研究显示 CEO 个人方差约 ⅓, 约 70% 来自行业 / 时代 / 运气 / 资本结构), 创始人崇拜, 区分可复制工艺与不可移植个人魅力, 治理与利益相关者责任 (员工 / 股东 / 社会), 反对 CEO 神话与 Welch 退休金扭曲 / Theranos / WeWork / FTX / Uber-Kalanick 时代 / Musk 80h+ / 996 工时崇拜。覆盖 founder-CEO (Bezos/Hastings/黄仁勋/Chesky/Brin/任正非) 与职业 CEO (Nadella/Gerstner/Pichai/Mulally/Lafley)。不含: 泛泛管理理论 (商业书已覆盖, 本 skill 专谈 C-suite 这个具体岗位), 不含: 「领导力」作为个人成长自助 (Robbins/Tracy/Maxwell 励志体裁), 不含: 「如何创业」早期战术 — 一旦有员工 / 董事会 / 资本, CEO 的工艺才开始。 master CLI scripts.
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
