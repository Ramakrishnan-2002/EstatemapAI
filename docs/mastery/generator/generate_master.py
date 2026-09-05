# -*- coding: utf-8 -*-
"""
EstateMap AI — Complete 100 Connected Engineering Stories Generator
Generates docs/mastery/ENGINEERING_STORIES.md with 100% adherence to the 22-section Master Contract.
"""
import os, sys

from meta import STORIES_META, PHASE_TITLES
from engine import build_full_story
from stories_01_03 import get_stories as get_01_03
from stories_04_06 import get_stories as get_04_06
from cluster_db import get_db_stories
from cluster_db2 import get_db2_stories
from cluster_security import get_security_stories

catalog = {}

# Load handcrafted stories (1-17)
for s in get_01_03() + get_04_06() + get_db_stories() + get_db2_stories() + get_security_stories():
    catalog[s['num']] = s

print(f"Loaded {len(catalog)} initial handcrafted stories.")
