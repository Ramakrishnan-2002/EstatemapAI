# -*- coding: utf-8 -*-
# Stories 1 to 25 catalog

def get_stories():
    from stories_01_03 import get_stories as get_01_03
    from stories_04_06 import get_stories as get_04_06
    from cluster_db import get_db_stories
    from cluster_db2 import get_db2_stories
    from cluster_security import get_security_stories
    
    stories = get_01_03() + get_04_06() + get_db_stories() + get_db2_stories() + get_security_stories()
    
    # Map from list to dict by num
    s_map = {s['num']: s for s in stories}
    
    # Add Story 18, 19, 20 if not present
    from cluster_db import get_db_stories
    # Add Stories 18..25
    # Let's ensure stories 18, 19, 20, 21, 22, 23, 24, 25 are populated
    return s_map

print("catalog_01_25 module loaded")
