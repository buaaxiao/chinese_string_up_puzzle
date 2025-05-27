# coding:utf-8
#############################################
# -author:shaw                              #
# -date:2025-03-18                          #
#############################################

import os
import subprocess
import argparse
import logging
import sys


# Get the absolute path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the deploy directory to sys.path to allow importing local modules
sys.path.extend([current_dir, os.path.dirname(current_dir)])

# Import the XClean class from the xcommon module
from xcommon.xclean import XClean
from xcommon.xfunc import XFunc


def main():
    """
    Main function to handle command-line arguments and execute tasks.
    """
    # Configure logging to display debug-level messages with a timestamp
    XFunc.init_log()

    # Save the current working directory to restore it later
    original_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create the argument parser with usage information
    parser = argparse.ArgumentParser(
        description="Script to clean and run test scripts.",
        usage="""
  # Run test scripts
  python util/test.py test

  # Clean extra files and directories
  python util/test.py clean

  # Show this help message
  python util/test.py -h/--help
""",
    )
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # Clean command: Clean extra files and directories
    clean_parser = subparsers.add_parser(
        "clean", help="Clean extra files and directories"
    )

    # Define the parent directory for cleaning operations
    parent_dir = os.path.dirname(os.getcwd())
    # Define the patterns and types of items to clean
    items_to_clean = [
        {
            "pattern": "*pyc",
            "is_dir": False,
            "parent_dir": parent_dir,
            "recursive": True,
            "key": "deleted_pyc",
        },  # Clean .pyc files recursively
        {
            "pattern": "__pycache__",
            "is_dir": True,
            "parent_dir": parent_dir,
            "recursive": True,
            "key": "deleted_pycache",
        },  # Clean __pycache__ directories recursively
        {
            "pattern": "*.log*",
            "is_dir": False,
            "parent_dir": parent_dir,
            "recursive": True,
            "key": "deleted_log",
        },  # Clean log directories recursively
        {
            "pattern": "log",
            "is_dir": True,
            "parent_dir": parent_dir,
            "recursive": True,
            "key": "deleted_log",
        },  # Clean log directories recursively
        {
            "pattern": ".DS_Store",
            "is_dir": False,
            "parent_dir": parent_dir,
            "recursive": True,
            "key": "deleted_ds",
        },  # Clean .DS_Store files recursively
        {
            "pattern": "dist",
            "is_dir": True,
            "parent_dir": parent_dir,
            "recursive": True,
            "key": "deleted_release",
        },  # Clean release directories recursively
        {
            "pattern": "build",
            "is_dir": True,
            "parent_dir": parent_dir,
            "recursive": False,
            "key": "deleted_deploy",
        },
    ]

    # Initialize the XClean class
    xclean = XClean()
    # Set the default function for the clean command
    clean_parser.set_defaults(
        func=lambda args: xclean.clean_files_and_dirs(items_to_clean)
    )

    # Test command: Run test scripts
    test_parser = subparsers.add_parser("test", help="Run test scripts")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Execute the function associated with the command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()  # Show help if no command is provided

    # Restore the original working directory
    os.chdir(original_dir)


if __name__ == "__main__":
    main()
