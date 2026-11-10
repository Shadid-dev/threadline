import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # lets this practice script find tools.py

import tools

print(tools.minutes_between("14:01", "14:09"))
print(tools.create_thread("checkout", "SIG-001", "14:01"))
print(tools.list_open_threads())