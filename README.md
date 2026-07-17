# Assistant API + Random API

Два сервера в одном проекте: голосовой помощник "Виктор" и генератор случайных данных

---

## Установка

### Подготовка окружения

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Запуск

### Голосовой помощник (assistant_server.py)
```bash
uvicorn assistant_server:app --host 0.0.0.0 --port 8000 --reload
```

### Random API (justapi.py)
```bash
uvicorn justapi:app --host 0.0.0.0 --port 8001 --reload
```

---

## Требования

Создайте файл `requirements.txt`:

```txt
fastapi
uvicorn
python-dotenv
httpx
speechrecognition
pyttsx3
pydantic
numpy
python-multipart
requests
```

Или установите одной командой:
```bash
pip install fastapi uvicorn python-dotenv httpx speechrecognition pyttsx3 pydantic numpy python-multipart requests
```

---

## Настройка

Создайте файл `.env` в корне проекта:

```env
OR_API_KEY=sk-or-v1-ваш-ключ-от-openrouter
```

Получить ключ можно на [OpenRouter](https://openrouter.ai/keys)

---

## API Эндпоинты

### Голосовой помощник (порт 8000)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/` | Информация о сервере |
| GET | `/api/status` | Статус сервера |
| POST | `/api/voice` | Обработка голосового запроса (base64 аудио) |
| POST | `/api/text` | Обработка текстового запроса |

**Пример текстового запроса:**
```bash
curl -X POST http://localhost:8000/api/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Виктор, какая погода?"}'
```

**Пример ответа:**
```json
{
  "text": "Сегодня солнечно, +22 градуса",
  "audio_base64": "U3RyaW5nIG9mIGF1ZGlvIGZpbGUgYmFzZTY0...",
  "action_type": "command",
  "command": {
    "type": "weather",
    "response": "Сегодня солнечно, +22 градуса",
    "params": {
      "temperature": 22,
      "condition": "sunny",
      "city": "Ufa"
    }
  }
}
```

---

### Random API (порт 8001)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/` | Информация о сервере |
| GET | `/random` | Список доступных эндпоинтов |
| GET | `/random/password` | Генерация пароля |
| GET | `/random/passwordv2` | Генерация пароля с параметрами |
| GET | `/random/word` | Случайное слово |
| GET | `/random/name` | Случайное имя с фильтрацией |
| GET | `/random/name/bulk` | Несколько случайных имен |
| GET | `/random/color` | Случайный цвет (hex/rgb/hsl) |
| GET | `/name/search` | Поиск имен по запросу |
| GET | `/name/params` | Параметры для фильтрации имен |
| GET | `/about` | Информация об API |

**Примеры:**

```bash
# Случайное имя (русское, мужское)
curl "http://localhost:8001/random/name?gender=male&origin=ru"

# Случайный пароль (длина 12, с цифрами и спецсимволами)
curl "http://localhost:8001/random/passwordv2?length=12&include_numbers=true&include_special=true"

# Поиск имен
curl "http://localhost:8001/name/search?query=Алек&limit=5"
```

**Параметры для `/random/name`:**
- `gender`: `male`, `female`, `all` (по умолчанию `all`)
- `origin`: `en`, `de`, `ru`, `fr`, `es`, `it`, `sc`, `all` (по умолчанию `all`)

**Параметры для `/random/passwordv2`:**
- `length`: от 3 до 20 (по умолчанию 8)
- `include_numbers`: `true`/`false` (по умолчанию `true`)
- `include_special`: `true`/`false` (по умолчанию `false`)

**Параметры для `/random/color`:**
- `format`: `hex`, `rgb`, `hsl` (по умолчанию `hex`)

---

## Особенности

### Голосовой помощник:
- Распознавание речи (Google Speech Recognition)
- Синтез речи (pyttsx3)
- Интеграция с OpenRouter AI
- Обработка команд (погода, время, приветствие)
- Активация по слову "Виктор"
- Поддержка аудио в base64

### Random API:
- Имена из 7 культур (en, de, ru, fr, es, it, sc)
- Генерация паролей (2 варианта)
- Случайные цвета (hex/rgb/hsl)
- Поиск имен
- Фильтрация по полу и происхождению

---

## Возможные проблемы

### Ошибка с pyttsx3 на Linux:
```bash
sudo apt-get install espeak libespeak1 libespeak-dev
sudo apt-get install alsa-utils
```

### Ошибка с speech_recognition:
```bash
pip install pyaudio
# или на Linux:
sudo apt-get install python3-pyaudio
```

### Порт уже занят:
```bash
# Убить процесс на порту
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:8001 | xargs kill -9
```

---

## Ссылки

- [OpenRouter](https://openrouter.ai/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SpeechRecognition](https://github.com/Uberi/speech_recognition)
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3)
=======
