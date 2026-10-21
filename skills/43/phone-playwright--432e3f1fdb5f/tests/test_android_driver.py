"""AndroidAdbDriver 输入通道与旋转视口单元测试。"""

import pytest
from phone_playwright.drivers.android_adb import (
    AndroidAdbDriver,
    _is_editable_class,
    parse_android_xml_hierarchy,
)
from phone_playwright.models.exceptions import PhonePlaywrightError
from phone_playwright.models.geometry import Rect
from phone_playwright.models.schema import RawNode


class ScriptedAdbDriver(AndroidAdbDriver):
    """以脚本化输出替代真实 adb 子进程的测试驱动。"""

    def __init__(self) -> None:
        super().__init__(device_id="emulator-scripted")
        self.commands: list[tuple[str, ...]] = []
        self.responses: dict[str, str] = {}
        self.tree_texts: list[str] = []

    async def _run_adb(self, *args: str, timeout: float = 15.0) -> str:
        self.commands.append(tuple(args))
        return self.responses.get(" ".join(args), "")

    async def dump_raw_tree(self) -> RawNode:
        children = [
            RawNode(
                class_name="android.widget.EditText",
                text=text,
                bounds=Rect(left=0, top=0, right=100, bottom=50),
            )
            for text in self.tree_texts
        ]
        return RawNode(
            class_name="android.widget.FrameLayout",
            bounds=Rect(left=0, top=0, right=1600, bottom=900),
            children=children,
        )


@pytest.mark.asyncio
async def test_viewport_uses_current_rotation_size():
    driver = ScriptedAdbDriver()
    driver.responses["shell dumpsys window displays"] = (
        "Display: init=900x1600 240dpi cur=1600x900 app=1600x900 rng=900x864-1600x1564"
    )

    size = await driver.get_viewport_size()

    assert size == (1600, 900)


@pytest.mark.asyncio
async def test_viewport_falls_back_to_wm_size():
    driver = ScriptedAdbDriver()
    driver.responses["shell wm size"] = "Physical size: 1080x2400"

    size = await driver.get_viewport_size()

    assert size == (1080, 2400)


@pytest.mark.asyncio
async def test_viewport_prefers_override_size_over_physical():
    """wm size 同时含 Physical 与 Override 时，应取 Override (逻辑分辨率)。

    三星云手机/模拟器常强制逻辑分辨率 (Override size) 而非物理面板尺寸，
    旧 re.search 取到首行物理尺寸导致横屏视口错位。
    """
    driver = ScriptedAdbDriver()
    driver.responses["shell wm size"] = "Physical size: 1080x1920\nOverride size: 1280x720"

    size = await driver.get_viewport_size()

    assert size == (1280, 720)


@pytest.mark.asyncio
async def test_type_text_ascii_uses_escaped_input_text():
    driver = ScriptedAdbDriver()

    await driver.type_text("hello world&")

    assert ("shell", "input", "text", "hello%sworld\\&") in driver.commands


@pytest.mark.asyncio
async def test_type_text_unicode_pastes_and_verifies_from_tree():
    driver = ScriptedAdbDriver()
    driver.tree_texts = ["无线局域网设置"]

    await driver.type_text("无线局域网设置")

    assert any("cmd clipboard" in " ".join(c) for c in driver.commands)
    paste_calls = [c for c in driver.commands if c == ("shell", "input", "keyevent", "279")]
    assert len(paste_calls) == 1


@pytest.mark.asyncio
async def test_type_text_unicode_raises_when_text_never_lands():
    driver = ScriptedAdbDriver()
    driver.tree_texts = []  # 校验始终找不到文本

    with pytest.raises(PhonePlaywrightError, match="非 ASCII 文本注入失败"):
        await driver.type_text("中文输入")

    # 通道正常的场景下应补发 Ctrl+V (CTRL_LEFT=113, V=47)
    assert ("shell", "input", "keycombination", "113", "47") in driver.commands


@pytest.mark.asyncio
async def test_type_text_unicode_no_ctrlv_retry_when_channel_unsupported():
    driver = ScriptedAdbDriver()
    driver.responses["shell cmd clipboard set text '无线局域网设置'"] = (
        "No shell command implementation."
    )
    driver.tree_texts = []

    with pytest.raises(PhonePlaywrightError, match="非 ASCII 文本注入失败"):
        await driver.type_text("无线局域网设置")

    # 通道未实现时不补发 Ctrl+V (避免把宿主剪贴板旧内容重复粘入)
    assert ("shell", "input", "keycombination", "113", "47") not in driver.commands


def test_editable_class_covers_autocompletetextview_family():
    """可编辑控件判定须覆盖类名不含 "edit" 的 AutoCompleteTextView 家族。

    三星 SearchView 的真实输入控件为 android.widget.AutoCompleteTextView，
    仅查 "edit" 子串会漏判，导致 fill / role=input 无法定位输入框。
    """
    assert _is_editable_class("android.widget.EditText")
    assert _is_editable_class("android.widget.AppCompatEditText")
    assert _is_editable_class("android.widget.AutoCompleteTextView")
    assert _is_editable_class("android.widget.MultiAutoCompleteTextView")
    assert _is_editable_class("androidx.appcompat.widget.SearchView$SearchAutoComplete")
    # 非可编辑控件不得误判
    assert not _is_editable_class("android.widget.TextView")
    assert not _is_editable_class("android.widget.Button")
    assert not _is_editable_class("android.widget.SearchView")


