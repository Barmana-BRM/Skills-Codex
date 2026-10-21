import base64
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/prepare_workbench_request.py'
spec = importlib.util.spec_from_file_location('prepare_request', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
prepare = module.prepare


class RequestTests(unittest.TestCase):
    def test_ratio_is_applied_even_when_prompt_has_no_ratio(self):
        for quality, expected in [('standard', (864, 1536)), ('high', (1152, 2048))]:
            body, info = prepare({'rewritten_prompt': 'A vintage baker portrait.', 'wh_ratio': '9:16'}, quality=quality, seed=0)
            self.assertEqual((body['width'], body['height']), expected)
            self.assertNotIn('sizeMode', body)
            self.assertEqual(body['prompt'], 'A vintage baker portrait.')
            self.assertFalse(info['submitted'])

    def test_manual_ab_canvas_overrides_suggested_ratio(self):
        body, info = prepare({'rewritten_prompt': '咖啡海报，标题"桂花拿铁"，价格"¥28"。', 'wh_ratio': '2:3'}, width=2048, height=2048, seed=0)
        self.assertEqual((body['width'], body['height']), (2048, 2048))
        self.assertEqual(info['size_source'], 'explicit-override')
        self.assertEqual(json.loads(json.dumps(body, ensure_ascii=False))['prompt'], '咖啡海报，标题"桂花拿铁"，价格"¥28"。')

    def test_common_ratios_stay_exact_and_legal(self):
        for ratio in ['1:1', '2:3', '3:2', '4:3', '3:4', '9:16', '16:9', '21:9', '1:8', '8:1']:
            for quality in ['standard', 'high']:
                body, _ = prepare({'rewritten_prompt': 'A scene', 'wh_ratio': ratio}, quality=quality)
                a, b = map(int, ratio.split(':'))
                self.assertEqual(body['width'] * b, body['height'] * a)
                self.assertTrue(module.legal_dimension(body['width']))
                self.assertTrue(module.legal_dimension(body['height']))

    def test_unusual_ratio_discloses_approximation(self):
        _, info = prepare({'rewritten_prompt': 'A scene', 'wh_ratio': '191:100'})
        self.assertTrue(info['approximate'])
        self.assertLess(abs(info['width'] / info['height'] - 1.91), .03)

    def test_edit_preserves_reference_bytes_and_has_no_ignored_size(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ref.png'
            raw = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jFocAAAAASUVORK5CYII=')
            path.write_bytes(raw)
            body, info = prepare({'rewritten_prompt': '把图片中的头巾改为红色，保持其他部分不变。', 'wh_ratio': '', 'ratio_follow': '<image1>'}, mode='edit', reference=path)
            self.assertEqual(body['steps'], 40)
            self.assertEqual(base64.b64decode(body['image'].split(',')[1]), raw)
            self.assertEqual(path.read_bytes(), raw)
            self.assertNotIn('width', body)
            self.assertEqual(info['output_sizing'], 'reference-aspect-1024-area')

    def test_unsupported_edit_ratio_is_not_silently_dropped(self):
        with self.assertRaisesRegex(ValueError, 'cannot apply a new output ratio'):
            prepare({'rewritten_prompt': '扩图', 'wh_ratio': '16:9', 'ratio_follow': ''}, mode='edit')

    def test_multi_reference_is_rejected_for_single_reference_backend(self):
        for data in [
            {'rewritten_prompt': '把<image2>的人放进<image1>', 'wh_ratio': '', 'ratio_follow': '<image1>'},
            {'rewritten_prompt': '改色', 'wh_ratio': '', 'ratio_follow': '<image2>'},
        ]:
            with self.assertRaisesRegex(ValueError, 'exactly one reference'):
                prepare(data, mode='edit')

    def test_invalid_schema_and_ratio_fail_before_any_output(self):
        for data in [[], {}, {'rewritten_prompt': '', 'wh_ratio': '1:1'},
                     {'rewritten_prompt': 'x', 'wh_ratio': 1},
                     {'rewritten_prompt': 'x', 'wh_ratio': '0:1'},
                     {'rewritten_prompt': 'x', 'wh_ratio': '100:1'},
                     {'rewritten_prompt': 'x', 'wh_ratio': '9:16', 'ratio_follow': '<image1>'},
                     {'rewritten_prompt': 'x', 'wh_ratio': '9:16', 'api_key': 'placeholder'}]:
            with self.assertRaises(ValueError):
                prepare(data)

    def test_explicit_sizes_and_numbers_are_validated(self):
        data = {'rewritten_prompt': 'cat', 'wh_ratio': '1:1'}
        for options in [{'width': 1080, 'height': 1920}, {'width': 1024}, {'width': 4096, 'height': 4096}, {'steps': 0}, {'steps': True}, {'seed': -1}, {'seed': True}, {'seed': 9007199254740992}]:
            with self.assertRaises(ValueError):
                prepare(data, **options)

    def test_cli_creates_valid_private_request_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rewrite, output = root / 'rewrite.json', root / 'request.json'
            rewrite.write_text(json.dumps({'rewritten_prompt': 'A cat.', 'wh_ratio': '9:16'}))
            args = [sys.executable, str(SCRIPT), str(rewrite), '--out', str(output), '--seed', '0']
            done = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertFalse(json.loads(done.stdout)['submitted'])
            self.assertEqual(json.loads(output.read_text())['width'], 864)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            before = output.read_bytes()
            again = subprocess.run(args, capture_output=True, text=True)
            self.assertNotEqual(again.returncode, 0)
            self.assertEqual(output.read_bytes(), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
