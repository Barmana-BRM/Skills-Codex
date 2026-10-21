// 用 7 个标准案例验证排盘引擎(mingpan+iztro)输出准确性
import * as fs from 'fs';
import * as path from 'path';
import { createChart } from './index';

const CASES = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];
const FIXTURE_DIR = path.join(__dirname, '..', '..', 'fixtures');

function gz(g: { gan: string; zhi: string }) {
  return g.gan + g.zhi;
}

async function run() {
  let totalChecks = 0;
  let totalPass = 0;
  const failures: string[] = [];

  for (const id of CASES) {
    const fixture = JSON.parse(fs.readFileSync(path.join(FIXTURE_DIR, `case-${id}.json`), 'utf-8'));
    const birthInfo = fixture.bazi.birthInfo;
    const result = await createChart(birthInfo);

    const checks: [string, any, any][] = [
      [`${id} 八字-年柱`, gz(result.bazi.siZhu.year), gz(fixture.bazi.siZhu.year)],
      [`${id} 八字-月柱`, gz(result.bazi.siZhu.month), gz(fixture.bazi.siZhu.month)],
      [`${id} 八字-日柱`, gz(result.bazi.siZhu.day), gz(fixture.bazi.siZhu.day)],
      [`${id} 八字-时柱`, gz(result.bazi.siZhu.hour), gz(fixture.bazi.siZhu.hour)],
      [`${id} 日主`, result.bazi.dayMaster, fixture.bazi.dayMaster],
      [`${id} 纳音-年`, result.bazi.naYin?.year, fixture.bazi.naYin.year],
      [`${id} 纳音-时`, result.bazi.naYin?.hour, fixture.bazi.naYin.hour],
      [`${id} 长生-年`, result.bazi.zhangSheng?.year, fixture.bazi.zhangSheng.year],
      [`${id} 长生-日`, result.bazi.zhangSheng?.day, fixture.bazi.zhangSheng.day],
      [`${id} 起运岁数(首步大运)`, result.bazi.dayunStart, fixture.bazi.dayun[0].startAge],
      [`${id} 大运1-干支`, gz(result.bazi.dayun[0].ganZhi), gz(fixture.bazi.dayun[0].ganZhi)],
      [`${id} 紫微-阴阳`, result.ziwei.yinYang, fixture.ziwei.yinYang],
      [`${id} 紫微-五行局`, result.ziwei.wuXingJu?.name, fixture.ziwei.wuXingJu.name],
    ];

    const fixtureMingGong = fixture.ziwei.gongs.find((g: any) => g.gong === '命宫');
    const resultMingGong = result.ziwei.gongs.find((g: any) => g.gong === '命宫');
    checks.push([`${id} 命宫-干支`, resultMingGong.tiangan + resultMingGong.dizhi, fixtureMingGong.tiangan + fixtureMingGong.dizhi]);
    checks.push([`${id} 命宫-主星`, JSON.stringify(resultMingGong.mainStars), JSON.stringify(fixtureMingGong.mainStars)]);
    checks.push([`${id} 命宫-大限`, `${resultMingGong.daXian.startAge}-${resultMingGong.daXian.endAge}`, `${fixtureMingGong.daXian.startAge}-${fixtureMingGong.daXian.endAge}`]);

    for (const [label, actual, expected] of checks) {
      totalChecks++;
      const pass = actual === expected;
      if (pass) totalPass++;
      else failures.push(`  ✗ ${label}: got "${actual}", expected "${expected}"`);
    }
  }

  console.log(`\n=== 验证结果: ${totalPass}/${totalChecks} 通过 ===\n`);
  if (failures.length) {
    console.log('失败项:');
    console.log(failures.join('\n'));
  } else {
    console.log('全部通过！');
  }
}

run().catch((e) => {
  console.error('验证脚本出错:', e);
  process.exit(1);
});
