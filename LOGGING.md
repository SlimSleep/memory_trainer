# Система логирования Memory Trainer

## Описание

Проект использует встроенный модуль Python `logging` для отслеживания ошибок, информационных сообщений и предупреждений. Логи записываются одновременно в:
- **Файл** с полной информацией (DEBUG и выше)
- **Консоль** с основной информацией (INFO и выше)

## Структура логирования

### Уровни логирования:
- **DEBUG** — детальная информация для диагностики
- **INFO** — информационные сообщения о нормальной работе
- **WARNING** — предупреждения о проблемах, которые нужно отследить
- **ERROR** — ошибки при выполнении операций
- **CRITICAL** — критические ошибки приложения

### Файлы логов

Логи сохраняются в папку `logs/` в корне проекта:
```
logs/
├── memory_trainer_2026-04-21_14-30-45.log
├── memory_trainer_2026-04-21_15-20-12.log
└── ...
```

Имена файлов содержат дату и время запуска приложения.

## Использование в коде

### Импорт логгера

```python
from logger import get_logger

# Получить логгер
logger = get_logger()

# Или использовать глобальный объект
from logger import logger
```

### Логирование событий

```python
# Информационный лог
logger.info("✓ Приложение запущено")

# Предупреждение
logger.warning("⚠ Не удалось загрузить файл конфигурации")

# Ошибка
logger.error("✗ Ошибка при подключении к базе данных")

# Отладка
logger.debug("Переменная x = 42")

# Критическая ошибка
logger.critical("⚠ Приложение будет остановлено")

# Логирование исключения с трассировкой стека
try:
    result = 1 / 0
except Exception:
    logger.exception("Произошла критическая ошибка при делении")
```

## Примеры логирования в модулях

### main.py
```python
from logger import get_logger

def main():
    logger = get_logger()
    logger.info("✓ Pygame инициализирован")
    logger.info(f"✓ Окно создано: {config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
```

### audio.py
```python
from logger import get_logger

_logger = get_logger()

def init_audio():
    try:
        pygame.mixer.init()
        _logger.info("✓ Pygame mixer инициализирован")
    except pygame.error as e:
        _logger.error(f"⚠ Не удалось инициализировать mixer: {e}")
```

### localization.py
```python
from logger import get_logger

_logger = get_logger()

# При загрузке локализации
_logger.info(f"✓ Локализация загружена: {json_file}")

# При ошибке
_logger.warning(f"⚠ Ошибка загрузки локализации: {e}")
```

## Просмотр логов

### В консоли
При запуске приложения в консоль выводятся логи уровня INFO и выше:
```
INFO: ✓ Pygame инициализирован
INFO: ✓ Окно создано: 1024x768
INFO: ✓ Локализатор инициализирован, язык: ru
```

### В файле
Откройте файл из папки `logs/` — там будут все логи (DEBUG и выше) с точными временными метками:
```
2026-04-21 14:30:45 | INFO     | memory_trainer - ✓ Pygame инициализирован
2026-04-21 14:30:45 | DEBUG    | memory_trainer - Проверка конфигурации...
2026-04-21 14:30:46 | INFO     | memory_trainer - ✓ Окно создано: 1024x768
2026-04-21 14:30:46 | WARNING  | memory_trainer - ⚠ Не удалось загрузить файл sound.mp3
2026-04-21 14:30:47 | ERROR    | memory_trainer - ✗ Ошибка базы данных
```

## Отладка проблем

### 1. Найти ошибку в приложении
1. Запустить приложение
2. Вызвать ошибку
3. Открыть файл лога из папки `logs/`
4. Найти строку с ERROR или WARNING

### 2. Отследить последовательность событий
Просмотреть файл лога — там в хронологическом порядке все события до ошибки.

### 3. Добавить отладочную информацию
```python
logger.debug(f"Состояние переменной: {variable}")
logger.debug(f"Аргументы функции: {args}")
```

## Миграция существующего кода

### Старый код:
```python
print("✓ Инициализация завершена")
print(f"⚠ Ошибка: {error_message}")
```

### Новый код:
```python
from logger import get_logger

logger = get_logger()
logger.info("✓ Инициализация завершена")
logger.warning(f"⚠ Ошибка: {error_message}")
```

## Конфигурация логирования

**Где изменять параметры:** `logger.py`

Текущие параметры:
- **Консоль:** выводит INFO, WARNING, ERROR, CRITICAL
- **Файл:** выводит DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Формат:** `%(asctime)s | %(levelname)-8s | %(name)s - %(message)s`
- **Кодировка:** UTF-8 (поддерживает русский текст)

## На что обратить внимание

1. **Логирование выполняется синхронно** — может медленно влиять на перформанс при очень большом объёме логов
2. **Файлы логов не удаляются автоматически** — периодически очищайте папку `logs/`
3. **Логирование исключений** — используйте `logger.exception()` вместо `logger.error()` для получения полной трассировки стека
4. **Форматирование сообщений** — старайтесь использовать f-строки для удобства

## Пример полного логирования функции

```python
from logger import get_logger

logger = get_logger()

def load_user_data(user_id):
    try:
        logger.debug(f"Загрузка данных пользователя: {user_id}")
        
        user = db.get_user_by_id(user_id)
        if not user:
            logger.warning(f"Пользователь не найден: {user_id}")
            return None
        
        logger.info(f"✓ Пользователь загружен: {user.username}")
        return user
        
    except Exception as e:
        logger.exception(f"Ошибка при загрузке пользователя {user_id}")
        return None
```

## Поддерживаемые файлы

Логирование уже добавлено в:
- ✅ `main.py`
- ✅ `modules/audio.py`
- ✅ `localization/localization.py`
- ⏳ `modules/screen/*.py` (в процессе)
- ⏳ `modules/games/*.py` (в процессе)
- ⏳ `modules/database/db_manager.py` (в процессе)
