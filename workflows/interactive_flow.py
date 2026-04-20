import logging
import shutil
from pathlib import Path
from typing import Optional

from tools.converter import convert, get_markdown_path
from tools.utils import safe_input

logger = logging.getLogger(__name__)


def confirm(prompt: str) -> bool:
    """Запрос подтверждения. Принимает y/yes/да (case-insensitive)."""
    answer = safe_input(prompt).lower().strip()
    return answer in ('y', 'yes', 'да')


def edit_file(path: Path) -> str:
    """Предложить пользователю редактировать файл.

    Returns:
        'edited' — файл был редактирован
        'skip' — пользователь пропустил редактирование
        'abort' — пользователь прервал работу
    """
    editor = Path.getenv('EDITOR', 'nano' if shutil.which('nano') else 'vim')
    answer = safe_input(f"Открыть {path} в {editor}? [y/e/s/a]: ").lower().strip()

    if answer in ('y', 'e'):
        import subprocess
        subprocess.run([editor, str(path)])
        return 'edited'
    elif answer == 's':
        return 'skip'
    else:
        return 'abort'


class InteractiveFlow:
    """Интерактивный конвейер обработки документов."""

    def __init__(self, temp_dir: Path, output_dir: Path, auto: bool = False, force: bool = False):
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        self.auto = auto
        self.force = force

    def process_file(self, input_path: Path) -> Optional[Path]:
        """Обработка одного файла.

        Returns:
            Path — путь к финальному файлу в output/
            None — файл пропущен или прерван
        """
        logger.info(f"Обработка: {input_path.name}")

        md_path = get_markdown_path(self.temp_dir, input_path.name)

        result = convert(input_path, self.temp_dir)

        if result == 'timeout':
            logger.error(f"Таймаут конвертации: {input_path}")
            if self.auto:
                logger.warning("Пропуск файла в auto-режиме")
                return None
            action = safe_input("[R]etry, [S]kip, [A]bort: ").lower().strip()
            if action == 'r':
                result = convert(input_path, self.temp_dir)
            elif action == 's':
                return None
            else:
                return None

        if result != 'ok':
            logger.error(f"Конвертация не удалась: {input_path}")
            return None

        if not md_path.exists():
            logger.error(f"Marker не создал файл: {md_path}")
            return None

        try:
            file_size = md_path.stat().st_size
        except OSError as e:
            logger.error(f"Нет доступа к файлу: {e}")
            return None

        if file_size == 0:
            logger.warning(f"Пустой результат: {md_path}")
            if not confirm("Продолжить с пустым файлом?"):
                return None

        if self.auto:
            final_path = self._save_to_output(md_path, input_path.name)
            return final_path

        print(f"\nРезультат: {md_path}")
        print(f"Размер: {md_path.stat().st_size} байт")

        action = safe_input("Подтвердить [Y], редактировать [E], пропустить [S], прервать [A]: ").lower().strip()

        if action == 'a':
            return None
        elif action == 's':
            return None
        elif action == 'e':
            result = edit_file(md_path)
            if result == 'abort':
                return None

        final_path = self._save_to_output(md_path, input_path.name)
        return final_path

    def _save_to_output(self, md_path: Path, original_name: str) -> Path:
        """Копирование файла из temp в output."""
        final_path = self.output_dir / md_path.name

        if final_path.exists() and not self.force:
            if not confirm(f"Файл {final_path.name} уже существует. Перезаписать?"):
                alt_path = self.output_dir / f"{md_path.stem}_new{md_path.suffix}"
                final_path = alt_path

        shutil.copy2(md_path, final_path)
        logger.info(f"Сохранено: {final_path}")
        return final_path

    def process_directory(self, input_dir: Path) -> None:
        """Обработка всех поддерживаемых файлов в директории."""
        from config.settings import SUPPORTED_EXTENSIONS

        files = []
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(input_dir.glob(f"*{ext}"))

        if not files:
            logger.warning(f"Нет файлов для обработки в {input_dir}")
            return

        logger.info(f"Найдено файлов: {len(files)}")

        for file_path in sorted(files):
            try:
                self.process_file(file_path)
            except Exception as e:
                logger.exception(f"Ошибка при обработке {file_path}: {e}")
                if not confirm("Продолжить с остальными файлами?"):
                    break