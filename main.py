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

    # Seleção automática de formato sem ffmpeg
    if "instagram.com" in url:
        formato = "mp4"  # Instagram precisa disso
    elif "tiktok.com" in url:
        formato = "mp4"  # TikTok baixa direto em MP4 sem ffmpeg
    else:
        formato = "18"   # YouTube MP4 360p com áudio

    ydl_opts = {
        "format": formato,
        "outtmpl": filename,
        "noplaylist": True,
        "merge_output_format": "mp4",  # evita erro mesmo sem ffmpeg
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return {"success": False, "error": str(e)}

    return {
        "success": True,
        "file": f"/file/{filename}"
    }

@app.get("/file/{filename}")
async def serve_file(filename: str):
    if not os.path.exists(filename):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(filename, media_type="video/mp4")
