// 统一排盘接口 —— 对接 mingpan(八字, Apache-2.0) + iztro(紫微, MIT)

import type { BirthInfo, ChartResult } from './types';
import { createBaziChartV2 } from './bazi-adapter';
import { createZiweiChartV2 } from './ziwei-adapter';

export async function createChart(birthInfo: BirthInfo): Promise<ChartResult> {
  try {
    // 先算八字（siZhu 权威来源），再把同一份 siZhu 喂给紫微侧展示，避免两套引擎各自算出不一致的四柱
    const bazi = await createBaziChartV2(birthInfo);
    const ziwei = createZiweiChartV2(birthInfo, bazi.siZhu);
    return { bazi, ziwei };
  } catch (error) {
    throw new Error(`排盘计算失败: ${error instanceof Error ? error.message : String(error)}`);
  }
}
