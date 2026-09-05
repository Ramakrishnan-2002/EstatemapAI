# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import meta
from render import render_story_markdown
from stories_01_03 import get_stories as g1
from stories_04_06 import get_stories as g2
from cluster_db import get_db_stories as g3
from cluster_db2 import get_db2_stories as g4
from cluster_security import get_security_stories as g5

# Load existing handcrafted stories 1-17
all_stories = {}
for s in g1() + g2() + g3() + g4() + g5():
    all_stories[s['num']] = s

print(f'Base loaded: {len(all_stories)} stories')
