import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from config import Config


class Logger:
    """Centralized logging system"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name):
        """Get or create a logger"""
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))

        # Create logs directory if not exists
        Path(Config.LOGS_DIR).mkdir(parents=True, exist_ok=True)

        # Main log file
        today = datetime.now().strftime("%Y-%m-%d")
        main_handler = logging.FileHandler(
            f"{Config.LOGS_DIR}/financial-news-{today}.log", encoding="utf-8"
        )
        main_handler.setLevel(logging.DEBUG)

        # Error log file
        error_handler = logging.FileHandler(
            f"{Config.LOGS_DIR}/errors-{today}.log", encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        main_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(main_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def cleanup_old_logs(cls):
        """Remove logs older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=Config.LOG_RETENTION_DAYS)
        logs_dir = Path(Config.LOGS_DIR)

        if not logs_dir.exists():
            return

        for log_file in logs_dir.glob("*.log"):
            try:
                # Extract date from filename
                date_str = log_file.stem.split("-")[-3:]
                if len(date_str) == 3:
                    file_date = datetime.strptime("-".join(date_str), "%Y-%m-%d")
                    if file_date < cutoff_date:
                        log_file.unlink()
                        print(f"Deleted old log: {log_file}")
            except (ValueError, IndexError):
                continue
