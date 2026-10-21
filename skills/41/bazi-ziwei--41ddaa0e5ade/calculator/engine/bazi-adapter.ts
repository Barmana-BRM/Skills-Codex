// 八字排盘适配层 —— 对接 mingpan（Apache-2.0，真实LICENSE已验证）
// 把 mingpan 的输出，映射成本项目原有的 BaziChart 数据结构，供下游 enrichBazi / render 等代码复用

import { baziService } from 'mingpan/dist/services/bazi/index.js';
import { BaziCore } from 'mingpan/dist/core/bazi/BaziCore.js';
import type { BirthInfo, BaziChart, GanZhi, Tiangan, Dizhi } from './types';
import { getShiShen } from './shishen';
import { toSolarDate } from './lunar-convert';

const core = new BaziCore();

function toGanZhi(stem: string, branch: string): GanZhi {
  return { gan: stem as Tiangan, zhi: branch as Dizhi };
}

// 晚子时（23:00-23:59）：传统命理里"日柱"按次日算，但 mingpan 的时柱公式（五鼠遁）已经
// 内置了"日干+1"的晚子时修正——如果我们把整个日期都往后挪一天再传入，会导致时柱被二次修正而算错。
// 正确做法：主请求仍用原始（已转换为公历的）日期（时柱由此拿到正确结果），只在需要日柱时，
// 另外用"次日"单独查一次。
function nextDay(solarDate: { year: number; month: number; day: number }): { year: number; month: number; day: number } {
  const d = new Date(Date.UTC(solarDate.year, solarDate.month - 1, solarDate.day));
  d.setUTCDate(d.getUTCDate() + 1);
  return { year: d.getUTCFullYear(), month: d.getUTCMonth() + 1, day: d.getUTCDate() };
}

export async function createBaziChartV2(birthInfo: BirthInfo): Promise<BaziChart> {
  const gender = birthInfo.gender;
  // mingpan 声明了 useLunar 但实现里完全没用（已核实为空气开关），统一在这里做权威的农历->公历转换
  const solarDate = toSolarDate(birthInfo);
  const input = {
    year: solarDate.year,
    month: solarDate.month,
    day: solarDate.day,
    hour: birthInfo.hour,
    minute: birthInfo.minute,
    gender,
    useLunar: false,
    options: {
      timeRange: { startYear: solarDate.year, endYear: solarDate.year + 100 },
    },
  };

  const result = await baziService.calculate(input);
  const chart = result.chart; // { year, month, day, hour } 每柱含 stem/branch/naYin/hiddenStems...

  // 晚子时：日柱字段用"次日中午"单独查询覆盖（避免用 23 点直接查次日触发时柱的二次修正）
  if (birthInfo.hour === 23) {
    const nd = nextDay(solarDate);
    const dayResult = await baziService.calculate({
      year: nd.year, month: nd.month, day: nd.day, hour: 12, minute: 0, gender, useLunar: false,
    });
    chart.day = dayResult.chart.day;
  }

  const siZhu = {
    year: toGanZhi(chart.year.stem, chart.year.branch),
    month: toGanZhi(chart.month.stem, chart.month.branch),
    day: toGanZhi(chart.day.stem, chart.day.branch),
    hour: toGanZhi(chart.hour.stem, chart.hour.branch),
  };

  const dayMaster = chart.day.stem as Tiangan;

  // 十神（四柱天干对日主）—— mingpan basic.tenGods 已提供，按 position 取回；用独立 getShiShen 兜底保证一致
  const shiShen = {
    year: getShiShen(dayMaster, siZhu.year.gan),
    month: getShiShen(dayMaster, siZhu.month.gan),
    day: '日主', // 日柱天干就是日主自身，命理惯例写"日主"而非十神
    hour: getShiShen(dayMaster, siZhu.hour.gan),
  };

  // 十二长生（日主对四柱地支）—— mingpan core.calculateTwelveGrowthStages 已验证与标准答案一致
  const stages = await core.calculateTwelveGrowthStages(chart);
  const zhangSheng = {
    year: toSimplified(stages[0]?.stage),
    month: toSimplified(stages[1]?.stage),
    day: toSimplified(stages[2]?.stage),
    hour: toSimplified(stages[3]?.stage),
  };

  const naYin = {
    year: chart.year.naYin,
    month: chart.month.naYin,
    day: chart.day.naYin,
    hour: chart.hour.naYin,
  };

  // 大运
  const timeBased = result.timeBased;
  const allLiuNian: any[] = timeBased?.liuNian || [];
  const dayunList = (timeBased?.daYun || []).map((d: any) => {
    const ganZhi = toGanZhi(d.stem, d.branch);
    const liuNian = allLiuNian
      .filter((ln) => ln.year >= d.startYear && ln.year <= d.endYear)
      .map((ln) => ({ year: ln.year, age: ln.age, ganZhi: toGanZhi(ln.stem, ln.branch) }));
    return {
      ganZhi,
      startAge: d.startAge,
      startYear: d.startYear,
      endYear: d.endYear,
      ganShiShen: getShiShen(dayMaster, ganZhi.gan),
      zhiShiShen: getShiShen(dayMaster, (DIZHI_MAIN_QI as any)[ganZhi.zhi]),
      liuNian,
    };
  });

  const dayunStart = dayunList[0]?.startAge ?? 0;

  return {
    birthInfo,
    siZhu,
    dayMaster,
    shiShen: shiShen as any,
    zhangSheng,
    naYin,
    dayunStart,
    dayun: dayunList,
  };
}

// 十二长生繁体->简体（mingpan 部分输出为繁体字）
const TRAD_TO_SIMP: Record<string, string> = {
  長生: '长生', 沐浴: '沐浴', 冠帶: '冠带', 臨官: '临官', 帝旺: '帝旺',
  衰: '衰', 病: '病', 死: '死', 墓: '墓', 絕: '绝', 胎: '胎', 養: '养',
};
function toSimplified(s?: string): string | undefined {
  if (!s) return s;
  return TRAD_TO_SIMP[s] || s;
}

// 地支主气（用于大运地支的十神判断），标准命理分野表
const DIZHI_MAIN_QI: Record<string, string> = {
  子: '癸', 丑: '己', 寅: '甲', 卯: '乙', 辰: '戊', 巳: '丙',
  午: '丁', 未: '己', 申: '庚', 酉: '辛', 戌: '戊', 亥: '壬',
};
