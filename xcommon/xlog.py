# coding:utf-8
#############################################
# -author:shaw                              #
# -date:2025-03-18                          #
#############################################

from collections import namedtuple
import logging
import logging.handlers
import os
import datetime
import inspect
import glob
import sys
import random

# Get the absolute path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the deploy directory to sys.path
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from xfunc import XFunc
import inspect


class XLogger(object):
    # Define configuration with types and defaults
    log_config_def = [
        ("path", True, None, str),
        ("size", False, 10, int),
        ("num", False, 2, int),
        ("console_level", False, "WARNING", str),
        ("file_level", False, "DEBUG", str),
        ("file_name", False, "test", str),
        ("logger_name", False, "test", str),
    ]

    def __init__(self):
        pass

    def init_log(self, log_config, user_class=None, log_format=None):
        if hasattr(self, "_logger"):
            for handler in self._logger.handlers[:]:
                self._logger.removeHandler(handler)
                handler.close()

        self.log_config = log_config

        # Set default user_class to caller's class name
        if user_class is None:
            # Get the frame of the caller
            caller_frame = inspect.currentframe().f_back
            try:
                # Get 'self' from caller's frame
                caller_self = caller_frame.f_locals.get("self")
                if caller_self is not None:
                    user_class = caller_self.__class__.__name__
                else:
                    user_class = "UnknownClass"
            finally:
                # Ensure frame reference is released to avoid reference cycles
                del caller_frame

        # Ensure log directory exists
        self.logpath = os.path.expandvars(self.log_config.path)
        XFunc.ensure_directory_exists(self.logpath)

        self._logger = logging.getLogger(self.log_config.logger_name or user_class)
        self._logger.setLevel(logging.DEBUG)
        self.log_num = self.log_config.num
        self.log_size = self.log_config.size * 1024 * 1024

        # Set log format
        if log_format is None:
            user_name = XFunc.get_username()
            log_format = "%(asctime)s-[{}]-%(name)s- %(caller_filename)s:%(caller_lineno)d[%(levelname)s] %(message)s".format(
                user_name
            )
        self.formatter = logging.Formatter(log_format)
        self._logger.propagate = False

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.console_level = self.log_config.console_level
        console_handler.setLevel(self.console_level)
        self._logger.addHandler(console_handler)

        # File handler
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_config.file_name or user_class
        self.logname = os.path.join(
            self.logpath,
            "{}_{}_{}.log".format(self.log_file, timestamp, random.randint(1000, 9999)),
        )

        file_handler = logging.handlers.RotatingFileHandler(
            self.logname,
            maxBytes=self.log_size,
            backupCount=self.log_num,
            encoding="utf-8",
        )
        file_handler.setFormatter(self.formatter)
        self.file_level = self.log_config.file_level
        file_handler.setLevel(self.file_level)
        self._logger.addHandler(file_handler)

        self._logger.debug(
            "log_path: {}".format(self.logpath),
            extra={
                "caller_filename": os.path.abspath(__file__),
                "caller_lineno": inspect.currentframe().f_lineno,
            },
        )
        self._logger.debug(
            "log_file: {}".format(self.log_file),
            extra={
                "caller_filename": os.path.abspath(__file__),
                "caller_lineno": inspect.currentframe().f_lineno,
            },
        )
        self._logger.debug(
            "log_size: {}".format(self.log_size),
            extra={
                "caller_filename": os.path.abspath(__file__),
                "caller_lineno": inspect.currentframe().f_lineno,
            },
        )
        self._logger.debug(
            "log_num: {}".format(self.log_num),
            extra={
                "caller_filename": os.path.abspath(__file__),
                "caller_lineno": inspect.currentframe().f_lineno,
            },
        )
        self._logger.debug(
            "console_level: {}".format(self.console_level),
            extra={
                "caller_filename": os.path.abspath(__file__),
                "caller_lineno": inspect.currentframe().f_lineno,
            },
        )
        self._logger.debug(
            "file_level: {}".format(self.file_level),
            extra={
                "caller_filename": os.path.abspath(__file__),
                "caller_lineno": inspect.currentframe().f_lineno,
            },
        )

        self._cleanup_old_logs()

    def init_log_from_file(self, config_file, user_class=None, log_format=None):
        from xconfig import XConfigParser

        config_parser = XConfigParser(config_file)
        log_configs = config_parser.get_config_data(
            section="log",
            config_class=config_parser.create_config_class(
                "log", XLogger.log_config_def
            ),
        )
        print(log_configs)

        log_config = (
            log_configs.get("log", [{}])[0]  # Get first config or empty dict
            if log_configs and isinstance(log_configs, dict)
            else {}
        )
        print(log_config)

        self.init_log(log_config, user_class, log_format)

    def _cleanup_old_logs(self):
        """
        Clean up old log files if the number exceeds the limit.
        """
        import re

        log_files = [
            f
            for f in glob.glob(os.path.join(self.logpath, "*"))
            if re.match(r".*\.log(\.\d+)?$", f)
        ]
        log_files.sort(key=os.path.getmtime)  # Sort by modification time (oldest first)

        while len(log_files) > self.log_num:
            oldest_file = log_files.pop(0)
            try:
                os.remove(oldest_file)
                self._logger.info(
                    "Removed old log file: {}".format(oldest_file),
                    extra={
                        "caller_filename": os.path.abspath(__file__),
                        "caller_lineno": inspect.currentframe().f_lineno,
                    },
                )
            except Exception as e:
                self._logger.critical(
                    "Failed to remove old log file {}: {}".format(oldest_file, e),
                    extra={
                        "caller_filename": os.path.abspath(__file__),
                        "caller_lineno": inspect.currentframe().f_lineno,
                    },
                )

    def get_current_logfile(self):
        """
        Get the current log file name.

        :return: The full path of the current log file.
        """
        return self.logname

    def _get_caller_info(self):
        """Get the filename and line number of the caller."""
        current_frame = inspect.currentframe()
        try:
            skip_frames = 4
            for _ in range(skip_frames):
                if current_frame.f_back:
                    current_frame = current_frame.f_back
            filename = current_frame.f_code.co_filename
            lineno = current_frame.f_lineno
            return os.path.abspath(filename), lineno
        finally:
            del current_frame

    def log(self, level, message, *args, **kwargs):
        """
        Generic log method

        Args:
            level: Logging level (DEBUG, INFO, etc.)
            message: Log message
            *args: Format args
            **kwargs: Additional params
        """
        extra = kwargs.pop("extra", {})
        # Ensure caller_filename and caller_lineno are set
        if "caller_filename" not in extra or "caller_lineno" not in extra:
            caller_filename, caller_lineno = self._get_caller_info()
            extra["caller_filename"] = caller_filename
            extra["caller_lineno"] = caller_lineno
        self._logger.log(level, message, *args, extra=extra, **kwargs)

    # Convenience methods
    def debug(self, message, *args, **kwargs):
        self.log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self.log(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self.log(logging.WARNING, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.log(logging.ERROR, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self.log(logging.CRITICAL, message, *args, **kwargs)
