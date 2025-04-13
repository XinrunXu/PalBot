import logging
import os
from pathlib import Path
import sys
import time
from datetime import datetime
from typing import Optional, Union, List

from pal_agent.utils import Singleton
from pal_agent.config.config import Config

config = Config()

class BaseLogger(metaclass=Singleton):
    """Base logger class with core logging functionality"""

    def __init__(self, name: str = "Logger"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        self._configure_handlers()

    def _configure_handlers(self):
        """Configure default console handlers"""
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.setFormatter(formatter)

        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.ERROR)
        stderr_handler.setFormatter(formatter)

        self._logger.addHandler(stdout_handler)
        self._logger.addHandler(stderr_handler)

    def log(self, level: int, message: str):
        """Base log method"""
        self._logger.log(level, message)

    def debug(self, message: str):
        self.log(logging.DEBUG, message)

    def info(self, message: str):
        self.log(logging.INFO, message)

    def warning(self, message: str):
        self.log(logging.WARNING, message)

    def error(self, message: str):
        self.log(logging.ERROR, message)

    def critical(self, message: str):
        self.log(logging.CRITICAL, message)


class FileLoggerMixin(metaclass=Singleton):
    """Mixin that adds file logging capability with timestamped filenames"""

    def __init__(self,
                 log_dir: str = config.work_dir,
                 log_file: str = None):
        # 如果没有提供log_file，则使用带时间戳的默认文件名
        self.log_file = 'palbot.log'

        self.log_dir = log_dir
        self._add_file_handler()

    def _add_file_handler(self):
        """Add file handler to logger with timestamped filename"""
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        log_path = os.path.join(self.log_dir, self.log_file)

        file_handler = logging.FileHandler(
            filename=log_path,
            mode='w',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self._logger.addHandler(file_handler)


class SystemMetricsFormatter(logging.Formatter, metaclass=Singleton):
    """Formatter that adds system metrics to log records"""

    def format(self, record):
        import psutil

        record.cpu_usage = psutil.cpu_percent(interval=None)
        record.memory_usage = psutil.virtual_memory().percent

        return super().format(record)


class SystemMetricsLoggerMixin(metaclass=Singleton):
    """Mixin that adds system metrics to logs"""

    def _configure_handlers(self):
        """Configure handlers with system metrics formatter"""
        formatter = SystemMetricsFormatter(
            '%(asctime)s - CPU: %(cpu_usage)s%%, Memory: %(memory_usage)s%% - '
            '%(name)s - %(levelname)s - %(message)s'
        )

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.setFormatter(formatter)

        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.ERROR)
        stderr_handler.setFormatter(formatter)

        self._logger.addHandler(stdout_handler)
        self._logger.addHandler(stderr_handler)


class ColoredFormatter(logging.Formatter, metaclass=Singleton):
    """Formatter that adds color to console output"""

    COLORS = {
        logging.WARNING: '\033[93m',  # Yellow
        logging.ERROR: '\033[91m',    # Red
        logging.DEBUG: '\033[92m',    # Green
        logging.INFO: '\033[97m',     # White
        logging.CRITICAL: '\033[91m\033[47m'  # Red on white
    }

    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelno, '')
        message = super().format(record)
        return f"{color}{message}{self.RESET}" if color else message


class ColoredLoggerMixin(metaclass=Singleton):
    """Mixin that adds colored output to console logs"""

    def _configure_handlers(self):
        """Configure handlers with colored formatter"""
        formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.setFormatter(formatter)

        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.ERROR)
        stderr_handler.setFormatter(formatter)

        self._logger.addHandler(stdout_handler)
        self._logger.addHandler(stderr_handler)


class Logger(BaseLogger, FileLoggerMixin, SystemMetricsLoggerMixin, ColoredLoggerMixin, metaclass=Singleton):
    """Main application logger combining all features"""

    def __init__(
        self,
        name: str = "Logger",
        log_dir: Optional[str] = config.work_dir,
        log_file: str = None
    ):
        BaseLogger.__init__(self, name)
        FileLoggerMixin.__init__(self, log_dir, log_file)


# Example usage
if __name__ == "__main__":

    logger = Logger("TestLogger")

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")