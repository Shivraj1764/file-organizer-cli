"""
Tests for CLI argument parsing, help output, and end-to-end command execution.
"""

from pathlib import Path
import pytest
from fileorganizer import (
    EXIT_INVALID_INPUT,
    EXIT_SUCCESS,
    create_parser,
    main,
)


class TestCLIParsing:
    """Test argument parsing rules, flags, and help text."""

    def test_help_flag_displays_usage_and_examples(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        parser = create_parser()
        with pytest.raises(SystemExit) as excinfo:
            parser.parse_args(["--help"])

        assert excinfo.value.code == 0
        captured = capsys.readouterr()
        assert "usage: fileorganizer" in captured.out
        assert "--dry-run" in captured.out
        assert "Supported Categories:" in captured.out
        assert "Exit Codes:" in captured.out
        assert "Examples:" in captured.out

    def test_missing_directory_argument_fails_cleanly(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        exit_code = main([])
        assert exit_code == EXIT_INVALID_INPUT
        captured = capsys.readouterr()
        assert "Error: the following arguments are required: directory" in captured.err
        assert "Use --help for usage instructions." in captured.err
        assert "Traceback" not in captured.err

    def test_end_to_end_cli_execution(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (tmp_path / "song.mp3").write_text("audio")
        (tmp_path / "doc.pdf").write_text("document")

        exit_code = main([str(tmp_path)])
        assert exit_code == EXIT_SUCCESS

        captured = capsys.readouterr()
        assert "Moved: song.mp3 -> Audio/" in captured.out
        assert "Moved: doc.pdf -> Documents/" in captured.out
        assert "Operation completed." in captured.out
        assert "Processed: 2" in captured.out
        assert "Skipped:   0" in captured.out

        assert (tmp_path / "Audio" / "song.mp3").exists()
        assert (tmp_path / "Documents" / "doc.pdf").exists()

    def test_end_to_end_cli_dry_run_execution(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (tmp_path / "video.mp4").write_text("video")

        exit_code = main([str(tmp_path), "--dry-run"])
        assert exit_code == EXIT_SUCCESS

        captured = capsys.readouterr()
        assert "[DRY RUN] video.mp4 -> Videos/" in captured.out
        assert "[DRY RUN] Summary:" in captured.out
        assert "Would move: 1" in captured.out

        # Verify file is still in root
        assert (tmp_path / "video.mp4").exists()
        assert not (tmp_path / "Videos").exists()
