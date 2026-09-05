# -*- coding: utf-8 -*-
"""
Verification suite for EstateMap AI Backend Mastery Curriculum.
"""
import os
import re

mastery_dir = "docs/mastery"
files = [
    "README.md",
    "ARCHITECTURE.md",
    "BACKEND_MASTER_BOOK.md",
    "BACKEND_ENGINEERING_STORIES.md",
    "SYSTEM_DESIGN.md",
    "INTERVIEW_PREP.md",
    "ACTIVE_RECALL.md",
    "BACKEND_ROADMAP.md",
    "BACKEND_DEPENDENCY_GRAPH.md"
]

for fname in files:
    fpath = os.path.join(mastery_dir, fname)
    assert os.path.exists(fpath), f"Missing {fpath}"

print("All 9 canonical backend curriculum files exist on disk!")

with open(os.path.join(mastery_dir, "BACKEND_ENGINEERING_STORIES.md"), "r", encoding="utf-8") as f:
    st_text = f.read()

stories = re.findall(r"^### Story (\d{2,3})", st_text, flags=re.MULTILINE)
print(f"Total backend stories: {len(stories)}")
assert len(stories) == 48, f"Expected 48 backend stories, got {len(stories)}"

essential_count = len(re.findall(r"\[ESSENTIAL\]", st_text))
important_count = len(re.findall(r"\[IMPORTANT\]", st_text))
print(f"Essential stories: {essential_count}, Important stories: {important_count}")
# 37 stories are ESSENTIAL, 11 are IMPORTANT
assert essential_count >= 37, f"Expected at least 37 essential, got {essential_count}"
assert important_count >= 11, f"Expected at least 11 important, got {important_count}"

modules = re.findall(r"^## Module \d{2}:", st_text, flags=re.MULTILINE)
print(f"Total modules: {len(modules)}")
assert len(modules) == 15, f"Expected 15 modules, got {len(modules)}"

# Check for banned patterns across all 9 files
banned_patterns = [
    r'zero hallucination',
    r'O\(log N\)',
    r'<5ms',
    r'sub-10ms',
    r'sub-50ms',
    r'sub-millisecond',
    r'3-5x faster',
    r'90%\+ resolution',
    r'99\.9% availability',
    r'50ms → 2ms',
    r'backend/app/ai/protocol\.py'
]

for fname in files:
    fpath = os.path.join(mastery_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    for bp in banned_patterns:
        matches = re.findall(bp, content, re.IGNORECASE)
        assert not matches, f"Banned pattern '{bp}' found in {fname}: {matches}"

print("Backend Curriculum Verification PASSED 100%!")
