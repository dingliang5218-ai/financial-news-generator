import os
import shutil
from pathlib import Path
from anthropic import Anthropic
from config import Config
from logger import Logger
from error_handler import FatalError

logger = Logger.get_logger("health_check")


class HealthCheck:
    """System health check"""

    @staticmethod
    def startup_check():
        """Comprehensive startup health check"""
        logger.info("Starting system health check...")

        checks = {
            "config": HealthCheck._check_config(),
            "dependencies": HealthCheck._check_dependencies(),
            "storage": HealthCheck._check_storage(),
            "api": HealthCheck._check_api_connection(),
        }

        failed_checks = [name for name, passed in checks.items() if not passed]

        if failed_checks:
            error_msg = f"Health check failed: {', '.join(failed_checks)}"
            logger.critical(error_msg)
            raise FatalError(error_msg)

        logger.info("All health checks passed ✓")
        return True

    @staticmethod
    def _check_config():
        """Check configuration"""
        try:
            Config.validate()
            logger.info("✓ Configuration valid")
            return True
        except Exception as e:
            logger.error(f"✗ Configuration check failed: {e}")
            return False

    @staticmethod
    def _check_dependencies():
        """Check required dependencies"""
        try:
            import feedparser
            import anthropic
            import apscheduler

            logger.info("✓ All dependencies installed")
            return True
        except ImportError as e:
            logger.error(f"✗ Missing dependency: {e}")
            return False

    @staticmethod
    def _check_storage():
        """Check storage directories and permissions"""
        try:
            # Check data directory
            Path(Config.DATA_DIR).mkdir(parents=True, exist_ok=True)
            Path(Config.BACKUP_DIR).mkdir(parents=True, exist_ok=True)
            Path(Config.LOGS_DIR).mkdir(parents=True, exist_ok=True)

            # Check write permissions
            test_file = Path(Config.DATA_DIR) / ".write_test"
            test_file.write_text("test")
            test_file.unlink()

            # Check disk space (at least 100MB)
            stat = shutil.disk_usage(Config.DATA_DIR)
            free_mb = stat.free / (1024 * 1024)
            if free_mb < 100:
                logger.warning(f"Low disk space: {free_mb:.1f}MB free")

            logger.info(f"✓ Storage check passed ({free_mb:.1f}MB free)")
            return True
        except Exception as e:
            logger.error(f"✗ Storage check failed: {e}")
            return False

    @staticmethod
    def _check_api_connection():
        """Test Claude API connection"""
        try:
            client = Anthropic(api_key=Config.CLAUDE_API_KEY)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}],
            )
            logger.info("✓ Claude API connection successful")
            return True
        except Exception as e:
            logger.error(f"✗ Claude API connection failed: {e}")
            return False

    @staticmethod
    def runtime_check():
        """Runtime health check before each task"""
        checks = {
            "disk_space": HealthCheck._check_disk_space(),
            "database": HealthCheck._check_database(),
        }

        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            logger.warning(f"Runtime health issues: {', '.join(failed)}")

        return all(checks.values())

    @staticmethod
    def _check_disk_space():
        """Check available disk space"""
        try:
            stat = shutil.disk_usage(Config.DATA_DIR)
            free_mb = stat.free / (1024 * 1024)
            if free_mb < 50:
                logger.error(f"Critical: Low disk space ({free_mb:.1f}MB)")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to check disk space: {e}")
            return False

    @staticmethod
    def _check_database():
        """Check database connection"""
        try:
            import sqlite3

            with sqlite3.connect(Config.DB_PATH) as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            return False
