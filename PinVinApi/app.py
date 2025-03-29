import asyncio
import uuid

import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Tuple
from pathlib import Path
from ai import *


tags_metadata =[
    {
        "name": "main",
        "description":"Выбор даты через динамический выпадающий список",
    },
    {
        "name": "managers",
        "description":"Выбор менеджера через динамический выпадающий список",
    },
    {
        "name": "submit",
        "description":"Отправляет форму на backend, запускает анализ данных",
    },
    {
        "name": "answer",
        "description":"Выдает ответ по запросу",
    },
    {
        "name":"dashboard",
        "description":"Дает доступ к DASHBOARD по UUID",
    }
]


app = FastAPI(
    title="PinVinAPI 3 CASE",
    description="API, позволяющий анализировать звонки менеджеров",
    version="1.0",
    contact={},
    license_info={},
    openapi_tags=tags_metadata,

)



# Подключаем статические файлы (если нужно)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")



@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response


@app.get("/", tags=["main"])
async def dates(request: Request):
    dates = get_folder_names("data")
    return templates.TemplateResponse("dates.html", {
        "request": request,
        "dates": dates
    })

@app.get("/managers/{date}", tags=["managers"])
async def managers(request: Request, date: str):
    managers = get_sorted_mp3_names(f"data/{date}")
    return templates.TemplateResponse("managers.html", {
        "request": request,
        "date": date,
        "managers": managers,
    })
@app.post("/submit", tags=["submit"])
async def submit_form(request: Request):
    # Парсим данные
    data = await request.json()
    date = data.get("date")
    manager = data.get("manager")
    # return {"status": "OK"}
    # Обработка данных формы
    wayToMP3 = f'data/{date}'
    arrayWithFile = get_sorted_mp3_find_names(f"./data/{date}", manager)
    print(arrayWithFile)
    # Блок С AI
    asyncio.create_task(analytics(manager, arrayWithFile))
    print(1231232)
    return {"status": "OK"}



@app.get("/answer", tags=["answer"])
async def answer_page(request: Request):
    return templates.TemplateResponse("answer.html", {"request": request})


@app.get("/dashboard/{dashboard_uuid}", tags=["dashboard"])
async def dashboard(request: Request, dashboard_uuid: uuid.UUID):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,

        "dashboard_uuid": dashboard_uuid
    })






def get_folder_names(directory: str) -> List[str]:
    """
    Возвращает список названий папок в указанной директории

    :param directory: Путь к директории
    :return: Список названий поддиректорий
    """
    try:
        # Используем Path для кроссплатформенности
        path = Path(directory)

        # Получаем только директории, исключая файлы
        folders = [item.name for item in path.iterdir() if item.is_dir()]

        return sorted(folders, key=lambda x: x.split('.')[::-1])  # Сортируем по алфавиту

    except Exception as e:
        print(f"Ошибка при чтении директории {directory}: {e}")
        return []



def get_sorted_mp3_names(directory: str) -> Tuple[str, ...]:
    """
    Возвращает кортеж отсортированных названий MP3 файлов (без расширения)

    :param directory: Путь к директории для поиска
    :return: Кортеж названий файлов без расширения .mp3
    """
    try:
        path = Path(directory)
        # Получаем все MP3 файлы, сортируем по имени и извлекаем названия без расширения
        mp3_names = sorted(
            file.stem.split("_")[0] for file in path.glob("*.mp3") if file.is_file()
        )
        return tuple(set(mp3_names))
    except Exception as e:
        print(f"Ошибка при обработке директории {directory}: {e}")
        return tuple()




def get_sorted_mp3_find_names(directory: str, manager : str) -> Tuple[str, ...]:
    """
    Возвращает кортеж отсортированных названий MP3 файлов (без расширения)

    :param directory: Путь к директории для поиска
    :return: Кортеж названий файлов без расширения .mp3
    """
    try:
        path = Path(directory)
        # Получаем все MP3 файлы, сортируем по имени и извлекаем названия без расширения
        mp3_names = sorted(
            f"{directory}/{file.stem}.mp3" for file in path.glob(f"{manager}_*.mp3") if file.is_file()
        )
        return tuple(mp3_names)
    except Exception as e:
        print(f"Ошибка при обработке директории {directory}: {e}")
        return tuple()

if __name__ == "__main__":
    uvicorn.run("app:app", host='127.0.0.1', port=8000, workers=2)