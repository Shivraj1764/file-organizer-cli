"""
Tests for unhappy paths, edge cases, and robust error handling.
"""

from pathlib import Path
from unittest.mock import patch
import pytest
from fileorganizer import (
    EXIT_INVALID_INPUT,
    EXIT_ORGANIZER_ERROR,
    EXIT_INTERRUPTED,
    EXIT_UNEXPECTED_ERROR,
    main,
    organize_directory,
    validate_directory,
)


class TestValidationErrors:
    """Test validation errors for missing paths and invalid directory targets."""

    def test_missing_directory_raises_filenotfound(self, tmp_path: Path) -> None:
        missing_dir = tmp_path / "non_existent_folder"
        with pytest.raises(FileNotFoundError, match="does not exist"):
            validate_directory(missing_dir)

    def test_file_instead_of_directory_raises_notadirectory(
        self, tmp_path: Path
    ) -> None:
        file_path = tmp_path / "sample.pdf"
        file_path.write_text("dummy")
        with pytest.raises(NotADirectoryError, match="is not a directory"):
            validate_directory(file_path)

    def test_missing_directory_cli_exit_code_and_message(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        missing_dir = tmp_path / "does_not_exist"
        exit_code = main([str(missing_dir)])

        assert exit_code == EXIT_INVALID_INPUT
        captured = capsys.readouterr()
        assert f"Error: Directory '{missing_dir}' does not exist." in captured.err
        assert "Traceback" not in captured.err

    def test_file_as_directory_cli_exit_code_and_message(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        file_path = tmp_path / "resume.pdf"
        file_path.write_text("content")

        exit_code = main([str(file_path)])
        assert exit_code == EXIT_INVALID_INPUT
        captured = capsys.readouterr()
        assert f"Error: '{file_path.name}' is not a directory." in captured.err
        assert "Traceback" not in captured.err


class TestFileCollisionAndSafety:
    """Test safe handling when destination file already exists."""

    def test_destination_file_exists_skips_and_does_not_overwrite(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Create source file
        source_file = tmp_path / "photo.jpg"
        source_file.write_text("new photo data")

        # Pre-create category folder and existing destination file with original content
        images_dir = tmp_path / "Images"
        images_dir.mkdir()
        dest_file = images_dir / "photo.jpg"
        dest_file.write_text("original existing photo data")

        processed, skipped, errors = organize_directory(tmp_path, dry_run=False)

        assert processed == 0
        assert skipped == 1
        assert errors == 0

        # Verify destination file content was NOT overwritten
        assert dest_file.read_text() == "original existing photo data"
        # Verify source file was NOT deleted
        assert source_file.exists()

        captured = capsys.readouterr()
        assert "Warning: 'photo.jpg' already exists in 'Images/'. Skipping." in captured.err

    def test_dry_run_destination_collision_warning(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (tmp_path / "photo.jpg").write_text("data")
        images_dir = tmp_path / "Images"
        images_dir.mkdir()
        (images_dir / "photo.jpg").write_text("existing data")

        processed, skipped, errors = organize_directory(tmp_path, dry_run=True)

        assert processed == 0
        assert skipped == 1
        assert errors == 0

        captured = capsys.readouterr()
        assert "[DRY RUN] Warning: 'photo.jpg' already exists in 'Images/'. Would skip." in captured.out


class TestRuntimeFailures:
    """Test file system exceptions, permission errors, and race conditions."""

    def test_file_disappears_during_processing(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (tmp_path / "ghost.txt").write_text("boo")

        # Mock shutil.move to simulate file being deleted right before move
        with patch("shutil.move", side_effect=FileNotFoundError("File vanished")):
            processed, skipped, errors = organize_directory(tmp_path, dry_run=False)

        assert processed == 0
        assert errors == 1
        captured = capsys.readouterr()
        assert "Error: Could not move 'ghost.txt': File no longer exists." in captured.err

    def test_permission_denied_on_individual_file_move(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (tmp_path / "locked.txt").write_text("locked data")
        (tmp_path / "normal.jpg").write_text("photo data")

        def mock_move(src: str, dst: str) -> None:
            if "locked.txt" in src:
                raise PermissionError("Access is denied")
            # Normal behavior for other files
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            Path(dst).write_text(Path(src).read_text())
            Path(src).unlink()

        with patch("shutil.move", side_effect=mock_move):
            processed, skipped, errors = organize_directory(tmp_path, dry_run=False)

        assert processed == 1
        assert errors == 1
        captured = capsys.readouterr()
        assert "Error: Could not move 'locked.txt': Permission denied." in captured.err
        assert (tmp_path / "Images" / "normal.jpg").exists()

    def test_permission_denied_on_directory_access(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with patch.object(Path, "iterdir", side_effect=PermissionError("Directory locked")):
            exit_code = main([str(tmp_path)])

        assert exit_code == EXIT_ORGANIZER_ERROR
        captured = capsys.readouterr()
        assert f"Error: Permission denied while accessing '{tmp_path}'." in captured.err


class TestInterruptionAndSignals:
    """Test graceful handling of KeyboardInterrupt (Ctrl+C)."""

    def test_keyboard_interrupt_returns_130_with_clean_message(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with patch("fileorganizer.organize_directory", side_effect=KeyboardInterrupt):
            exit_code = main([str(tmp_path)])

        assert exit_code == EXIT_INTERRUPTED
        captured = capsys.readouterr()
        assert "Operation cancelled by user." in captured.err
        assert "Traceback" not in captured.err

    def test_unexpected_exception_returns_1_without_raw_traceback(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with patch("fileorganizer.organize_directory", side_effect=RuntimeError("Unexpected glitch")):
            exit_code = main([str(tmp_path)])

        assert exit_code == EXIT_UNEXPECTED_ERROR
        captured = capsys.readouterr()
        assert "Error: An unexpected problem occurred." in captured.err
        assert "Try running the command again or use --help." in captured.err
        assert "Traceback" not in captured.err
