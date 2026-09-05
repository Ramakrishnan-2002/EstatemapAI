# -*- coding: utf-8 -*-
"""
EstateMap AI — Complete 100 Stories Phase Writer & Compiler
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(__file__))

import meta
from render import render_story_markdown
from stories_01_03 import get_stories as g1
from stories_04_06 import get_stories as g2
from cluster_db import get_db_stories as g3
from cluster_db2 import get_db2_stories as g4
from cluster_security import get_security_stories as g5

# 1. Collect all initial handcrafted stories (1-17)
stories_dict = {}
for s in g1() + g2() + g3() + g4() + g5():
    stories_dict[s['num']] = s

print(f"Base loaded: {len(stories_dict)} stories (Stories 1-17)")

