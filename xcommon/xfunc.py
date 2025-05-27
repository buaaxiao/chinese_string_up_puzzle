# coding:utf-8
#############################################
# -author:shaw                              #
# -date:2025-03-18                          #
#############################################

from functools import partial
import logging
import os
import pwd
import re
import sys
import io
import readline

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] >= 3


class XFunc:
    def __init__(self):
        pass

    @staticmethod
    def clear_input_chache():
        """
        clear the readline cache
        """
        readline.clear_history()
        readline.redisplay()

    @staticmethod
    def user_input(prompt, exit_on_interrupt=False):
        """
        Handle user input with support for graceful exit on KeyboardInterrupt.

        Args:
            prompt (str): The prompt message to display.
            exit_on_interrupt (bool): Whether to exit on KeyboardInterrupt.

        Returns:
            str: The user input, or None if interrupted and exit_on_interrupt is False.
        """
        try:
            if PY2:
                return raw_input(prompt)  # type: ignore # Python 2
            else:
                return input(prompt)  # Python 3
        except KeyboardInterrupt:
            XFunc.clear_input_chache()
            if PY2:
                print
            else:
                print()
            if exit_on_interrupt:
                sys.exit(1)  # Exit with non-zero status
            return None
        finally:
            XFunc.clear_input_chache()

    @staticmethod
    def get_parent_path(file_name, file_path=__file__):
        """
        Get the parent directory of the given file path and join it with the specified file name.
        :param file_path: The file path.
        :param file_name: The file name to join with the parent directory.
        :return: The joined file path.
        """
        logging.debug("Get parent directory of {}".format(file_path))
        logging.debug("Get file name {}".format(file_name))
        scrpt_dir = os.path.dirname(os.path.abspath(file_path))
        parent_dir = os.path.dirname(scrpt_dir)

        return os.path.join(parent_dir, file_name)

    @staticmethod
    def ensure_directory_exists(path):
        """
        Ensure a directory exists. If not, create it.
        :param path: The directory path.
        """
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                logging.info("Created directory: %s", path)
            except OSError as e:
                logging.error("Failed to create directory %s: %s", path, e)
                raise

    @staticmethod
    def touch(file_path, update_time=False):
        """
        Create an empty file or update its access and modification times.
        :param file_path: Path to the file.
        :param update_time: If True, update the file's access and modification times.
                        If False, only create the file if it doesn't exist.
        """
        try:
            # Open the file in append mode (creates the file if it doesn't exist)
            with open(file_path, "a"):
                # Update the file's access and modification times if requested
                if update_time:
                    os.utime(file_path, None)
            logging.info("Touched file: %s", file_path)
        except OSError as e:
            logging.error("Failed to touch file %s: %s", file_path, e)
            raise

    @staticmethod
    def get_username():
        """
        Get the current system username.
        :return: The username as a string.
        """
        return pwd.getpwuid(os.getuid())[0]

    @staticmethod
    def str_count(str):
        import string

        """Find out the number of Chinese and English, spaces, numbers, and punctuation marks in the string"""
        count_en = count_dg = count_sp = count_zh = count_pu = 0

        if PY2:
            for s in str.decode("utf-8"):
                # English
                if s in string.ascii_letters:
                    count_en += 1
                # digital
                elif s.isdigit():
                    count_dg += 1
                # space
                elif s.isspace():
                    count_sp += 1
                # Chinese
                elif s.isalpha():
                    count_zh += 1
                # Special Character
                else:
                    count_pu += 1
        else:
            for s in str:
                # English
                if s in string.ascii_letters:
                    count_en += 1
                # digital
                elif s.isdigit():
                    count_dg += 1
                # space
                elif s.isspace():
                    count_sp += 1
                # Chinese
                elif s.isalpha():
                    count_zh += 1
                # Special Character
                else:
                    count_pu += 1

        return count_zh

    @staticmethod
    def str_count_1(input_str):
        """
        Calculate the display width of a string, compatible with Python 2 and Python 3.
        :param input_str: The input string.
        :return: The display width of the string.
        """
        # Ensure the input is Unicode in Python 2
        if PY2 and isinstance(input_str, str):
            input_str = input_str.decode("utf-8")

        width = 0
        import unicodedata

        for char in input_str:
            # Use unicodedata.east_asian_width to determine character width
            if unicodedata.east_asian_width(char) in ("F", "W", "A"):
                width += 2  # Full-width characters
            else:
                width += 1  # Half-width characters
        return width

    @staticmethod
    def format_prompt(text="", default=None, quit=True):
        """Generate input prompt with options (Python 2/3 compatible)

        Args:
            text: Main prompt text
            default: Default value to show
            quit: Show quit option (default True)
        """
        options = []
        if quit:
            options.append("q to quit")
        options.append("default: {}".format(default))
        return (
            "{} ({}): ".format(text, ", ".join(options))
            if options
            else "{}: ".format(text)
        )

    @staticmethod
    def sanitised_input(
        prompt=None,
        type_=None,
        max_=None,
        min_=None,
        range_=None,
        defaultvalue=None,
        regex_pattern=None,
        regex_flags=0,
    ):
        """
        Get sanitized user input with validation

        Args:
            prompt: Prompt message to display
            type_: Expected type (int/float/str etc)
            max_: Maximum allowed value
            min_: Minimum allowed value
            range_: Allowed values (list/tuple/range)
                - Example: [1,2] allows only 1 or 2
                - Example: range(1,3) allows values 1-2
            defaultvalue: Default value if user quits
            regex_pattern: Regex pattern for validation (str or compiled pattern)
            regex_flags: Flags for regex compilation (re.IGNORECASE etc)

        Returns:
            Validated value or default value
        """
        prompt = XFunc.format_prompt(text=prompt, default=defaultvalue)

        # Parameter validation
        if min_ is not None and max_ is not None and max_ < min_:
            raise ValueError("max_ must be greater than min_")

        # Compile regex if needed
        if isinstance(regex_pattern, str):
            try:
                regex_pattern = re.compile(regex_pattern, regex_flags)
            except re.error as e:
                raise ValueError("Invalid regex pattern: {}".format(e))

        while True:
            try:
                ui = XFunc.user_input(prompt=prompt)

                # Handle quit
                if not ui or ui.lower() == "q":
                    return defaultvalue

                ui = ui.strip()

                # Type conversion
                if type_ is not None:
                    try:
                        ui = type_(ui)
                    except ValueError:
                        logging.warning("Input must be of type: %s", type_.__name__)
                        continue

                # Regex validation
                if regex_pattern is not None:
                    if not regex_pattern.match(ui):
                        logging.warning("Input not match")
                        continue

                # Value validation
                validation_passed = True

                # Check min/max bounds
                if max_ is not None and ui > max_:
                    logging.warning("Value must be <= %s", max_)
                    validation_passed = False
                elif min_ is not None and ui < min_:
                    logging.warning("Value must be >= %s", min_)
                    validation_passed = False

                # Check allowed values
                if validation_passed and range_ is not None:
                    if ui not in range_:
                        logging.warning(
                            "Value must be one of: %s", ", ".join(map(str, range_))
                        )
                        validation_passed = False

                if validation_passed:
                    return ui

            except (KeyboardInterrupt, EOFError):
                return defaultvalue

    @staticmethod
    def read_hosts_from_file(host_file, comment_prefixes=("#", "--")):
        """
        Reads a list of remote hosts from a specified host file, filtering out comment lines and empty lines.

        :param host_file: Path to the host file.
        :param comment_prefixes: Prefix symbols for comment lines, defaults to ('#', '--').
        :return: A list of non-comment host addresses.
        :raises FileNotFoundError: If the file does not exist.
        :raises IOError: If the file cannot be read.
        :raises UnicodeDecodeError: If the file encoding is incorrect.
        """
        if not os.path.exists(host_file):
            raise IOError("Host file '{}' does not exist.".format(host_file))

        try:
            with io.open(host_file, "r", encoding="utf-8") as f:
                remote_hosts = []
                for line in f:
                    line = line.strip()
                    if line and not any(
                        line.startswith(prefix) for prefix in comment_prefixes
                    ):
                        # Remove inline comments (starting with comment prefixes)
                        for prefix in comment_prefixes:
                            if prefix in line:
                                line = line.split(prefix)[0].strip()
                        remote_hosts.append(line)
                return remote_hosts
        except IOError as e:
            if "Permission denied" in str(e):
                raise IOError("Permission denied to read file '{}'.".format(host_file))
            else:
                raise IOError("Failed to read file '{}': {}".format(host_file, e))
        except UnicodeDecodeError:
            raise UnicodeDecodeError(
                "File '{}' has an encoding error. Please ensure the file is UTF-8 encoded.".format(
                    host_file
                )
            )
        except Exception as e:
            raise IOError(
                "An unknown error occurred while reading file '{}': {}".format(
                    host_file, e
                )
            )

    @staticmethod
    def expand_path(path, to_absolute=True):
        """
        Expand environment variables in a path string.
        :param path: The path string (e.g., '$APP_HOME/bss/bill2/').
        :return: The expanded path string.
        """
        path = os.path.expandvars(path)
        if to_absolute:
            path = os.path.abspath(path)
        return path

    @staticmethod
    def get_username():
        return pwd.getpwuid(os.getuid())[0]

    @staticmethod
    def get_host(bak_name):
        config_file = sys.path[0] + "/config/" + bak_name
        if not os.path.exists(config_file):
            config_file = sys.path[0] + "/" + bak_name
        return config_file

    @staticmethod
    def get_data(validators, opt="ipv4"):
        """Get validated data

        Args:
            ip_version: Either 'ipv4' or 'ipv6'

        Returns:
            Validated IP address string

        Raises:
            ValueError: If invalid IP version specified
        """
        validator = validators.get(opt.lower())
        if validator:
            return validator()
        logging.warning("Invalid IP version specified. Use 'ipv4' or 'ipv6'")

    @staticmethod
    def get_datas(field_defs):
        """Get validated data list"""
        values = {}
        for field, validator in field_defs:
            data = XFunc.get_data(validator, field)
            if not data:
                return None
            values[field] = data

        return values

    @staticmethod
    def init_log(log_level=logging.DEBUG):
        # Configure logging
        logging.basicConfig(
            level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
        )


