# CLAUDE.md — Инструкции для ассистента по проекту Document-to-Markdown Pipeline

> **Назначение**: Этот файл содержит контекст и инструкции специально для нейросети-ассистента для эффективной помощи в разработке, отладке и использовании проекта.

---

## 🎯 Роль ассистента в этом проекте

Вы — технический помощник, который помогает пользователю:
1. **Разрабатывать** консольный конвейер конвертации документов (PDF/DOCX → Markdown)
2. **Отлаживать** проблемы с Marker CLI, обработкой ошибок, интерактивным вводом
3. **Расширять** функциональность: добавлять новые инструменты, форматы, рабочие процессы
4. **Обучать** пользователя: объяснять архитектуру, помогать с запуском, интерпретировать ошибки

### Принципы взаимодействия
```
✅ ДЕЛАТЬ:
• Предлагать конкретные, готовые к использованию фрагменты кода
• Объяснять технические решения простым языком с примерами
• Учитывать, что пользователь работает локально, без облачных зависимостей
• Предупреждать о потенциальных проблемах (таймауты, память, зависимости)
• Сохранять модульность: каждый инструмент — отдельный скрипт

❌ НЕ ДЕЛАТЬ:
• Не предлагать решения, требующие GUI или веб-интерфейса (MVP — только CLI)
• Не усложнять архитектуру без явного запроса пользователя
• Не игнорировать требование интерактивного подтверждения шагов
• Не предлагать замену Marker без обоснования преимуществ
```

---

## 📁 Контекст проекта (кратко)

| Компонент | Описание | Ключевой файл |
|-----------|----------|---------------|
| **Оркестратор** | Главный CLI-скрипт, управляет потоком обработки | `main.py` |
| **Конвертер** | Обёртка над Marker CLI для PDF/DOCX → MD | `tools/converter.py` |
| **Интерактив** | Логика запроса подтверждения, редактирования | `workflows/interactive_flow.py` |
| **Утилиты** | `safe_input()`, валидация, логирование | `tools/utils.py` |
| **Конфигурация** | Пути, параметры Marker, флаги | `config/settings.py` |

### Ключевые ограничения MVP
```python
# Поддерживаемые форматы (строго!)
SUPPORTED_EXTENSIONS = {'.pdf', '.docx'}

# Папки (создаются автоматически)
INPUT_DIR = 'input/'    # только чтение
TEMP_DIR = 'temp/'      # промежуточные файлы, редактируемые человеком
OUTPUT_DIR = 'output/'  # финальные результаты

# Интерактивный режим (по умолчанию)
# --auto флаг отключает запросы подтверждения
```

---

## 🔧 Технические детали для ассистента

### Работа с Marker CLI
```bash
# Базовый вызов (используется в tools/converter.py)
marker input/document.pdf --output_dir ./temp --output_format markdown

# Важные флаги Marker:
--strip_existing_ocr     # Удалить встроенный OCR (улучшает качество)
--languages rus,eng      # Языки для распознавания (критично для кириллицы)
--paginate_output        # Сохранять нумерацию страниц в выходе
--max_pages 10           # Ограничить обработку (для тестов)

# Возвращаемые коды:
0  # Успех
1  # Ошибка файла (не найден, повреждён)
2  # Ошибка зависимостей (не установлен torch, и т.д.)
124 # Таймаут (обработать в Python!)
```

### Надёжный ввод от пользователя (critical!)
```python
# ВСЕГДА использовать safe_input() для запросов подтверждения
# Обычный input() ломается при перенаправлении stdin (|, <, CI/CD)

from tools.utils import safe_input

answer = safe_input("Продолжить? [Y/N]: ").lower()
if answer not in ('y', 'yes', 'да'):
    # Обработать отказ
```

