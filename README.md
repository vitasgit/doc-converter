# Document-to-Markdown Converter

Консольный конвейер конвертации документов PDF/DOCX в Markdown с интерактивным подтверждением.

## Установка

```bash
pip install -r requirements.txt
```

### Зависимости

- **Python 3.10+**
- **Marker** — для конвертации PDF/DOCX

```bash
pip install marker-pdf
```

Для CPU-only PyTorch:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Быстрый старт

```bash
# Интерактивный режим (по умолчанию)
python main.py

# Пакетная обработка (без подтверждений)
python main.py --auto

# Все опции
python main.py \
  --input-dir ./input \
  --output-dir ./output \
  --temp-dir ./temp \
  --auto \
  --verbose \
  --force
```

## Структура папок

| Папка | Назначение |
|-------|------------|
| `input/` | Исходные файлы PDF/DOCX |
| `temp/` | Промежуточные Markdown (можно редактировать) |
| `output/` | Финальные результаты |
| `logs/` | Логи работы |

## Опции CLI

| Опция | Описание |
|-------|----------|
| `--input-dir` | Папка с исходными файлами (default: `input/`) |
| `--output-dir` | Папка для результатов (default: `output/`) |
| `--temp-dir` | Папка для промежуточных файлов (default: `temp/`) |
| `--auto` | Пропустить все запросы подтверждения |
| `--verbose, -v` | Подробный вывод |
| `--force` | Перезаписывать существующие файлы |

## Интерактивный режим

При обработке каждого файла доступны действия:

- **Y** — подтвердить и сохранить
- **E** — открыть в редакторе (`$EDITOR`), затем сохранить
- **S** — пропустить файл
- **A** — прервать обработку

## Таймаут

Если конвертация превышает 5 минут, предлагается:

- **R** — повторить попытку
- **S** — пропустить файл
- **A** — прервать работу

## Логирование

Логи сохраняются в `logs/converter.log`. При ошибках — полный traceback.

## Расширение

Для добавления нового формата:

1. Создать `tools/{format}_converter.py` с функцией `convert(input_path, output_dir) -> bool`
2. Добавить расширение в `config/settings.SUPPORTED_EXTENSIONS`
3. Обновить `tools/converter.py` для маршрутизации

## Лицензия

MIT
