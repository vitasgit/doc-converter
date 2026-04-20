import logging
import subprocess
from pathlib import Path

from config.settings import MARKER_FLAGS, MARKER_LANGUAGES, MARKER_TIMEOUT

logger = logging.getLogger(__name__)


def get_markdown_path(output_dir: Path, input_name: str) -> Path:
    """Путь к markdown-файлу, который создаст Marker."""
    return output_dir / f"{Path(input_name).stem}.md"


def convert(input_path: Path, output_dir: Path, **marker_kwargs) -> str:
    """Конвертация файла через Marker CLI.

    Args:
        input_path: Путь к исходному файлу (.pdf или .docx)
        output_dir: Директория для сохранения результата
        **marker_kwargs: Дополнительные флаги для Marker

    Returns:
        str: 'ok' при успехе, 'timeout' при таймауте, 'error' при ошибке

    Raises:
        FileNotFoundError: Если файл не существует
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Файл не найден: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        'marker',
        str(input_path),
        '--output_dir', str(output_dir),
        '--output_format', 'markdown',
        '--languages', MARKER_LANGUAGES,
    ]

    for flag in MARKER_FLAGS:
        cmd.append(flag)

    for key, value in marker_kwargs.items():
        cmd.extend([f'--{key}', str(value)])

    logger.debug(f"Запуск: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=MARKER_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        logger.error(f"Таймаут ({MARKER_TIMEOUT}s) при обработке {input_path}")
        return 'timeout'
    except FileNotFoundError:
        logger.error("Marker не найден. Установите: pip install marker-pdf")
        raise

    if result.returncode == 0:
        logger.info(f"Конвертация завершена: {input_path}")
        if result.stdout:
            logger.debug(f"Marker stdout: {result.stdout}")
        return 'ok'

    logger.error(f"Marker вернул код {result.returncode}: {input_path}")
    if result.stderr:
        logger.error(f"Marker stderr: {result.stderr}")

    return 'error'