### Обработка ошибок — шаблон
```python
try:
    success = convert(input_path, output_path)
    if not success:
        logger.error(f"Конвертация не вернула успех: {input_path}")
        return False
except subprocess.TimeoutExpired:
    logger.error(f"Таймаут при обработке {input_path}")
    # Предложить пользователю: повторить / пропустить / увеличить таймаут
    return False
except FileNotFoundError:
    logger.error(f"Файл не найден: {input_path}")
    return False
except Exception as e:
    logger.exception(f"Неожиданная ошибка: {e}")
    # Сохранить стек в logs/traceback.log для отладки
    return False
```

---

## 🤝 Типовые сценарии помощи

### Сценарий 1: "Не устанавливается Marker"
```
Возможные причины:
1. Не установлен PyTorch → предложить: pip install torch --index-url https://download.pytorch.org/whl/cpu
2. Недостаточно памяти → предложить: --max_pages 5 для тестов
3. Конфликт версий Python → проверить: python --version (требуется 3.10+)

Диагностика:
$ python -c "import marker; print(marker.__version__)"
$ marker --help  # должен показать справку

Решение: Предложить установить в venv и дать пошаговую инструкцию.
```

### Сценарий 2: "Конвертация проходит, но Markdown пустой"
```
Чек-лист отладки:
1. Проверить исходный файл: открывается ли в обычном PDF-ридере?
2. Запустить Marker вручную: marker file.pdf --output_dir ./debug --verbose
3. Проверить вывод Marker: есть ли предупреждения о страницах/шрифтах?
4. Проверить кодировку: открывать .md с encoding='utf-8'

Частые причины:
• Скан-копии без OCR → предложить: --ocr_lang rus или внешний OCR
• Зашифрованный PDF → сообщить: требуется пароль, не поддерживается в MVP
• Нестандартные шрифты → предложить: попробовать Docling как fallback

Действие: Предложить пользователю прислать пример файла (если возможно) или логи.
```

### Сценарий 3: "Хочу добавить поддержку нового формата"
```
Алгоритм расширения:
1. Выбрать инструмент для формата (например, pandoc для .rtf)
2. Создать tools/rtf_converter.py по аналогии с converter.py
3. Добавить определение расширения в main.py:
   if ext == '.rtf': converter = 'tools/rtf_converter.py'
4. Обновить PROJECT.md и этот CLAUDE.md
5. Протестировать на 2-3 примерах разной сложности

Важно: Сохранить интерфейс convert(input, output) -> bool для совместимости.
```

### Сценарий 4: "Как интегрировать с моей нейросетью?"
```
Рекомендуемый подход (через CLI, как требует архитектура):

1. После получения output/document.md:
   $ python tools/llm_query.py --file output/document.md --prompt "Решите задачу..."

2. Пример llm_query.py (заглушка для будущего):
   ```python
   # tools/llm_query.py
   import sys, json, os
   from pathlib import Path
   
   def query_llm(file_path: str, prompt: str, model: str = "ollama/llama3"):
       # Читаем Markdown
       content = Path(file_path).read_text(encoding='utf-8')
       
       # Формируем запрос (пример для Ollama локально)
       import requests
       response = requests.post("http://localhost:11434/api/generate", json={
           "model": model,
           "prompt": f"{prompt}\n\nКонтекст:\n{content}",
           "stream": False
       })
       return response.json().get("response", "")
   
   if __name__ == "__main__":
       # Парсинг аргументов и вызов query_llm()
       ...
   ```

3. Интеграция в workflow:
   • Добавить шаг после подтверждения temp-файла
   • Сохранить результат LLM в output/final_*.md
   • Снова запросить подтверждение перед финальным сохранением

Примечание: Не реализовывать в MVP — только заложить архитектуру.
```

---

## 🎨 Стиль кода и конвенции

### Общие правила
```python
# Типизация — обязательно для функций
from pathlib import Path
from typing import Optional, List

def process_file(input_path: Path, output_dir: Path) -> bool:
    ...

# Логирование — через logging, не print (кроме CLI-вывода для пользователя)
import logging
logger = logging.getLogger(__name__)

# Пути — только через pathlib, не os.path
config_path = Path(__file__).parent / "config" / "settings.py"

# Обработка исключений — конкретно, не bare except
try:
    ...
except (FileNotFoundError, PermissionError) as e:
    logger.warning(f"Проблема с файлом: {e}")
```

