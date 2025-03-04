import unittest
import logging

from hijiki.logger import configure_logger


class TestLoggerConfig(unittest.TestCase):
    def test_logger_configuration(self):
        configure_logger()
        logger = logging.getLogger()
        self.assertTrue(any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers))