"""Tests for CLI argument parsing."""

import sys
from unittest import mock

from src.cli import main


def test_cli_missing_file(capsys):
    with mock.patch.object(sys, "argv", ["documents.py", "nonexistent.spec.md"]):
        try:
            main(["nonexistent.spec.md"])
        except SystemExit as e:
            assert "not found" in str(e)
