# -*- coding: utf-8 -*-
import os, sys

stories_db = {}

def register_story(s):
    stories_db[s["num"]] = s

print("Builder initialized successfully with UTF-8")
