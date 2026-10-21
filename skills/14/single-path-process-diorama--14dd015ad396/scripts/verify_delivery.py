#!/usr/bin/env python3
"""校验交付文件及审查哈希绑定；不生成图片，也不作视觉验收。

默认只读；除 --help 外 stdout 始终是一份 JSON。只有 --manifest 明确指定时才写报告。
PNG 解压校验有 512 MiB 的资源保护上限，不把达到上限误报为视觉问题。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys
import zlib


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_DECOMPRESSED_BYTES = 512 * 1024 * 1024
LIMITATION = "仅检查 PNG 核心块/扫描行完整性、精确画幅比例及审查哈希绑定；不渲染像素，不验证附属元数据语义、视觉质量、流程语义、版权或 QA 文案结论。"


class ValidationError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValidationError("arguments", f"命令参数无效：{message}")


def parse_ratio(value: str) -> tuple[int, int]:
    if not re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", value):
        raise ValidationError("ratio_argument", "画幅比例必须是正整数 宽:高，例如 3:4。")
    try:
        return tuple(int(part) for part in value.split(":"))
    except ValueError as exc:
        raise ValidationError("ratio_argument", "画幅比例数字过长。") from exc


def _scanline_layout(width: int, height: int, bits_per_pixel: int, interlace: int):
    # Each pass consists of rows containing one filter byte followed by packed pixels.
    passes = [(0, 0, 1, 1)] if interlace == 0 else [
        (0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4),
        (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2),
    ]
    layout = []
    for start_x, start_y, step_x, step_y in passes:
        pass_width = max(0, (width - start_x + step_x - 1) // step_x)
        pass_height = max(0, (height - start_y + step_y - 1) // step_y)
        if pass_width and pass_height:
            layout.append((1 + (pass_width * bits_per_pixel + 7) // 8, pass_height))
    return layout


def _validate_scanlines(compressed: bytes, layout: list[tuple[int, int]]) -> int:
    expected = sum(row_bytes * rows for row_bytes, rows in layout)
    if expected > MAX_DECOMPRESSED_BYTES:
        raise ValidationError("png_resource_limit", "PNG 预计解压数据超过 512 MiB 资源保护上限，未继续验证。")
    decoder = zlib.decompressobj()
    total = 0
    pass_index = row_index = row_offset = 0

    def consume(data: bytes) -> None:
        nonlocal total, pass_index, row_index, row_offset
        total += len(data)
        if total > expected:
            raise ValidationError("png_scanline_length", "PNG 解压数据多于 IHDR 尺寸要求的扫描行长度。")
        offset = 0
        while offset < len(data):
            row_bytes, rows = layout[pass_index]
            if row_offset == 0 and data[offset] > 4:
                raise ValidationError("png_filter", "PNG 扫描行包含非法过滤器类型（必须为 0–4）。")
            take = min(row_bytes - row_offset, len(data) - offset)
            offset += take
            row_offset += take
            if row_offset == row_bytes:
                row_offset = 0
                row_index += 1
                if row_index == rows:
                    pass_index += 1
                    row_index = 0

    try:
        # Bound each decompression allocation; never build a decoded raster image.
        for offset in range(0, len(compressed), 65536):
            pending = compressed[offset:offset + 65536]
            while pending:
                consume(decoder.decompress(pending, 65536))
                pending = decoder.unconsumed_tail
                if decoder.unused_data:
                    raise ValidationError("png_zlib_trailing", "PNG IDAT 在压缩流结束后仍包含多余数据。")
        # Drain output buffered when the last bounded call consumed all input.
        while True:
            tail = decoder.decompress(b"", 65536)
            if not tail:
                break
            consume(tail)
    except zlib.error as exc:
        raise ValidationError("png_decompression", f"PNG IDAT 解压失败：{exc}") from exc
    if not decoder.eof:
        raise ValidationError("png_zlib_incomplete", "PNG IDAT 压缩流未完整结束，可能已截断。")
    if total != expected:
        raise ValidationError("png_scanline_length", f"PNG 解压长度不符：预期 {expected} 字节，实际 {total} 字节。")
    return total


def validate_png(data: bytes) -> dict:
    """Validate PNG framing and raster stream without rendering or changing the image."""
    if not data.startswith(PNG_SIGNATURE):
        raise ValidationError("png_signature", "final.png 缺少完整 PNG 签名。")
    offset = len(PNG_SIGNATURE)
    chunks = []
    idat_parts = []
    header = None
    palette_seen = idat_seen = idat_ended = iend_seen = False
    while offset < len(data):
        if len(data) - offset < 12:
            raise ValidationError("png_truncated", "PNG 块头或 CRC 被截断。")
        length = struct.unpack_from(">I", data, offset)[0]
        chunk_type = data[offset + 4:offset + 8]
        if length > 0x7FFFFFFF:
            raise ValidationError("png_chunk_length", "PNG 块长度超过格式允许的上限。")
        end = offset + 12 + length
        if end > len(data):
            raise ValidationError("png_truncated", "PNG 块数据或 CRC 被截断。")
        if not re.fullmatch(rb"[A-Za-z]{4}", chunk_type) or not 65 <= chunk_type[2] <= 90:
            raise ValidationError("png_chunk_type", "PNG 块类型或保留位非法。")
        payload = data[offset + 8:offset + 8 + length]
        stored_crc = struct.unpack_from(">I", data, offset + 8 + length)[0]
        actual_crc = zlib.crc32(payload, zlib.crc32(chunk_type)) & 0xFFFFFFFF
        name = chunk_type.decode("ascii")
        if stored_crc != actual_crc:
            raise ValidationError("png_crc", f"PNG {name} 块 CRC 校验失败。")
        if not chunks and chunk_type != b"IHDR":
            raise ValidationError("png_ihdr_order", "PNG 第一个块必须是 IHDR。")
        if chunk_type == b"IHDR":
            if header is not None or length != 13:
                raise ValidationError("png_ihdr", "PNG 必须只有一个长度为 13 字节的 IHDR。")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if not (0 < width <= 0x7FFFFFFF and 0 < height <= 0x7FFFFFFF):
                raise ValidationError("png_dimensions", "PNG 宽高必须为非零且不超过 2³¹−1 的整数。")
            depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
            if color not in depths or depth not in depths[color]:
                raise ValidationError("png_ihdr", "PNG IHDR 的颜色类型与位深组合非法。")
            if compression != 0 or filtering != 0 or interlace not in (0, 1):
                raise ValidationError("png_ihdr", "PNG IHDR 的压缩、过滤或交错方法非法。")
            header = {"width": width, "height": height, "bit_depth": depth, "color_type": color, "interlace": interlace}
        elif chunk_type == b"PLTE":
            if palette_seen or idat_seen or length == 0 or length % 3 or length > 768:
                raise ValidationError("png_palette", "PNG PLTE 重复、顺序错误或长度非法。")
            if header["color_type"] in (0, 4):
                raise ValidationError("png_palette", "灰度 PNG 不允许包含 PLTE。")
            if header["color_type"] == 3 and length // 3 > 2 ** header["bit_depth"]:
                raise ValidationError("png_palette", "PNG 调色板条目超过位深允许的数量。")
            palette_seen = True
        elif chunk_type == b"IDAT":
            if idat_ended:
                raise ValidationError("png_idat_order", "PNG 的所有 IDAT 块必须连续。")
            if header["color_type"] == 3 and not palette_seen:
                raise ValidationError("png_palette", "索引色 PNG 必须在 IDAT 前包含 PLTE。")
            idat_seen = True
            idat_parts.append(payload)
        elif chunk_type == b"IEND":
            if length != 0:
                raise ValidationError("png_iend", "PNG IEND 块必须为空。")
            if not idat_seen:
                raise ValidationError("png_idat_missing", "PNG 缺少 IDAT 图像数据。")
            if end != len(data):
                raise ValidationError("png_trailing_data", "PNG IEND 后存在多余数据或重复块。")
            iend_seen = True
        elif 65 <= chunk_type[0] <= 90:
            raise ValidationError("png_unknown_critical", f"PNG 包含无法验证的关键块：{name}。")
        if idat_seen and chunk_type != b"IDAT":
            idat_ended = True
        chunks.append(name)
        offset = end
    if not iend_seen:
        raise ValidationError("png_iend_missing", "PNG 缺少 IEND 结束块。")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[header["color_type"]]
    layout = _scanline_layout(header["width"], header["height"], channels * header["bit_depth"], header["interlace"])
    decompressed = _validate_scanlines(b"".join(idat_parts), layout)
    return {**header, "chunks": chunks, "decompressed_bytes": decompressed, "integrity_verified": True}


def new_report(outputs: str | None = None) -> dict:
    return {"schema_version": 1, "ok": False, "summary": "交付验证尚未完成。", "outputs_dir": outputs,
            "image": None, "documents": {}, "review": {"provided": False, "hash_bound": False},
            "visual_review_status": "未验证", "errors": [], "limitations": [LIMITATION]}


def add_error(report: dict, error: ValidationError, path: Path | None = None) -> None:
    item = {"code": error.code, "message": str(error)}
    if path is not None:
        item["path"] = str(path)
    report["errors"].append(item)


def finalize(report: dict) -> None:
    report["ok"] = not report["errors"]
    report["summary"] = "文件交付校验通过；视觉正确性未验证。" if report["ok"] else f"文件交付校验未通过：发现 {len(report['errors'])} 项错误；视觉正确性未验证。"


def verify_delivery(outputs: Path, ratio: tuple[int, int], review_path: Path | None = None, require_all_docs: bool = False) -> dict:
    outputs = outputs.resolve()
    report = new_report(str(outputs))
    report["expected_ratio"] = f"{ratio[0]}:{ratio[1]}"
    report["require_all_docs"] = require_all_docs
    if not outputs.is_dir():
        add_error(report, ValidationError("outputs_directory", "交付目录不存在或不是目录。"), outputs)
        finalize(report)
        return report
    image_path = outputs / "final.png"
    try:
        data = image_path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        report["image"] = {"path": str(image_path), "sha256": digest, "size_bytes": len(data), "integrity_verified": False}
        report["image"].update(validate_png(data))
        width, height = report["image"]["width"], report["image"]["height"]
        common = math.gcd(width, height)
        report["image"]["actual_ratio"] = f"{width // common}:{height // common}"
        report["image"]["ratio_matches"] = width * ratio[1] == height * ratio[0]
        if not report["image"]["ratio_matches"]:
            raise ValidationError("image_ratio", f"图片画幅比例不符：实际 {width}×{height}，预期精确比例 {ratio[0]}:{ratio[1]}。")
    except OSError as exc:
        add_error(report, ValidationError("image_read", f"无法读取 final.png：{exc}"), image_path)
    except ValidationError as exc:
        add_error(report, exc, image_path)
    for name, required in (("prompt.md", True), ("scene-contract.md", require_all_docs), ("qa.md", require_all_docs)):
        path = outputs / name
        record = {"required": required, "present": path.exists(), "nonempty": False}
        report["documents"][name] = record
        if not record["present"] and not required:
            continue
        try:
            content = path.read_text(encoding="utf-8-sig")
            if not content.strip():
                raise ValidationError("document_empty", f"文档 {name} 不能为空或只有空白。")
            record["nonempty"] = True
        except (OSError, UnicodeError) as exc:
            add_error(report, ValidationError("document_read", f"无法读取非空 UTF-8 文档 {name}：{exc}"), path)
        except ValidationError as exc:
            add_error(report, exc, path)
    if review_path is not None:
        review_path = review_path.resolve()
        report["review"] = {"provided": True, "path": str(review_path), "hash_bound": False}
        try:
            review = json.loads(review_path.read_text(encoding="utf-8-sig"))
            digest = review.get("reviewed_image_sha256") if isinstance(review, dict) else None
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                raise ValidationError("review_hash_field", "审查 JSON 顶层必须提供 64 位十六进制 reviewed_image_sha256。")
            report["review"]["reviewed_image_sha256"] = digest.lower()
            if report["image"] is None:
                raise ValidationError("review_image_unavailable", "无法读取最终图片，不能校验审查哈希绑定。")
            if digest.lower() != report["image"]["sha256"]:
                raise ValidationError("review_hash_mismatch", "审查哈希与当前 final.png 不匹配；拒绝将旧图或其他图片的审查绑定到本次交付。")
            report["review"]["hash_bound"] = True
        except (OSError, UnicodeError, ValueError) as exc:
            add_error(report, ValidationError("review_read", f"无法读取有效 UTF-8 审查 JSON：{exc}"), review_path)
        except ValidationError as exc:
            add_error(report, exc, review_path)
    finalize(report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = JsonArgumentParser(description="只读校验 PNG 交付、非空文档与审查哈希；不作视觉验收。")
    parser.add_argument("outputs", help="含 final.png、prompt.md 的交付目录")
    parser.add_argument("--ratio", default="3:4", help="精确宽高比，默认 3:4（不采用近似容差）")
    parser.add_argument("--review", type=Path, help="可选审查 JSON，须含 reviewed_image_sha256")
    parser.add_argument("--require-all-docs", action="store_true", help="成品模式：同时强制 scene-contract.md 与 qa.md 非空存在；不验证其视觉断言")
    parser.add_argument("--manifest", type=Path, help="仅显式指定时写入此 JSON 报告文件；父目录须存在")
    try:
        args = parser.parse_args(argv)
        ratio = parse_ratio(args.ratio)
        report = verify_delivery(Path(args.outputs), ratio, args.review, args.require_all_docs)
        if args.manifest is not None:
            manifest = args.manifest.resolve()
            protected = [(Path(args.outputs) / name).resolve() for name in ("final.png", "prompt.md", "scene-contract.md", "qa.md")]
            if args.review is not None:
                protected.append(args.review.resolve())
            if manifest in protected or any(path.exists() and manifest.exists() and manifest.samefile(path) for path in protected):
                add_error(report, ValidationError("manifest_collision", "报告路径不能覆盖交付输入或审查文件。"), manifest)
                finalize(report)
            else:
                try:
                    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                except OSError as exc:
                    add_error(report, ValidationError("manifest_write", f"无法写入显式指定的报告：{exc}"), manifest)
                    finalize(report)
    except ValidationError as exc:
        report = new_report()
        add_error(report, exc)
        finalize(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
