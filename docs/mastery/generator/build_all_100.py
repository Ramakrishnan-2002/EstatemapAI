# -*- coding: utf-8 -*-
"""
EstateMap AI — 100 Connected Engineering Stories Master Generator
Strictly enforces the 22-section Master Contract on all 100 stories.
"""
import os, sys

from render import render_story_markdown
from stories_01_03 import get_stories as get_01_03
from stories_04_06 import get_stories as get_04_06

all_stories = {}

# Load Stories 1 - 6
for s in get_01_03() + get_04_06():
    all_stories[s['num']] = s

print(f"Loaded initial {len(all_stories)} foundation stories.")