class XValidator(object):
    """validation utilities"""

    # Strict IPv4 regex pattern
    IPV4_REGEX = re.compile(
        r"^"
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        r"$"
    )
    # TODO ipv6 regex need to be correct
    IPV6_REGEX = re.compile(
        r"^"
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        r"$"
    )

    # Configure both validators
    ip_validators = {
        "ipv4": partial(
            XFunc.sanitised_input,
            type_=str,
            regex_pattern=IPV4_REGEX,
            defaultvalue="127.0.0.1",
            prompt="Enter IPv4 address [xxx.xxx.xxx.xxx]: ",
        ),
        "ipv6": partial(
            XFunc.sanitised_input,
            type_=str,
            regex_pattern=IPV6_REGEX,
            defaultvalue="::1",
            prompt="Enter IPv6 address: ",
        ),
    }

    # Pre-configured validators using partial
    validators = {
        "number_input": partial(
            XFunc.sanitised_input,
            prompt="Enter a number between 1 and 10: ",
            type_=int,
            min_=1,
            max_=10,
            defaultvalue=2,
        ),
        "yes_no_input": partial(
            XFunc.sanitised_input,
            prompt="Enable debug mode? (1=Yes, 2=No)",
            type_=int,
            range_=[1, 2],
            defaultvalue=2,
        ),
        "age_input": partial(
            XFunc.sanitised_input,
            type_=int,
            min_=6,
            max_=18,
            range_=range(6, 19),  # Extra validation
            defaultvalue=10,
        ),
        "menu_input": partial(
            XFunc.sanitised_input,
            prompt="Select action (1=View, 2=Edit, 3=Delete, 9=Exit)",
            type_=int,
            range_=[1, 2, 3, 9],  # 9 for exit
        ),
    }


def main():
    try:
        # Test get_parent_path
        XFunc.init_log()

        # Test get_username
        logging.debug("Current username: %s" % XFunc.get_username())

        # Test str_count
        test_str = "Hello 世界 123! ！🚀"
        width = XFunc.str_count(test_str)
        logging.debug("Display width of '%s': %s" % (test_str, width))

        # Test sanitised_input
        num = XFunc.get_data(XValidator.validators, "number_input")
        logging.debug("User entered: {}".format(num))

        choice = XFunc.get_data(XValidator.validators, "yes_no_input")
        logging.debug("User entered: {}".format(choice))

        age = XFunc.get_data(XValidator.validators, "age_input")
        logging.debug("User entered: {}".format(age))

        selection = XFunc.get_data(XValidator.validators, "menu_input")
        logging.debug("User entered: {}".format(selection))

        # Get IPv4 address
        ipv4 = XFunc.get_data(XValidator.ip_validators, "ipv4")
        logging.debug("Validated IPv4: {}".format(ipv4))

    except KeyboardInterrupt as e:
        print(e)
    except IOError as e:
        print(e)
    except ValueError as e:
        print(e)
    finally:
        print("Bye!")


# Example usage
if __name__ == "__main__":
    main()
