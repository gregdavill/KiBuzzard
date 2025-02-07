#!/usr/bin/env python3

import os

print("fake_entrypoint.py")

# Change the working dir to this script's directory
os.chdir(os.path.dirname(__file__))

# Run the real entrypoint at KiBuzzard/plugin.py

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "KiBuzzard"))

import plugin

plugin.main()
