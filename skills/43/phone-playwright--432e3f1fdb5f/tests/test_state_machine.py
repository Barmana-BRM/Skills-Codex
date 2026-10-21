"""状态机与可用性检查 (Actionability) 算法单测。"""

import pytest
from phone_playwright.drivers.base import BaseDriver
from phone_playwright.models.geometry import Rect
from phone_playwright.models.schema import RawNode
from phone_playwright.models.exceptions import (
    ActionabilityTimeoutError,
    SelectorNotFoundError,
    OffscreenElementError,
)
from phone_playwright.core.pruner import SemanticPruner
from phone_playwright.api.async_api import AsyncPhonePage


class MockDriver(BaseDriver):
    """用于测试可用性状态机的虚拟驱动。"""

    def __init__(self) -> None:
        super().__init__("mock-device-1")
        self.sample_step = 0
        self.tapped_coords: list[tuple[int, int]] = []
        self.long_pressed_coords: list[tuple[int, int, int]] = []
        self.typed_texts: list[str] = []
        self.pressed_keys: list[str | int] = []

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def get_viewport_size(self) -> tuple[int, int]:
        return (1080, 2400)

    async def dump_raw_tree(self) -> RawNode:
        # 模拟前 1 次采样元素在运动，第 2 次及以后静止
        self.sample_step += 1
        y_offset = 100 if self.sample_step == 1 else 150

        btn = RawNode(
            class_name="android.widget.Button",
            text="确认支付",
            bounds=Rect(left=200, top=y_offset, right=600, bottom=y_offset + 100),
            clickable=True,
            enabled=True,
        )
        return RawNode(
            class_name="android.widget.FrameLayout",
            bounds=Rect(left=0, top=0, right=1080, bottom=2400),
            children=[btn],
        )

    async def tap(self, x: int, y: int) -> None:
        self.tapped_coords.append((x, y))

    async def type_text(self, text: str) -> None:
        self.typed_texts.append(text)

    async def swipe(self, sx: int, sy: int, ex: int, ey: int, duration_ms: int = 300) -> None:
        pass

    async def long_press(self, x: int, y: int, duration_ms: int = 800) -> None:
        self.long_pressed_coords.append((x, y, duration_ms))

    async def press_key(self, key: str | int) -> None:
        self.pressed_keys.append(key)

    async def take_screenshot(self) -> bytes:
        return b"fake-png-bytes"

    async def get_current_app(self) -> tuple[str | None, str | None]:
        return "com.test.app", "MainActivity"


@pytest.mark.asyncio
async def test_auto_waiting_click_stability_check():
    mock_driver = MockDriver()
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=mock_driver, pruner=pruner)

    # 显式指定 stable_sample_count=2 检验多周期防动画滑动判定
    result = await page.locator("text=确认支付").click(timeout_s=3.0, stable_sample_count=2)

    assert result.success
    # 按钮静止在 top=150, bottom=250, left=200, right=600，中心点为 (400, 200)
    assert len(mock_driver.tapped_coords) == 1
    assert mock_driver.tapped_coords[0] == (400, 200)


@pytest.mark.asyncio
async def test_hover_and_wait_for():
    mock_driver = MockDriver()
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=mock_driver, pruner=pruner)

    # 1. 测试 hover 长按
    hover_res = await page.locator("text=确认支付").hover(timeout_s=3.0, duration_ms=500, stable_sample_count=2)
    assert hover_res.success
    assert len(mock_driver.long_pressed_coords) == 1
    assert mock_driver.long_pressed_coords[0] == (400, 200, 500)

    # 2. 测试 wait_for 显式可见性断言
    wait_res = await page.locator("text=确认支付").wait_for(state="visible", timeout_s=3.0)
    assert wait_res.success

    # 3. 测试系统键
    await page.press_back()
    await page.press_home()
    assert mock_driver.pressed_keys == ["back", "home"]


class FlakyDumpDriver(MockDriver):
    """模拟在转场过程中前 2 次 dump 抛出瞬态异常的驱动。"""

    def __init__(self) -> None:
        super().__init__()
        self.call_count = 0

    async def dump_raw_tree(self) -> RawNode:
        self.call_count += 1
        if self.call_count <= 2:
            raise RuntimeError("UiAutomator transient error: could not get idle state")
        return await super().dump_raw_tree()


@pytest.mark.asyncio
async def test_auto_waiting_survives_transient_dump_errors():
    """验证转场期瞬态 Dump 异常被有效隔离，状态机打满超时窗口并最终自愈执行。"""
    driver = FlakyDumpDriver()
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=driver, pruner=pruner)

    # 应该成功度过前 2 次抛出的 RuntimeError
    result = await page.locator("text=确认支付").click(timeout_s=3.0)
    assert result.success
    assert len(driver.tapped_coords) == 1
    assert driver.call_count > 2


