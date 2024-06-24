from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger
from mpi4py import MPI

logger.configure(extra={"classname": "None"})


class Logger:
    def __init__(self) -> None:
        """Initialize logger."""
        self.logger = logger.bind(
            classname=f"({self.__module__.split('.')[0]}) {self.__class__.__name__}"
        )


def default_logger(
    logfile: Path,
    level: str = "INFO",
    fmt_console: str | None = None,
    fmt_file: str | None = None,
) -> list[int]:
    """Set up default logger for console and file sinks.

    Suppresses output from all MPI processes except rank 0.

    Args:
        logfile: path to output log file
        level: reported log level
        fmt_console: optional console log format
        fmt_file: optional log file format

    Returns:
        list of integer identifiers for console and file sinks
    """
    logfile.unlink(missing_ok=True)
    if not fmt_console:
        fmt_console = (
            "<lvl>{level:<8}</> | "
            "<c>{extra[classname]:<30}:{function:<8}</> - <lvl>{message}</>"
        )
    if not fmt_file:
        fmt_file = (
            "{time:YYYY-MM-DDTHH:mm:ss.SSS} ({elapsed}) | {level:<8} | "
            "{extra[classname]:<30}:{function:<8} - {message}"
        )
    logger.remove()
    i_c = logger.add(
        sys.stderr,
        format=fmt_console,
        level=level,
        filter=lambda rec: MPI.COMM_WORLD.rank == 0,
    )
    i_f = logger.add(
        logfile,
        format=fmt_file,
        level=level,
        filter=lambda rec: MPI.COMM_WORLD.rank == 0,
        rotation="100 MB",
        compression="gz",
    )
    return [i_c, i_f]
