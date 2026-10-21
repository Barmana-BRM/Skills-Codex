// 十神 / 地支藏干 —— 独立实现（基于五行生克公式推导，不依赖任何第三方排盘库）
//
// 十神推导原理（标准命理公式，非某一具体代码库的表达）：
//   1. 取日主与目标天干的五行、阴阳
//   2. 五行相同 -> 比肩(同阴阳)/劫财(异阴阳)
//      日主生我  -> 食神(同阴阳)/伤官(异阴阳)   [我生者]
//      我生日主  -> 偏财(同阴阳)/正财(异阴阳)   [我克者]
//      日主克我  -> 七杀(同阴阳)/正官(异阴阳)   [克我者]
//      我克日主  -> 偏印(同阴阳)/正印(异阴阳)   [生我者]

const GAN_WUXING: Record<string, string> = {
  甲: '木', 乙: '木', 丙: '火', 丁: '火', 戊: '土', 己: '土',
  庚: '金', 辛: '金', 壬: '水', 癸: '水',
};

const GAN_YINYANG: Record<string, '阳' | '阴'> = {
  甲: '阳', 乙: '阴', 丙: '阳', 丁: '阴', 戊: '阳', 己: '阴',
  庚: '阳', 辛: '阴', 壬: '阳', 癸: '阴',
};

// 五行相生：木生火、火生土、土生金、金生水、水生木
const SHENG: Record<string, string> = { 木: '火', 火: '土', 土: '金', 金: '水', 水: '木' };
// 五行相克：木克土、土克水、水克火、火克金、金克木
const KE: Record<string, string> = { 木: '土', 土: '水', 水: '火', 火: '金', 金: '木' };

export function getShiShen(dayMasterGan: string, targetGan: string): string {
  const dmWx = GAN_WUXING[dayMasterGan];
  const tgWx = GAN_WUXING[targetGan];
  const sameYinYang = GAN_YINYANG[dayMasterGan] === GAN_YINYANG[targetGan];

  if (dmWx === tgWx) return sameYinYang ? '比肩' : '劫财';
  if (SHENG[dmWx] === tgWx) return sameYinYang ? '食神' : '伤官'; // 日主生它
  if (KE[dmWx] === tgWx) return sameYinYang ? '偏财' : '正财';   // 日主克它
  if (KE[tgWx] === dmWx) return sameYinYang ? '七杀' : '正官';   // 它克日主
  if (SHENG[tgWx] === dmWx) return sameYinYang ? '偏印' : '正印'; // 它生日主
  throw new Error(`无法判定十神: ${dayMasterGan} vs ${targetGan}`);
}

// 地支藏干（标准分野表，公共命理知识）
const DIZHI_CANGGAN: Record<string, string[]> = {
  子: ['癸'],
  丑: ['己', '癸', '辛'],
  寅: ['甲', '丙', '戊'],
  卯: ['乙'],
  辰: ['戊', '乙', '癸'],
  巳: ['丙', '戊', '庚'],
  午: ['丁', '己'],
  未: ['己', '丁', '乙'],
  申: ['庚', '壬', '戊'],
  酉: ['辛'],
  戌: ['戊', '辛', '丁'],
  亥: ['壬', '甲'],
};

export function getZhiCangGanFull(zhi: string, dayMasterGan: string): Array<{ gan: string; shiShen: string }> {
  const list = DIZHI_CANGGAN[zhi] || [];
  return list.map((gan) => ({ gan, shiShen: getShiShen(dayMasterGan, gan) }));
}
