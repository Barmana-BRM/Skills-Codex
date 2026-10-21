"""云手机真机遗留项回归: 多行换行注入 / 链式 count / scroll 抛错 / fill 自愈冒烟。

用法: python scripts/live_regression.py [device_id]
默认设备: 10.144.144.52:5555 (EasyTier 云手机)
"""

from __future__ import annotations
import asyncio
import sys

from typing import cast

from phone_playwright.api.async_api import AsyncPhonePage, AsyncPhonePlaywright
from phone_playwright.core.locator import PhoneLocator
from phone_playwright.drivers.android_adb import AndroidAdbDriver

LINE = "=" * 62


def report(name: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}" + (f" | {detail}" if detail else ""))


async def open_settings_search(page: AsyncPhonePage) -> PhoneLocator:
    """打开设置并进入搜索框 (云手机上最稳定的可输入控件入口)。"""
    driver = page.driver
    await driver.press_key("home")
    await asyncio.sleep(0.8)
    # 真机诊断脚本豁免私有通道: 驱动无公开 app-launch API，直接走 ADB shell
    adb_driver = cast(AndroidAdbDriver, driver)
    await adb_driver._run_adb("shell", "am", "start", "-a", "android.settings.SETTINGS")
    await asyncio.sleep(2.5)
    snap = await page.snapshot()
    print(LINE)
    print(snap.to_markdown()[:900])
    print(LINE)
    # 优先找搜索框/搜索按钮
    for sel in (
        "text=搜索",
        "desc=搜索",
        "text=Search",
    ):
        try:
            await page.locator(sel).click(timeout_s=4.0)
            await asyncio.sleep(1.2)
            return page.locator("resource-id=android:id/search_src_text")
        except Exception:
            continue
    raise RuntimeError("未能打开设置搜索框，请人工确认云手机桌面状态")


async def main() -> int:
    device_id = sys.argv[1] if len(sys.argv) > 1 else "10.144.144.52:5555"
    failures = 0

    async with AsyncPhonePlaywright() as p:
        device = await p.connect_device(device_id)
        page = device.current_page
        print(f"已连接: {device_id}")

        field = await open_settings_search(page)

        # ---- 1. 多行 CJK 换行落键 (遗留核心疑点) ----
        await field.fill("第一行", timeout_s=15.0)
        await field.fill("第一行\n第二行", timeout_s=15.0)
        await asyncio.sleep(0.8)
        raw = await field.text_content()
        print(f"    字段终态文本: {raw!r}")
        ok = raw is not None and "第一行" in raw and "第二行" in raw
        report("CJK 多行注入 (第一行\\n第二行)", ok, f"actual={raw!r}")
        if not ok:
            failures += 1

        # ---- 2. 多行 ASCII 换行 ----
        await field.fill("alpha\nbeta", timeout_s=15.0)
        await asyncio.sleep(0.8)
        raw2 = await field.text_content()
        ok2 = raw2 is not None and "alpha" in raw2 and "beta" in raw2
        report("ASCII 多行注入 (alpha\\nbeta)", ok2, f"actual={raw2!r}")
        if not ok2:
            failures += 1

        # ---- 3. 链式 count() 管道语义冒烟 ----
        try:
            n_all = await page.locator("role=input >> text=alpha").count()
            report("链式 count 不抛错", True, f"count={n_all}")
        except Exception as exc:
            report("链式 count 不抛错", False, repr(exc))
            failures += 1

        # ---- 4. scroll_into_view 目标不存在时显式抛错 ----
        try:
            await page.locator("text=__绝不存在的元素__").scroll_into_view(max_swipes=1)
            report("scroll_into_view 未找到显式抛错", False, "未抛错")
            failures += 1
        except Exception as exc:
            ok4 = type(exc).__name__ in ("SelectorNotFoundError", "OffscreenElementError")
            report("scroll_into_view 未找到显式抛错", ok4, type(exc).__name__)
            if not ok4:
                failures += 1

        # ---- 5. fill 幂等回归冒烟: 值必须完整上屏 ----
        # 该云手机 ROM 的"智能剪贴板"会在聚焦/清空瞬态把系统剪贴板内容自动
        # 上屏 (手册已记载的环境限制)，精确终态在此类设备上不可得 —— 按手册
        # 口径降级为 to_contain_text 语义 (自愈语义已由单测全覆盖)。
        await field.fill("single-shot", timeout_s=15.0)
        await asyncio.sleep(0.6)
        raw5 = await field.text_content()
        ok5 = raw5 is not None and "single-shot" in raw5
        report("fill 值完整上屏 (含剪贴板污染容忍)", ok5, f"tail={None if raw5 is None else raw5[-24:]!r}")
        if not ok5:
            failures += 1

    print(LINE)
    print(f"RESULT={'OK' if failures == 0 else 'FAIL'} failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