class OffscreenDriver(MockDriver):
    """模拟元素在屏幕可视区域之外的驱动。"""

    async def dump_raw_tree(self) -> RawNode:
        btn = RawNode(
            class_name="android.widget.Button",
            text="底部离屏按钮",
            bounds=Rect(left=200, top=2600, right=600, bottom=2750),  # vh=2400
            clickable=True,
            enabled=True,
        )
        return RawNode(
            class_name="android.widget.FrameLayout",
            bounds=Rect(left=0, top=0, right=1080, bottom=2400),
            children=[btn],
        )


@pytest.mark.asyncio
async def test_error_barrier_offscreen_element():
    """验证屏幕外元素触发明确的 OffscreenElementError 屏障。"""
    driver = OffscreenDriver()
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=driver, pruner=pruner)

    with pytest.raises(OffscreenElementError):
        await page.locator("text=底部离屏按钮").click(timeout_s=0.3)


@pytest.mark.asyncio
async def test_error_barrier_selector_not_found():
    """验证不存在的元素触发明确的 SelectorNotFoundError。"""
    driver = MockDriver()
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=driver, pruner=pruner)

    with pytest.raises(SelectorNotFoundError):
        await page.locator("text=不存在的按钮").click(timeout_s=0.3)


@pytest.mark.asyncio
async def test_page_snapshot_with_screenshot():
    """验证 snapshot(include_screenshot=True) 契约正常回填 Base64 截图。"""
    driver = MockDriver()
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=driver, pruner=pruner)

    snap = await page.snapshot(include_screenshot=True)
    assert snap.screenshot_base64 is not None
    assert len(snap.screenshot_base64) > 0


class CountDumpDriver(MockDriver):
    def __init__(self) -> None:
        super().__init__()
        self.dumps_count = 0

    async def dump_raw_tree(self) -> RawNode:
        self.dumps_count += 1
        return await super().dump_raw_tree()


@pytest.mark.asyncio
async def test_warm_cache_instant_click():
    """验证快照后的温热缓存机制生效，避免紧随其后的首次点击发起冗余 Dump。"""
    driver = CountDumpDriver()
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=driver, pruner=pruner)

    # 1. 抓取快照 (触发 1 次 dump)
    snap = await page.snapshot()
    assert len(snap.elements) > 0
    assert driver.dumps_count == 1

    # 2. 紧接着调用 click: 应该命中 1.0s 内的温热缓存，dumps_count 不再递增
    res = await page.locator("text=确认支付").click(timeout_s=1.0)
    assert res.success
    assert driver.dumps_count == 1
    assert len(driver.tapped_coords) == 1


class ScrollableTestDriver(MockDriver):
    def __init__(self) -> None:
        super().__init__()
        self.swiped_count = 0
        self.scrolled_in = False

    async def swipe(self, sx: int, sy: int, ex: int, ey: int, duration_ms: int = 300) -> None:
        self.swiped_count += 1
        self.scrolled_in = True

    async def dump_raw_tree(self) -> RawNode:
        # 滑动前在屏幕外 (top=2500)，滑动后进入视口 (top=1200)
        top_y = 1200 if self.scrolled_in else 2500
        btn = RawNode(
            class_name="android.widget.Button",
            text="关于手机",
            bounds=Rect(left=100, top=top_y, right=900, bottom=top_y + 100),
            clickable=True,
            enabled=True,
        )
        return RawNode(
            class_name="android.widget.FrameLayout",
            bounds=Rect(left=0, top=0, right=1080, bottom=2400),
            children=[btn],
        )


@pytest.mark.asyncio
async def test_scroll_into_view_and_queries():
    """验证 scroll_into_view 自动搜寻，以及 is_visible / count / text_content 查询 API。"""
    driver = ScrollableTestDriver()
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=driver, pruner=pruner)

    locator = page.locator("text=关于手机")

    # 初始处于离屏状态
    assert await locator.is_visible() is False

    # 自动滚动搜寻进入视口
    await locator.scroll_into_view(max_swipes=3, direction="up")
    assert driver.swiped_count >= 1

    # 滚动后已在视口可见
    assert await locator.is_visible() is True
    assert await locator.count() == 1
    assert await locator.text_content() == "关于手机"


