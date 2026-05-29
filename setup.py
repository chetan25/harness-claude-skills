#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path

def setup_local(project_root=None):
    if project_root is None:
        project_root = Path.cwd()
    
    harness_dir = Path(project_root) / ".harness"
    (harness_dir / "generated").mkdir(parents=True, exist_ok=True)
    (harness_dir / "config").mkdir(parents=True, exist_ok=True)
    print("Local setup complete at " + str(harness_dir))

def setup_global_install():
    home = Path.home()
    harness_home = home / ".harness"
    harness_home.mkdir(parents=True, exist_ok=True)
    print("Global setup complete at " + str(harness_home))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--global-install", action="store_true")
    args = parser.parse_args()
    
    if args.local:
        setup_local()
    elif args.global_install:
        setup_global_install()
    else:
        setup_local()
