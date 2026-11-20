"""The terminal front-end: login, exam choice, the examshell and its display.

Unlike the core, this package prints, and it uses rich and textual (the full
screen, see tui.py), copied into vendor/ so that nothing has to be installed.
Importing this package puts vendor/ first in Python's path, so its libraries
come before any other ones.
"""

import sys
from pathlib import Path

VENDOR_DIR = Path(__file__).resolve().parent.parent.parent / "vendor"

if str(VENDOR_DIR) not in sys.path:
	sys.path.insert(0, str(VENDOR_DIR))
