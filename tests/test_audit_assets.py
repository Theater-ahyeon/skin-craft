"""Behavioral tests use disposable synthetic files, never project artwork."""

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / '.agents/skills/skin-craft/scripts/audit_assets.py'
spec = importlib.util.spec_from_file_location('audit_assets', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        image = Image.new('RGBA', (8, 8), (24, 37, 86, 255))
        image.putpixel((0, 0), (0, 0, 0, 0))
        image.save(self.root / 'source.png')
        image.save(self.root / 'runtime.webp', lossless=True, exact=True)
        self.manifest = self.root / 'assets.json'
        self.row = {
            'id': 'scene', 'source': 'source.png', 'runtime': 'runtime.webp',
            'size': [8, 8], 'require_transparency': True,
            'must_match_source_pixels': True,
        }

    def tearDown(self):
        self.temp.cleanup()

    def write_manifest(self, rows=None):
        self.manifest.write_text(json.dumps({
            'version': 1, 'assets': [self.row] if rows is None else rows,
        }), encoding='utf-8')

    def run_audit(self):
        self.write_manifest()
        return module.audit(self.root, self.manifest)

    def test_lossless_conversion_passes_without_modifying_files(self):
        self.row['source_sha256'] = hashlib.sha256((self.root / 'source.png').read_bytes()).hexdigest()
        self.write_manifest()
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        result = module.audit(self.root, self.manifest)
        self.assertTrue(result['ok'], result)
        self.assertTrue(result['assets'][0]['source_pixels_identical'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_detects_rgb_change_even_with_unchanged_alpha(self):
        with Image.open(self.root / 'source.png') as image:
            image.putpixel((4, 4), (24, 38, 86, 255))
            image.save(self.root / 'runtime.webp', lossless=True, exact=True)
        result = self.run_audit()
        self.assertFalse(result['ok'])
        self.assertIn('RGBA pixels differ', result['errors'][0])

    def test_detects_wrong_dimensions(self):
        self.row['size'] = [9, 8]
        self.assertFalse(self.run_audit()['ok'])

    def test_rejects_opaque_and_empty_cutouts(self):
        for alpha in (255, 0):
            with self.subTest(alpha=alpha):
                Image.new('RGBA', (8, 8), (24, 37, 86, alpha)).save(self.root / 'runtime.webp', lossless=True)
                self.assertFalse(self.run_audit()['ok'])

    def test_detects_changed_source_hash(self):
        self.row['source_sha256'] = '0' * 64
        self.assertFalse(self.run_audit()['ok'])

    def test_rejects_path_escape(self):
        self.row['runtime'] = '../outside.png'
        result = self.run_audit()
        self.assertFalse(result['ok'])
        self.assertIn('escapes project root', result['errors'][0])

    def test_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / 'outside.png'
            Image.new('RGB', (8, 8)).save(target)
            try:
                (self.root / 'link.png').symlink_to(target)
            except OSError:
                self.skipTest('OS does not allow creating symlinks')
            self.row['runtime'] = 'link.png'
            self.assertFalse(self.run_audit()['ok'])

    def test_rejects_missing_and_invalid_files(self):
        for value in ('missing.png', 'assets.json'):
            with self.subTest(path=value):
                self.row['runtime'] = value
                self.assertFalse(self.run_audit()['ok'])

    def test_rejects_duplicate_ids_and_mistyped_flags(self):
        self.write_manifest([self.row, self.row])
        self.assertFalse(module.audit(self.root, self.manifest)['ok'])
        self.row['require_transparency'] = 'true'
        self.assertFalse(self.run_audit()['ok'])

    def test_animated_pixel_identity_is_not_a_first_frame_claim(self):
        frames = [Image.new('RGB', (8, 8), color) for color in ('red', 'blue')]
        frames[0].save(self.root / 'animation.gif', save_all=True, append_images=frames[1:])
        self.row['runtime'] = 'animation.gif'
        self.row['require_transparency'] = False
        result = self.run_audit()
        self.assertFalse(result['ok'])
        self.assertIn('only for static images', result['errors'][0])

    def test_cli_exit_codes_and_existing_report_protection(self):
        self.write_manifest()
        command = [sys.executable, str(SCRIPT), '--root', str(self.root), '--manifest', str(self.manifest)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        source_before = (self.root / 'source.png').read_bytes()
        result = subprocess.run(command + ['--report', str(self.root / 'source.png')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(source_before, (self.root / 'source.png').read_bytes())
        result = subprocess.run(command + ['--report', str(self.root / 'report.json')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(json.loads((self.root / 'report.json').read_text())['ok'])


if __name__ == '__main__':
    unittest.main()
