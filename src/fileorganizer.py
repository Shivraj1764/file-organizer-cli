#!/usr/bin/env python3
"""
🗂️ File Organizer CLI
👨‍💻 Developed by SHIV PATIL

A command-line tool that organizes files in a specified directory
into category folders based on their file extensions.

Built with robust error handling, sensible exit codes, and dry-run capability.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# Ensure Windows terminal supports UTF-8 and emoji display
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Exit codes
EXIT_SUCCESS: int = 0
EXIT_UNEXPECTED_ERROR: int = 1
EXIT_INVALID_INPUT: int = 2
EXIT_ORGANIZER_ERROR: int = 3
EXIT_INTERRUPTED: int = 130

# File extension mappings to category folders
CATEGORIES: Dict[str, Tuple[str, ...]] = {
    "Images": (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"),
    "Documents": (".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"),
    "Spreadsheets": (".xls", ".xlsx", ".csv"),
    "Presentations": (".ppt", ".pptx"),
    "Audio": (".mp3", ".wav", ".aac", ".flac", ".ogg"),
    "Videos": (".mp4", ".mkv", ".avi", ".mov", ".wmv"),
    "Archives": (".zip", ".rar", ".7z", ".tar", ".gz"),
}

DEFAULT_CATEGORY: str = "Others"


def get_category(file_path: Path) -> str:
    """
    Determine the category folder name based on the file extension.

    Args:
        file_path: Path object representing the file.

    Returns:
        The matching category name, or 'Others' if unrecognized.
    """
    extension = file_path.suffix.lower()
    if not extension:
        return DEFAULT_CATEGORY

    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category

    return DEFAULT_CATEGORY


def validate_directory(target_path: Path) -> None:
    """
    Validate that the given path exists, is a directory, and is accessible.

    Args:
        target_path: Path object to validate.

    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path points to a file.
        PermissionError: If directory permissions prevent reading.
    """
    if not target_path.exists():
        raise FileNotFoundError(f"Directory '{target_path}' does not exist.")

    if not target_path.is_dir():
        raise NotADirectoryError(f"'{target_path}' is not a directory.")

    try:
        # Test directory read accessibility
        list(target_path.iterdir())
    except PermissionError:
        raise PermissionError(f"Permission denied while accessing '{target_path}'.")


def organize_directory(
    directory_path: Path, dry_run: bool = False
) -> Tuple[int, int, int]:
    """
    Scan files in the directory and move them into categorized subfolders.

    Args:
        directory_path: The directory to organize.
        dry_run: If True, preview actions without modifying files or creating folders.

    Returns:
        Tuple of (processed_count, skipped_count, error_count)
    """
    processed_count = 0
    skipped_count = 0
    error_count = 0

    try:
        entries = list(directory_path.iterdir())
    except PermissionError:
        print(
            f"Error: Permission denied while accessing '{directory_path}'.",
            file=sys.stderr,
        )
        return (0, 0, 1)

    # Filter for files only (skip subdirectories and category folders)
    files_to_organize: List[Path] = [
        entry for entry in entries if entry.is_file() and not entry.is_symlink()
    ]

    if not files_to_organize:
        print(f"No files found to organize in '{directory_path}'.")
        return (0, 0, 0)

    for item in files_to_organize:
        category = get_category(item)
        dest_dir = directory_path / category
        dest_file = dest_dir / item.name

        if dry_run:
            if dest_file.exists():
                print(
                    f"[DRY RUN] Warning: '{item.name}' already exists in '{category}/'. Would skip.",
                    file=sys.stdout,
                )
                skipped_count += 1
            else:
                print(f"[DRY RUN] {item.name} -> {category}/", file=sys.stdout)
                processed_count += 1
            continue

        # Check if destination file already exists to prevent accidental overwrites
        if dest_file.exists():
            print(
                f"Warning: '{item.name}' already exists in '{category}/'. Skipping.",
                file=sys.stderr,
            )
            skipped_count += 1
            continue

        try:
            # Create category directory if it does not exist
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Move file to destination folder
            shutil.move(str(item), str(dest_file))
            print(f"Moved: {item.name} -> {category}/", file=sys.stdout)
            processed_count += 1

        except FileNotFoundError:
            print(
                f"Error: Could not move '{item.name}': File no longer exists.",
                file=sys.stderr,
            )
            error_count += 1
        except PermissionError:
            print(
                f"Error: Could not move '{item.name}': Permission denied.",
                file=sys.stderr,
            )
            error_count += 1
        except OSError as os_err:
            print(
                f"Error: Could not move '{item.name}': {os_err}",
                file=sys.stderr,
            )
            error_count += 1
        except Exception as exc:
            print(
                f"Error: Could not move '{item.name}': {exc}",
                file=sys.stderr,
            )
            error_count += 1

    return (processed_count, skipped_count, error_count)


class SafeArgumentParser(argparse.ArgumentParser):
    """
    Custom ArgumentParser that outputs clean error messages and exits
    with code 2 (Invalid user input) instead of raising raw exceptions.
    """

    def error(self, message: str) -> None:
        print(f"Error: {message}", file=sys.stderr)
        print("Use --help for usage instructions.", file=sys.stderr)
        sys.exit(EXIT_INVALID_INPUT)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    epilog_text = """
