# coding:utf-8
#############################################
# -author:shaw                              #
# -date:2025-03-18                          #
#############################################

import logging
import os
import re
import shutil
import sys

# Get the absolute path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the deploy directory to sys.path
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from xfunc import XFunc


class XClean:

    def __init__(self):
        """
        Initialize the XClean class.
        """
        pass

    def clean_files_and_dirs(self, items_to_clean, hide_dirs_to_deal=[]):
        """
        Clean files and directories.
        :param items_to_clean: List of dictionaries containing patterns and types of items to clean.
        :return: A dictionary containing the lists of deleted items.
        """
        parent_dir = os.path.dirname(os.getcwd())

        # Dictionary to store the results
        deleted_items = {}

        # Clean files and directories
        for item in items_to_clean:
            deleted = self.clean(
                target=item["pattern"],
                root_dir=item["parent_dir"],
                recursive=item["recursive"],
                is_dir=item["is_dir"],
                hide_dirs_to_deal=hide_dirs_to_deal,
            )
            deleted_items[item["pattern"]] = deleted

        # Log detailed deleted items
        logging.info("\n\nDetailed deleted items:")
        for key, items in deleted_items.items():
            if items:
                logging.info("- %s: %d", key, len(items))
                for item in items:
                    logging.info("  - %s", item)
            else:
                logging.info("- %s: No items deleted.", key)

        # Return the lists of deleted items
        return deleted_items

    def clean(
        self, target, root_dir=None, recursive=False, is_dir=False, hide_dirs_to_deal=[]
    ):
        """
        Delete a specific file or directory. If target is a path (absolute or relative), delete it directly.
        Otherwise, use regex to match files or directories under root_dir.

        :param target: String pattern for the file or directory to delete (e.g., '*pyc' or './path/to/file').
        :param root_dir: Root directory to search for the target (ignored if target is a path).
        :param recursive: If True, search directories recursively (ignored if target is a path).
        :param is_dir: If True, target is a directory (ignored if target is a path).
        :return: List of deleted items (files or directories).
        """

        # If target is a path (absolute or relative), delete it directly
        if os.path.sep in target:
            target_path = os.path.abspath(target)
            logging.info("Target is a path, deleting directly: %s", target_path)
            if self.safe_delete(target_path, is_dir=os.path.isdir(target_path)):
                return [target_path]
            else:
                return []

        # If root_dir is not provided, use the current directory
        if root_dir is None:
            root_dir = os.getcwd()
        logging.debug("root_dir: %s", root_dir)

        # Convert the target string into a valid regex pattern
        regex_pattern = self._convert_to_regex(target)
        logging.debug("Regex pattern: %s", regex_pattern.pattern)

        # Collect items to delete
        items_to_delete = []
        for root, dirs, files in os.walk(root_dir):
            hide_dirs_to_deal = [
                ".remote_login",
            ]

            # Skip hidden directories
            filtered = [
                d
                for d in dirs
                if not (d.startswith(".") and d not in hide_dirs_to_deal)
            ]

            # Modify original list in-place by slice assignment
            dirs[:] = filtered

            logging.debug("Searching in %s", root)
            logging.debug("Directories: %s", dirs)
            logging.debug("Files: %s", files)
            if is_dir:
                for dir_name in dirs:
                    if regex_pattern.match(dir_name):
                        dir_path = os.path.join(root, dir_name)
                        items_to_delete.append((dir_path, True))
            else:
                for file_name in files:
                    if regex_pattern.match(file_name):
                        file_path = os.path.join(root, file_name)
                        items_to_delete.append((file_path, False))

            if not recursive:
                break  # Stop after the top-level directory

        # Delete collected items
        deleted_items = []
        for path, is_dir in items_to_delete:
            if self.safe_delete(path, is_dir=is_dir):
                deleted_items.append(path)

        # Log results
        delete_count = len(deleted_items)
        logging.info(
            "Deleted %d %s matching '%s'",
            delete_count,
            "directories" if is_dir else "files",
            target,
        )
        if deleted_items:
            logging.info("Deleted items:\n%s", "\n".join(deleted_items))
        else:
            logging.info("No items deleted.")
        return deleted_items

    def _convert_to_regex(self, pattern):
        """
        Convert a shell-like pattern (e.g., '*pyc') into a valid regex pattern.

        :param pattern: Shell-like pattern (e.g., '*pyc').
        :return: Compiled regex pattern.
        """
        # Replace '*' with '.*' and escape other special characters
        regex_pattern = re.escape(pattern).replace(r"\*", ".*")
        return re.compile(regex_pattern)

    def safe_delete(self, path, is_dir=False):
        """
        Safely delete a file or directory.

        :param path: Path to the file or directory.
        :param is_dir: If True, path is a directory.
        :return: True if deletion was successful, False otherwise.
        """
        if not os.path.exists(path):
            logging.warning("File or directory not found: %s", path)
            return False
        if not os.access(path, os.W_OK):
            logging.error("Permission denied: %s", path)
            return False
        try:
            if is_dir:
                shutil.rmtree(path)
            else:
                os.remove(path)
            logging.info("Deleted %s: %s", "directory" if is_dir else "file", path)
            return True
        except OSError as e:
            logging.error("Failed to delete %s: %s", path, e)
            return False


def main():
    XFunc.init_log()

    """
    Test main function to demonstrate the functionality of XClean.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    # Example usage of the methods
    test_clean_dir_ = XFunc.get_parent_path("test_clean")
    test_clean_dir_lib_test = XFunc.get_parent_path("test_clean/test")
    test_clean_dir_lib_log = XFunc.get_parent_path("test_clean/tlog")
    XFunc.ensure_directory_exists(test_clean_dir_)
    XFunc.ensure_directory_exists(test_clean_dir_lib_test)
    XFunc.ensure_directory_exists(test_clean_dir_lib_log)
    XFunc.touch(test_clean_dir_lib_test + "/test1.tcln")
    XFunc.touch(test_clean_dir_lib_test + "/test2.tcln")
    XFunc.touch(test_clean_dir_lib_test + "/test3.tcln")

    # Define the patterns and types of items to clean
    items_to_clean = [
        {
            "pattern": "*tcln",
            "is_dir": False,
            "parent_dir": parent_dir,
            "recursive": True,
        },
        {
            "pattern": "test",
            "is_dir": True,
            "parent_dir": parent_dir,
            "recursive": True,
        },
        {
            "pattern": "tlog",
            "is_dir": True,
            "parent_dir": parent_dir,
            "recursive": True,
        },
        {
            "pattern": "test_clean",
            "is_dir": True,
            "parent_dir": parent_dir,
            "recursive": False,
        },
    ]

    # Initialize XClean
    xclean = XClean()
    # Clean files and directories
    xclean.clean_files_and_dirs(items_to_clean)


if __name__ == "__main__":
    main()
