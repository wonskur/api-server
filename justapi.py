import words
import base64
import random
import re
import asyncio
from fastapi import *
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from words import names_en_male, names_de_male, names_ru_male, names_fr_male, names_es_male, names_it_male, names_sc_male
from words import names_en_female, names_de_female, names_ru_female, names_fr_female, names_es_female, names_it_female, names_sc_female

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

all_names = names_en_male + names_de_male + names_ru_male + names_fr_male + names_es_male + names_it_male + names_sc_male + \
            names_en_female + names_de_female + names_ru_female + names_fr_female + names_es_female + names_it_female + names_sc_female

parts = [
    random.choice(words.word_list),
    str(random.randint(0, 10000)),
    random.choice(words.word_list),
    random.choice(words.sym_list),
    random.choice(words.word_list),
    str(random.randint(0, 10000))
]
@app.get("/about")
async def about():
    return {"message": "random things API by 67"}

@app.get("/random")
async def random_endpoint():
    return {"message": "Try /random/password or /random/word or /random/phase or /random/name."}

@app.get("/random/password")
async def password():
    random.shuffle(parts)
    return "".join(parts)

@app.get("/random/word")
async def word():
    return random.choice(words.word_list)

@app.get("/random/name")
async def get_random_name(
    gender: Optional[str] = Query(None, description="male, female, или all"),
    origin: Optional[str] = Query(None, description="en, de, ru, fr, es, it, sc, или all")
):
    name_lists = {
        "en_male": names_en_male,
        "de_male": names_de_male,
        "ru_male": names_ru_male,
        "fr_male": names_fr_male,
        "es_male": names_es_male,
        "it_male": names_it_male,
        "sc_male": names_sc_male,
        "en_female": names_en_female,
        "de_female": names_de_female,
        "ru_female": names_ru_female,
        "fr_female": names_fr_female,
        "es_female": names_es_female,
        "it_female": names_it_female,
        "sc_female": names_sc_female,
    }
    
    if not gender or gender.lower() == "all":
        gender = "all"
    else:
        gender = gender.lower()
    
    if not origin or origin.lower() == "all":
        origin = "all"
    else:
        origin = origin.lower()
    
    available_lists = []
    genders = ["male", "female"] if gender == "all" else [gender]
    origins = ["en", "de", "ru", "fr", "es", "it", "sc"] if origin == "all" else [origin]
    
    for g in genders:
        for o in origins:
            key = f"{o}_{g}"
            if key in name_lists:
                available_lists.extend(name_lists[key])
    
    if not available_lists:
        return {
            "error": "Нет имен для указанных параметров",
            "available": list(name_lists.keys())
        }
    
    chosen_name = random.choice(available_lists)
    
    return {
        "name": chosen_name,
        "gender": gender if gender != "all" else "random",
        "origin": origin if origin != "all" else "random",
        "total_available": len(available_lists)
    }

@app.get("/random/name/bulk")
async def get_multiple_names(
    count: int = Query(5, description="Количество имен (1-100)"),
    gender: Optional[str] = Query(None, description="male, female, или all"),
    origin: Optional[str] = Query(None, description="en, de, ru, fr, es, it, sc, или all")
):
    count = min(max(count, 1), 100)
    name_lists = {
        "en_male": names_en_male,
        "de_male": names_de_male,
        "ru_male": names_ru_male,
        "fr_male": names_fr_male,
        "es_male": names_es_male,
        "it_male": names_it_male,
        "sc_male": names_sc_male,
        "en_female": names_en_female,
        "de_female": names_de_female,
        "ru_female": names_ru_female,
        "fr_female": names_fr_female,
        "es_female": names_es_female,
        "it_female": names_it_female,
        "sc_female": names_sc_female,
    }
    
    if not gender or gender.lower() == "all":
        gender = "all"
    else:
        gender = gender.lower()
    
    if not origin or origin.lower() == "all":
        origin = "all"
    else:
        origin = origin.lower()
    
    genders = ["male", "female"] if gender == "all" else [gender]
    origins = ["en", "de", "ru", "fr", "es", "it", "sc"] if origin == "all" else [origin]
    
    available_lists = []
    for g in genders:
        for o in origins:
            key = f"{o}_{g}"
            if key in name_lists:
                available_lists.extend(name_lists[key])
    
    if not available_lists:
        return {
            "error": "Нет имен для указанных параметров",
            "available": list(name_lists.keys())
        }
    
    if len(available_lists) < count:
        count = len(available_lists)
    
    chosen_names = random.sample(available_lists, count) if count > 0 else []
    
    return {
        "names": chosen_names,
        "count": len(chosen_names),
        "gender": gender if gender != "all" else "random",
        "origin": origin if origin != "all" else "random"
    }

