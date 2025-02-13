# YouTube to MP3 Converter - FastAPI + Celery

## Overview
This project provides a **YouTube to MP3 Converter** using **FastAPI** as the backend and **Celery** as the task queue for background processing. It downloads a YouTube video, converts it to an MP3 file, and provides a downloadable link. The frontend is built using **Bootstrap** for a modern, minimal UI.

## Features
- Accepts YouTube URLs for video conversion.
- Uses **Celery with SQLite** for background task processing.
- Converts video to MP3 using **yt-dlp** and **MoviePy**.
- Provides a **Bootstrap-based UI** for easy interaction.
- Polls task status and updates UI dynamically.

---

## Installation & Setup

### 1. Create a Python Virtual Environment
```sh
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

### 2. Install Dependencies using uv
```sh
uv lock
uv sync
```

### 3. Run the FastAPI Backend
```sh
uvicorn main:app --port 8000
```

### 4. Start Celery Worker
```sh
celery -A main.celery worker --loglevel=info
```

---

## Project Structure
```
project/
│── main.py           # FastAPI app with Celery integration
│── worker.py         # Celery worker setup
│── templates/
│   └── index.html    # Bootstrap-based frontend
│── static/           # Stores MP3 files
│── requirements.txt  # Dependencies
│── venv/             # Virtual environment (if used)
```

---

## Usage
1. Open **http://127.0.0.1:8000/** in your browser.
2. Enter a YouTube video URL and click **Convert**.
3. The UI will display a processing status with a loader.
4. Once completed, a **Download MP3** button appears.
5. Click the button to download the converted MP3 file.

---

## Troubleshooting
- If Celery is not running properly, check logs with:
  ```sh
  celery -A main.celery worker --loglevel=debug
  ```
- Ensure SQLite database files (`celery_broker.db`, `celery_backend.db`) are accessible.
- Restart both FastAPI (`uvicorn main:app --port 8000`) and Celery (`celery -A main.celery worker --loglevel=info`) if tasks are stuck.
- Use `pip list` or `uv sync` to ensure dependencies are installed properly.

---

## License
This project is open-source and available for modification and redistribution under the **MIT License**.

