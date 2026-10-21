// 农历 -> 公历 统一转换层
//
// 背景：mingpan 声明了 useLunar 参数但实现里完全没用（已核实：BaziCore.ts/BaziService.ts
// 全文搜不到 useLunar，等于摆设）；iztro 的 byLunar/bySolar 在节气边界附近月柱计算另有误差
// （已核实：1989-08-02，立秋在 1989-08-07 21:03:52 之后，月柱应为"未"，iztro 算成"申"）。
// 解法：统一在这一层用 lunar-typescript（原项目就信任的库）做唯一权威的农历->公历转换，
// 两个引擎一律只喂公历日期，不依赖各自内部的农历处理。

import { Lunar } from 'lunar-typescript';
import type { BirthInfo } from './types';

export interface SolarDate {
  year: number;
  month: number;
  day: number;
}

// 把 BirthInfo 转成一定是公历的 { year, month, day }；isLunar=false 时原样返回
export function toSolarDate(birthInfo: BirthInfo): SolarDate {
  if (!birthInfo.isLunar) {
    return { year: birthInfo.year, month: birthInfo.month, day: birthInfo.day };
  }
  const lunar = Lunar.fromYmd(birthInfo.year, birthInfo.month, birthInfo.day);
  const solar = lunar.getSolar();
  return { year: solar.getYear(), month: solar.getMonth(), day: solar.getDay() };
}
