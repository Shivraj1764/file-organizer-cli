"""
Tests for file organization logic, category mappings, and directory handling.
"""

from pathlib import Path
import pytest
from fileorganizer import (
    CATEGORIES,
    DEFAULT_CATEGORY,
    get_category,
    organize_directory,
)


class TestCategoryMapping:
    """Test mapping of file extensions to their correct category folders."""

    def test_image_extensions(self) -> None:
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"]:
            path = Path(f"sample{ext}")
            assert get_category(path) == "Images"
            # Test case insensitivity
            path_upper = Path(f"sample{ext.upper()}")
            assert get_category(path_upper) == "Images"

    def test_document_extensions(self) -> None:
        for ext in [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"]:
            path = Path(f"doc{ext}")
            assert get_category(path) == "Documents"
            assert get_category(Path(f"doc{ext.upper()}")) == "Documents"

    def test_spreadsheet_extensions(self) -> None:
        for ext in [".xls", ".xlsx", ".csv"]:
            path = Path(f"data{ext}")
            assert get_category(path) == "Spreadsheets"

    def test_presentation_extensions(self) -> None:
        for ext in [".ppt", ".pptx"]:
            path = Path(f"slides{ext}")
            assert get_category(path) == "Presentations"

    def test_audio_extensions(self) -> None:
        for ext in [".mp3", ".wav", ".aac", ".flac", ".ogg"]:
            path = Path(f"track{ext}")
            assert get_category(path) == "Audio"

    def test_video_extensions(self) -> None:
        for ext in [".mp4", ".mkv", ".avi", ".mov", ".wmv"]:
            path = Path(f"film{ext}")
            assert get_category(path) == "Videos"

    def test_archive_extensions(self) -> None:
        for ext in [".zip", ".rar", ".7z", ".tar", ".gz"]:
            path = Path(f"bundle{ext}")
            assert get_category(path) == "Archives"

    def test_unrecognized_and_no_extension(self) -> None:
        assert get_category(Path("file.unknownext")) == DEFAULT_CATEGORY
        assert get_category(Path("file.xyz123")) == DEFAULT_CATEGORY
        assert get_category(Path("LICENSE")) == DEFAULT_CATEGORY
        assert get_category(Path(".hiddenfile")) == DEFAULT_CATEGORY


class TestDirectoryOrganization:
    """Test the file organizing behavior on temporary filesystem fixtures."""

    def test_organize_multiple_categories(self, tmp_path: Path) -> None:
        # Create test files
        (tmp_path / "photo.jpg").write_text("image-data")
        (tmp_path / "resume.pdf").write_text("pdf-data")
        (tmp_path / "data.xlsx").write_text("spreadsheet-data")
        (tmp_path / "slides.pptx").write_text("presentation-data")
        (tmp_path / "song.mp3").write_text("audio-data")
        (tmp_path / "movie.mp4").write_text("video-data")
        (tmp_path / "archive.zip").write_text("archive-data")
        (tmp_path / "notes.unknown").write_text("other-data")

        processed, skipped, errors = organize_directory(tmp_path, dry_run=False)

        assert processed == 8
        assert skipped == 0
        assert errors == 0

        # Verify files were moved into category folders
        assert (tmp_path / "Images" / "photo.jpg").exists()
        assert (tmp_path / "Documents" / "resume.pdf").exists()
        assert (tmp_path / "Spreadsheets" / "data.xlsx").exists()
        assert (tmp_path / "Presentations" / "slides.pptx").exists()
        assert (tmp_path / "Audio" / "song.mp3").exists()
        assert (tmp_path / "Videos" / "movie.mp4").exists()
        assert (tmp_path / "Archives" / "archive.zip").exists()
        assert (tmp_path / "Others" / "notes.unknown").exists()

        # Verify original files are no longer in root
        assert not (tmp_path / "photo.jpg").exists()
        assert not (tmp_path / "resume.pdf").exists()

    def test_subdirectories_are_not_moved(self, tmp_path: Path) -> None:
        # Create an existing subfolder and a file
        subfolder = tmp_path / "ExistingFolder"
        subfolder.mkdir()
        (subfolder / "inner.txt").write_text("inner file")
        (tmp_path / "root_file.txt").write_text("root file")

        processed, skipped, errors = organize_directory(tmp_path, dry_run=False)

        assert processed == 1
        assert (tmp_path / "Documents" / "root_file.txt").exists()
        # Verify ExistingFolder remains intact
        assert subfolder.exists()
        assert (subfolder / "inner.txt").exists()

    def test_empty_directory_handling(self, tmp_path: Path) -> None:
        processed, skipped, errors = organize_directory(tmp_path, dry_run=False)
        assert processed == 0
        assert skipped == 0
        assert errors == 0

    def test_dry_run_mode_makes_no_changes(self, tmp_path: Path) -> None:
        (tmp_path / "photo.jpg").write_text("image-data")
        (tmp_path / "notes.txt").write_text("text-data")

        processed, skipped, errors = organize_directory(tmp_path, dry_run=True)

        assert processed == 2
        assert skipped == 0
        assert errors == 0

        # Verify no category folders were created
        assert not (tmp_path / "Images").exists()
        assert not (tmp_path / "Documents").exists()

        # Verify files remain in original root location
        assert (tmp_path / "photo.jpg").exists()
        assert (tmp_path / "notes.txt").exists()
