from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import subprocess
import shutil
import yt_dlp
from celery import Celery
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

# FastAPI app instance
app = FastAPI()

# Celery configuration
celery = Celery(
    "tasks",
    broker=f"sqla+sqlite:///celery_broker.db",
    backend=f"db+sqlite:///celery_backend.db"
)

# Ensure static directory exists
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Request model
class VideoRequest(BaseModel):
    youtube_url: str

def extract_audio_ffmpeg(video_filename):
    mp3_filename = os.path.splitext(video_filename)[0] + ".mp3"
    command = [
        "ffmpeg",
        "-i", video_filename,   # Input video file
        "-q:a", "0",            # Highest quality
        "-map", "a",            # Extract only the audio
        mp3_filename
    ]
    
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return mp3_filename

@celery.task
def download_and_convert(youtube_url):
    try:
        # Download video using yt-dlp
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"downloads/%(title)s.%(ext)s"
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_filename = ydl.prepare_filename(info)

        # Convert to MP3
        mp3_filename = extract_audio_ffmpeg(video_filename)
        
        # Move to static folder
        final_path = os.path.join(STATIC_DIR, os.path.basename(mp3_filename))
        shutil.move(mp3_filename, final_path)
        
        return {"mp3_url": f"/{STATIC_DIR}/{os.path.basename(mp3_filename)}"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/convert/")
def convert_video(request: VideoRequest, background_tasks: BackgroundTasks):
    task = download_and_convert.apply_async(args=[request.youtube_url])
    return {"task_id": task.id}

@app.get("/task/{task_id}")
def get_task_status(task_id: str):
    task = download_and_convert.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "Processing..."}
    elif task.state == "SUCCESS":
        return {"status": "Completed", "result": task.result}
    elif task.state == "FAILURE":
        return {"status": "Failed", "error": str(task.info)}
    return {"status": task.state}

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})