"""Document generator – thin wrapper around the ``src`` package.

Usage:
    python documents.py <spec-file>

Example:
    python documents.py .speckit/specifications/example.spec.md

For the full implementation see the ``src/`` package.
"""

from src.cli import main

if __name__ == "__main__":
    main()
