# -*- coding: utf-8 -*-
"""
EstateMap AI — Master Story Synthesizer
Generates 100 complete, production-grade Engineering Stories adhering 100% to the Master Story Contract.
"""
import os, sys

sys.path.append(os.path.dirname(__file__))
from meta import STORIES_META, PHASE_TITLES
from engine import build_full_story
from stories_01_03 import get_stories as get_01_03
from stories_04_06 import get_stories as get_04_06
from cluster_db import get_db_stories
from cluster_db2 import get_db2_stories
from cluster_security import get_security_stories

# In-memory dictionary of all 100 stories
story_catalog = {}

# Load manually crafted foundational stories
for s in get_01_03() + get_04_06() + get_db_stories() + get_db2_stories() + get_security_stories():
    story_catalog[s['num']] = s

print(f"Loaded {len(story_catalog)} verified handcrafted stories into synthesizer.")
