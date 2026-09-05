# -*- coding: utf-8 -*-
import os
import re

mastery_dir = 'docs/mastery'
files = [
    'README.md',
    'ARCHITECTURE.md',
    'MASTER_BOOK.md',
    'ENGINEERING_STORIES.md',
    'KNOW_YOUR_CODE.md',
    'SYSTEM_DESIGN_AND_TRADEOFFS.md',
    'INTERVIEW_PREP.md',
    'ACTIVE_RECALL.md',
    'LEARNING_ROADMAP.md',
    'LEARNING_DEPENDENCY_GRAPH.md',
    'STORY_CLAIM_EVIDENCE_MATRIX.md',
    'CURRICULUM_INTEGRITY_AUDIT.md'
]

# Ensure no hallucinations in the canonical curriculum files
forbidden_fabrications = [
    'RankingEngine',
    'SpatialService',
    'CacheManager',
    'AskMapAgent',
    '10-turn history',
    'Redis session history',
    '001_initial_property_schema'
]

for fname in files:
    fpath = os.path.join(mastery_dir, fname)
    assert os.path.exists(fpath), f'Missing {fpath}'
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    for term in forbidden_fabrications:
        matches = re.findall(r'\\b' + re.escape(term) + r'\\b', text, flags=re.IGNORECASE)
        assert len(matches) == 0, f'Found forbidden fabrication {term} in {fname}'

print('All 12 files exist and contain 0 fabricated symbols/architectures!')

with open(os.path.join(mastery_dir, 'ENGINEERING_STORIES.md'), 'r', encoding='utf-8') as f:
    st_text = f.read()

stories = re.findall(r'^### Story (\d{2,3})', st_text, flags=re.MULTILINE)
print(f'Total stories: {len(stories)}')
assert len(stories) == 100, f'Expected 100, got {len(stories)}'

statuses = re.findall(r'^\* \*\*Implementation Status\*\*:\s*\[(CURRENT|THEORY|PARTIAL|FUTURE)\]', st_text, flags=re.MULTILINE)
print(f'Total statuses: {len(statuses)}')
counts = {s: statuses.count(s) for s in set(statuses)}
print(f'Status breakdown: {counts}')
assert counts == {'CURRENT': 68, 'PARTIAL': 12, 'THEORY': 7, 'FUTURE': 13}, f'Unexpected counts: {counts}'

reality_checks = re.findall(r'#### EstateMap Reality Check', st_text)
print(f'Reality checks: {len(reality_checks)}')
assert len(reality_checks) == 100, f'Expected 100 reality checks, got {len(reality_checks)}'

print('Curriculum verification PASSED 100%!')
