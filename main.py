from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import uuid
import os

app = FastAPI()

@app.post("/download")
async def download_video(data: dict):
    url = data.get("url")
    if not url:
        return JSONResponse({"success": False, "error": "Missing URL"}, status_code=400)

    unique = uuid.uuid4().hex[:8]
    filename = f"video_{unique}.mp4"

    ydl_opts = {
        "format": "18",  # vídeo mp4 360p com áudio (não usa ffmpeg)
        "outtmpl": filename,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return {"success": False, "error": str(e)}

    # expõe o arquivo na URL /file/<nome>
    return {
        "success": True,
        "file": f"/file/{filename}"
    }

@app.get("/file/{filename}")
async def serve_file(filename: str):
    if not os.path.exists(filename):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(filename, media_type="video/mp4")
