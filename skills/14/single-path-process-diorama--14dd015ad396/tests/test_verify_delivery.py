"""Dependency-free fixtures are synthetic PNGs, not visual review evidence."""

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_delivery.py"
SPEC = importlib.util.spec_from_file_location("verify_delivery", SCRIPT)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


def chunk(kind, payload=b""):
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def make_png(width=3, height=4, raw=None, compressed=None, suffix=None, interlace=0, color=2, depth=8):
    header = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, depth, color, 0, 0, interlace))
    if compressed is None:
        if raw is None:
            layout = VERIFIER._scanline_layout(width, height, {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color] * depth, interlace)
            raw = b"".join((b"\0" * row_bytes) * rows for row_bytes, rows in layout)
        compressed = zlib.compress(raw)
    if suffix is None:
        suffix = chunk(b"IEND")
    palette = chunk(b"PLTE", b"\x00\x00\x00\xff\xff\xff") if color == 3 else b""
    return VERIFIER.PNG_SIGNATURE + header + palette + chunk(b"IDAT", compressed) + suffix


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.image = self.root / "final.png"
        self.image.write_bytes(make_png())
        (self.root / "prompt.md").write_text("实际生成提示词", encoding="utf-8")

    def verify(self, review=None, ratio=(3, 4)):
        return VERIFIER.verify_delivery(self.root, ratio, review)

    def assert_error(self, code, report=None):
        report = self.verify() if report is None else report
        self.assertFalse(report["ok"])
        self.assertIn(code, [error["code"] for error in report["errors"]])

    def review_file(self, digest):
        path = self.root / "review.json"
        path.write_text(json.dumps({"reviewed_image_sha256": digest, "visual_quality": "通过"}), encoding="utf-8")
        return path

    def run_cli(self, *extra):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = VERIFIER.main([str(self.root), *extra])
        return result, json.loads(output.getvalue())

    def test_valid_png_and_optional_documents_absent(self):
        report = self.verify()
        self.assertTrue(report["ok"])
        self.assertEqual(report["image"]["width"], 3)
        self.assertEqual(report["image"]["height"], 4)
        self.assertEqual(report["image"]["decompressed_bytes"], 40)
        self.assertEqual(report["image"]["sha256"], hashlib.sha256(self.image.read_bytes()).hexdigest())
        self.assertEqual(report["visual_review_status"], "未验证")
        self.assertFalse(report["review"]["hash_bound"])

    def test_complete_delivery_requires_all_documents(self):
        code, report = self.run_cli("--require-all-docs")
        self.assertEqual(code, 1)
        self.assertTrue(report["require_all_docs"])
        self.assertTrue(report["documents"]["scene-contract.md"]["required"])
        self.assertTrue(report["documents"]["qa.md"]["required"])
        self.assertEqual(len(report["errors"]), 2)

    def test_complete_delivery_accepts_all_documents_without_visual_claim(self):
        for name in ("scene-contract.md", "qa.md"):
            (self.root / name).write_text("文档内容", encoding="utf-8")
        code, report = self.run_cli("--require-all-docs")
        self.assertEqual(code, 0)
        self.assertEqual(report["visual_review_status"], "未验证")

    def test_complete_delivery_rejects_empty_qa(self):
        (self.root / "scene-contract.md").write_text("场景契约", encoding="utf-8")
        (self.root / "qa.md").write_text("  ", encoding="utf-8")
        code, report = self.run_cli("--require-all-docs")
        self.assertEqual(code, 1)
        self.assert_error("document_empty", report)

    def test_crc_corruption(self):
        data = bytearray(make_png())
        data[29] ^= 1
        self.image.write_bytes(data)
        self.assert_error("png_crc")

    def test_truncated_chunk(self):
        self.image.write_bytes(make_png()[:-3])
        self.assert_error("png_truncated")

    def test_no_iend(self):
        self.image.write_bytes(make_png(suffix=b""))
        self.assert_error("png_iend_missing")

    def test_decompression_failure_with_valid_chunk_crc(self):
        self.image.write_bytes(make_png(compressed=b"not-zlib"))
        self.assert_error("png_decompression")

    def test_incomplete_zlib(self):
        self.image.write_bytes(make_png(compressed=zlib.compress(b"\0" * 40)[:-2]))
        self.assert_error("png_zlib_incomplete")

    def test_ratio_mismatch(self):
        self.image.write_bytes(make_png(width=4, height=3))
        self.assert_error("image_ratio")

    def test_empty_prompt(self):
        (self.root / "prompt.md").write_text(" \n\t", encoding="utf-8")
        self.assert_error("document_empty")

    def test_missing_prompt(self):
        (self.root / "prompt.md").unlink()
        self.assert_error("document_read")

    def test_optional_document_empty_is_rejected(self):
        (self.root / "qa.md").write_text("", encoding="utf-8")
        self.assert_error("document_empty")

    def test_invalid_document_utf8(self):
        (self.root / "scene-contract.md").write_bytes(b"\xff")
        self.assert_error("document_read")

    def test_old_review_hash_rejected(self):
        report = self.verify(self.review_file("0" * 64))
        self.assert_error("review_hash_mismatch", report)
        self.assertFalse(report["review"]["hash_bound"])

    def test_correct_review_binds_but_does_not_verify_visuals(self):
        digest = hashlib.sha256(self.image.read_bytes()).hexdigest()
        report = self.verify(self.review_file(digest.upper()))
        self.assertTrue(report["ok"])
        self.assertTrue(report["review"]["hash_bound"])
        self.assertEqual(report["visual_review_status"], "未验证")

    def test_review_hash_must_be_valid_hex(self):
        self.assert_error("review_hash_field", self.verify(self.review_file("z" * 64)))

    def test_review_json_must_be_object(self):
        path = self.root / "review.json"
        path.write_text("[]", encoding="utf-8")
        self.assert_error("review_hash_field", self.verify(path))

    def test_invalid_review_json(self):
        path = self.root / "review.json"
        path.write_text("not-json", encoding="utf-8")
        self.assert_error("review_read", self.verify(path))

    def test_bad_signature(self):
        self.image.write_bytes(b"not-a-png")
        self.assert_error("png_signature")

    def test_zero_dimensions(self):
        self.image.write_bytes(make_png(width=0, compressed=zlib.compress(b"")))
        self.assert_error("png_dimensions")

    def test_trailing_data_after_iend(self):
        self.image.write_bytes(make_png() + b"untrusted suffix")
        self.assert_error("png_trailing_data")

    def test_extra_compressed_stream(self):
        self.image.write_bytes(make_png(compressed=zlib.compress(b"\0" * 40) + zlib.compress(b"")))
        self.assert_error("png_zlib_trailing")

    def test_scanline_length_mismatch(self):
        self.image.write_bytes(make_png(raw=b"\0" * 39))
        self.assert_error("png_scanline_length")

    def test_scanline_too_long(self):
        self.image.write_bytes(make_png(raw=b"\0" * 41))
        self.assert_error("png_scanline_length")

    def test_invalid_scanline_filter(self):
        self.image.write_bytes(make_png(raw=b"\5" + b"\0" * 39))
        self.assert_error("png_filter")

    def test_valid_adam7(self):
        self.image.write_bytes(make_png(interlace=1))
        self.assertTrue(self.verify()["ok"])

    def test_large_scanlines_cross_decompression_buffer(self):
        self.image.write_bytes(make_png(width=600, height=800))
        self.assertTrue(self.verify()["ok"])

    def test_indexed_png(self):
        self.image.write_bytes(make_png(color=3, depth=1))
        self.assertTrue(self.verify()["ok"])

    def test_indexed_png_requires_palette(self):
        data = make_png(color=3, depth=1)
        self.image.write_bytes(data[:33] + data[51:])
        self.assert_error("png_palette")

    def test_ihdr_must_be_first(self):
        self.image.write_bytes(VERIFIER.PNG_SIGNATURE + chunk(b"tEXt", b"k\0v") + make_png()[8:])
        self.assert_error("png_ihdr_order")

    def test_ihdr_must_be_unique(self):
        data = make_png()
        self.image.write_bytes(data[:33] + data[8:33] + data[33:])
        self.assert_error("png_ihdr")

    def test_unknown_critical_chunk_rejected(self):
        data = make_png()
        self.image.write_bytes(data[:33] + chunk(b"ABCD") + data[33:])
        self.assert_error("png_unknown_critical")

    def test_resource_limit_is_explicit(self):
        self.image.write_bytes(make_png(width=30000, height=40000, compressed=zlib.compress(b"")))
        self.assert_error("png_resource_limit")

    def test_separate_idat_blocks_must_be_contiguous(self):
        data = make_png()
        compressed = zlib.compress(b"\0" * 40)
        self.image.write_bytes(data[:33] + chunk(b"IDAT", compressed[:3]) + chunk(b"tEXt", b"key\0value") + chunk(b"IDAT", compressed[3:]) + chunk(b"IEND"))
        self.assert_error("png_idat_order")

    def test_contiguous_idat_blocks_are_valid(self):
        data = make_png()
        compressed = zlib.compress(b"\0" * 40)
        self.image.write_bytes(data[:33] + chunk(b"IDAT", compressed[:3]) + chunk(b"IDAT", compressed[3:]) + chunk(b"IEND"))
        self.assertTrue(self.verify()["ok"])

    def test_cli_is_read_only_by_default(self):
        before = {path.name: path.read_bytes() for path in self.root.iterdir()}
        code, report = self.run_cli("--ratio", "3:4")
        self.assertEqual(code, 0)
        self.assertTrue(report["ok"])
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.root.iterdir()})

    def test_cli_only_writes_requested_manifest(self):
        manifest = self.root / "verification.json"
        code, report = self.run_cli("--manifest", str(manifest))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(manifest.read_text(encoding="utf-8")), report)

    def test_manifest_cannot_overwrite_input(self):
        before = self.image.read_bytes()
        code, report = self.run_cli("--manifest", str(self.image))
        self.assertEqual(code, 1)
        self.assert_error("manifest_collision", report)
        self.assertEqual(self.image.read_bytes(), before)

    def test_manifest_cannot_overwrite_review(self):
        review = self.review_file(hashlib.sha256(self.image.read_bytes()).hexdigest())
        before = review.read_bytes()
        code, report = self.run_cli("--review", str(review), "--manifest", str(review))
        self.assertEqual(code, 1)
        self.assert_error("manifest_collision", report)
        self.assertEqual(review.read_bytes(), before)

    def test_manifest_cannot_overwrite_hardlinked_input(self):
        alias = self.root / "report.json"
        alias.hardlink_to(self.image)
        before = self.image.read_bytes()
        code, report = self.run_cli("--manifest", str(alias))
        self.assertEqual(code, 1)
        self.assert_error("manifest_collision", report)
        self.assertEqual(self.image.read_bytes(), before)

    def test_manifest_parent_must_exist(self):
        code, report = self.run_cli("--manifest", str(self.root / "missing" / "report.json"))
        self.assertEqual(code, 1)
        self.assert_error("manifest_write", report)

    def test_invalid_ratio_still_returns_json(self):
        code, report = self.run_cli("--ratio", "3/4")
        self.assertEqual(code, 1)
        self.assert_error("ratio_argument", report)

    def test_invalid_arguments_still_return_json(self):
        code, report = self.run_cli("--unknown")
        self.assertEqual(code, 1)
        self.assert_error("arguments", report)


if __name__ == "__main__":
    unittest.main()
