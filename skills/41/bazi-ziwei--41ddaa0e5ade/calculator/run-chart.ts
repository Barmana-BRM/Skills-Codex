// 排盘单一入口 — 输入生辰, 输出完整 JSON (排盘引擎 + enrichBazi)
//
// 用法:
//   npx tsx run-chart.ts --year=2000 --month=1 --day=1 --hour=12 --minute=0 --gender=male
//   可选: --isLunar=true --timeZone=8 --output=path/to/file.json
//
// 不指定 --output 则打印到 stdout

import { createChart } from './engine/index';
import { getZhiCangGanFull } from './engine/shishen';
import { toSolarDate } from './engine/lunar-convert';
import { enrichBazi } from './bazi-enrich/enrich';
import * as fs from 'fs';

function parseArgs(): Record<string, string> {
  const args: Record<string, string> = {};
  for (const a of process.argv.slice(2)) {
    const m = a.match(/^--([^=]+)=(.*)$/);
    if (m) args[m[1]] = m[2];
  }
  return args;
}

async function main() {
  const args = parseArgs();
  const required = ['year','month','day','hour','minute','gender'];
  for (const k of required) {
    if (!args[k]) {
      console.error(`Missing required arg: --${k}=...`);
      console.error('Usage: npx tsx run-chart.ts --year=2000 --month=1 --day=1 --hour=12 --minute=0 --gender=male');
      process.exit(1);
    }
  }
  const gender = args.gender === 'male' || args.gender === 'female' ? args.gender : (args.gender === '男' ? 'male' : 'female');

  const birthInfo = {
    year: +args.year,
    month: +args.month,
    day: +args.day,
    hour: +args.hour,
    minute: +args.minute,
    isLunar: args.isLunar === 'true',
    gender: gender as 'male'|'female',
    timeZone: args.timeZone ? +args.timeZone : 8,
  };

  // Step 1: 排盘引擎层 — 四柱+紫微+大运+流年
  const chart: any = await createChart(birthInfo);

  // 附加真实公历日期（若输入为农历，下游展示"阳历"字段时不能直接照抄用户输入的农历数字）
  chart.solarDate = toSolarDate(birthInfo);

  // 附加地支藏干 (含十神)
  const dm = chart.bazi.dayMaster;
  const z = chart.bazi.siZhu;
  chart.bazi.cangGan = {
    year: getZhiCangGanFull(z.year.zhi, dm),
    month: getZhiCangGanFull(z.month.zhi, dm),
    day:   getZhiCangGanFull(z.day.zhi, dm),
    hour:  getZhiCangGanFull(z.hour.zhi, dm),
  };

  // 补 endAge 字段 (下游脚本会查 endAge)
  if (chart.bazi.dayun && Array.isArray(chart.bazi.dayun)) {
    for (const d of chart.bazi.dayun) {
      if (d.startAge !== undefined && d.endAge === undefined) {
        d.endAge = d.startAge + 9;
      }
    }
  }

  // Step 2: enrichBazi 补层 — 格局/旺衰/调候/刑冲合害/盖头
  const siZhuForEnrich = {
    '年': chart.bazi.siZhu.year,
    '月': chart.bazi.siZhu.month,
    '日': chart.bazi.siZhu.day,
    '时': chart.bazi.siZhu.hour,
  };
  chart.bazi.enrichment = enrichBazi(siZhuForEnrich);

  const json = JSON.stringify(chart, null, 2);

  if (args.output) {
    fs.writeFileSync(args.output, json, 'utf-8');
    console.error(`Chart written to ${args.output}`);
  } else {
    process.stdout.write(json);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
