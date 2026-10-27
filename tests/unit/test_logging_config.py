# tests/unit/test_logging_config.py

import logging

import pytest

from app.logging_config import LOGGER_NAME, close_logging, setup_logging


@pytest.fixture
def log_file(tmp_path):
    """Set logging up with a log file in a temporary folder, and clean up afterwards."""
    path = tmp_path / "logs" / "app.log"
    setup_logging(log_file=path)
    yield path
    close_logging()


def read(path):
    return path.read_text(encoding="utf-8")


def test_log_folder_and_file_are_created(log_file):
    assert log_file.parent.is_dir()
    assert log_file.exists()


@pytest.mark.parametrize("method, level", [
    ("info", "INFO"),
    ("warning", "WARNING"),
    ("error", "ERROR"),
])
def test_each_level_is_written_to_the_file(log_file, method, level):
    getattr(logging.getLogger(LOGGER_NAME), method)("something happened")
    assert f"{level} calculator: something happened" in read(log_file)


def test_child_loggers_end_up_in_the_same_file(log_file):
    logging.getLogger("calculator.operations").info("from the operations module")
    assert "calculator.operations: from the operations module" in read(log_file)


def test_debug_messages_are_not_written(log_file):
    logging.getLogger(LOGGER_NAME).debug("too detailed")
    assert "too detailed" not in read(log_file)


def test_calling_setup_twice_does_not_repeat_messages(tmp_path):
    path = tmp_path / "app.log"
    setup_logging(log_file=path)
    setup_logging(log_file=path)
    logging.getLogger(LOGGER_NAME).info("only once")
    close_logging()
    assert read(path).count("only once") == 1


def test_close_logging_stops_writing_to_the_file(tmp_path):
    path = tmp_path / "app.log"
    setup_logging(log_file=path)
    close_logging()
    logging.getLogger(LOGGER_NAME).info("after close")
    assert "after close" not in read(path)


def test_setup_logging_accepts_a_different_level(tmp_path):
    path = tmp_path / "app.log"
    setup_logging(level=logging.ERROR, log_file=path)
    logging.getLogger(LOGGER_NAME).warning("quiet")
    logging.getLogger(LOGGER_NAME).error("loud")
    close_logging()
    text = read(path)
    assert "quiet" not in text
    assert "loud" in text