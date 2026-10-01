"""Check package metadata, linked references and declared helper without host dependencies."""

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / '.agents/skills/skin-craft'
entry = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
match = re.match(r'^---\n(.*?)\n---', entry, re.S)
assert match, 'missing frontmatter'
metadata = yaml.safe_load(match.group(1))
assert metadata['name'] == SKILL.name
assert isinstance(metadata['description'], str) and 0 < len(metadata['description']) <= 1024
ui = yaml.safe_load((SKILL / 'agents/openai.yaml').read_text(encoding='utf-8'))
assert '$skin-craft' in ui['interface']['default_prompt']
assert 25 <= len(ui['interface']['short_description']) <= 64
assert ui.get('policy', {}).get('allow_implicit_invocation', True) is True
for document in [ROOT / 'README.md', *SKILL.rglob('*.md')]:
    for target in re.findall(r'\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
        if target.startswith(('https://', 'http://', '#')):
            continue
        target_path = (document.parent / target.split('#')[0]).resolve()
        assert target_path.is_relative_to(ROOT), f'outside package: {target}'
        assert target_path.exists(), f'missing reference: {document.name} -> {target}'
assert (SKILL / 'scripts/audit_assets.py').is_file()
print('Skill metadata, invocation, references and helper verified.')
