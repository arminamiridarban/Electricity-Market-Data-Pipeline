import sys
from pathlib import Path

"""
Path resolver for test files to ensure that the project root is in the Python path, allowing imports from the app package to work correctly in test modules.
"""

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