Exit Codes:
  0   Success (files organized or dry-run complete)
  1   Unexpected error
  2   Invalid user input or path (directory does not exist, path is a file)
  3   File-system or permission error
  130 Operation cancelled by user (Ctrl+C)

Supported Categories:
  🖼️  Images:        .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg
  📄 Documents:     .pdf, .doc, .docx, .txt, .rtf, .odt
  📊 Spreadsheets:  .xls, .xlsx, .csv
  📽️  Presentations: .ppt, .pptx
  🎵 Audio:         .mp3, .wav, .aac, .flac, .ogg
  🎬 Videos:        .mp4, .mkv, .avi, .mov, .wmv
  📦 Archives:      .zip, .rar, .7z, .tar, .gz
  📁 Others:        All unrecognized file extensions

Examples:
  Organize a Downloads folder:
    python fileorganizer.py Downloads

  Preview organization without moving files:
    python fileorganizer.py Downloads --dry-run

  Organize using an absolute path on Windows:
    python fileorganizer.py "C:\\Users\\Username\\Documents"

✨ Thanks for using file organizer! ✨
👨‍💻 Developed by SHIV PATIL
"""

    parser = SafeArgumentParser(
        prog="fileorganizer",
        description="Organize files in a directory into category folders based on their extensions.",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "directory",
        help="Path to the directory containing files to organize.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the organization process without creating folders or moving files.",
    )

    return parser


def run_interactive_mode() -> int:
    """
    Run an interactive console session when the executable is double-clicked
    or run without command-line arguments in an interactive terminal.
    """
    print("=" * 54)
    print("             🗂️  File Organizer CLI  🗂️")
    print("           👨‍💻 Developed by SHIV PATIL")
    print("=" * 54)
    print("✨ Organize files into clean category folders by extension.\n")

    try:
        raw_path = input(
            "📁 Enter folder path to organize (or drag & drop a folder here):\n> "
        ).strip()
        if not raw_path:
            print("❌ Error: No folder path entered.", file=sys.stderr)
            print("\n✨ Thanks for using file organizer! ✨")
            print("👨‍💻 Developed by SHIV PATIL")
            input("\nPress Enter to exit...")
            return EXIT_INVALID_INPUT

        # Clean surrounding quotes (e.g., from drag-and-drop in Windows)
        cleaned_path = raw_path.strip('"\'')
        target_path = Path(cleaned_path)

        dry_run_choice = (
            input("\n🔍 Preview only without moving files (Dry Run)? [Y/n]: ")
            .strip()
            .lower()
        )
        is_dry_run = dry_run_choice in ("y", "yes", "")

        print("\n" + "-" * 54)
        try:
            validate_directory(target_path)
        except FileNotFoundError:
            print(f"Error: Directory '{target_path}' does not exist.", file=sys.stderr)
            print("\n✨ Thanks for using file organizer! ✨")
            print("👨‍💻 Developed by SHIV PATIL")
            input("\nPress Enter to exit...")
            return EXIT_INVALID_INPUT
        except NotADirectoryError:
            print(f"Error: '{target_path.name}' is not a directory.", file=sys.stderr)
            print("\n✨ Thanks for using file organizer! ✨")
            print("👨‍💻 Developed by SHIV PATIL")
            input("\nPress Enter to exit...")
            return EXIT_INVALID_INPUT
        except PermissionError:
            print(
                f"Error: Permission denied while accessing '{target_path}'.",
                file=sys.stderr,
            )
            print("\n✨ Thanks for using file organizer! ✨")
            print("👨‍💻 Developed by SHIV PATIL")
            input("\nPress Enter to exit...")
            return EXIT_ORGANIZER_ERROR

        processed, skipped, errors = organize_directory(
            target_path, dry_run=is_dry_run
        )

        if is_dry_run:
            print("\n[DRY RUN] Summary:")
            print(f"Would move: {processed}")
            print(f"Would skip: {skipped}")

            if processed > 0:
                proceed_choice = (
                    input(
                        "\n🚀 Do you want to proceed with organizing these files now? [y/N]: "
                    )
                    .strip()
                    .lower()
                )
                if proceed_choice in ("y", "yes"):
                    print("\n" + "-" * 54)
                    print("🚀 Organizing files...\n")
                    proc_real, skip_real, err_real = organize_directory(
                        target_path, dry_run=False
                    )
                    print("\nOperation completed.")
                    print(f"Processed: {proc_real}")
                    print(f"Skipped:   {skip_real}")
                    if err_real > 0:
                        print(f"Errors:    {err_real}", file=sys.stderr)
                else:
                    print("\nNo files were moved.")
            else:
                print("\nNo files to organize.")
        else:
            print("\nOperation completed.")
            print(f"Processed: {processed}")
            print(f"Skipped:   {skipped}")
            if errors > 0:
                print(f"Errors:    {errors}", file=sys.stderr)

        print("\n" + "=" * 54)
        print("✨ Thanks for using file organizer! ✨")
        print("👨‍💻 Developed by SHIV PATIL")
        print("=" * 54)
        input("\nPress Enter to close this window...")
        return EXIT_SUCCESS

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        print("\n✨ Thanks for using file organizer! ✨")
        print("👨‍💻 Developed by SHIV PATIL")
        input("\nPress Enter to exit...")
        return EXIT_INTERRUPTED
    except Exception:
        print("Error: An unexpected problem occurred.", file=sys.stderr)
        print("Try running the command again or use --help.", file=sys.stderr)
        print("\n✨ Thanks for using file organizer! ✨")
        print("👨‍💻 Developed by SHIV PATIL")
        input("\nPress Enter to exit...")
        return EXIT_UNEXPECTED_ERROR


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Main entry point for the File Organizer CLI.

    Args:
        argv: Optional list of CLI arguments (defaults to sys.argv[1:]).

    Returns:
        Integer exit code.
    """
    # If launched without arguments (e.g. double-clicked .exe), open interactive mode
    if argv is None and len(sys.argv) == 1 and sys.stdin.isatty():
        return run_interactive_mode()

    parser = create_parser()

    try:
        args = parser.parse_args(argv)
        target_path = Path(args.directory)

        # 1. Pre-flight validation
        try:
            validate_directory(target_path)
        except FileNotFoundError as fnf_err:
            print(f"Error: Directory '{target_path}' does not exist.", file=sys.stderr)
            return EXIT_INVALID_INPUT
        except NotADirectoryError:
            print(f"Error: '{target_path.name}' is not a directory.", file=sys.stderr)
            return EXIT_INVALID_INPUT
        except PermissionError:
            print(
                f"Error: Permission denied while accessing '{target_path}'.",
                file=sys.stderr,
            )
            return EXIT_ORGANIZER_ERROR

        # 2. Run organization
        processed, skipped, errors = organize_directory(
            target_path, dry_run=args.dry_run
        )

        # 3. Print summary
        if args.dry_run:
            print("\n[DRY RUN] Summary:")
            print(f"Would move: {processed}")
            print(f"Would skip: {skipped}")
        else:
            print("\nOperation completed.")
            print(f"Processed: {processed}")
            print(f"Skipped:   {skipped}")
            if errors > 0:
                print(f"Errors:    {errors}", file=sys.stderr)

        if errors > 0 and processed == 0:
            return EXIT_ORGANIZER_ERROR

        return EXIT_SUCCESS

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return EXIT_INTERRUPTED

    except SystemExit as sys_exit:
        return (
            sys_exit.code
            if isinstance(sys_exit.code, int)
            else EXIT_INVALID_INPUT
        )

    except Exception:
        print("Error: An unexpected problem occurred.", file=sys.stderr)
        print(
            "Try running the command again or use --help.",
            file=sys.stderr,
        )
        return EXIT_UNEXPECTED_ERROR


if __name__ == "__main__":
    sys.exit(main())
