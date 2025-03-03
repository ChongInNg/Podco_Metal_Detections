import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from logging.handlers import RotatingFileHandler

RED = '\033[91m'
RESET = '\033[0m'

class Identifiable(ABC):
    @abstractmethod
    def get_identity(self) -> str:
        # returns the identity of the object. the object have to provide
        pass

class Logger:
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.logger = logging.getLogger('server_logger')
            cls._instance.logger.handlers = []
        return cls._instance
    
    def init(self, log_folder:str, log_file_level: int, 
             max_bytes=1024, backup_count=10):
        self.log_file_level = log_file_level
        os.makedirs(log_folder, exist_ok=True)

        log_file = "server.log"
        full_log_path = os.path.join(log_folder, log_file)
        self.logger.setLevel(self.log_file_level)
        formatter = logging.Formatter('[%(levelname)s]-%(message)s')
        self.file_handler = RotatingFileHandler(
            filename=full_log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        self.file_handler.setFormatter(formatter)
        self.file_handler.setLevel(logging.ERROR)
        self.logger.addHandler(self.file_handler)
        self.log_file = full_log_path

    @classmethod
    def debug(cls, message: str, *args):
        cls.instance()._debug(message, *args)

    @classmethod
    def info(cls, message: str, *args):
        cls.instance()._info(message, *args)

    @classmethod
    def warning(cls, message: str, *args):
        cls.instance()._warning(message, *args)

    @classmethod
    def error(cls, message: str, *args):
        cls.instance()._error(message, *args)

    @classmethod
    def critical(cls, message: str, *args):
        cls.instance()._critical(message, *args)

    @classmethod
    def debug_with_identity(cls, obj: Identifiable, message: str, *args):
        cls.instance()._debug(f"{obj.get_identity()} {message}", *args)

    @classmethod
    def info_with_identity(cls, obj: Identifiable, message: str, *args):
        cls.instance()._info(f"{obj.get_identity()} {message}", *args)

    @classmethod
    def warning_with_identity(cls, obj: Identifiable, message: str, *args):
        cls.instance()._warning(f"{obj.get_identity()} {message}", *args)

    @classmethod
    def error_with_identity(cls, obj: Identifiable, message: str, *args):
        cls.instance()._error(f"{obj.get_identity()} {message}", *args)

    @classmethod
    def critical_with_identity(cls, obj: Identifiable, message: str, *args):
        cls.instance()._critical(f"{obj.get_identity()} {message}", *args)

    def _debug(self, message, *args):
        self._log(logging.DEBUG, message, *args)

    def _info(self, message, *args):
        self._log(logging.INFO, message, *args)

    def _warning(self, message, *args):
        self._log(logging.WARNING, message, *args)

    def _error(self, message, *args):
        self._log(logging.ERROR, message, *args)
        self.file_handler.flush()

    def _critical(self, message, *args):
        self._log(logging.CRITICAL, message, *args)
        self.file_handler.flush()

    def _log(self, log_level, message, *args):
        if log_level < logging.INFO:
            # no need to log
            return

        timestamp = datetime.now().isoformat(timespec='milliseconds')
        log_message = f"[{timestamp}] {message}"
        if args:
            log_message += ', ' + ', '.join(map(str, args))

        if log_level < logging.ERROR:
            print(f"[{self.get_level_name(log_level)}]-{log_message}")
        else:
            print(f"{RED}[{self.get_level_name(log_level)}]-{log_message}{RESET}")

        if log_level >= self.log_file_level:
            self.logger.log(log_level, log_message)

    def get_level_name(self, log_level: int)->str:
        # CRITICAL = 50
        # FATAL = CRITICAL
        # ERROR = 40
        # WARNING = 30
        # WARN = WARNING
        # INFO = 20
        # DEBUG = 10
        # NOTSET = 0
        if log_level == 0:
            return "NOTSET"
        elif log_level == 10:
            return "DEBUG"
        elif log_level == 20:
            return "INFO"
        elif log_level == 30:
            return "WARNING"
        elif log_level == 40:
            return "ERROR"
        elif log_level == 50:
            return "CRITICAL"
        else:
            return "UNKNOWN"
        