### CLI-аргументы (argparse + click)
```python
# Использовать click для удобства, если не противоречит простоте
import click

@click.command()
@click.option('--input-dir', default='input', help='Папка с исходными файлами')
@click.option('--auto', is_flag=True, help='Пропустить запросы подтверждения')
@click.option('--verbose', '-v', is_flag=True, help='Подробный вывод')
def main(input_dir: str, auto: bool, verbose: bool):
    ...
```

### Документирование
```python
# Docstring в Google style для всех публичных функций
def convert(input_path: str, output_path: str) -> bool:
    """Конвертирует документ через Marker CLI.
    
    Args:
        input_path: Путь к исходному файлу (.pdf или .docx)
        output_path: Путь для сохранения Markdown
        
    Returns:
        bool: True при успешной конвертации, False при ошибке
        
    Raises:
        FileNotFoundError: Если входной файл не существует
        TimeoutError: Если Marker не ответил за 5 минут
    """
```

---

## 🧪 Тестирование и отладка

### Чек-лист перед ответом пользователю
```
[ ] Код синтаксически корректен (проверено через python -m py_compile)
[ ] Импорт зависимостей указан в requirements.txt
[ ] Пути к файлам используют pathlib, не строковые конкатенации
[ ] Обработаны основные исключения (FileNotFound, Timeout, Permission)
[ ] CLI-аргументы имеют --help описание
[ ] Для интерактивных запросов используется safe_input()
[ ] Логи пишутся в files, не только в stdout
```

### Быстрые команды для отладки
```bash
# Проверить установку Marker
$ python -c "from marker.convert import convert_single_pdf; print('OK')"

# Протестировать конвертер изолированно
$ python tools/converter.py --input tests/sample.pdf --output tests/out.md

# Запустить с подробным логом
$ python main.py --input-dir ./input --verbose 2>&1 | tee logs/run.log

# Проверить интерактивный ввод в разных окружениях
$ echo "y" | python main.py --input-dir ./input  # stdin перенаправлен
$ python main.py --input-dir ./input < /dev/null  # без stdin
```

---

## 📚 Полезные ссылки (держать под рукой)

| Ресурс | Зачем нужен |
|--------|-------------|
| [Marker GitHub](https://github.com/datalab-to/marker) | Документация, флаги, примеры |
| [Marker Issues](https://github.com/datalab-to/marker/issues) | Поиск известных проблем и workarounds |
| [Click Documentation](https://click.palletsprojects.com/) | Если решим перейти на Click для CLI |
| [Python Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html) | Настройка логирования |
| [Pathlib Guide](https://treyhunner.com/2018/12/why-you-should-be-using-pathlib/) | Лучшие практики работы с путями |

---

## 🔄 Обновление контекста

Если пользователь вносит изменения в архитектуру или требования:
1. Обновить соответствующие разделы этого CLAUDE.md
2. Добавить запись в `CHANGELOG.md` с датой и описанием
3. При существенных изменениях — обновить `PROJECT.md` и `README.md`

```markdown
## Changelog для ассистента
- 2026-01-15: Изначальная версия — MVP с PDF/DOCX → MD через Marker
- [Дата]: [Описание изменения] — обновлено [разделы]
```

---

> 💡 **Памятка для ассистента**:  
> Этот проект — не просто конвертер, а *интерактивный конвейер с человеком в цикле*.  
> Каждая автоматизация должна оставлять пользователю точку контроля.  
> Простота > полнота. Надёжность > скорость. Локальность > облачность.  
> Если сомневаетесь — спросите пользователя, прежде чем предлагать сложное решение.

*Документ поддерживается в актуальном состоянии. Последнее обновление: 2026-01-15*