def test_xml_hierarchy_marks_autocompletetextview_editable():
    """端到端: uiautomator XML 中 AutoCompleteTextView 应被解析为 editable。"""
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<hierarchy rotation=\"0\">"
        '<node class="android.widget.AutoCompleteTextView" focusable="true" '
        'clickable="true" text="搜索设置项" bounds="[142,57][684,111]" />'
        "</hierarchy>"
    )

    root = parse_android_xml_hierarchy(xml, default_width=720, default_height=1280)

    field = root.children[0]
    assert field.editable is True
    assert field.text == "搜索设置项"


class TimeoutRecordingAdbDriver(AndroidAdbDriver):
    """记录每条 ADB 命令及其超时档位，并回放预设输出。"""

    def __init__(self) -> None:
        super().__init__(device_id="emulator-scripted")
        self.calls: list[tuple[tuple[str, ...], float]] = []
        self.tree_texts: list[str] = []
        # 额外回放表: 命中键的命令返回预设输出 (如剪贴板通道未实现标记)
        self.responses: dict[str, str] = {}
        self.xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<hierarchy rotation=\"0\">"
            '<node class="android.widget.Button" text="确认" bounds="[0,0][100,50]" />'
            "</hierarchy>"
        )

    async def _run_adb(self, *args: str, timeout: float = 15.0) -> str:
        self.calls.append((tuple(args), timeout))
        joined = " ".join(args)
        if joined in self.responses:
            return self.responses[joined]
        if joined.startswith("shell cat"):
            fields = "".join(
                f'<node class="android.widget.EditText" text="{txt}" bounds="[0,0][100,50]" />'
                for txt in self.tree_texts
            )
            return (
                '<?xml version="1.0" encoding="UTF-8"?><hierarchy rotation="0">'
                f'<node class="android.widget.FrameLayout" bounds="[0,0][1080,2400]">{fields}</node>'
                "</hierarchy>"
            )
        if "dumpsys" in joined:
            return "cur=1080x2400"
        return ""


@pytest.mark.asyncio
async def test_dump_raw_tree_uses_weak_network_timeout():
    """uiautomator dump 与 cat 均须使用 30s 弱网超时档，而非 15s 默认值。

    树转储是全框架最高频操作，弱网隧道下 15s 必然频繁超时。
    """
    driver = TimeoutRecordingAdbDriver()

    await driver.dump_raw_tree()

    dump_calls = [
        timeout
        for args, timeout in driver.calls
        if "uiautomator" in args and "dump" in args
    ]
    cat_calls = [timeout for args, timeout in driver.calls if args[:2] == ("shell", "cat")]
    assert dump_calls == [30.0]
    assert cat_calls == [30.0]


@pytest.mark.asyncio
async def test_type_text_ascii_newline_splits_with_enter_keyevent():
    """ASCII 注入遇换行符须按段拆分，段间以 ENTER (keyevent 66) 落键。

    `input text` 不接受换行参数 —— 直接透传会让注入静默失败或截断。
    """
    driver = TimeoutRecordingAdbDriver()

    await driver.type_text("ab\ncd")

    commands = [args for args, _ in driver.calls]
    assert ("shell", "input", "text", "ab") in commands
    assert ("shell", "input", "keyevent", "66") in commands
    assert ("shell", "input", "text", "cd") in commands
    # 换行不得原样透传进 input text 参数
    assert not any("\n" in (args[-1] if args else "") for args in commands if args[:3] == ("shell", "input", "text"))


@pytest.mark.asyncio
async def test_type_text_ascii_multiline_blank_segment_only_sends_enter():
    """连续换行 (空段) 只发 ENTER 键，不得发送空的 input text 命令。"""
    driver = TimeoutRecordingAdbDriver()

    await driver.type_text("a\n\nb")

    commands = [args for args, _ in driver.calls]
    text_args = [args for args in commands if args[:3] == ("shell", "input", "text")]
    assert text_args == [("shell", "input", "text", "a"), ("shell", "input", "text", "b")]
    enter_calls = [args for args in commands if args == ("shell", "input", "keyevent", "66")]
    assert len(enter_calls) == 2


@pytest.mark.asyncio
async def test_type_text_multiline_cjk_splits_segments_with_enter():
    """非 ASCII 多行文本须与 ASCII 路径同构: 逐段走三通道注入，段间 ENTER (66)。

    真机实证 (SM 云手机): 多行 EditText 上 AdbIME 整段含 \n 提交可落换行，
    但单行控件 (搜索框) 上换行必丢 —— 整段终态校验因此永远 miss 并误报
    "注入失败"。拆段后逐段校验在两类控件上都可靠。
    """
    driver = TimeoutRecordingAdbDriver()
    driver.tree_texts = ["甲行", "乙行"]
    # 剪贴板通道回未实现标记，强制走 AdbIME 广播通道，断言才可确定
    driver.responses = {
        "shell cmd clipboard set text '甲行'": "No shell command implementation.",
        "shell cmd clipboard set text '乙行'": "No shell command implementation.",
        "shell ime list -a": "com.android.adbkeyboard/.AdbIME",
    }

    await driver.type_text("甲行\n乙行")

    commands = [args for args, _ in driver.calls]
    broadcasts = [c for c in commands if "ADB_INPUT_B64" in " ".join(c)]
    assert len(broadcasts) == 2  # 每段一次 AdbIME 广播 (无含换行整段的第三次)
    assert ("shell", "input", "keyevent", "66") in commands
    # 含换行的整段原文不得被直接塞进任何通道参数
    assert not any("\n" in " ".join(c) for c in commands)
