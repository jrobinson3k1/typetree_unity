"""Logging configuration."""

import os
import logging
from logging import LogRecord
from logging import StreamHandler


class _NoStackTraceStreamHandler(StreamHandler):
    """Does not emit stack trace to stream."""

    __doc__ += StreamHandler.__doc__

    def emit(self, record):  # noqa: D102
        try:
            if record.exc_info:
                record = LogRecord(
                    record.name, record.levelname, record.pathname, record.lineno,
                    record.msg, record.args, None, record.funcName, record.stack_info
                )
            super().emit(record)
        except Exception:  # pylint: disable=broad-except
            self.handleError(record)


logs_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "logs"
)
if not os.path.isdir(logs_dir):
    os.mkdir(logs_dir)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M:%S",
    filename=os.path.join(logs_dir, "logs.txt"),
    filemode="w"
)
logging.info("--- Init logging ---")

console = _NoStackTraceStreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(message)s'))
logging.getLogger().addHandler(console)

def set_level(level):
    """Set the log level on the terminal output."""
    console.setLevel(level)
