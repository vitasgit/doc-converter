from pathlib import Path

SUPPORTED_EXTENSIONS = {'.pdf', '.docx'}

BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / 'input'
TEMP_DIR = BASE_DIR / 'temp'
OUTPUT_DIR = BASE_DIR / 'output'
LOG_DIR = BASE_DIR / 'logs'

MARKER_TIMEOUT = 300
MARKER_LANGUAGES = 'rus,eng'
MARKER_FLAGS = [
    '--strip_existing_ocr',
    '--paginate_output',
]