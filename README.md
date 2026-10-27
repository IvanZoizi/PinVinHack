# PinVinHack — PinVinAPI

> Hackathon project (Case #3): an API that analyzes sales managers' phone calls and turns them into readable reports.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)

## About

PinVinAPI takes recorded manager calls and call data, runs them through an LLM, and produces per-manager analytics that you explore from a small web UI. You pick a **date** and a **manager**, submit, and the service returns an AI-generated summary plus a dashboard view.

## Features

- 📞 AI analysis of managers' calls via the OpenAI API
- 🗂️ Data organized by date (`data/<date>/…`) with results exported to Excel reports
- 🖥️ Lightweight web interface (Jinja2 templates: date picker, manager picker, answer, dashboard)
- 🎧 Audio preprocessing with bundled `ffmpeg`
- 📊 Tabular processing with `pandas`
- 📚 Auto-generated OpenAPI docs (FastAPI `/docs`)

## Tech stack

**Python · FastAPI · Uvicorn · Jinja2 · pandas · OpenAI · ffmpeg · openpyxl**

## API

| Method | Route | Description |
|---|---|---|
| `GET`  | `/` | Main page — date dropdown |
| `GET`  | `/managers/{date}` | Managers available for a date |
| `POST` | `/submit` | Runs the analysis for the chosen date/manager |
| `GET`  | `/answer` | Returns the generated answer |
| `GET`  | `/dashboard` | Dashboard view |

## Getting started

```bash
cd PinVinApi

# 1. install dependencies
pip install fastapi uvicorn jinja2 pandas openai openpyxl

# 2. provide your OpenAI key (used by ai.py / gpt.py)
export OPENAI_API_KEY="sk-..."

# 3. run
uvicorn app:app --reload --port 8000
```

Then open http://localhost:8000 (API docs at http://localhost:8000/docs).

## Project structure

```
PinVinApi/
├── app.py            # FastAPI app & routes
├── ai.py             # analysis orchestration
├── gpt.py            # OpenAI calls
├── promt.py          # prompt templates
├── templates/        # Jinja2 pages (dates, managers, answer, dashboard)
├── data/             # input data grouped by date
├── reports/          # generated .xlsx reports
└── ffmpeg/           # bundled audio tooling
```

## Notes

Built under hackathon time pressure, so the code favors a working demo over polish. Keys and data paths are configured directly in the API modules.
