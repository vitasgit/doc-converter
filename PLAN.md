# PLAN.md — Document-to-Markdown Pipeline

> План реализации MVP консольного конвейера конвертации документов

---

## 📋 Обзор проекта

**Цель**: CLI-конвейер для конвертации PDF/DOCX в Markdown с интерактивным подтверждением пользователя.

**Принципы**: Простота > полнота, Надёжность > скорость, Локальность > облачность, Человек в цикле

---

## 🗂️ Структура проекта

```
doc-converter/
├── main.py                    # CLI entry point (Click)
├── requirements.txt           # click>=8.0.0
├── config/
│   └── settings.py             # Конфигурация
├── tools/
│   ├── __init__.py
│   ├── converter.py           # Marker CLI wrapper
│   └── utils.py                # safe_input, logging
├── workflows/
│   ├── __init__.py
│   └── interactive_flow.py     # Интерактивный workflow
├── input/                      # Исходные файлы
├── temp/                       # Промежуточные (редактируемые)
├── output/                     # Финальные результаты
└── logs/                       # Логи
```

---

## 📦 Этапы реализации

### Этап 1: Скелет проекта ✅
- [x] `requirements.txt` — click>=8.0.0
- [x] `config/settings.py` — SUPPORTED_EXTENSIONS, пути (pathlib), MARKER_TIMEOUT, MARKER_LANGUAGES, MARKER_FLAGS
- [x] `tools/__init__.py`, `workflows/__init__.py` (пустые)
- [x] Директории: input/, temp/, output/, logs/

### Этап 2: Утилиты (`tools/utils.py`) ✅
- [x] `safe_input(prompt) -> str` — fallback через sys.stdin.readline()
- [x] `setup_logging(verbose, log_file)` — rotating file handler, формат с timestamp
- [x] `ensure_dirs()` — создание директорий

### Этап 3: Конвертер (`tools/converter.py`) ✅
- [x] `convert(input_path, output_dir, **marker_kwargs) -> str` ('ok', 'timeout', 'error')
- [x] Проверка расширения, subprocess.run с timeout
- [x] Коды возврата: 0=OK, 1=файл, 2=зависимости, 124=timeout
- [x] `get_markdown_path(output_dir, input_name) -> Path`

### Этап 4: Интерактивный workflow (`workflows/interactive_flow.py`) ✅
- [x] `confirm(prompt) -> bool` — y/yes/да case-insensitive
- [x] `edit_file(path) -> str` — 'edited'/'skip'/'abort'
- [x] `InteractiveFlow.process_file(input_path) -> Optional[Path]`
- [x] `InteractiveFlow.process_directory(input_dir) -> None`

### Этап 5: Главный CLI (`main.py`) ✅
- [x] Click CLI: --input-dir, --output-dir, --temp-dir, --auto, --verbose, --force
- [x] Проверка `marker --version`
- [x] Инициализация логирования
- [x] Запуск InteractiveFlow

### Этап 6: Обработка edge cases ✅
- [x] Пустая папка input/ — логируется warning
- [x] Пустой Markdown (size == 0) — предупреждение + подтверждение
- [x] Timeout — Retry/Skip/Abort в интерактивном, Skip в auto
- [x] Файл существует в output/ — --force пропускает, иначе backup с `_new`
- [x] Права на запись — OSError обрабатывается

### Этап 7: Документация ✅ (тесты — в будущем)
- [x] README.md — установка, использование, опции
- [x] .gitignore
- [ ] tests/ — базовые тесты (mock subprocess) — **будущее**

---

## ✅ Готово к коммиту
