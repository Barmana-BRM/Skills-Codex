// 核心数据类型定义

// 生辰信息
export interface BirthInfo {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  isLunar: boolean; // 是否为农历
  gender: 'male' | 'female';
  timeZone: number; // 时区偏移，默认为8（北京时间）
}

// 天干地支
export type Tiangan = '甲' | '乙' | '丙' | '丁' | '戊' | '己' | '庚' | '辛' | '壬' | '癸';
export type Dizhi = '子' | '丑' | '寅' | '卯' | '辰' | '巳' | '午' | '未' | '申' | '酉' | '戌' | '亥';

// 干支组合
export interface GanZhi {
  gan: Tiangan;
  zhi: Dizhi;
}

// 四柱信息
export interface SiZhu {
  year: GanZhi;
  month: GanZhi;
  day: GanZhi;
  hour: GanZhi;
}

// 十神
export type ShiShen = '比肩' | '劫财' | '食神' | '伤官' | '偏财' | '正财' | '七杀' | '正官' | '偏印' | '正印' | '日主';

// 大运详情
export interface DayunDetail {
  ganZhi: GanZhi;
  startAge: number;
  startYear: number;
  endYear: number;
  ganShiShen: ShiShen;
  zhiShiShen: ShiShen;
  liuNian: { year: number; age: number; ganZhi: GanZhi }[];
}

// 八字排盘结果
export interface BaziChart {
  birthInfo: BirthInfo;
  siZhu: SiZhu;
  dayMaster: Tiangan;
  shiShen: { year: ShiShen; month: ShiShen; day: ShiShen; hour: ShiShen };
  zhangSheng?: { year?: string; month?: string; day?: string; hour?: string };
  naYin?: { year?: string; month?: string; day?: string; hour?: string };
  dayunStart: number;
  dayun: DayunDetail[];
}

// 紫微斗数十二宫信息
export interface ZiweiGongInfo {
  gong: string;
  dizhi: Dizhi;
  tiangan: Tiangan;
  mainStars: string[];
  auxStars: string[];
  sihua: { star: string; hua: string }[];
  daXian?: { startAge: number; endAge: number; isCurrent?: boolean; daXianGongName?: string };
  liuNian?: number[];
  liuNianYear?: number;
  liuNianGongName?: string;
}

// 紫微斗数排盘结果
export interface ZiweiChart {
  birthInfo: BirthInfo;
  gongs: ZiweiGongInfo[];
  mingGongIndex: number;
  shenGongIndex: number;
  yinYang?: '阳男' | '阴男' | '阳女' | '阴女';
  wuXingJu?: { name: string; number: number };
  siZhu?: SiZhu;
  lunarDate?: { year: number; month: number; day: number; monthCn?: string; dayCn?: string };
}

// 完整排盘结果
export interface ChartResult {
  bazi: BaziChart;
  ziwei: ZiweiChart;
}
