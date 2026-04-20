import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def safe_input(prompt: str) -> str:
    """Надёный ввод с fallback для перенаправленного stdin."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        pass
    try:
        return sys.stdin.readline().strip()
    except (EOFError, KeyboardInterrupt):
        return ''


def setup_logging(verbose: bool, log_file: Path) -> None:
    """Настройка логирования с ротацией файлов."""
    level = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if root_logger.handlers:
        root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def ensure_dirs(dirs: list[Path]) -> None:
    """Создание директорий, если не существуют."""
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)