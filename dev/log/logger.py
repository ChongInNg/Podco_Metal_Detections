import logging
from abc import ABC, abstractmethod
from datetime import datetime

# output print or logging
GLOABLE_OUTPUT_PRINT = True



class Identifiable(ABC):
    @abstractmethod
    def get_identity(self) -> str:
        """Returns the identity of the object."""
        pass

class Logger:
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            log_level = logging.DEBUG
            cls._instance.__init_manual__(log_level)
        return cls._instance

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

    def __init_manual__(self, log_level=logging.DEBUG):
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(levelname)s] - %(message)s',
        )
        self.logger = logging.getLogger('BlackJack_logger')

    def _debug(self, message, *args):
        self._log(logging.DEBUG, message, *args)

    def _info(self, message, *args):
        self._log(logging.INFO, message, *args)

    def _warning(self, message, *args):
        self._log(logging.WARNING, message, *args)

    def _error(self, message, *args):
        self._log(logging.ERROR, message, *args)

    def _critical(self, message, *args):
        self._log(logging.CRITICAL, message, *args)

    def _log(self, log_level, message, *args):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}"
        if args:
            log_message += ', ' + ', '.join(map(str, args))
        
        global GLOABLE_OUTPUT_PRINT
        if not GLOABLE_OUTPUT_PRINT:
            self.logger.log(log_level, log_message)
        else:
            print(f"{log_level}: {log_message}")