@app.get("/name/params")
async def nameparams():
    return {
        "message": "Параметры для фильтрации имен",
        "gender": {
            "male": "Мужские имена",
            "female": "Женские имена",
            "all": "Все имена (если не указан gender)"
        },
        "origin": {
            "en": "Английские/Американские",
            "de": "Немецкие/Австрийские",
            "ru": "Русские",
            "fr": "Французские",
            "es": "Испанские",
            "it": "Итальянские",
            "sc": "Скандинавские",
            "all": "Все регионы (если не указан origin)"
        },
        "example": "/random/name?gender=male&origin=ru"
    }

@app.get("/name/search")
async def search_names(
    query: str = Query(..., description="Часть имени для поиска"),
    gender: Optional[str] = Query(None, description="male, female, или all"),
    origin: Optional[str] = Query(None, description="en, de, ru, fr, es, it, sc, или all"),
    limit: int = Query(10, description="Максимальное количество результатов")
):
    name_lists = {
        "en_male": names_en_male,
        "de_male": names_de_male,
        "ru_male": names_ru_male,
        "fr_male": names_fr_male,
        "es_male": names_es_male,
        "it_male": names_it_male,
        "sc_male": names_sc_male,
        "en_female": names_en_female,
        "de_female": names_de_female,
        "ru_female": names_ru_female,
        "fr_female": names_fr_female,
        "es_female": names_es_female,
        "it_female": names_it_female,
        "sc_female": names_sc_female,
    }
    
    if not gender or gender.lower() == "all":
        gender = "all"
    else:
        gender = gender.lower()
    
    if not origin or origin.lower() == "all":
        origin = "all"
    else:
        origin = origin.lower()
    
    genders = ["male", "female"] if gender == "all" else [gender]
    origins = ["en", "de", "ru", "fr", "es", "it", "sc"] if origin == "all" else [origin]
    
    all_names_list = []
    for g in genders:
        for o in origins:
            key = f"{o}_{g}"
            if key in name_lists:
                for name in name_lists[key]:
                    all_names_list.append({
                        "name": name,
                        "gender": g,
                        "origin": o
                    })
    
    query_lower = query.lower()
    results = [
        item for item in all_names_list 
        if query_lower in item["name"].lower()
    ][:limit]
    
    return {
        "query": query,
        "results": results,
        "count": len(results),
        "total_matches": len([i for i in all_names_list if query_lower in i["name"].lower()])
    }

@app.get("/")
async def root():
    return {"message": "API для генерации случайных имен", 
            "endpoints": {
                "/random/name": "Получить случайное имя",
                "/random/name/bulk": "Получить несколько имен",
                "/name/params": "Параметры для фильтрации"
            }}

@app.get("/random/passwordv2")
async def random_username(
    length: int = Query(8, ge=3, le=20),
    include_numbers: bool = Query(True),
    include_special: bool = Query(False)
):
    
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if include_numbers:
        chars += "0123456789"
    if include_special:
        chars += "!@#$%^&*"
    
    password = ''.join(random.choice(chars) for _ in range(length))
    return {"username": password, "length": length}

@app.get("/random/color")
async def random_color(
    format: str = Query("hex", description="hex, rgb, hsl")
):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    
    if format == "hex":
        color = f"#{r:02x}{g:02x}{b:02x}"
    elif format == "rgb":
        color = f"rgb({r}, {g}, {b})"
    elif format == "hsl":
        h = random.randint(0, 360)
        s = random.randint(50, 100)
        l = random.randint(30, 70)
        color = f"hsl({h}, {s}%, {l}%)"
    else:
        color = f"#{r:02x}{g:02x}{b:02x}"
    
    return {"color": color, "r": r, "g": g, "b": b}
