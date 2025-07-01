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

from xFunc import XFunc, PY2

if PY2:
    reload(sys)  # type: ignore
    sys.setdefaultencoding("utf-8")
    text_type = unicode  # type: ignore
    binary_type = str
else:
    text_type = str
    binary_type = bytes


class UTF8SafeFormatter(logging.Formatter):
    def format(self, record):
        message = super(UTF8SafeFormatter, self).format(record)
        if not isinstance(message, text_type):
            try:
                message = message.decode("utf-8", errors="replace")
            except (UnicodeDecodeError, AttributeError):
                message = text_type(message, "utf-8", errors="replace")
        return message


class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            message = self.format(record)
            if not isinstance(message, text_type):
                message = text_type(message, "utf-8", errors="replace")

            if PY2:
                message = message.encode("utf-8", errors="replace")

            stream = self.stream
            stream.write(message)
            stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


class XLogger(object):
    # Define configuration with types and defaults
    log_config_def = [
        ("path", True, None, str),
        ("size", False, 10, int),
        ("num", False, 0, int),
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
            try:
                caller_frame = inspect.currentframe().f_back
                caller_self = caller_frame.f_locals.get("self")
                user_class = (
                    caller_self.__class__.__name__ if caller_self else "UnknownClass"
                )
            except Exception:
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

        self._log_init_info()

        if 0 != self.log_num:
            self._cleanup_old_logs()

        self._logger.debug(
            "Logger initialized successfully",
            extra=self._get_caller_extra(1),
        )

    def _log_init_info(self):
        debug_info = {
            "log_path": self.logpath,
            "log_file": self.log_file,
            "log_size": self.log_size,
            "log_num": self.log_num,
            "console_level": self.log_config.console_level,
            "file_level": self.log_config.file_level,
        }

        for key, value in debug_info.items():
            self._logger.debug(
                "{}: {}".format(key, value),
                extra=self._get_caller_extra(1),
            )

    def _get_caller_extra(self, levels_up=2):
        current_frame = inspect.currentframe()
        try:
            for _ in range(levels_up):
                if current_frame.f_back:
                    current_frame = current_frame.f_back
            return {
                "caller_filename": os.path.abspath(current_frame.f_code.co_filename),
                "caller_lineno": current_frame.f_lineno,
            }
        finally:
            del current_frame

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

    def init_log_from_file(self, config_file, user_class=None, log_format=None):
        from x_common.xConfig import XConfigParser

        config_parser = XConfigParser(config_file)
        log_configs = config_parser.get_config_data(
            section="log",
            config_class=config_parser.create_config_class(
                "log", XLogger.log_config_def
            ),
        )
        # print(log_configs)

        log_config = (
            log_configs.get("log", [{}])[0]  # Get first config or empty dict
            if log_configs and isinstance(log_configs, dict)
            else {}
        )
        # print(log_config)

        self.init_log(log_config, user_class, log_format)

    def get_current_logfile(self):
        """
        Get the current log file name.

        :return: The full path of the current log file.
        """
        return self.logname

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
            extra = self._get_caller_extra(4)
            # Ensure the message is a Unicode string before logging

        safe_message = XFunc.ensure_text(message)
        self._logger.log(level, safe_message, *args, extra=extra, **kwargs)

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


if __name__ == "__main__":
    logger = XLogger()
    XLogger.log_config_def
    logger.init_log_from_file(
        XFunc.get_parent_path("config/config.xml"),
        user_class="demo",
        log_format=None,
    )

    logger.info("这是一条中文日志信息")
    logger.debug("Debug message with Chinese: 中文调试信息")
    logger.warning("Warning with special chars: öäüß")
    logger.error("Error message with special chars: öäüß")
    logger.critical("Critical message with special chars: öäüß")
    current_logfile = logger.get_current_logfile()
    logger.warning("Current log file: {}".format(current_logfile))