class EditableFieldDriver(MockDriver):
    """带可编辑输入框的有状态虚拟驱动，用于 fill 注入/自愈语义验证。

    junk_prefix 模拟云手机 ROM 智能剪贴板：仅在首次注入时把剪贴板内容拼接上屏，
    自愈重注后不再污染 (与实测天翼云手机行为一致)。
    """

    def __init__(self) -> None:
        super().__init__()
        self.field_text: str | None = None
        self.cleared_count = 0
        self.type_count = 0
        self.junk_prefix = ""

    async def dump_raw_tree(self) -> RawNode:
        field = RawNode(
            class_name="android.widget.EditText",
            resource_id="com.demo:id/username",
            text=self.field_text,
            bounds=Rect(left=200, top=300, right=880, bottom=420),
            editable=True,
            enabled=True,
        )
        return RawNode(
            class_name="android.widget.FrameLayout",
            bounds=Rect(left=0, top=0, right=1080, bottom=2400),
            children=[field],
        )

    async def clear_text(self) -> None:
        self.cleared_count += 1
        self.field_text = None

    async def type_text(self, text: str) -> None:
        self.type_count += 1
        base = self.field_text or ""
        self.field_text = base + self.junk_prefix + text
        self.junk_prefix = ""  # 智能剪贴板仅在首次注入时上屏


@pytest.mark.asyncio
async def test_fill_types_exactly_once_on_first_match():
    """回归防护: fill 首次注入精确命中后必须停止，不得在自愈循环外再冗余注入一次。"""
    driver = EditableFieldDriver()
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=driver, pruner=pruner)

    res = await page.locator("resource-id=com.demo:id/username").fill("hello")

    assert res.success
    assert res.verb == "fill"
    assert driver.field_text == "hello"
    assert driver.type_count == 1
    assert driver.cleared_count == 1


@pytest.mark.asyncio
async def test_fill_self_heals_when_smart_clipboard_pollutes_field():
    """验证智能剪贴板污染注入结果 (字段变为 剪贴板+新文本) 时，fill 重清重注一次自愈。"""
    driver = EditableFieldDriver()
    driver.junk_prefix = "clipboard-junk|"
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=driver, pruner=pruner)

    res = await page.locator("resource-id=com.demo:id/username").fill("hello")

    assert res.success
    assert driver.field_text == "hello"
    # 尝试 1: 清空+注入 (被污染) -> 尝试 2: 再次清空+注入 (自愈成功)
    assert driver.type_count == 2
    assert driver.cleared_count == 2


class KeyboardOcclusionDriver(EditableFieldDriver):
    """模拟键盘弹起导致输入框滚出视口、注入后无法观测的驱动。"""

    async def dump_raw_tree(self) -> RawNode:
        if self.type_count >= 1:
            return RawNode(
                class_name="android.widget.FrameLayout",
                bounds=Rect(left=0, top=0, right=1080, bottom=2400),
                children=[],
            )
        return await super().dump_raw_tree()


@pytest.mark.asyncio
async def test_fill_does_not_reinject_when_field_unobservable():
    """验证注入后字段不可观测 (实际值为 None) 时按既有语义成功返回，不盲目二次注入。"""
    driver = KeyboardOcclusionDriver()
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=driver, pruner=pruner)

    res = await page.locator("resource-id=com.demo:id/username").fill("hello")

    assert res.success
    assert driver.type_count == 1
    assert driver.cleared_count == 1


@pytest.mark.asyncio
async def test_scroll_into_view_raises_when_target_absent():
    """回归防护: 滚动打满预算后目标仍不存在时须显式抛 SelectorNotFoundError，不得静默返回。"""
    driver = MockDriver()  # 树中只有 确认支付 按钮，目标永远不存在
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=driver, pruner=pruner)

    with pytest.raises(SelectorNotFoundError):
        await page.locator("text=永不存在的元素").scroll_into_view(max_swipes=1)



class ScrollDiagnosticsDeadDriver(ScrollableTestDriver):
    """目标始终留在屏幕外、且滚动后诊断转储失效的驱动。"""

    def __init__(self) -> None:
        super().__init__()
        self.dump_calls = 0

    async def swipe(self, sx: int, sy: int, ex: int, ey: int, duration_ms: int = 300) -> None:
        pass  # 元素始终留在屏幕外

    async def dump_raw_tree(self) -> RawNode:
        self.dump_calls += 1
        if self.dump_calls > 1:
            raise RuntimeError("UiAutomator dead during scroll diagnostics")
        return await super().dump_raw_tree()


@pytest.mark.asyncio
async def test_scroll_into_view_tolerates_dead_diagnostics():
    """回归防护: 诊断转储瞬态失效时按既有容忍语义返回，不误抛裸 RuntimeError。"""
    driver = ScrollDiagnosticsDeadDriver()
    pruner = SemanticPruner()
    page = AsyncPhonePage(driver=driver, pruner=pruner)

    locator = page.locator("text=关于手机")
    result = await locator.scroll_into_view(max_swipes=1)

    assert result is locator
    assert driver.dump_calls == 2  # 滚动搜寻 1 次 + 最终诊断 1 次
