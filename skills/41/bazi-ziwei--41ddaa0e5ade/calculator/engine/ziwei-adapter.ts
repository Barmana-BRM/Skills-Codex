// 紫微斗数排盘适配层 —— 对接 iztro（MIT，真实LICENSE已验证，star数4千+）
// 把 iztro 的 Astrolabe 输出，映射成本项目原有的 ZiweiChart 数据结构

import { astro } from 'iztro';
import type { BirthInfo, ZiweiChart, ZiweiGongInfo, SiZhu, Dizhi, Tiangan } from './types';
import { toSolarDate } from './lunar-convert';

const DIZHI_ORDER: Dizhi[] = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

// iztro 宫位命名 -> 本项目宫位命名（仅"仆役"与"交友"这一项不同，其余一致）
const GONG_NAME_MAP: Record<string, string> = {
  仆役: '交友',
};

function mapGongName(name: string): string {
  return GONG_NAME_MAP[name] || name;
}

// 时辰(0-23) -> iztro 时辰序号(0-11, 子丑寅卯...)
function hourToShichenIndex(hour: number): number {
  // 23:00-00:59 属子时(0)，其余每2小时一个时辰，从01:00(丑,1)开始
  if (hour === 23) return 0;
  return Math.floor((hour + 1) / 2) % 12;
}

// bazi 侧的 siZhu（可选传入）：由 mingpan + lunar-typescript 算出，已验证准确。
// iztro 在节气边界附近月柱计算有误差（已核实：1989-08-02 应为"未"月，iztro 算成"申"月），
// 所以紫微盘展示用的四柱，优先复用 bazi 侧结果，而不是信任 iztro 自己的 chineseDate。
export function createZiweiChartV2(birthInfo: BirthInfo, baziSiZhu?: SiZhu): ZiweiChart {
  // iztro 的 byLunar 内部转换 + 节气边界计算都不完全可靠，统一改用我们自己转换好的公历日期
  const solarDate = toSolarDate(birthInfo);
  const dateStr = `${solarDate.year}-${solarDate.month}-${solarDate.day}`;
  const shichenIndex = hourToShichenIndex(birthInfo.hour);
  const genderCn = birthInfo.gender === 'male' ? '男' : '女';

  const astrolabe = astro.bySolar(dateStr, shichenIndex, genderCn, true, 'zh-CN');

  const gongs: ZiweiGongInfo[] = astrolabe.palaces.map((p: any) => {
    const sihua: { star: string; hua: string }[] = [];
    const allStars = [...p.majorStars, ...p.minorStars];
    for (const s of allStars) {
      if (s.mutagen) sihua.push({ star: s.name, hua: `化${s.mutagen}` });
    }

    return {
      gong: mapGongName(p.name) as any,
      dizhi: p.earthlyBranch as Dizhi,
      tiangan: p.heavenlyStem as Tiangan,
      mainStars: p.majorStars.map((s: any) => s.name),
      auxStars: p.minorStars.map((s: any) => s.name),
      sihua,
      daXian: {
        startAge: p.decadal.range[0],
        endAge: p.decadal.range[1],
      },
    };
  });

  const mingGongDizhi = astrolabe.earthlyBranchOfSoulPalace as Dizhi;
  const shenGongDizhi = astrolabe.earthlyBranchOfBodyPalace as Dizhi;

  const yinYangMap: Record<string, '阳男' | '阴男' | '阳女' | '阴女'> = {
    阳男: '阳男', 阴男: '阴男', 阳女: '阳女', 阴女: '阴女',
  };
  // 阴阳男女判定必须用【公历年干】，不能用 chineseDate 里立春校正后的安星年柱
  // （紫微安星年干用农历年/节气年，但阴阳男女这一项按规范固定用公历年）
  const GAN_ORDER = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
  const solarYearGanIndex = ((solarDate.year - 4) % 10 + 10) % 10;
  const solarYearGan = GAN_ORDER[solarYearGanIndex];
  const yangGan = ['甲', '丙', '戊', '庚', '壬'];
  const isYangYear = yangGan.includes(solarYearGan);
  const yinYangKey = `${isYangYear ? '阳' : '阴'}${birthInfo.gender === 'male' ? '男' : '女'}`;

  let siZhu: SiZhu;
  if (baziSiZhu) {
    siZhu = baziSiZhu;
  } else {
    const [yearGz, monthGz, dayGz, hourGz] = astrolabe.chineseDate.split(' ');
    siZhu = {
      year: { gan: yearGz[0] as Tiangan, zhi: yearGz[1] as Dizhi },
      month: { gan: monthGz[0] as Tiangan, zhi: monthGz[1] as Dizhi },
      day: { gan: dayGz[0] as Tiangan, zhi: dayGz[1] as Dizhi },
      hour: { gan: hourGz[0] as Tiangan, zhi: hourGz[1] as Dizhi },
    };
  }

  return {
    birthInfo,
    gongs,
    mingGongIndex: DIZHI_ORDER.indexOf(mingGongDizhi),
    shenGongIndex: DIZHI_ORDER.indexOf(shenGongDizhi),
    yinYang: yinYangMap[yinYangKey],
    wuXingJu: {
      name: astrolabe.fiveElementsClass,
      number: parseWuxingJuNumber(astrolabe.fiveElementsClass),
    },
    siZhu,
    lunarDate: parseLunarDate(astrolabe.lunarDate, birthInfo.year),
  };
}

function parseWuxingJuNumber(name: string): number {
  const map: Record<string, number> = { 水二局: 2, 木三局: 3, 金四局: 4, 土五局: 5, 火六局: 6 };
  return map[name] || 0;
}

// iztro lunarDate 形如 "一九七八年正月廿五"，粗解析出中文月/日供展示用
function parseLunarDate(cn: string, solarYear: number) {
  const monthMatch = cn.match(/年(.+?)月/);
  const dayMatch = cn.match(/月(.+)$/);
  return {
    year: solarYear,
    month: 0,
    day: 0,
    monthCn: monthMatch ? monthMatch[1] : undefined,
    dayCn: dayMatch ? dayMatch[1] : undefined,
  };
}
