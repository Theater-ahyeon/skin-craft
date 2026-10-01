#!/usr/bin/env python3
"""Read-only image audit. Requires Pillow; never generates or edits artwork."""

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image


def project_file(root, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('asset path must be a nonempty string')
    relative = Path(value)
    if relative.is_absolute():
        raise ValueError('asset paths must be relative to root')
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('asset path escapes project root')
    if not path.is_file():
        raise ValueError(f'asset file is missing: {value}')
    return path


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def image_info(path):
    with Image.open(path) as image:
        image.load()
        rgba = image.convert('RGBA')
        info = {
            'size': list(image.size),
            'frames': getattr(image, 'n_frames', 1),
            'alpha_range_first_frame': list(rgba.getchannel('A').getextrema()),
            'format': image.format,
        }
    return info, rgba


def audit(root, manifest):
    """Return JSON-compatible results; all image and manifest access is read-only."""
    root = Path(root).resolve()
    result = {'ok': False, 'assets': [], 'errors': []}
    if not root.is_dir():
        result['errors'].append('project root is not a directory')
        return result
    try:
        payload = json.loads(Path(manifest).read_text(encoding='utf-8'))
        if not isinstance(payload, dict) or type(payload.get('version')) is not int or payload['version'] != 1:
            raise ValueError('manifest must have version 1')
        if set(payload) - {'version', 'assets'}:
            raise ValueError('unknown manifest field')
        rows = payload.get('assets')
        if not isinstance(rows, list) or not rows:
            raise ValueError('assets must be a nonempty array')
    except (OSError, ValueError) as error:
        result['errors'].append(str(error))
        return result

    allowed = {
        'id', 'runtime', 'source', 'size', 'require_transparency',
        'source_sha256', 'must_match_source_pixels',
    }
    identifiers = set()
    for index, row in enumerate(rows):
        item = {'id': row.get('id') if isinstance(row, dict) else None, 'ok': False}
        result['assets'].append(item)
        try:
            if not isinstance(row, dict) or set(row) - allowed:
                raise ValueError('invalid asset object or unknown field')
            identifier = row.get('id')
            if not isinstance(identifier, str) or not identifier.strip():
                raise ValueError('asset id must be a nonempty string')
            if identifier in identifiers:
                raise ValueError('duplicate asset id')
            identifiers.add(identifier)
            for flag in ('require_transparency', 'must_match_source_pixels'):
                if flag in row and not isinstance(row[flag], bool):
                    raise ValueError(f'{flag} must be boolean')
            size = row.get('size')
            if size is not None and (
                not isinstance(size, list) or len(size) != 2
                or any(type(value) is not int or value <= 0 for value in size)
            ):
                raise ValueError('size must be two positive integers')

            runtime = project_file(root, row.get('runtime'))
            info, rgba = image_info(runtime)
            item.update(info)
            item['runtime'] = row['runtime']
            if size is not None and info['size'] != size:
                raise ValueError('runtime dimensions do not match size')
            low, high = info['alpha_range_first_frame']
            if row.get('require_transparency') and (low == 255 or high == 0):
                raise ValueError('runtime needs visible content and transparency')

            source = project_file(root, row['source']) if 'source' in row else None
            expected_hash = row.get('source_sha256')
            if expected_hash is not None:
                if not isinstance(expected_hash, str) or not re.fullmatch(
                    r'[0-9a-fA-F]{64}', expected_hash
                ):
                    raise ValueError('source_sha256 must be a 64-digit SHA-256')
                if source is None:
                    raise ValueError('source_sha256 requires source')
                item['source_sha256'] = digest(source)
                if item['source_sha256'] != expected_hash.lower():
                    raise ValueError('source file hash changed')
            if row.get('must_match_source_pixels'):
                if source is None:
                    raise ValueError('pixel identity requires source')
                source_info, source_rgba = image_info(source)
                if info['frames'] != 1 or source_info['frames'] != 1:
                    raise ValueError('pixel identity is supported only for static images')
                # Compare full RGBA bytes: alpha-only bounding boxes can hide RGB drift.
                if rgba.size != source_rgba.size or rgba.tobytes() != source_rgba.tobytes():
                    raise ValueError('decoded source/runtime RGBA pixels differ')
                item['source_pixels_identical'] = True
            item['ok'] = True
        except (OSError, ValueError, Image.DecompressionBombError) as error:
            message = f'asset {index}: {error}'
            item['error'] = message
            result['errors'].append(message)
    result['ok'] = not result['errors']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--report', type=Path, help='optional new JSON report; never overwrite')
    args = parser.parse_args()
    result = audit(args.root, args.manifest)
    if args.report:
        try:
            # No mkdir or image rewrites. Exclusive creation protects any existing file.
            with args.report.open('x', encoding='utf-8') as stream:
                json.dump(result, stream, ensure_ascii=False, indent=2)
                stream.write('\n')
        except OSError:
            result['ok'] = False
            result['errors'].append('report must be a new file in an existing directory')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
