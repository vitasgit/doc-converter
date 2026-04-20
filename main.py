#!/usr/bin/env python3
import sys
import shutil
import subprocess
from pathlib import Path

import click

from config.settings import INPUT_DIR, OUTPUT_DIR, TEMP_DIR, LOG_DIR
from tools.utils import setup_logging, ensure_dirs
from workflows.interactive_flow import InteractiveFlow


def check_marker() -> bool:
    """Проверка установки Marker CLI."""
    if not shutil.which('marker'):
        click.echo("Ошибка: Marker не найден.", err=True)
        click.echo("Установите: pip install marker-pdf", err=True)
        click.echo("Или: pip install torch --index-url https://download.pytorch.org/whl/cpu", err=True)
        return False
    try:
        subprocess.run(['marker', '--version'], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        click.echo("Ошибка: Marker не работает корректно.", err=True)
        return False
    return True


@click.command()
@click.option('--input-dir', default=str(INPUT_DIR), help='Папка с исходными файлами')
@click.option('--output-dir', default=str(OUTPUT_DIR), help='Папка для результатов')
@click.option('--temp-dir', default=str(TEMP_DIR), help='Папка для промежуточных файлов')
@click.option('--auto', is_flag=True, help='Пропустить все запросы подтверждения')
@click.option('--verbose', '-v', is_flag=True, help='Подробный вывод')
@click.option('--force', is_flag=True, help='Перезаписывать существующие файлы')
def main(
    input_dir: str,
    output_dir: str,
    temp_dir: str,
    auto: bool,
    verbose: bool,
    force: bool,
) -> None:
    """Конвертер документов PDF/DOCX в Markdown.

    Интерактивный режим (по умолчанию) запрашивает подтверждение
    для каждого файла. Используйте --auto для пакетной обработки.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    temp_path = Path(temp_dir)
    log_path = LOG_DIR / 'converter.log'

    setup_logging(verbose, log_path)

    ensure_dirs([input_path, output_path, temp_path, LOG_DIR])

    if not check_marker():
        sys.exit(1)

    click.echo(f"Input:  {input_path}")
    click.echo(f"Output: {output_path}")
    click.echo(f"Temp:   {temp_path}")
    click.echo()

    flow = InteractiveFlow(temp_path, output_path, auto=auto, force=force)
    flow.process_directory(input_path)

    click.echo("\nГотово.")


if __name__ == '__main__':
    main()