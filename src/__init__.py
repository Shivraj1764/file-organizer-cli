"""
File Organizer CLI Package
Developed by SHIV PATIL
"""

from .fileorganizer import (
    CATEGORIES,
    DEFAULT_CATEGORY,
    EXIT_INTERRUPTED,
    EXIT_INVALID_INPUT,
    EXIT_ORGANIZER_ERROR,
    EXIT_SUCCESS,
    EXIT_UNEXPECTED_ERROR,
    SafeArgumentParser,
    create_parser,
    get_category,
    main,
    organize_directory,
    run_interactive_mode,
    validate_directory,
)

__all__ = [
    "CATEGORIES",
    "DEFAULT_CATEGORY",
    "EXIT_SUCCESS",
    "EXIT_UNEXPECTED_ERROR",
    "EXIT_INVALID_INPUT",
    "EXIT_ORGANIZER_ERROR",
    "EXIT_INTERRUPTED",
    "get_category",
    "validate_directory",
    "organize_directory",
    "create_parser",
    "SafeArgumentParser",
    "run_interactive_mode",
    "main",
]
