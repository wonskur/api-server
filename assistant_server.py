import base64
import os
from datetime import datetime
from typing import Optional, List
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import tempfile
import requests

load_dotenv()

WAKE_WORD = "виктор"
OR_API_KEY = os.getenv("OR_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

app = FastAPI(title="Голосовой помощник Виктор")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VoiceRequest(BaseModel):
    audio_base64: str
    format: str = "wav"
    sample_rate: int = 16000

class TextRequest(BaseModel):
    text: str
    context: Optional[List[dict]] = None

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def audio_base64_to_text(self, audio_base64: str) -> str:
        try:
            audio_bytes = base64.b64decode(audio_base64)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            with sr.AudioFile(tmp_path) as source:
                audio_data = self.recognizer.record(source)
                
            try:
                text = self.recognizer.recognize_google(audio_data, language="ru-RU")
                return text.lower()
            except:
                return ""
                
        except Exception:
            return ""
        
        finally:
            if 'tmp_path' in locals():
                try:
                    os.unlink(tmp_path)
                except:
                    pass
    
    def text_to_wake_check(self, text: str) -> tuple:
        text_lower = text.lower()
        if WAKE_WORD in text_lower:
            command = text_lower.replace(WAKE_WORD, "").strip()
            return command, True
        return text_lower, False

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 0.9)
        
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'russian' in voice.name.lower() or 'русский' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def text_to_base64_audio(self, text: str) -> Optional[str]:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_path = tmp_file.name
            
            self.engine.save_to_file(text, tmp_path)
            self.engine.runAndWait()
            
            with open(tmp_path, 'rb') as f:
                audio_bytes = f.read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return audio_base64
            
        except Exception:
            return None
        
        finally:
            if 'tmp_path' in locals():
                try:
                    os.unlink(tmp_path)
                except:
                    pass

class AIAssistant:
    def __init__(self):
        self.context = []
        self.max_context = 10
        
    async def process_with_ai(self, text: str) -> str:
        if not OR_API_KEY:
            return "API ключ не настроен. Добавьте OR_API_KEY в .env файл"
            
        try:
            async with httpx.AsyncClient() as client:
                messages = [
                    {"role": "system", "content": "Ты - Виктор, голосовой помощник. Отвечай кратко и по делу"},
                    {"role": "user", "content": text}
                ]
                
                response = await client.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OR_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "Voice Assistant"
                    },
                    json={
                        "model": "poolside/laguna-xs-2.1:free",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    return "Сервер временно недоступен"
                    
        except Exception:
            return "Произошла ошибка, попробуйте позже"

class CommandProcessor:
    def __init__(self):
        self.commands = {
            "время": self.get_time,
            "погода": self.get_weather,
            "привет": self.greeting,
            "стоп": self.stop
        }
    
    def get_time(self, text=""):
        now = datetime.now()
        return {
            "type": "time",
            "response": f"Сейчас {now.strftime('%H:%M')}",
            "params": {"time": now.strftime("%H:%M")}
        }
    
    def get_weather(self, text=""):
        try:
            response = requests.get(
                "https://wttr.in/Ufa?format=%C+%t&lang=ru",
                timeout=5
            )
            
            if response.status_code == 200:
                weather_text = response.text.strip()
                parts = weather_text.rsplit(' ', 1)
                if len(parts) == 2:
                    condition = parts[0]
                    temp = parts[1].replace('+', '').replace('°C', '')
                    
                    return {
                        "type": "weather",
                        "response": f"Сегодня {condition.lower()}, {temp} градусов",
                        "params": {
                            "temperature": int(float(temp)),
                            "condition": condition.lower(),
                            "city": "Ufa"
                        }
                    }
            
            return {
                "type": "weather",
                "response": "Не удалось получить погоду",
                "params": {}
            }
            
        except Exception:
            return {
                "type": "weather",
                "response": "Ошибка получения погоды",
                "params": {}
            }
    
    def greeting(self, text=""):
        return {
            "type": "greeting",
            "response": "Привет! Чем могу помочь?",
            "params": {}
        }
    
    def stop(self, text=""):
        return {
            "type": "stop",
            "response": "До свидания!",
            "params": {"action": "sleep"}
        }
    
    def process(self, text: str) -> Optional[dict]:
        text_lower = text.lower()
        
        for cmd, handler in self.commands.items():
            if cmd in text_lower:
                return handler(text_lower)
        
        return None

stt = SpeechToText()
tts = TextToSpeech()
ai = AIAssistant()
command_processor = CommandProcessor()

@app.get("/")
async def root():
    return {
        "name": "Голосовой помощник Виктор",
        "version": "1.0.0",
        "wake_word": WAKE_WORD,
        "status": "online"
    }

@app.post("/api/voice")
async def process_voice(request: VoiceRequest):
    try:
        text = stt.audio_base64_to_text(request.audio_base64)
        
        if not text:
            return JSONResponse(content={
                "text": "Не удалось распознать речь",
                "action_type": "error",
                "confidence": 0.0
            })
        
        command_text, is_activated = stt.text_to_wake_check(text)
        
        if not is_activated:
            return JSONResponse(content={
                "text": f"Скажите '{WAKE_WORD}' для активации",
                "action_type": "error",
                "confidence": 0.0
            })
        
        command_result = command_processor.process(command_text)
        
        if command_result:
            audio_base64 = tts.text_to_base64_audio(command_result["response"])
            
            return JSONResponse(content={
                "text": command_result["response"],
                "audio_base64": audio_base64,
                "action_type": "command",
                "command": command_result,
                "confidence": 1.0
            })
        
        ai_response = await ai.process_with_ai(command_text)
        audio_base64 = tts.text_to_base64_audio(ai_response)
        
        return JSONResponse(content={
            "text": ai_response,
            "audio_base64": audio_base64,
            "action_type": "response",
            "confidence": 0.95
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/text")
async def process_text(request: TextRequest):
    try:
        command_text, is_activated = stt.text_to_wake_check(request.text)
        
        if not is_activated:
            return JSONResponse(content={
                "text": f"Скажите '{WAKE_WORD}' для активации",
                "action_type": "error"
            })
        
        command_result = command_processor.process(command_text)
        
        if command_result:
            audio_base64 = tts.text_to_base64_audio(command_result["response"])
            return JSONResponse(content={
                "text": command_result["response"],
                "audio_base64": audio_base64,
                "action_type": "command",
                "command": command_result
            })
        
        ai_response = await ai.process_with_ai(command_text)
        audio_base64 = tts.text_to_base64_audio(ai_response)
        
        return JSONResponse(content={
            "text": ai_response,
            "audio_base64": audio_base64,
            "action_type": "response"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "wake_word": WAKE_WORD,
        "timestamp": datetime.now().isoformat(),
        "context_length": len(ai.context)
    }
