#!/usr/bin/env python3
"""
System Integration Test Script
Tests all components without making real API calls
"""

import sys
from pathlib import Path
from datetime import datetime

from config import Config
from logger import Logger
from storage import Storage
from error_handler import RetryableError, FatalError, handle_errors

logger = Logger.get_logger("test")


class SystemTest:
    """System integration tests"""

    def __init__(self):
        self.storage = Storage()
        self.passed = 0
        self.failed = 0

    def run_all_tests(self):
        """Run all system tests"""
        logger.info("=" * 60)
        logger.info("Starting System Integration Tests")
        logger.info("=" * 60)

        tests = [
            ("Configuration", self.test_config),
            ("Logger", self.test_logger),
            ("Storage", self.test_storage),
            ("Error Handler", self.test_error_handler),
            ("Health Check", self.test_health_check),
        ]

        for name, test_func in tests:
            try:
                logger.info(f"\nTesting: {name}")
                test_func()
                self.passed += 1
                logger.info(f"✓ {name} test passed")
            except Exception as e:
                self.failed += 1
                logger.error(f"✗ {name} test failed: {e}")

        self.print_summary()
        return self.failed == 0

    def test_config(self):
        """Test configuration"""
        # Test config loading
        assert Config.VERSION, "Version not set"
        assert Config.DATA_DIR, "Data directory not set"

        # Skip API key check in test mode
        # assert Config.CLAUDE_API_KEY, "API key not set"

        # Test validation (will fail if API key not set, but that's ok for testing)
        try:
            Config.validate()
        except ValueError as e:
            # Expected if no API key or RSS feeds configured
            logger.info(f"  - Config validation: {e} (expected in test mode)")

        logger.info("  - Config loaded successfully")
        logger.info(f"  - Version: {Config.VERSION}")
        logger.info(f"  - Data directory: {Config.DATA_DIR}")

    def test_logger(self):
        """Test logging system"""
        test_logger = Logger.get_logger("test_component")

        # Test different log levels
        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")

        # Check log file exists
        log_file = (
            Path(Config.LOGS_DIR) / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        )
        assert log_file.exists(), "Log file not created"

        logger.info("  - All log levels working")
        logger.info(f"  - Log file: {log_file}")

    def test_storage(self):
        """Test storage operations"""
        # Test database initialization
        assert Path(Config.DB_PATH).exists(), "Database not created"

        # Test article storage
        test_article = {
            "title": "Test Article",
            "content": "Test content",
            "summary": "Test summary",
            "category": "test",
            "keywords": ["test", "article"],
            "source_urls": ["http://example.com"],
            "generated_at": datetime.now().isoformat(),
        }

        article_id = self.storage.save_article(test_article)
        assert article_id, "Failed to save article"

        # Test article retrieval
        retrieved = self.storage.get_article(article_id)
        assert retrieved, "Failed to retrieve article"
        assert retrieved["title"] == test_article["title"], "Article data mismatch"

        # Test article listing
        articles = self.storage.get_recent_articles(limit=1)
        assert len(articles) > 0, "Failed to list articles"

        # Test article search
        results = self.storage.search_articles("Test")
        assert len(results) > 0, "Failed to search articles"

        logger.info("  - Database operations working")
        logger.info(f"  - Test article ID: {article_id}")

    def test_error_handler(self):
        """Test error handling"""

        # Test retryable error with retry
        @handle_errors(max_retries=2, retry_delay=0.1)
        def failing_function():
            raise RetryableError("Test error")

        # Should return None after retries (recoverable)
        result = failing_function()
        assert result is None, "Should return None for recoverable error"

        # Test fatal error
        try:
            raise FatalError("Test fatal error")
        except FatalError as e:
            assert str(e) == "Test fatal error", "Fatal error message mismatch"

        logger.info("  - Error handling working")
        logger.info("  - Retry mechanism tested")

    def test_health_check(self):
        """Test health check system"""
        from health_check import HealthCheck

        # Test storage check
        assert HealthCheck._check_storage(), "Storage check failed"

        # Test disk space check
        assert HealthCheck._check_disk_space(), "Disk space check failed"

        # Test database check
        assert HealthCheck._check_database(), "Database check failed"

        # Test runtime check
        assert HealthCheck.runtime_check(), "Runtime check failed"

        logger.info("  - Health checks working")
        logger.info("  - All subsystems healthy")

    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 60)
        logger.info("Test Summary")
        logger.info("=" * 60)
        logger.info(f"Passed: {self.passed}")
        logger.info(f"Failed: {self.failed}")
        logger.info(f"Total:  {self.passed + self.failed}")

        if self.failed == 0:
            logger.info("\n✓ All tests passed!")
        else:
            logger.error(f"\n✗ {self.failed} test(s) failed")


def main():
    """Main test entry point"""
    try:
        tester = SystemTest()
        success = tester.run_all_tests()
        return 0 if success else 1

    except Exception as e:
        logger.critical(f"Test suite failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
