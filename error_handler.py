import time
from functools import wraps
from config import Config
from logger import Logger

logger = Logger.get_logger("error_handler")


class ErrorType:
    """Error classification"""

    RECOVERABLE = "recoverable"
    DEGRADABLE = "degradable"
    FATAL = "fatal"


class RetryableError(Exception):
    """Error that can be retried"""

    pass


class DegradableError(Exception):
    """Error that allows degraded operation"""

    pass


class FatalError(Exception):
    """Fatal error that requires shutdown"""

    pass


def retry_with_backoff(max_retries=None, base_delay=None):
    """Decorator for exponential backoff retry"""
    if max_retries is None:
        max_retries = Config.MAX_RETRIES
    if base_delay is None:
        base_delay = Config.RETRY_DELAY_BASE

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RetryableError as e:
                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise

                    delay = base_delay * (2**attempt)
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)
                except (DegradableError, FatalError):
                    raise
                except Exception as e:
                    logger.error(f"{func.__name__} encountered unexpected error: {e}")
                    raise

        return wrapper

    return decorator


def handle_errors(max_retries=None, retry_delay=None, error_type=ErrorType.RECOVERABLE):
    """Decorator for error handling with retry support"""
    if max_retries is None:
        max_retries = Config.MAX_RETRIES
    if retry_delay is None:
        retry_delay = Config.RETRY_DELAY_BASE

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RetryableError as e:
                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} retries: {e}"
                        )
                        if error_type == ErrorType.RECOVERABLE:
                            return None
                        raise

                    delay = retry_delay * (2**attempt)
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)
                except DegradableError as e:
                    logger.error(f"Degradable error in {func.__name__}: {e}")
                    if error_type == ErrorType.DEGRADABLE:
                        return None
                    raise
                except FatalError as e:
                    logger.critical(f"Fatal error in {func.__name__}: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                    raise

        return wrapper

    return decorator
