# 🗂️ File Organizer CLI

A robust, production-grade command-line tool built in Python to automatically sort and organize files in any directory into clean, categorized subfolders based on file extensions.

Built with a primary focus on **real error handling**, safety, sensible exit codes, informative `--help`, dry-run simulation, and clean `Ctrl+C` interrupt handling without exposing raw tracebacks to users.

---

## 📑 Table of Contents
1. [📖 Project Overview](#1--project-overview)
2. [✨ Features](#2--features)
3. [⚙️ Requirements](#3-️-requirements)
4. [🚀 Installation](#4--installation)
5. [📁 Project Structure](#5--project-structure)
6. [💻 Usage](#6--usage)
7. [🔍 Dry Run](#7--dry-run)
8. [📂 Supported File Types](#8--supported-file-types)
9. [🛡️ Error Handling](#9-️-error-handling)
10. [🔢 Exit Codes](#10--exit-codes)
11. [🧪 Testing](#11--testing)
12. [💡 Examples](#12--examples)
13. [🔮 Future Improvements](#13--future-improvements)
14. [📜 License](#14--license)

---

## 1. 📖 Project Overview

Messy folders (such as `Downloads/` or `Desktop/`) quickly become cluttered with hundreds of mixed files. **File Organizer CLI** solves this by scanning a target directory and safely moving files into organized category directories (e.g., `Images/`, `Documents/`, `Videos/`, `Spreadsheets/`, etc.).

Unlike basic scripts that crash when encountering missing files, permission issues, or duplicate names, this tool prioritizes **unhappy paths**—handling every potential failure gracefully, reporting user-friendly diagnostics to `stderr`, and returning standardized process exit codes.

---

## 2. ✨ Features

- 🎯 **Automated Categorization**: Maps file extensions to intuitive category folders.
- 🔍 **Dry-Run Preview (`--dry-run`)**: Inspect exactly what actions would occur without touching disk contents.
- 🛡️ **Non-Destructive Collision Protection**: Skips existing destination files with a clear warning instead of silently overwriting them.
- 🚫 **Zero Raw Tracebacks**: User-facing errors and edge cases are caught and displayed as clear, actionable messages.
- 🛑 **Interrupt Resilience**: Gracefully traps `Ctrl+C` (`SIGINT` / `KeyboardInterrupt`) and exits cleanly with code `130`.
- 📁 **Subdirectory Preservation**: Scans only root-level files in the target directory and preserves existing subdirectories and category folders.
- 🌐 **Cross-Platform Compatibility**: Fully compatible with Windows, macOS, and Linux using Python's native `pathlib`.
- 📦 **Standard Library Core**: Zero external runtime dependencies required for the main application.
- 🖱️ **Double-Click Interactive Mode**: Double-clicking `fileorganizer.exe` opens an interactive menu with drag-and-drop support that stays open.

---

## 3. ⚙️ Requirements

- 🐍 **Python 3.9+** (Compatible with Python 3.9, 3.10, 3.11, 3.12, and 3.13+)
- 💻 **Operating System**: Windows 10/11, Linux, or macOS
- 🛠️ **Development Environment**: VS Code / any terminal

---

## 4. 🚀 Installation

### 1. Clone the repository
```powershell
git clone <repository-url>
cd file-organizer-cli
```

### 2. Create a virtual environment
```powershell
python -m venv .venv
```

### 3. Activate the virtual environment
- **On Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  *(If execution policies block script activation in PowerShell, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **On Windows (Command Prompt):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

- **On macOS / Linux:**
  ```bash
  source .venv/bin/activate
  ```

### 4. Install dependencies (for testing)
```powershell
pip install -r requirements.txt
```

### 5. (Optional) Build Standalone Windows Executable (.exe)
To distribute to end users who do not have Python installed:
```powershell
pip install pyinstaller
pyinstaller --onefile --name fileorganizer fileorganizer.py
```
The standalone binary will be generated at `dist/fileorganizer.exe`.
End users can run it directly:
```powershell
.\dist\fileorganizer.exe "C:\Users\Username\Downloads" --dry-run
```

---

## 5. 📁 Project Structure

```text
file-organizer-cli/
│
├── fileorganizer.py          # Main application file (CLI, logic & error handling)
├── requirements.txt          # Development & test dependencies (pytest)
├── .gitignore                # Git ignore rules for Python, virtual envs, and IDEs
├── README.md                 # Complete documentation and usage guide
│
├── dist/
│   └── fileorganizer.exe     # Standalone Windows executable
│
├── test-files/               # Sample test folder
│   └── photo.jpg
│
└── tests/
    ├── __init__.py           # Test package initialization
    ├── test_cli.py           # CLI argument parsing, --help, and end-to-end tests
    ├── test_organization.py  # Category mapping and directory organization tests
    └── test_errors.py        # Unhappy paths, permissions, collisions, and interrupt tests
```

---

## 6. 💻 Usage

### Basic Syntax
```powershell
python fileorganizer.py <directory>
```

### Examples
- Organize a relative folder:
  ```powershell
  python fileorganizer.py Downloads
  ```
- Organize using an absolute path on Windows:
  ```powershell
  python fileorganizer.py "C:\Users\YourUser\Downloads"
  ```
- Display comprehensive help:
  ```powershell
  python fileorganizer.py --help
  ```

---

## 7. 🔍 Dry Run

Use the `--dry-run` flag to preview what files will be organized without actually moving or modifying any files:

```powershell
python fileorganizer.py Downloads --dry-run
```

**Example Output:**
```text
[DRY RUN] photo.jpg -> Images/
[DRY RUN] report.pdf -> Documents/
[DRY RUN] data.xlsx -> Spreadsheets/
[DRY RUN] Warning: 'archive.zip' already exists in 'Archives/'. Would skip.

[DRY RUN] Summary:
Would move: 3
Would skip: 1
```

---

## 8. 📂 Supported File Types

| Category | Extensions | Icon |
| :--- | :--- | :---: |
| **Images** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg` | 🖼️ |
| **Documents** | `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt` | 📄 |
| **Spreadsheets** | `.xls`, `.xlsx`, `.csv` | 📊 |
| **Presentations**| `.ppt`, `.pptx` | 📽️ |
| **Audio** | `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg` | 🎵 |
| **Videos** | `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv` | 🎬 |
| **Archives** | `.zip`, `.rar`, `.7z`, `.tar`, `.gz` | 📦 |
| **Others** | Any unrecognized extension or extensionless file | 📁 |

*Note: Extension checking is case-insensitive (`.JPG`, `.Pdf`, `.PNG` are mapped identically).*

---

## 9. 🛡️ Error Handling

The application handles edge cases cleanly and sends diagnostics to `stderr` without exposing raw stack traces:

| Scenario / Unhappy Path | User-Facing Message | Exit Code |
| :--- | :--- | :---: |
| ❌ **Missing Directory** | `Error: Directory 'folder' does not exist.` | `2` |
| ❌ **Target is a File** | `Error: 'file.txt' is not a directory.` | `2` |
| ❌ **Missing CLI Argument** | `Error: the following arguments are required: directory` | `2` |
| 🔒 **Permission Denied (Directory)** | `Error: Permission denied while accessing 'folder'.` | `3` |
| ⚠️ **Destination File Exists** | `Warning: 'photo.jpg' already exists in 'Images/'. Skipping.` | `0` *(or `3` if all fail)* |
| 💨 **File Vanished Mid-Run** | `Error: Could not move 'photo.jpg': File no longer exists.` | Continues remaining files |
| 🚫 **Locked File / Move Permission** | `Error: Could not move 'locked.txt': Permission denied.` | Continues remaining files |
| 🛑 **User Interruption (`Ctrl+C`)** | `\nOperation cancelled by user.` | `130` |
| 💥 **Unexpected Crash** | `Error: An unexpected problem occurred.\nTry running the command again or use --help.` | `1` |

---

## 10. 🔢 Exit Codes

File Organizer CLI uses standardized POSIX / CLI exit codes:

- **`0` — Success**: All valid operations were executed, or `--dry-run` finished normally.
- **`1` — Unexpected Error**: Generic unexpected exception caught by top-level handler.
- **`2` — Invalid User Input / Path**: Directory does not exist, target path is a file, or invalid flags.
- **`3` — File-System / Organizer Error**: Directory access permission denied or disk/IO failure.
- **`130` — Interrupted (`Ctrl+C`)**: Terminated cleanly by user interrupt signal.

---

## 11. 🧪 Testing

The project includes an automated test suite with **27 pytest test cases** covering happy paths, edge cases, error scenarios, and CLI exit codes.

### Running all tests
```powershell
pytest -v
```

### Running with test coverage (optional)
```powershell
pytest --cov=fileorganizer tests/
```

### What is tested:
- 🧪 **`test_organization.py`**: Extension categorization, uppercase extensions, subfolder creation, subfolder preservation, empty folders, dry-run safety.
- 🧪 **`test_errors.py`**: Missing directories, files passed as directories, destination collisions, file disappearing race conditions, directory permissions, file-level permissions, `Ctrl+C` interrupt, and unexpected exceptions.
- 🧪 **`test_cli.py`**: Argument parsing, `--help` output formatting, missing argument handling, and end-to-end execution.

---

## 12. 💡 Examples

### Example 1: Successful Organization
**Folder contents before:**
```text
Downloads/
├── photo.jpg
├── resume.pdf
├── budget.xlsx
└── song.mp3
```

**Command:**
```powershell
python fileorganizer.py Downloads
```

**Output:**
```text
Moved: photo.jpg -> Images/
Moved: resume.pdf -> Documents/
Moved: budget.xlsx -> Spreadsheets/
Moved: song.mp3 -> Audio/

Operation completed.
Processed: 4
Skipped:   0
```

---

### Example 2: Non-Existent Directory
**Command:**
```powershell
python fileorganizer.py NonExistentFolder
```

**Output:**
```text
Error: Directory 'NonExistentFolder' does not exist.
```

---

### Example 3: File Passed Instead of Directory
**Command:**
```powershell
python fileorganizer.py README.md
```

**Output:**
```text
Error: 'README.md' is not a directory.
```

---

### Example 4: Destination Conflict (Safe Skip)
**Command:**
```powershell
python fileorganizer.py Downloads
```

**Output:**
```text
Warning: 'photo.jpg' already exists in 'Images/'. Skipping.

Operation completed.
Processed: 0
Skipped:   1
```

---

### Example 5: User Cancellation (`Ctrl+C`)
**Command:**
```powershell
python fileorganizer.py LargeFolder
# User presses Ctrl+C
```

**Output:**
```text
Operation cancelled by user.
```
*(Exit code: `130`)*

---

## 13. 🔮 Future Improvements

- ⚙️ **Custom Configuration Files**: Support `.fileorganizerrc` or `config.json` for custom categories and user-defined extension mappings.
- 📅 **Date-based Sorting**: Option to organize files by creation or modification year/month (e.g. `2024/August/`).
- ⏪ **Undo / Rollback**: A transaction log to reverse organization operations (`python fileorganizer.py undo`).
- 🔁 **Recursive Mode (`--recursive` / `-r`)**: Optional flag to recursively organize nested subfolders.
- 🔍 **Duplicate Detection**: Hash-based (SHA256) duplicate file detection to find identical files regardless of name.

---

## 14. 📜 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it.

---

## 👨‍💻 Author
Developed with ❤️ by **SHIV PATIL**

✨ *Thanks for using file organizer!* ✨
